import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import {
  PRESIGN_TTL_SECONDS,
  RETENTION,
  validateUploadRequest,
} from "../../shared/policy.mjs";

/**
 * Cloudflare Worker: signs short-lived R2 PUT URLs. File bytes never pass here.
 *
 * Secrets (Worker secrets, never code):
 *   R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET,
 *   UPLOAD_TOKEN
 * Vars (wrangler.toml [vars]):
 *   R2_PUBLIC_BASE_URL, ALLOWED_ORIGINS (optional, comma separated)
 * Binding: UPLOAD_RATE_LIMITER (ratelimits, see wrangler.toml)
 */

const json = (body, status = 200, extra = {}) =>
  new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      ...extra,
    },
  });

function corsHeaders(request, env) {
  const origin = request.headers.get("Origin");
  const allowed = (env.ALLOWED_ORIGINS ?? "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  // No Origin header = non-browser client (curl / node). Allow it.
  if (!origin || allowed.includes("*") || allowed.includes(origin)) {
    return {
      "access-control-allow-origin": origin || "*",
      "access-control-expose-headers": "location",
      vary: "Origin",
    };
  }
  return null; // disallowed browser origin -> caller returns 403
}

function clientIp(request) {
  return (
    request.headers.get("CF-Connecting-IP") ||
    request.headers.get("X-Forwarded-For") ||
    "unknown"
  );
}

function tolerantEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string") return false;
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

function makeS3(env) {
  return new S3Client({
    region: "auto",
    endpoint: `https://${env.R2_ACCOUNT_ID}.r2.cloudflarestorage.com`,
    credentials: {
      accessKeyId: env.R2_ACCESS_KEY_ID,
      secretAccessKey: env.R2_SECRET_ACCESS_KEY,
    },
  });
}

function randomSuffix() {
  const bytes = new Uint8Array(6);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
}

/** Build a collision-resistant, flat object key. */
export function buildKey(validated, now = new Date()) {
  const dir = validated.filename.includes("/")
    ? validated.filename.slice(0, validated.filename.lastIndexOf("/") + 1)
    : "";
  const base = validated.filename.split("/").pop() || "file";
  const dot = base.lastIndexOf(".");
  const stem = dot > 0 ? base.slice(0, dot) : base;
  const ext = dot > 0 ? base.slice(dot) : "";
  const safeStem = stem
    .normalize("NFKD")
    .replace(/[^a-zA-Z0-9._-]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 80) || "file";
  const ts = now.toISOString().replace(/[:.]/g, "-");
  const key = `${RETENTION[validated.retention].prefix}${dir}${safeStem}-${ts}-${randomSuffix()}${ext.toLowerCase()}`;
  return { key, safeStem, ext: ext.toLowerCase() };
}

async function handlePresign(request, env, ctx) {
  const cors = corsHeaders(request, env);
  if (!cors) return json({ error: "origin not allowed" }, 403);

  if (request.method !== "POST") {
    return json({ error: "method not allowed; use POST" }, 405, cors);
  }

  // 1. Auth. Accept the compatibility token and named personal tokens.
  const configured = Object.entries(env)
    .filter(
      ([name, value]) =>
        (name === "UPLOAD_TOKEN" || /^UPLOAD_TOKEN_[A-Z0-9_]+$/.test(name)) &&
        typeof value === "string" &&
        value.length > 0,
    )
    .map(([, value]) => value);
  const provided = request.headers.get("Authorization")?.replace(/^Bearer\s+/i, "") ?? "";
  const authorized = configured.reduce(
    (matches, token) => tolerantEqual(provided, token) || matches,
    false,
  );
  if (!configured.length || !provided || !authorized) {
    return json({ error: "unauthorized" }, 401, cors);
  }

  // 2. Rate limit per client IP, so tokens from one machine share an allowance.
  // Cloudflare docs note IP keys can be shared behind NAT — acceptable here.
  if (env.UPLOAD_RATE_LIMITER) {
    const { success } = await env.UPLOAD_RATE_LIMITER.limit({
      key: clientIp(request),
    });
    if (!success) {
      return json({ error: "rate limited; retry later" }, 429, {
        ...cors,
        "retry-after": "60",
      });
    }
  }

  // 3. Parse JSON with a small body cap.
  let raw;
  try {
    if (Number(request.headers.get("Content-Length")) > 8192) {
      return json({ error: "request body too large" }, 413, cors);
    }
    raw = await request.json();
  } catch {
    return json({ error: "invalid JSON body" }, 400, cors);
  }

  // 4. Validate against the shared policy.
  const checked = validateUploadRequest(raw);
  if (!checked.ok) return json({ error: checked.error }, 400, cors);

  // 5. Release assets never expire. Require a separate token so an agent that
  // only holds the normal token fails closed if it accidentally selects release.
  if (checked.value.retention === "release") {
    const configuredRelease = env.UPLOAD_RELEASE_TOKEN;
    const providedRelease = request.headers.get("X-Release-Token")?.replace(/^Bearer\s+/i, "") ?? "";
    if (!configuredRelease || !providedRelease || !tolerantEqual(providedRelease, configuredRelease)) {
      return json(
        { error: "release retention requires a separate release token; use temp for verification media" },
        403,
        cors,
      );
    }
  }

  // 6. Sign a single PUT. Content-Length is fixed to the declared size.
  const { key } = buildKey(checked.value);
  const command = new PutObjectCommand({
    Bucket: env.R2_BUCKET,
    Key: key,
    ContentType: checked.value.contentType,
    ContentLength: checked.value.size,
  });
  const uploadUrl = await getSignedUrl(makeS3(env), command, {
    expiresIn: PRESIGN_TTL_SECONDS,
    signableHeaders: new Set(["content-type"]),
  });

  const base = (env.R2_PUBLIC_BASE_URL ?? "").replace(/\/$/, "");
  const publicUrl = base ? `${base}/${key}` : null;

  return json(
    {
      ok: true,
      key,
      uploadUrl,
      publicUrl,
      method: "PUT",
      headers: { "Content-Type": checked.value.contentType },
      expiresIn: PRESIGN_TTL_SECONDS,
      retention: checked.value.retention,
    },
    200,
    cors,
  );
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.pathname === "/health") {
      return json({ ok: true, service: "file-upload-signer" });
    }

    if (url.pathname === "/presign") {
      try {
        return await handlePresign(request, env, ctx);
      } catch (err) {
        // Never leak credentials or stack traces to the caller.
        console.error("presign failed:", err?.message ?? String(err));
        return json({ error: "internal signer error" }, 500);
      }
    }

    return json({ error: "not found" }, 404);
  },
};

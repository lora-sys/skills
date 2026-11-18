#!/usr/bin/env node
import { readFile, stat } from "node:fs/promises";
import { execFileSync } from "node:child_process";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";
import { validateUploadRequest, mimeFor } from "../shared/policy.mjs";

const MAX_ATTEMPTS = 3;
const BASE_BACKOFF_MS = 1000;
const HTTP_TIMEOUT_MS = 30_000;
const DEFAULT_UPLOAD_SIGNER_URL =
  "https://asset-upload-signer.3526039967.workers.dev";
const KEYCHAIN_SERVICE = "lora-file-upload";
const PROXY_ENV_NAMES = [
  "HTTP_PROXY",
  "HTTPS_PROXY",
  "ALL_PROXY",
  "http_proxy",
  "https_proxy",
  "all_proxy",
];

// Node fetch needs this flag before its first request to honor proxy variables.
if (
  process.env.NODE_USE_ENV_PROXY === undefined &&
  PROXY_ENV_NAMES.some((name) => process.env[name])
) {
  process.env.NODE_USE_ENV_PROXY = "1";
}

let keychainTokenRead = false;
let keychainTokenValue = "";

function readKeychainToken() {
  if (keychainTokenRead) return keychainTokenValue;
  keychainTokenRead = true;
  if (process.platform !== "darwin") return "";

  const account = process.env.USER || process.env.LOGNAME;
  if (!account) return "";
  try {
    keychainTokenValue = execFileSync(
      "/usr/bin/security",
      ["find-generic-password", "-a", account, "-s", KEYCHAIN_SERVICE, "-w"],
      { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"], timeout: 10_000 },
    ).trim();
  } catch {
    keychainTokenValue = "";
  }
  return keychainTokenValue;
}

function env(name) {
  let v = process.env[name];
  if (!v && name === "UPLOAD_SIGNER_URL") v = DEFAULT_UPLOAD_SIGNER_URL;
  if (!v && name === "UPLOAD_TOKEN") v = readKeychainToken();
  if (!v) {
    const source = name === "UPLOAD_TOKEN" ? ` or macOS Keychain item ${KEYCHAIN_SERVICE}` : "";
    fail(`missing environment variable ${name}${source} (see references/setup.md)`);
  }
  return v;
}

function fail(msg) {
  const err = new Error(msg);
  err.isUploadError = true;
  throw err;
}

function usage() {
  return `Usage: upload.mjs <file> [--retention temp|release]

Uploads one file via a presigned R2 PUT URL and prints a public link.

Env (required): UPLOAD_TOKEN (or macOS Keychain item "lora-file-upload")
Env (optional): UPLOAD_SIGNER_URL (defaults to the lora-sys signer), R2_PUBLIC_BASE_URL
`;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function parseArgs(argv) {
  const positional = argv.filter((a, i) => {
    if (a.startsWith("--")) return false;
    return argv[i - 1] !== "--retention";
  });
  const file = positional[0];
  let retention = "temp";
  const rIdx = argv.indexOf("--retention");
  if (rIdx >= 0) retention = argv[rIdx + 1];
  const confirmRelease = argv.includes("--confirm-release");
  if (argv.includes("--help") || argv.includes("-h") || !file) {
    process.stdout.write(usage());
    process.exit(0);
  }
  if (retention === "release" && !confirmRelease && !process.env.UPLOAD_RELEASE_TOKEN) {
    fail("retention=release needs --confirm-release and UPLOAD_RELEASE_TOKEN; verification media must use temp");
  }
  return { file, retention };
}

async function requestPresign({ file, size, retention }) {
  const url = env("UPLOAD_SIGNER_URL").replace(/\/$/, "") + "/presign";
  const body = JSON.stringify({
    filename: basename(file),
    size,
    contentType: mimeFor(file),
    retention,
  });
  let lastErr;
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    try {
      const headers = {
        "content-type": "application/json",
        authorization: `Bearer ${env("UPLOAD_TOKEN")}`,
      };
      if (retention === "release") {
        headers["x-release-token"] = env("UPLOAD_RELEASE_TOKEN");
      }
      const res = await fetch(url, {
        method: "POST",
        headers,
        body,
        signal: AbortSignal.timeout(HTTP_TIMEOUT_MS),
      });
      const text = await res.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch {
        throw new Error(`signer returned non-JSON (${res.status}): ${text.slice(0, 200)}`);
      }
      if (!res.ok) {
        if (res.status === 429) {
          const wait = res.headers.get("retry-after") ?? "60";
          const err = new Error(`signer 429: rate limited; wait ${wait}s; do not re-run this command`);
          err.status = 429;
          err.retryAfter = wait;
          throw err;
        }
        const err = new Error(`signer ${res.status}: ${data.error ?? text.slice(0, 200)}`);
        err.status = res.status;
        throw err;
      }
      return data;
    } catch (err) {
      lastErr = err;
      if (err.status && err.status < 500 && err.status !== 429) throw err; // non-retryable
      if (err.status === 429) throw err; // respect rate limit; no retry storm
      if (attempt < MAX_ATTEMPTS) await sleep(BASE_BACKOFF_MS * 2 ** (attempt - 1));
    }
  }
  throw lastErr;
}

async function putFile(signerResult, bytes, size) {
  const headers = { ...(signerResult.headers ?? {}) };
  // Some R2 presign flows require the exact Content-Length too; Node sets it from the body.
  let lastErr;
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    try {
      const timeoutMs = Math.max(HTTP_TIMEOUT_MS, Math.ceil((size / 512_000) * 1000));
      const res = await fetch(signerResult.uploadUrl, {
        method: "PUT",
        headers,
        body: bytes,
        signal: AbortSignal.timeout(timeoutMs),
      });
      if (!res.ok) {
        const err = new Error(`R2 PUT ${res.status}: ${(await res.text()).slice(0, 200)}`);
        err.status = res.status;
        throw err;
      }
      return;
    } catch (err) {
      lastErr = err;
      if (err.status && err.status < 500 && err.status !== 429) throw err;
      if (attempt < MAX_ATTEMPTS) await sleep(BASE_BACKOFF_MS * 2 ** (attempt - 1));
    }
  }
  throw lastErr;
}

async function verifyPublicUrl(publicUrl) {
  for (let attempt = 1; attempt <= 2; attempt++) {
    try {
      // HEAD only checks accessibility; GET would download the whole video.
      const res = await fetch(publicUrl, {
        method: "HEAD",
        signal: AbortSignal.timeout(HTTP_TIMEOUT_MS),
      });
      if (res.ok) return true;
      if (res.status >= 500 && attempt < 2) {
        await sleep(BASE_BACKOFF_MS);
        continue;
      }
      return false;
    } catch {
      if (attempt < 2) {
        await sleep(BASE_BACKOFF_MS);
        continue;
      }
      return false;
    }
  }
  return false;
}

export async function run(argv) {
  const { file, retention } = parseArgs(argv);

  const info = await stat(file).catch(() => fail(`file not found: ${file}`));
  if (!info.isFile()) fail(`not a regular file: ${file}`);

  const checked = validateUploadRequest({
    filename: basename(file),
    size: info.size,
    retention,
  });
  if (!checked.ok) fail(checked.error);

  const bytes = await readFile(file);
  if (bytes.length !== info.size) fail("file changed while reading; aborting");

  // Signer retries once per presign; if the presign expires mid-upload, re-sign once.
  let signerResult = await requestPresign({ file, size: info.size, retention });
  try {
    await putFile(signerResult, bytes, info.size);
  } catch (err) {
    if (/ 403/.test(err.message)) {
      signerResult = await requestPresign({ file, size: info.size, retention });
      await putFile(signerResult, bytes, info.size);
    } else {
      throw err;
    }
  }

  const publicUrl =
    signerResult.publicUrl ||
    (process.env.R2_PUBLIC_BASE_URL
      ? `${process.env.R2_PUBLIC_BASE_URL.replace(/\/$/, "")}/${signerResult.key}`
      : null);

  if (!publicUrl) {
    fail("upload succeeded but no public URL was returned; set R2_PUBLIC_BASE_URL");
  }

  const verified = await verifyPublicUrl(publicUrl);
  if (!verified) {
    fail("upload succeeded but public URL is not accessible; check domain binding and CORS");
  }

  return {
    ok: true,
    file,
    key: signerResult.key,
    url: publicUrl,
    retention,
    size: info.size,
    verified: true,
  };
}

// CLI entry: only run when executed directly (allows in-process tests via import).
const isMain =
  process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1];
if (isMain) {
  run(process.argv.slice(2))
    .then((result) => process.stdout.write(JSON.stringify(result) + "\n"))
    .catch((err) => {
      console.error(`upload: ${err?.message ?? String(err)}`);
      process.exit(1);
    });
}

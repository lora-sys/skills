// Shared upload policy. Imported by both the Worker and the local client.
// Keeping one copy prevents the signer and the uploader from disagreeing.

export const MAX_SIZE_BYTES = 500 * 1024 * 1024; // 500 MiB hard ceiling
export const PRESIGN_TTL_SECONDS = 15 * 60;

// Extension -> MIME. Unknown extensions are rejected; no sniffing of user input.
export const ALLOWED_TYPES = Object.freeze({
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".gif": "image/gif",
  ".avif": "image/avif",
  ".mp4": "video/mp4",
  ".webm": "video/webm",
  ".mov": "video/quicktime",
  ".m4v": "video/x-m4v",
  ".pdf": "application/pdf",
  ".txt": "text/plain",
  ".md": "text/markdown",
  ".json": "application/json",
  ".log": "text/plain",
  ".zip": "application/zip",
});

export const RETENTION = Object.freeze({
  temp: { prefix: "temp/", days: 90 },
  release: { prefix: "release/", days: 0 }, // 0 = keep until manually deleted
});

export const RETENTION_VALUES = Object.freeze(Object.keys(RETENTION));

/**
 * Return the MIME type for a file name, or null when the extension is unknown.
 * @param {string} name
 */
export function mimeFor(name) {
  const dot = String(name).lastIndexOf(".");
  if (dot < 0) return null;
  return ALLOWED_TYPES[String(name).slice(dot).toLowerCase()] ?? null;
}

/**
 * Validate an upload request. Returns { ok: true, value } or { ok: false, error }.
 * @param {{ filename?: unknown, size?: unknown, contentType?: unknown, retention?: unknown }} input
 */
export function validateUploadRequest(input) {
  const filename = String(input?.filename ?? "").trim();
  if (!filename || filename.length > 200) {
    return { ok: false, error: "filename must be 1-200 characters" };
  }
  if (/[\u0000-\u001f\u007f]/.test(filename)) {
    return { ok: false, error: "filename contains control characters" };
  }
  // Allow one optional slash for subdirectories, but reject traversal and abs paths.
  const parts = filename.split("/");
  if (parts.length > 2 || parts.some((p) => !p || p === "." || p === "..")) {
    return { ok: false, error: "filename contains an unsafe path" };
  }
  if (/^[a-zA-Z]:/.test(filename)) {
    return { ok: false, error: "filename must be relative" };
  }

  // Credential-like names must never enter a public bucket, even as renamed evidence.
  const lowerBase = (filename.split("/").pop() || "").toLowerCase();
  if (
    lowerBase.startsWith(".env") ||
    /^(id_rsa|id_dsa|id_ecdsa|id_ed25519)(\.|$)/.test(lowerBase) ||
    /\.(pem|key|p12|pfx)$/.test(lowerBase) ||
    lowerBase.includes("secret")
  ) {
    return { ok: false, error: "credential-like filenames are not allowed" };
  }

  const expectedMime = mimeFor(filename);
  if (!expectedMime) {
    return { ok: false, error: "unsupported file extension" };
  }

  const size = Number(input?.size);
  if (!Number.isSafeInteger(size) || size <= 0 || size > MAX_SIZE_BYTES) {
    return { ok: false, error: `size must be a positive integer <= ${MAX_SIZE_BYTES}` };
  }

  if (input?.contentType != null && String(input.contentType) !== expectedMime) {
    return { ok: false, error: `contentType must be ${expectedMime} for this extension` };
  }

  const retention = input?.retention ?? "temp";
  if (!RETENTION_VALUES.includes(retention)) {
    return { ok: false, error: `retention must be one of: ${RETENTION_VALUES.join(", ")}` };
  }

  return {
    ok: true,
    value: { filename, size, contentType: expectedMime, retention },
  };
}

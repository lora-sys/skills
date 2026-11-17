import assert from "node:assert/strict";
import { test } from "node:test";
import { validateUploadRequest, mimeFor, MAX_SIZE_BYTES } from "../../shared/policy.mjs";

const base = { filename: "shot.png", size: 1024, contentType: "image/png", retention: "temp" };

test("accepts a normal image", () => {
  const r = validateUploadRequest(base);
  assert.equal(r.ok, true);
  assert.equal(r.value.contentType, "image/png");
  assert.equal(r.value.retention, "temp");
});

test("defaults retention to temp", () => {
  const r = validateUploadRequest({ filename: "a.mp4", size: 10 });
  assert.equal(r.ok, true);
  assert.equal(r.value.retention, "temp");
});

test("rejects oversized files", () => {
  assert.equal(validateUploadRequest({ ...base, size: MAX_SIZE_BYTES + 1 }).ok, false);
});

test("rejects zero and non-integer sizes", () => {
  assert.equal(validateUploadRequest({ ...base, size: 0 }).ok, false);
  assert.equal(validateUploadRequest({ ...base, size: 1.5 }).ok, false);
});

test("rejects unknown extensions", () => {
  assert.equal(validateUploadRequest({ ...base, filename: "evil.exe" }).ok, false);
});

test("rejects content type mismatch", () => {
  assert.equal(validateUploadRequest({ ...base, contentType: "text/html" }).ok, false);
});

test("rejects path traversal and absolute paths", () => {
  assert.equal(validateUploadRequest({ ...base, filename: "../a.png" }).ok, false);
  assert.equal(validateUploadRequest({ ...base, filename: "/a.png" }).ok, false);
  assert.equal(validateUploadRequest({ ...base, filename: "C:/a.png" }).ok, false);
});

test("rejects control characters and bad retention", () => {
  assert.equal(validateUploadRequest({ ...base, filename: "a\n.png" }).ok, false);
  assert.equal(validateUploadRequest({ ...base, retention: "forever" }).ok, false);
});

test("accepts release retention", () => {
  assert.equal(validateUploadRequest({ ...base, retention: "release" }).ok, true);
});

test("mimeFor is case-insensitive and null for unknown", () => {
  assert.equal(mimeFor("A.JPG"), "image/jpeg");
  assert.equal(mimeFor("noext"), null);
});


test("rejects credential-like filenames", () => {
  for (const name of [".env", ".env.local", "id_rsa", "server.key", "cert.pem", "api_secret.txt"]) {
    const result = validateUploadRequest({ filename: name, size: 1 });
    assert.equal(result.ok, false, `${name} must be rejected`);
  }
});

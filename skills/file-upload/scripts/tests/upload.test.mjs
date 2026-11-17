import assert from "node:assert/strict";
import { test } from "node:test";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { run } from "../upload.mjs";

function tempFile(name, content) {
  const dir = mkdtempSync(join(tmpdir(), "fu-test-"));
  const file = join(dir, name);
  writeFileSync(file, content);
  return file;
}

function stubFetch(handler) {
  globalThis.__origFetch ??= globalThis.fetch;
  globalThis.fetch = handler;
  return () => {
    globalThis.fetch = globalThis.__origFetch;
  };
}

test("run(): presign -> PUT -> public URL end to end", async () => {
  const file = tempFile("shot.png", Buffer.from("12345678"));
  process.env.UPLOAD_SIGNER_URL = "https://signer.example.com/";
  process.env.UPLOAD_TOKEN = "test-token";

  const calls = [];
  const restore = stubFetch(async (url, opts) => {
    calls.push({ url: String(url), opts });
    if (String(url).endsWith("/presign")) {
      const body = JSON.parse(opts.body);
      assert.equal(body.filename, "shot.png");
      assert.equal(body.size, 8);
      assert.equal(body.retention, "temp");
      assert.equal(body.contentType, "image/png");
      assert.equal(opts.headers.authorization, "Bearer test-token");
      return new Response(
        JSON.stringify({
          ok: true,
          key: "temp/shot-abc.png",
          uploadUrl: "https://r2.example.com/put",
          publicUrl: "https://assets.example.com/temp/shot-abc.png",
          headers: { "Content-Type": "image/png" },
          retention: "temp",
        }),
        { status: 200, headers: { "content-type": "application/json" } },
      );
    }
    if (String(url) === "https://r2.example.com/put") {
      assert.equal(opts.method, "PUT");
      assert.equal(opts.headers["Content-Type"], "image/png");
      assert.equal(opts.body.length, 8);
      return new Response("", { status: 200 });
    }
    if (String(url) === "https://assets.example.com/temp/shot-abc.png") {
      assert.equal(opts.method, "HEAD");
      return new Response("data", { status: 200 });
    }
    throw new Error(`unexpected fetch: ${url}`);
  });

  let out;
  try {
    out = await run([file, "--retention", "temp"]);
  } finally {
    restore();
  }

  assert.equal(out.ok, true);
  assert.equal(out.retention, "temp");
  assert.equal(out.size, 8);
  assert.equal(out.url, "https://assets.example.com/temp/shot-abc.png");
  assert.equal(out.verified, true);
  assert.equal(calls.length, 3, "expect presign, PUT, and public URL GET");
});

test("run(): rejects unsupported files before any network call", async () => {
  const file = tempFile("evil.exe", Buffer.from("x"));
  let called = false;
  const restore = stubFetch(async () => {
    called = true;
    throw new Error("should not be called");
  });
  try {
    await assert.rejects(run([file]), /unsupported file extension/);
    assert.equal(called, false);
  } finally {
    restore();
  }
});

test("run(): falls back to R2_PUBLIC_BASE_URL when signer omits publicUrl", async () => {
  const file = tempFile("a.jpg", Buffer.from("1234"));
  process.env.UPLOAD_SIGNER_URL = "https://signer.example.com";
  process.env.UPLOAD_TOKEN = "t";
  process.env.R2_PUBLIC_BASE_URL = "https://fallback.example.com/";
  const restore = stubFetch(async (url) => {
    if (String(url).endsWith("/presign")) {
      return new Response(
        JSON.stringify({ ok: true, key: "temp/2026/a.jpg", uploadUrl: "https://r2.example.com/put" }),
        { status: 200, headers: { "content-type": "application/json" } },
      );
    }
    return new Response("", { status: 200 });
  });
  let out;
  try {
    out = await run([file]);
  } finally {
    restore();
    delete process.env.R2_PUBLIC_BASE_URL;
  }
  assert.equal(out.url, "https://fallback.example.com/temp/2026/a.jpg");
});

test("run(): non-retryable signer error (401) fails fast without PUT", async () => {
  const file = tempFile("c.png", Buffer.from("1234"));
  process.env.UPLOAD_SIGNER_URL = "https://signer.example.com";
  process.env.UPLOAD_TOKEN = "bad-token";
  let presigns = 0;
  const restore = stubFetch(async () => {
    presigns++;
    return new Response(JSON.stringify({ error: "unauthorized" }), {
      status: 401,
      headers: { "content-type": "application/json" },
    });
  });
  try {
    await assert.rejects(run([file]), /signer 401: unauthorized/);
    assert.equal(presigns, 1, "must not retry a 401");
  } finally {
    restore();
  }
});

test("run(): re-signs once on expired (403) PUT", async () => {
  const file = tempFile("b.webm", Buffer.from("12345"));
  process.env.UPLOAD_SIGNER_URL = "https://signer.example.com";
  process.env.UPLOAD_TOKEN = "t";
  let presigns = 0;
  let puts = 0;
  const restore = stubFetch(async (url, opts) => {
    if (String(url).endsWith("/presign")) {
      presigns++;
      return new Response(
        JSON.stringify({
          ok: true,
          key: "temp/b-abc.webm",
          uploadUrl: "https://r2.example.com/put",
          publicUrl: "https://assets.example.com/temp/b-abc.webm",
        }),
        { status: 200, headers: { "content-type": "application/json" } },
      );
    }
    if (opts.method === "HEAD") return new Response(null, { status: 200 });
    puts++;
    if (puts === 1) return new Response("expired", { status: 403 });
    return new Response("", { status: 200 });
  });
  let out;
  try {
    out = await run([file]);
  } finally {
    restore();
  }
  assert.equal(presigns, 2, "re-signed after 403");
  assert.equal(puts, 2, "two PUT attempts only; HEAD is not a PUT");
  assert.equal(out.ok, true);
});

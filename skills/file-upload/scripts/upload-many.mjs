#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { stat } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const uploader = join(here, "upload.mjs");

// One session should not write unbounded bytes into R2. Raise only with --force.
const MAX_FILES = 10;
const MAX_BATCH_BYTES = 1024 * 1024 * 1024; // 1 GiB

const rawArgs = process.argv.slice(2);
if (rawArgs.length === 0 || rawArgs.includes("--help") || rawArgs.includes("-h")) {
  process.stdout.write(`Usage: upload-many.mjs [--retention temp|release] [--force] <file> [<file> ...]

Uploads files one by one. Prints one JSON line per file, then a summary line.
A failed file does not stop the batch. Default budget: ${MAX_FILES} files / 1 GiB total.
--force raises the local budget only; the signer still enforces per-file limits.
Use --retention release only for approved permanent assets.\n`);
  process.exit(0);
}

const force = rawArgs.includes("--force");
const args = rawArgs.filter((a) => a !== "--force");
const retentionIdx = args.indexOf("--retention");
const retention = retentionIdx >= 0 && args[retentionIdx + 1] === "release" ? "release" : "temp";
const files = args.filter((a, i) => !a.startsWith("--") && args[i - 1] !== "--retention");

if (files.length === 0) {
  process.stderr.write("upload-many: no files given\n");
  process.exit(1);
}

const infos = await Promise.all(
  files.map(async (file) => {
    try {
      return { file, size: (await stat(file)).size };
    } catch {
      return { file, error: "not found" };
    }
  }),
);
const totalBytes = infos.reduce((sum, f) => sum + (f.size ?? 0), 0);
if (!force && (files.length > MAX_FILES || totalBytes > MAX_BATCH_BYTES)) {
  process.stderr.write(
    `upload-many: batch budget exceeded: ${files.length} files, ${totalBytes} bytes ` +
      `(limit ${MAX_FILES} files / ${MAX_BATCH_BYTES} bytes). Upload in smaller batches or use --force.\n`,
  );
  process.exit(1);
}

const results = [];
for (const file of files) {
  const cmdArgs = [uploader, file];
  if (retention === "release") cmdArgs.push("--retention", "release", "--confirm-release");
  const res = spawnSync(process.execPath, cmdArgs, { encoding: "utf8" });
  if (res.status !== 0) {
    process.stderr.write(`upload-many: ${file}: ${res.stderr.trim()}\n`);
    results.push({ ok: false, file, error: res.stderr.trim() });
  } else {
    results.push({ ok: true, ...JSON.parse(res.stdout.trim()) });
  }
}

const ok = results.filter((r) => r.ok);
process.stdout.write(
  JSON.stringify({ ok: true, summary: true, uploaded: ok.length, failed: results.length - ok.length }) + "\n",
);
if (ok.length !== results.length) process.exitCode = 1;

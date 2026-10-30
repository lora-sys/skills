import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { test } from "node:test";

const dirs = new Set<string>();

export const tempDir = (prefix: string) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), prefix));
  dirs.add(dir);
  return dir;
};

test.after(() => {
  for (const dir of dirs) fs.rmSync(dir, { recursive: true, force: true });
});

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { test } from "node:test";

export const createTempDirFactory = () => {
  const dirs = new Set<string>();

  test.after(() => {
    const errors: unknown[] = [];
    for (const dir of dirs) {
      try {
        fs.rmSync(dir, { recursive: true, force: true });
      } catch (error) {
        errors.push(error);
      }
    }
    dirs.clear();
    if (errors.length)
      throw new AggregateError(errors, `Failed to remove ${errors.length} Statechart test temp dirs`);
  });

  return (prefix: string) => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), prefix));
    dirs.add(dir);
    return dir;
  };
};

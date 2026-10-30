import assert from "node:assert/strict";
import path from "node:path";
import { test } from "node:test";
import { resolveToolPaths } from "../run.ts";

test("resolves caller-relative TLC and Java paths before running from a snapshot folder", () => {
  const caller = path.join(path.sep, "work", "project");
  assert.deepEqual(
    resolveToolPaths(
      { TLA2TOOLS: "vendor/tla2tools.jar", JAVA: "./jdk/bin/java" },
      caller,
    ),
    {
      jar: path.join(caller, "vendor", "tla2tools.jar"),
      java: path.join(caller, "jdk", "bin", "java"),
    },
  );
});

test("keeps a Java executable name for PATH lookup", () => {
  assert.deepEqual(resolveToolPaths({ TLA2TOOLS: "/opt/tla/tla2tools.jar", JAVA: "java" }), {
    jar: "/opt/tla/tla2tools.jar",
    java: "java",
  });
});

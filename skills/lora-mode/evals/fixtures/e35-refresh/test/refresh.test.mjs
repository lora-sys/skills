import assert from "node:assert/strict";
import test from "node:test";
import { refresh, reset } from "../src/refresh.mjs";

test("one refresh token succeeds at most once under concurrent requests", async () => {
  reset();
  let arrivals = 0;
  let release;
  const bothVerified = new Promise((resolve) => { release = resolve; });
  const verify = async () => {
    arrivals += 1;
    if (arrivals === 2) release();
    await bothVerified;
    return true;
  };

  const results = await Promise.all([refresh({ verify }), refresh({ verify })]);
  assert.equal(results.filter((result) => result.ok).length, 1);
});

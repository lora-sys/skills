let currentToken = "initial";
let nextToken = 1;
const consumed = new Set();

export function reset() {
  currentToken = "initial";
  nextToken = 1;
  consumed.clear();
}

export async function refresh({ verify = async () => true } = {}) {
  const presented = currentToken;
  if (consumed.has(presented)) return { ok: false };
  if (!(await verify(presented))) return { ok: false };
  consumed.add(presented);
  currentToken = `refresh-${nextToken++}`;
  return { ok: true, token: currentToken };
}

import worker from "./src/index.js";
const env = { ASSETS: { fetch: () => new Response("asset") } };
const cases = [
  ["http://nusuphd.com/about/", 301, "https://nusuphd.com/about/"],
  ["https://www.nusuphd.com/x?y=1", 301, "https://nusuphd.com/x?y=1"],
  ["http://www.nusuphd.com/", 301, "https://nusuphd.com/"],
  ["https://nusuphd.com/", 200, null],
  ["https://ddunddun-leak.rlawhddls.workers.dev/", 200, null],
];
for (const [u, st, loc] of cases) {
  const r = await worker.fetch(new Request(u), env);
  if (r.status !== st || (loc && r.headers.get("location") !== loc)) throw new Error(`FAIL ${u} ${r.status} ${r.headers.get("location")}`);
}
console.log("redirect checks ok");

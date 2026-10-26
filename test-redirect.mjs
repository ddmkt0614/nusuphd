import worker from "./src/index.js";
const env = { ASSETS: { fetch: () => new Response("asset") } };
const enc = (p) => "https://nusuphd.com" + encodeURI(p);
const cases = [
  ["http://nusuphd.com/about/", 301, "https://nusuphd.com/about/"],
  ["https://www.nusuphd.com/x?y=1", 301, "https://nusuphd.com/x?y=1"],
  ["http://www.nusuphd.com/", 301, "https://nusuphd.com/"],
  ["https://nusuphd.com/", 200, null],
  ["https://nusuphd.wufudenv.workers.dev/", 200, null],
  // 옛 영문 주소 → 한글 주소(한 번에)
  ["https://nusuphd.com/area/seoul/jongno/gahoe-dong/", 301, enc("/서울-종로구-가회동-누수탐지/")],
  ["http://www.nusuphd.com/area/seoul/jongno/gahoe-dong", 301, enc("/서울-종로구-가회동-누수탐지/")],
  ["https://nusuphd.com/area/seoul/jongno/index.html", 301, enc("/서울-종로구-누수탐지/")],
  ["https://nusuphd.com/station/gangnam-station/?q=1", 301, enc("/강남역-누수탐지/") + "?q=1"],
  ["https://nusuphd.com/area/", 200, null],
  ["https://nusuphd.com/" + encodeURI("서울-종로구-가회동-누수탐지") + "/", 200, null],
];
for (const [u, st, loc] of cases) {
  const r = await worker.fetch(new Request(u), env);
  if (r.status !== st || (loc && r.headers.get("location") !== loc)) throw new Error(`FAIL ${u} ${r.status} ${r.headers.get("location")}`);
}
console.log("redirect checks ok");

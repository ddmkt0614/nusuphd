import worker from "./src/index.js";
let lastAsset = "";
// 정적 파일 흉내: 끝 슬래시 없는 폴더 주소는 307 로 슬래시 붙이기
const env = { ASSETS: { fetch: (req) => {
  const u = new URL(req.url); lastAsset = u.pathname;
  if (u.pathname === "/_sub/nowon/x") return new Response(null, { status: 307, headers: { location: "/_sub/nowon/x/" } });
  return new Response("asset");
} } };
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
  ["https://nusuphd.com/area/seoul/gwangjin/hwayang-dong/index.html", 301, enc("/서울-광진구-화양동-누수탐지/")],
  ["https://nusuphd.com/area/seoul/gwangjin/hwayang-dong/?q=1", 301, enc("/서울-광진구-화양동-누수탐지/") + "?q=1"],
  // 동 대표 쪽(2026-10-28): 옛 영문 주소 → /{구}-{동}-누수탐지/, 보관 상세 주소는 그대로 404
  ["https://nusuphd.com/area/seoul/jungnang/junghwa-dong/", 301, enc("/중랑구-중화동-누수탐지/")],
  ["http://www.nusuphd.com/area/seoul/dobong/banghak-dong", 301, enc("/도봉구-방학동-누수탐지/")],
  ["https://nusuphd.com/" + encodeURI("서울-중랑구-중화동-누수탐지") + "/", 200, null],
  // 아직 보관 중인 페이지의 옛 주소는 옮기지 않음(정적 파일 → 404 페이지)
  ["https://nusuphd.com/area/seoul/jongno/", 200, null],
  ["https://nusuphd.com/station/gangnam-station/", 200, null],
  ["https://nusuphd.com/area/", 200, null],
  ["https://nusuphd.com/" + encodeURI("서울-종로구-가회동-누수탐지") + "/", 200, null],
  // 하위 주소 사이트(nowon)
  ["https://nowon.nusuphd.com/", 200, null, "/_sub/nowon/"],
  ["https://nowon.nusuphd.com/" + encodeURI("서울-노원구-공릉동-누수탐지") + "/", 200, null, "/_sub/nowon/" + encodeURI("서울-노원구-공릉동-누수탐지") + "/"],
  ["https://nowon.nusuphd.com/assets/style.css", 200, null, "/assets/style.css"],
  ["https://nowon.nusuphd.com/x", 307, "https://nowon.nusuphd.com/x/"],
  ["http://nowon.nusuphd.com/a/?q=1", 301, "https://nowon.nusuphd.com/a/?q=1"],
  ["https://nusuphd.com/_sub/nowon/", 200, null, "/__none__/"],
  ["https://nusuphd.com/area/seoul/nowon/gongreung-dong/?q=1", 301, "https://nowon.nusuphd.com/" + encodeURI("서울-노원구-공릉동-누수탐지") + "/?q=1"],
  ["https://nusuphd.com/" + encodeURI("서울-노원구-누수탐지") + "/", 301, "https://nowon.nusuphd.com/"],
  ["https://other.nusuphd.com/", 200, null],
];
for (const [u, st, loc, asset] of cases) {
  lastAsset = "";
  const r = await worker.fetch(new Request(u), env);
  if (r.status !== st || (loc && r.headers.get("location") !== loc)) throw new Error(`FAIL ${u} ${r.status} ${r.headers.get("location")}`);
  if (asset && lastAsset !== asset) throw new Error(`FAIL ${u} asset ${lastAsset}`);
}
console.log("redirect checks ok");

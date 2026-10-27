// 누수박사: http → https, www.nusuphd.com → nusuphd.com 영구 이동, 옛 영문 지역·역 주소 → 한글 주소 영구 이동, 나머지는 정적 파일.
// 하위 주소(nowon.nusuphd.com 등)는 public/_sub/<이름>/ 폴더를 그 호스트의 사이트로 보여 준다. 본 도메인에서 /_sub/ 는 없는 주소.
import OLD_TO_NEW from "./redirects.json" with { type: "json" };

const HOST = "nusuphd.com";
const SUBS = new Set(["nowon"]);

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const sub = url.hostname.endsWith(`.${HOST}`) ? url.hostname.slice(0, -HOST.length - 1) : null;
    if (sub && SUBS.has(sub)) {
      if (url.protocol === "http:") {
        url.protocol = "https:";
        return Response.redirect(url.toString(), 301);
      }
      if (url.pathname.startsWith("/assets/")) return env.ASSETS.fetch(request);  // 그림·글꼴·스크립트는 본 사이트 것 공유
      const dir = `/_sub/${sub}`;
      const inner = new URL(url);
      inner.pathname = dir + url.pathname;
      const res = await env.ASSETS.fetch(new Request(inner, request));
      const loc = res.headers.get("location");
      if (!loc) return res;
      // 끝 슬래시 맞춤 등 정적 파일 쪽 이동은 하위 주소 기준으로 돌려 준다
      const to = new URL(loc, inner);
      to.hostname = url.hostname;
      if (to.pathname.startsWith(dir + "/")) to.pathname = to.pathname.slice(dir.length);
      return new Response(null, { status: res.status, headers: { location: to.toString() } });
    }
    const isCustom = url.hostname === HOST || url.hostname === `www.${HOST}`;
    if (url.pathname.startsWith("/_sub/")) {
      return env.ASSETS.fetch(new Request(new URL("/__none__/", url), request));  // 404 페이지
    }
    // 옛 주소(/area/seoul/jongno/gahoe-dong/, /station/gangnam-station/ 등): 끝 슬래시·index.html 유무와 상관없이 한 번에 새 주소로
    const oldPath = url.pathname.replace(/index\.html$/, "").replace(/\/?$/, "/");
    let decoded = oldPath;
    try { decoded = decodeURIComponent(oldPath); } catch {}
    const moved = OLD_TO_NEW[oldPath] ?? OLD_TO_NEW[decoded];
    if (moved || (isCustom && (url.protocol === "http:" || url.hostname !== HOST))) {
      if (moved?.startsWith("https://")) {                        // 하위 주소로 옮긴 페이지
        const to = new URL(moved);
        to.search = url.search;
        return Response.redirect(to.toString(), 301);
      }
      if (isCustom) {
        url.protocol = "https:";
        url.hostname = HOST;
      }
      if (moved) url.pathname = moved;
      return Response.redirect(url.toString(), 301);
    }
    return env.ASSETS.fetch(request);
  }
};

// 누수박사: http → https, www.nusuphd.com → nusuphd.com 영구 이동, 옛 영문 지역·역 주소 → 한글 주소 영구 이동, 나머지는 정적 파일.
import OLD_TO_NEW from "./redirects.json" with { type: "json" };

const HOST = "nusuphd.com";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const isCustom = url.hostname === HOST || url.hostname === `www.${HOST}`;
    // 옛 주소(/area/seoul/jongno/gahoe-dong/, /station/gangnam-station/ 등): 끝 슬래시·index.html 유무와 상관없이 한 번에 새 주소로
    const oldPath = url.pathname.replace(/index\.html$/, "").replace(/\/?$/, "/");
    const moved = OLD_TO_NEW[oldPath];
    if (moved || (isCustom && (url.protocol === "http:" || url.hostname !== HOST))) {
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

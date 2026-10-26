// 누수박사: http → https, www.nusuphd.com → nusuphd.com 영구 이동, 나머지는 정적 파일.
const HOST = "nusuphd.com";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const isCustom = url.hostname === HOST || url.hostname === `www.${HOST}`;
    if (isCustom && (url.protocol === "http:" || url.hostname !== HOST)) {
      url.protocol = "https:";
      url.hostname = HOST;
      return Response.redirect(url.toString(), 301);
    }
    return env.ASSETS.fetch(request);
  }
};

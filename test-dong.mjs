// 동 대표 쪽(/{구}-{동}-누수탐지/) 검사: 제목·H1·키워드 횟수·사진 전용·지역 안내 양방향 링크·문장 겹침·보관 상세 노출 금지
import { readFileSync, existsSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const PUB = "public";
const SITE = "https://nusuphd.com";
// hold: 같은 법정동의 보관 상세(열지 않는다 — 열면 같은 검색어로 서로 다툼). legal: 행정동 쪽의 법정동. photos: 사진 수 범위.
// hubLine: /area/ 구 칸에 칩 대신 '이름+한 줄+링크'로 붙은 쪽(행정동 이름은 칩에 없음)
const DONGS = [
  { gu: "중랑구", dong: "중화동", hold: "/서울-중랑구-중화동-누수탐지/" },
  { gu: "도봉구", dong: "방학동", hold: "/서울-도봉구-방학동-누수탐지/" },
];
const NOT_HERE = ["다른 현장", "현장은 아닙니다", "현장이 아닙니다", "현장을 찍은 것은 아닙니다", "참고 사진"];
const BANNED = ["최고", "1위", "완벽", "하수구", "막힘"];
const OTHER_SITES = ["justnusu.com", "ddnusu.com", "smartnusu.com"];
// 한 글자 어간('창동' → '창')은 일반 낱말과 겹쳐 빼고, 행정동 쪽은 법정동 이름도 막는다
const stem = (d) => d.replace(/동$/, "");
const REGION_ALL = [...new Set(DONGS.flatMap((p) => [p.gu, p.dong, p.gu.replace(/구$/, ""), ...(p.legal ? [p.legal] : []), ...[p.dong, p.legal].filter(Boolean).map(stem).filter((s) => s.length >= 2)])), "서울"];

const walk = (d) => readdirSync(d).flatMap((f) => (statSync(join(d, f)).isDirectory() ? walk(join(d, f)) : [join(d, f)]));
const files = walk(PUB);
const htmls = files.filter((f) => f.endsWith(".html"));
const read = (f) => readFileSync(f, "utf8");
const text = (h) => h.slice(h.indexOf("<main>"), h.indexOf("</main>")).replace(/<script[\s\S]*?<\/script>/g, " ").replace(/<[^>]+>/g, " ").replace(/&amp;/g, "&").replace(/\s+/g, " ").trim();
const meta = (h, k) => (h.match(new RegExp(`<meta (?:name|property)="${k}" content="([^"]*)"`)) || [])[1];
const fails = [];
const check = (name, ok, info = "") => { if (!ok) fails.push(`${name} ${info}`); };

const pageOf = (p) => join(PUB, `${p.gu}-${p.dong}-누수탐지`, "index.html");
const pathOf = (p) => `/${p.gu}-${p.dong}-누수탐지/`;
const area = read(join(PUB, "area", "index.html"));
const sitemap = read(join(PUB, "sitemap.xml"));
const home = read(join(PUB, "index.html"));
const mainOf = (h) => h.slice(h.indexOf("<main>"), h.indexOf("</main>"));
// 동 대표 쪽 폴더가 DONGS 목록과 같아야 한다(목록에 안 적은 새 쪽이 검사에서 빠지지 않게)
const found = readdirSync(PUB).filter((d) => /^[^-]+구-[^-]+동-누수탐지$/.test(d)).sort();
const listed = DONGS.map((p) => `${p.gu}-${p.dong}-누수탐지`).sort();
check("동 대표 쪽 폴더 = DONGS", JSON.stringify(found) === JSON.stringify(listed), found.join(","));
const K = 15;
// 한쪽은 3칸 간격, 다른 쪽은 모든 위치에서 조각을 떠서 시작 위치가 어긋난 복사도 잡는다
const grams = (t, step = 3) => { t = t.replace(/\s/g, ""); const s = new Set(); for (let i = 0; i + K <= t.length; i += step) s.add(t.slice(i, i + K)); return s; };
const overlap = (x, y) => { const a = grams(x), b = grams(y, 1); return [...a].filter((g) => b.has(g)).length / a.size; };

for (const p of DONGS) {
  const f = pageOf(p), path = pathOf(p), name = `${p.gu} ${p.dong} 누수탐지`;
  check(`${path} 파일`, existsSync(f));
  if (!existsSync(f)) continue;
  const h = read(f), body = text(h);
  const title = (h.match(/<title>([^<]*)<\/title>/) || [])[1] || "";
  check(`${path} 제목 '${name} '로 시작·'누수탐지' 1번`, title.startsWith(`${name} `) && title.split("누수탐지").length === 2, title);
  const h1s = h.match(/<h1[^>]*>([\s\S]*?)<\/h1>/g) || [];
  check(`${path} H1 1개·'${name}'로 시작`, h1s.length === 1 && h1s[0].replace(/<[^>]+>/g, "").trim().startsWith(name), h1s.join());
  const nA = body.split(name).length - 1;
  const nB = (body.match(new RegExp(`${p.dong} 누수(?!탐지)`, "g")) || []).length;
  check(`${path} 본문 '${name}' 5회·'${p.dong} 누수' 5회`, nA === 5 && nB === 5, `${nA}·${nB}`);
  const h2s = (h.match(/<h2[^>]*>[\s\S]*?<\/h2>/g) || []).map((x) => x.replace(/<[^>]+>/g, ""));
  check(`${path} 소제목에 '${p.gu} ${p.dong}' 3번까지`, h2s.filter((x) => x.includes(`${p.gu} ${p.dong}`)).length <= 3);
  check(`${path} 글자 수 1,800~2,800`, body.length >= 1800 && body.length <= 2800, body.length);
  const desc = meta(h, "description") || "";
  check(`${path} 설명 80자 이내·og 같음`, desc.length > 0 && desc.length <= 80 && meta(h, "og:description") === desc, desc.length);
  const canon = (h.match(/<link rel="canonical" href="([^"]+)"/) || [])[1];
  check(`${path} canonical·og:url`, canon === SITE + encodeURI(path) && meta(h, "og:url") === canon, canon);
  check(`${path} 금지 문구 없음`, !NOT_HERE.some((w) => h.includes(w)));
  check(`${path} 본문 금지어 없음`, !BANNED.some((w) => body.includes(w)), BANNED.filter((w) => body.includes(w)).join(","));
  if (p.hubLine) {
    const line = (area.match(new RegExp(`<p class="hub-line"><a href="${path}">${p.dong} 누수탐지</a> ([^<]+)</p>`)) || [])[1];
    check(`/area/ 구 칸에 ${p.dong} 이름+한 줄+링크`, !!line);
    check(`${path} 구 칸 한 줄이 본문과 다름`, line && !body.includes(line.trim()));
  }
  // 지역 안내(/area/) 양방향
  check(`${path} → /area/ 링크(본문 안)`, mainOf(h).includes('href="/area/"'));
  check(`/area/ → ${path} 링크`, area.includes(`href="${path}"`));
  check(`${path} sitemap(인코딩 주소)`, sitemap.includes(`<loc>${SITE}${encodeURI(path)}</loc>`) && !sitemap.includes(`<loc>${SITE}${path}</loc>`));
  check(`${path} 동네 검색 목록(홈·/area/)`, [area, home].every((x) => x.includes(`["${p.dong}", "${p.gu}", "${path}"]`)));
  check(`${path} 서울 탭 카드(홈·/area/)`, [area, home].every((x) => x.includes(`<a href="${path}"><strong>서울 ${p.gu} ${p.dong} 누수탐지</strong></a>`)));
  // 사진: 파일 있음, 쪽 안에서 1번씩, 다른 쪽에 안 나옴, 설명에 지역 이름 없음
  const imgs = [...h.matchAll(/<img [^>]*src="(\/assets\/photo\/dong\/[^"]+)"[^>]*alt="([^"]*)"/g)].map((m) => ({ src: m[1], alt: m[2] }));
  const [lo, hi] = p.photos || [7, 9];
  check(`${path} 사진 ${lo}~${hi}장`, imgs.length >= lo && imgs.length <= hi, imgs.length);
  check(`${path} 사진 파일 있음`, imgs.every((x) => existsSync(join(PUB, x.src))));
  check(`${path} 사진 쪽 안에서 1번씩`, new Set(imgs.map((x) => x.src)).size === imgs.length);
  const elsewhere = htmls.filter((g) => g !== f && imgs.some((x) => read(g).includes(x.src)));
  check(`${path} 사진이 다른 쪽에 안 나옴`, elsewhere.length === 0, elsewhere.join(","));
  const caps = [...h.matchAll(/<figcaption>([\s\S]*?)<\/figcaption>/g)].map((m) => m[1].replace(/<[^>]+>/g, ""));
  const words = [...imgs.map((x) => x.alt), ...caps];
  check(`${path} 사진 설명·alt 에 지역 이름 없음`, words.every((t) => !REGION_ALL.some((w) => t.includes(w))), words.filter((t) => REGION_ALL.some((w) => t.includes(w))).join("|"));
  // 보관 상세는 열지 않고, 어디에도 이어지지 않는다
  check(`${p.hold} 보관 상태`, !existsSync(join(PUB, p.hold)));
  const leak = files.filter((g) => /\.(html|xml|txt)$/.test(g)).filter((g) => { const s = read(g); return s.includes(p.hold) || s.includes(encodeURI(p.hold)); });
  check(`${p.hold} 공개 파일에 링크 없음`, leak.length === 0, leak.join(","));
}

// 다른 세 사이트로 가는 링크 없음(서로 링크하지 않는다)
const toOthers = htmls.filter((g) => OTHER_SITES.some((d) => read(g).includes(d)));
check("공개 html 에 다른 세 사이트 주소 없음", toOthers.length === 0, toOthers.join(","));

// 문장 겹침: 동 대표 쪽끼리, 그리고 공개된 동 상세와 15자 조각 25% 미만
const mine = DONGS.filter((p) => existsSync(pageOf(p))).map((p) => [pathOf(p), text(read(pageOf(p)))]);
const others = readdirSync(PUB).filter((d) => /^(서울|경기)-.+-누수탐지$/.test(d)).map((d) => [d, text(read(join(PUB, d, "index.html")))]);
for (let i = 0; i < mine.length; i++) {
  for (const [n, t] of [...mine.slice(i + 1), ...others]) {
    const [m, mt] = mine[i];
    const r = Math.max(overlap(mt, t), overlap(t, mt));
    check(`문장 겹침 ${m} ~ ${n} 25% 미만`, r < 0.25, `${(r * 100).toFixed(0)}%`);
  }
}

if (fails.length) { console.error(fails.join("\n")); process.exit(1); }
console.log(`dong pages ok (${DONGS.length})`);

"""구 하나를 하위 주소 사이트로 공개.  python -I tools/sub_site.py <사이트 루트> <하위 이름> <구 폴더명>
예: python -I tools/sub_site.py . nowon 서울-노원구-누수탐지  →  https://nowon.nusuphd.com/
unpublished/ 의 구 페이지(→ 하위 첫 화면)와 그 구의 동 페이지(→ 하위 /서울-노원구-○○동-누수탐지/)를 public/_sub/<하위>/ 로 옮긴다.
워커(src/index.js)가 하위 호스트 요청을 이 폴더로 돌려준다. 하위 안 링크는 상대 주소, 본 사이트 쪽은 https://nusuphd.com 절대 주소.
canonical·og:url·JSON-LD·sitemap·robots·rss 는 하위 호스트 기준. 본 사이트 지역 목록·허브 칩은 하위 주소로 연결, 옛 주소는 301.
원고·시공 사진은 따로(tools/pages.py + tools/build.py)."""
import re, sys, json, shutil, pathlib, subprocess
from urllib.parse import unquote, quote

root = pathlib.Path(sys.argv[1]); sub, gu = sys.argv[2], sys.argv[3]
pub = root / "public"; hold = root / "unpublished"; out = pub / "_sub" / sub
MAIN, HOST = "https://nusuphd.com", f"https://{sub}.nusuphd.com"
prefix = gu[:-len("누수탐지")]                                 # '서울-노원구-'
dongs = sorted(d.name for d in hold.iterdir() if d.name.startswith(prefix) and d.name != gu)
assert (hold / gu).is_dir() and dongs and not out.exists(), (gu, dongs)
NEW = {f"/{gu}/": "/", **{f"/{d}/": f"/{d}/" for d in dongs}}  # 본 사이트 경로 → 하위 경로

out.mkdir(parents=True)
shutil.move(str(hold / gu / "index.html"), str(out / "index.html")); (hold / gu).rmdir()
for d in dongs: shutil.move(str(hold / d), str(out / d))
hide = {d.name for d in hold.iterdir() if d.is_dir()} | {"station"}

def hidden(p): return p.strip("/").split("/")[0] in hide
A = re.compile(r'<a\b([^>]*?)\bhref="([^"]+)"([^>]*)>(.*?)</a>', re.S)
def relink(m):
    href = m.group(2); p = unquote(href)
    if not p.startswith("/") or p.startswith("/assets/") or p == "/rss.xml": return m.group(0)
    if p in NEW: return f'<a{m.group(1)}href="{NEW[p]}"{m.group(3)}>{m.group(4)}</a>'
    if hidden(p):
        attrs = re.sub(r'\s(?:target|rel|aria-label)="[^"]*"', "", m.group(1) + m.group(3)).strip()
        tag = "g" if re.search(r"<(?:text|circle|path|rect)\b", m.group(4)) else "span"
        return f"<{tag}{(' ' + attrs) if attrs else ''}>{m.group(4)}</{tag}>"
    return f'<a{m.group(1)}href="{MAIN}{href}"{m.group(3)}>{m.group(4)}</a>'

pages = [out / "index.html"] + [out / d / "index.html" for d in dongs]
for f in pages:
    t = f.read_text(encoding="utf-8")
    t = re.sub(r'<li><a href="/station/">[^<]*</a></li>', "", t)
    t = re.sub(r'<a href="/station/">역별 출장</a>', "", t)
    t = re.sub(r'<meta name="naver-site-verification"[^>]*>', "", t)  # 하위 주소는 서치어드바이저에 따로 등록
    for old, new in NEW.items():                                    # canonical·og:url·JSON-LD
        t = t.replace(MAIN + quote(old), HOST + quote(new)).replace(MAIN + old, HOST + new)
    t = A.sub(relink, t)
    t = re.sub(r'(<a class="brand" href=")[^"]*', r"\1/", t)        # 로고는 하위 첫 화면
    f.write_text(t, encoding="utf-8")

# 없는 주소: 본 사이트 404 를 하위용으로
t = (pub / "404.html").read_text(encoding="utf-8")
t = re.sub(r'<meta name="naver-site-verification"[^>]*>', "", t)
(out / "404.html").write_text(A.sub(relink, t), encoding="utf-8")

urls = [HOST + quote(p) for p in NEW.values()]
(out / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {HOST}/sitemap.xml\n", encoding="utf-8")
(out / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"<url><loc>{u}</loc><lastmod>2026-10-27</lastmod></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
def rss_item(f, u):
    s = f.read_text(encoding="utf-8")
    ti = re.search(r"<title>([^<]*)</title>", s).group(1); de = re.search(r'<meta name="description" content="([^"]*)">', s).group(1)
    return f"<item><title>{ti}</title><link>{u}</link><guid>{u}</guid><description>{de}</description><pubDate>Tue, 27 Oct 2026 09:00:00 +0900</pubDate></item>"
(out / "rss.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>누수박사</title>'
    f"<link>{HOST}/</link><description>누수박사</description><language>ko</language>"
    + "".join(rss_item(f, u) for f, u in zip(pages, urls)) + "</channel></rss>\n", encoding="utf-8")

# 본 사이트: 지역 찾기 목록·검색 데이터·허브 칩을 하위 주소로
def old(path): return subprocess.run(["git", "-C", str(root), "show", f"1cad97e^:{path}"], capture_output=True, check=True).stdout.decode("utf-8")
for rel in ("index.html", "area/index.html"):
    f = pub / rel; t = f.read_text(encoding="utf-8"); o = old(f"public/{rel}")
    region = "seoul" if gu.startswith("서울-") else "gyeonggi"
    for d in dongs:
        url = f"/{d}/"; new = HOST + url
        card = re.search(r'<a href="%s"><strong>[^<]*</strong>(?:<span>[^<]*</span>)?</a>' % re.escape(url), o).group(0).replace(url, new)
        t = re.sub(r'(<div class="region-grid dong-grid" data-panel="%s"[^>]*>.*?)(</div>)' % region, lambda m: m.group(1) + card + m.group(2), t, count=1, flags=re.S)
        entry = re.search(r'\["[^"]*", "[^"]*", "%s"\]' % re.escape(url), o).group(0).replace(url, new)
        last = list(re.finditer(r'\["[^"]*", "[^"]*", "(?:%s)?/%s-[^"]*"\]' % (re.escape(HOST), gu.split("-")[0]), t))[-1]
        t = t[:last.end()] + ", " + entry + t[last.end():]
    hub = re.search(r'<div class="hub"><h3><a href="/%s/">([^<]*)</a></h3>' % re.escape(gu), o)
    if hub:
        name = hub.group(1)
        t = t.replace(f'<div class="hub"><h3><span>{name}</span></h3>', f'<div class="hub"><h3><a href="{HOST}/">{name}</a></h3>', 1)
        m = re.search(r'(<div class="hub"><h3><a href="%s/">%s</a></h3><p class="chips[^"]*">)(.*?)(</p>)' % (re.escape(HOST), re.escape(name)), t, re.S)
        chips = m.group(2)
        for d in dongs:
            dn = d.split("-")[2]; chips = chips.replace(f"<span>{dn}</span>", f'<a href="{HOST}/{d}/">{dn}</a>', 1)
        t = t[:m.start(2)] + chips + t[m.end(2):]
    for r in ("seoul", "gyeonggi"):
        m = re.search(r'<div class="region-grid dong-grid" data-panel="%s"[^>]*>(.*?)</div>' % r, t, re.S)
        t = re.sub(r'(data-tab="%s"[^>]*>[^<]*<small>)\d+곳' % r, lambda x: x.group(1) + f"{m.group(1).count('<a ')}곳", t, count=1)
    f.write_text(t, encoding="utf-8")

# 옛 주소(영문·본 사이트 한글) → 하위 주소 301
f = root / "src" / "redirects.json"; mp = json.loads(f.read_text(encoding="utf-8")); full = json.loads(old("src/redirects.json"))
mp.update({k: HOST + NEW[v] for k, v in full.items() if v in NEW})
mp.update({k: HOST + v for k, v in NEW.items()})
f.write_text(json.dumps(mp, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

bad = [(f.parent.name, h) for f in pages for h in re.findall(r'href="(/[^"]*)"', f.read_text(encoding="utf-8"))
       if not (h.startswith("/assets/") or h == "/rss.xml" or unquote(h) in NEW.values())]
assert not bad, bad[:5]
print("sub", HOST, "pages", len(pages), "dongs", [d.split("-")[2] for d in dongs], "redirects", len(mp))

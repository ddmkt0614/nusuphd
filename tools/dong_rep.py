"""동 대표 쪽(2026-10-28 사장님·웹사이트2): '{구} {동} 누수탐지' 짧은 검색어를 맡는 동 단위 안내.  python -I tools/dong_rep.py public
주소 /{구}-{동}-누수탐지/, title·H1 은 '{구} {동} 누수탐지'로 시작(각 1회). 본문 '{구} {동} 누수탐지' 5회·'{동} 누수' 5회(test-dong.mjs 가 센다).
같은 동의 보관 상세(/서울-{구}-{동}-누수탐지/)는 열지 않는다(같은 검색어로 다툼). 동네 사실은 구청·위키백과에서 확인된 것만(sources).
작업 사진은 그 동 현장이 아니다 → 사진 설명에 지역 이름을 쓰지 않고, '다른 현장' 같은 안내 문구도 넣지 않는다.
지역 안내는 /area/ 허브: 그 구 칩을 링크로 바꾸고(양방향), sitemap 에 한 줄 더한다. 다른 쪽은 건드리지 않는다."""
import sys, re, json, html, pathlib
from urllib.parse import quote
sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from dong_rep_data import PAGES

pub = pathlib.Path(sys.argv[1])
SITE = "https://nusuphd.com"
TEL, TEL_TXT = "050713549387", "0507-1354-9387"
LASTMOD = "2026-10-28"
TPL = (pub / "서울-광진구-화양동-누수탐지" / "index.html").read_text(encoding="utf-8")   # 머리·바닥글·스크립트 틀
e = lambda t: html.escape(t, quote=False)
a = lambda t: html.escape(t)

def img(p, cls="", lazy=True):
    return (f'<img{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} src="/assets/photo/dong/{p["file"]}.webp" alt="{a(p["alt"])}" width="1000" height="750"'
            + (' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"') + ">")

def build(P):
    gu, dong, date = P["gu"], P["dong"], P.get("date", LASTMOD)
    name = f"{gu} {dong} 누수탐지"; path = f"/{gu}-{dong}-누수탐지/"; url = SITE + quote(path)
    B = P.get("buildings")                                          # 두 번째 묶음부터는 없음(동 소개·작업 순서·방문·FAQ 만)
    title = f"{name} {P['headline']} | 누수박사"
    main = (
        '<section class="hero hero-place"><div class="wrap hero-grid">\n'
        f'  <div class="hero-copy"><p class="hero-kicker">서울 {e(gu)}</p><h1>{e(name)} {e(P["headline"])}</h1>\n'
        f'  <p class="hero-lead">{e(P["topic"])}</p>\n'
        f'  <p class="hero-actions"><a class="btn-call" href="tel:{TEL}">{TEL_TXT}</a></p><p class="badge-ok">출장 가능 지역</p></div>\n'
        f'  <div class="hero-visual"><figure class="hero-photo">{img(P["hero"], "hero-img", lazy=False)}</figure></div></div></section>\n'
        f'<section class="summary"><div class="wrap"><p class="summary-label">한눈에 보기</p><p class="summary-text">{e(P["intro"])}</p></div></section>'
        f'<section class="block block-article"><div class="wrap article-body"><h2>{e(P["about_title"])}</h2>'
        + "".join(f"<p>{e(x)}</p>" for x in P["about"]) + "</div></section>"
        + (f'<section class="block block-steps"><div class="wrap"><h2 class="block-title">{e(B["title"])}</h2><p class="lead">{e(B["lead"])}</p><ol class="steps">'
           + "".join(f"<li><span><strong>{e(t)}</strong> {e(d)}</span></li>" for t, d in B["items"]) + "</ol></div></section>" if B else "")
        + f'<section class="block block-signs"><div class="wrap"><h2 class="block-title">방문 전 확인할 것</h2><ul class="signs">'
        + "".join(f"<li>{e(x)}</li>" for x in P["visit"]) + "</ul></div></section>"
        f'<section class="block block-cases"><div class="wrap"><h2 class="block-title">작업 과정</h2><p class="lead">{e(P["work"]["lead"])}</p><p class="lead">{e(P["work"]["outro"])}</p><div class="case-grid">'
        + "".join(f'<figure>{img(s)}<figcaption><strong>{e(s["title"])}</strong> {e(s["text"])}</figcaption></figure>' for s in P["work"]["steps"])
        + '</div></div></section>\n'
        f'<section class="block block-faq"><div class="wrap"><h2 class="block-title">자주 묻는 질문</h2><div class="faq">'
        + "".join(f"<details><summary>{e(q)}</summary><p>{e(x)}</p></details>" for q, x in P["faq"]) + "</div></div></section>"
        + (f'<section class="block "><div class="wrap"><h2 class="block-title">가까운 동네</h2><p class="chips ">'
           + "".join(f"<span>{e(x)}</span>" for x in P["near"])
           + f'</p><p class="more-link"><a href="/area/">서울·경기 출장 지역 전체 보기</a></p></div></section>' if P.get("near")
           else '<section class="block "><div class="wrap"><p class="more-link"><a href="/area/">서울·경기 출장 지역 전체 보기</a></p></div></section>')
        + f'<section class="callout"><div class="wrap"><h2>{e(P["callout"])}</h2><p>{e(P["callout_text"])}</p><a class="btn-call" href="tel:{TEL}">{TEL_TXT}</a></div></section>\n'
    )
    s = TPL
    s = re.sub(r"<title>[^<]*</title>", f"<title>{e(title)}</title>", s, count=1)
    for k, v in (("description", P["description"]), ("og:title", title), ("og:description", P["description"]), ("og:url", url),
                 ("og:image", f'{SITE}/assets/photo/dong/{P["hero"]["file"]}.webp'), ("geo.placename", f"서울특별시 {gu} {dong}")):
        s, n = re.subn(rf'(<meta (?:name|property)="{re.escape(k)}" content=")[^"]*(">)', lambda m: m.group(1) + a(v) + m.group(2), s, count=1); assert n == 1, k
    s = re.sub(r'(<link rel="canonical" href=")[^"]*(">)', lambda m: m.group(1) + url + m.group(2), s, count=1)
    g = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S).group(1))["@graph"]
    base = [x for x in g if x["@type"] in ("Plumber", "WebSite")]; assert len(base) == 2
    graph = [*base,
             {"@type": "WebPage", "@id": url, "url": url, "name": title, "description": P["description"], "isPartOf": {"@id": f"{SITE}/#website"},
              "about": {"@id": f"{SITE}/#business"}, "dateModified": date, "inLanguage": "ko-KR",
              "primaryImageOfPage": {"@type": "ImageObject", "url": f'{SITE}/assets/photo/dong/{P["hero"]["file"]}.webp', "width": 1000, "height": 750}},
             {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "홈", "item": f"{SITE}/"},
                                                             {"@type": "ListItem", "position": 2, "name": "출장 지역", "item": f"{SITE}/area/"},
                                                             {"@type": "ListItem", "position": 3, "name": f"{gu} {dong}", "item": url}]},
             {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in P["faq"]]},
             {"@type": "Service", "name": name, "serviceType": "누수탐지·누수공사", "provider": {"@id": f"{SITE}/#business"},
              "areaServed": {"@type": "Place", "name": f"서울특별시 {gu} {dong}"}}]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>',
               lambda m: '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False).replace("</", "<\\/") + "</script>", s, count=1, flags=re.S)
    s = re.sub(r'<body class="[^"]*">', '<body class="page-dong d-callout-accent has-callbar">', s, count=1)
    s = re.sub(r'<nav class="crumbs".*?</nav>', f'<nav class="crumbs" aria-label="현재 위치"><div class="wrap"><a href="/">홈</a><a href="/area/">출장 지역</a><span aria-current="page">{e(gu)} {e(dong)}</span></div></nav>', s, count=1, flags=re.S)
    s = s[:s.index("<main>") + len("<main>")] + "\n\n" + main + s[s.index("</main>"):]
    out = pub / f"{gu}-{dong}-누수탐지" / "index.html"; out.parent.mkdir(exist_ok=True); out.write_text(s, encoding="utf-8")
    return path

def hub_block(s, gu):
    short = gu if len(gu) == 2 else gu[:-1]                         # 허브 제목: 중랑구 → 중랑누수탐지, 중구 → 중구누수탐지
    return re.search(rf'<h3><span>{short}누수탐지</span></h3><p class="chips chips-dense">.*?</p>(?:<p class="hub-line">.*?</p>)*', s, re.S)

def link_hub(P, path):
    """/area/ 허브의 그 구 칸. 법정동 쪽은 그 칩(span)을 링크로, 행정동 쪽(칩에 이름이 없음)은 칩 아래에 '이름+한 줄+링크'를 더한다.
    홈·/area/ 동네 검색 목록(var D, 칠 때만 보임)과 서울 탭 카드에도 넣는다."""
    gu, dong = P["gu"], P["dong"]
    p = pub / "area" / "index.html"; s = p.read_text(encoding="utf-8")
    if f'href="{path}"' not in s:
        m = hub_block(s, gu)
        if P.get("hub_line"):
            hub = m.group(0) + f'<p class="hub-line"><a href="{path}">{e(dong)} 누수탐지</a> {e(P["hub_line"])}</p>'
        else:
            hub, n = re.subn(rf"<span>{dong}</span>", f'<a href="{path}">{dong}</a>', m.group(0), count=1); assert n == 1, dong
        p.write_text(s[:m.start()] + hub + s[m.end():], encoding="utf-8")
    for p in (pub / "area" / "index.html", pub / "index.html"):
        s = p.read_text(encoding="utf-8")
        if f'"{path}"]' not in s:
            s, n = re.subn(r"(var D=\[.*?)\];", lambda m: m.group(1) + json.dumps([dong, gu, path], ensure_ascii=False) + ", ];", s, count=1, flags=re.S)
            assert n == 1, p
        # 서울 탭 카드 목록 끝에 한 장 더하고 탭 숫자(N곳)를 카드 수로 맞춘다(사장님 2026-10-28)
        m = re.search(r'(<div class="region-grid dong-grid" data-panel="seoul"[^>]*>)(.*?)(</div>)', s, re.S); assert m, p
        cards = m.group(2)
        if f'href="{path}"' not in cards:
            cards += f'<a href="{path}"><strong>서울 {gu} {dong} 누수탐지</strong></a>'
            s = s[:m.start(2)] + cards + s[m.end(2):]
        s, n = re.subn(r'(data-tab="seoul"[^>]*>서울 <small>)\d+(곳</small>)', lambda x: x.group(1) + str(cards.count("<a ")) + x.group(2), s, count=1)
        assert n == 1, p; p.write_text(s, encoding="utf-8")

def add_sitemap(path, date):
    p = pub / "sitemap.xml"; s = p.read_text(encoding="utf-8"); loc = f"<loc>{SITE}{quote(path)}</loc>"
    if loc in s: return
    line = f"<url>{loc}<lastmod>{date}</lastmod><priority>0.6</priority></url>\n"
    i = s.index(f"<url><loc>{SITE}/faq/</loc>"); p.write_text(s[:i] + line + s[i:], encoding="utf-8")

# 쓰기 전에 모든 쪽의 허브 칸을 먼저 확인한다(중간에 멈추면 반쯤 쓴 public 이 남으므로)
_area = (pub / "area" / "index.html").read_text(encoding="utf-8")
for P in PAGES:
    m = hub_block(_area, P["gu"]); assert m, P["gu"]
    assert P.get("hub_line") or f"<span>{P['dong']}</span>" in m.group(0) or f'href="/{P["gu"]}-{P["dong"]}-누수탐지/"' in m.group(0), P["dong"]

for P in PAGES:
    path = build(P); link_hub(P, path); add_sitemap(path, P.get("date", LASTMOD))
    print("built", path)

"""공개 동 페이지 6곳에 원고 적용 + 키워드 횟수 검사.  python build.py <public> [--check]"""
import sys, re, json, html, pathlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from pages import PAGES

pub = pathlib.Path(sys.argv[1]); CHECK = "--check" in sys.argv
TARGET = {"S": (30, 30), "G": (30, 30), "D": (30, 30), "누수탐지": (35, 37), "누수": (40, 50),
          "S G": (30, 30), "G D": (27, 30), "D 누수탐지": (25, 25), "G D 누수탐지": (25, 25), "S G D 누수탐지": (25, 25)}

def main_text(s):
    m = s[s.find("<main>"):s.find("</main>")]
    m = re.sub(r"<script.*?</script>", " ", m, flags=re.S)
    m = re.sub(r"<[^>]+>", " ", m)
    return re.sub(r"\s+", " ", html.unescape(m)).strip()

def counts(txt, S, G, D):
    out = {}
    for k in TARGET:
        out[k] = txt.count(k.replace("S", S, 1).replace("G", G, 1).replace("D", D, 1) if k not in ("누수탐지", "누수") else k)
    return out

def esc(t): return html.escape(t, quote=False)

def apply(page, P):
    S, G, D = P["S"], P["G"], P["D"]
    F, SGD, SG = f"{S} {G} {D} 누수탐지", f"{S} {G} {D}", f"{S} {G}"
    fill = lambda t: t.replace("{F}", F).replace("{SGD}", SGD).replace("{SG}", SG)
    p = pub / page / "index.html"; s = p.read_text(encoding="utf-8")
    # 첫 화면
    s = re.sub(r'<p class="hero-kicker">[^<]*</p><h1>[^<]*</h1>', f'<p class="hero-kicker">{SG}</p><h1>{F}</h1>', s, count=1)
    s = re.sub(r'<p class="hero-lead">[^<]*</p>', f'<p class="hero-lead">{esc(P["lead"])}</p>', s, count=1)
    # 요약 + 본문
    art = "".join(f'<h2>{esc(fill(h))}</h2>' + "".join(f"<p>{esc(fill(x))}</p>" for x in ps) for h, ps in P["article"])
    summary = (f'<section class="summary"><div class="wrap"><p class="summary-label">한눈에 보기</p>'
               f'<p class="summary-text">{esc(fill(P["summary"]))}</p></div></section>'
               f'<section class="block block-article"><div class="wrap article-body">{art}</div></section>'
               '<section class="block block-steps"><div class="wrap"><h2 class="block-title">누수탐지 진행 순서</h2><ol class="steps">'
               + "".join(f"<li><span>{esc(x)}</span></li>" for x in P["steps"]) + "</ol></div></section>")
    s = re.sub(r'<section class="summary">.*?</section>(<section class="block block-article">.*?</section>)?(<section class="block block-steps">.*?</section>)?',
               lambda m: summary, s, count=1, flags=re.S)
    # 출장 안내(위치 문장만 새로)
    s = re.sub(r'(<section class="block block-facts"><div class="wrap"><h2 class="block-title">)[^<]*(</h2>)', r"\1출장 안내\2", s, count=1)
    s = re.sub(r'<div><dt>위치</dt><dd>.*?</dd></div>', f'<div><dt>위치</dt><dd>{esc(fill(P["where"]))}</dd></div>', s, count=1, flags=re.S)
    # 증상
    s = re.sub(r'(<section class="block block-signs"><div class="wrap"><h2 class="block-title">)[^<]*(</h2>)', lambda m: m.group(1) + esc(fill(P["signs"])) + m.group(2), s, count=1)
    # 건물 특성 블록은 본문에 녹였으므로 뺌
    s = re.sub(r'<section class="block block-building">.*?</section>', "", s, count=1, flags=re.S)
    # 보험
    s = re.sub(r'(<section class="block block-ins"><div class="wrap"><h2 class="block-title">)[^<]*(</h2>)<p>.*?</p>',
               lambda m: m.group(1) + "누수 보험 처리" + m.group(2) + f"<p>{esc(fill(P['ins']))}</p>", s, count=1, flags=re.S)
    # 자주 묻는 질문
    faq = "".join(f"<details><summary>{esc(fill(q))}</summary><p>{esc(fill(a))}</p></details>" for q, a in P["faq"])
    s = re.sub(r'<section class="block block-faq">.*?</section>',
               f'<section class="block block-faq"><div class="wrap"><h2 class="block-title">{esc(F)} 자주 묻는 질문</h2><div class="faq">{faq}</div></div></section>', s, count=1, flags=re.S)
    # 자주 묻는 질문은 맨 아래(상담 띠 바로 위)로
    m = re.search(r'<section class="block block-faq">.*?</section>', s, re.S)
    faq_html = m.group(0); s = s[:m.start()] + s[m.end():]
    i = s.index('<section class="callout">'); s = s[:i] + faq_html + s[i:]
    # 서비스: 동 이름 빼기
    s = re.sub(r'(<section class="block block-services"><div class="wrap"><h2 class="block-title">)[^<]*(</h2>)', r"\1함께 많이 찾는 서비스\2", s, count=1)
    def svc(m): return re.sub(r"<strong>(?:\S+ )?%s ([^<]*)</strong>" % re.escape(D), r"<strong>\1</strong>", m.group(0))
    s = re.sub(r'<section class="block block-services">.*?</section>', svc, s, count=1, flags=re.S)
    # 지도 제목은 동 이름만
    s = re.sub(r"<figcaption><strong>[^<]*주변 지도</strong>", f"<figcaption><strong>{D} 주변 지도</strong>", s, count=1)
    # 가까운 동네: 이름만, '…전체' 빼기
    def near(m):
        body = re.sub(r"<span>[^<]*전체</span>", "", m.group(2)); body = body.replace(" 누수탐지</span>", "</span>")
        return m.group(1) + body
    s = re.sub(r'(<section class="block "><div class="wrap"><h2 class="block-title">)[^<]*(</h2>.*?</section>)',
               lambda m: near(re.match(r"(.*?)(</h2>.*)", m.group(1) + "가까운 동네" + m.group(2), re.S)), s, count=1, flags=re.S)
    # 상담 띠
    s = re.sub(r'(<section class="callout"><div class="wrap"><h2>)[^<]*(</h2>)', lambda m: m.group(1) + esc(F) + " 상담" + m.group(2), s, count=1)
    # 머리: 제목·설명·구조화 데이터
    title = f"{F} | 누수박사"
    desc = fill("{F}. 계량기와 배관 압력부터 확인하고 장비로 찾은 자리만 고칩니다. 상담 0507-1354-9387")
    s = re.sub(r"<title>[^<]*</title>", f"<title>{esc(title)}</title>", s, count=1)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{html.escape(desc)}">', s, count=1)
    s = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{html.escape(title)}">', s, count=1)
    s = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{html.escape(desc)}">', s, count=1)
    def ld(m):
        d = json.loads(m.group(1))
        for g in d["@graph"]:
            if g["@type"] == "WebPage": g["name"], g["description"] = title, desc
            if g["@type"] == "Service": g["name"] = F
            if g["@type"] == "FAQPage":
                g["mainEntity"] = [{"@type": "Question", "name": fill(q), "acceptedAnswer": {"@type": "Answer", "text": fill(a)}} for q, a in P["faq"]]
        return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + "</script>"
    s = re.sub(r'<script type="application/ld\+json">(.*?)</script>', ld, s, count=1, flags=re.S)
    return p, s

ok = True
texts = {}
for page, P in PAGES.items():
    p, s = apply(page, P)
    c = counts(main_text(s), P["S"], P["G"], P["D"]); texts[page] = main_text(s)
    bad = {k: v for k, v in c.items() if not (TARGET[k][0] <= v <= TARGET[k][1])}
    ok &= not bad
    print(P["D"], " ".join(f"{k.replace('S',P['S'],1).replace('G',P['G'],1).replace('D',P['D'],1) if k not in ('누수탐지','누수') else k}:{v}" for k, v in c.items()), "| 글자", len(main_text(s)), "| 맞지 않음:", bad or "없음")
    if not CHECK: p.write_text(s, encoding="utf-8")

# 페이지끼리 문장 겹침(15자 조각 기준)
def grams(t): t = re.sub(r"\s", "", t); return {t[i:i + 15] for i in range(0, len(t) - 15, 3)}
names = list(texts)
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        a, b = grams(texts[names[i]]), grams(texts[names[j]])
        print(f"겹침 {PAGES[names[i]]['D']}~{PAGES[names[j]]['D']}: {len(a & b) / min(len(a), len(b)) * 100:.0f}%")
print("ALL OK" if ok else "NEEDS FIX")

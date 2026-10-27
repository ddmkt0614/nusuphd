"""보관 페이지 추가 공개.  python -I tools/open_page.py <사이트 루트> <페이지 폴더명> [...]
unpublished/ 에서 public/ 으로 옮기고, 그 페이지 안의 숨긴 페이지 링크는 글자로 바꾼다.
지역 찾기 목록·검색 데이터·지역 허브·사이트맵·옛 주소 301 에는 단계 공개 전(1cad97e^) 모습을 가져와 다시 넣는다.
원고·시공 사진은 따로(tools/pages.py + tools/build.py)."""
import re, sys, json, shutil, pathlib, subprocess
from urllib.parse import unquote, quote

root = pathlib.Path(sys.argv[1]); pub = root / "public"; hold = root / "unpublished"; NAMES = sys.argv[2:]
BEFORE = "1cad97e^"                                            # 단계 공개 직전 커밋
def old(path): return subprocess.run(["git", "-C", str(root), "show", f"{BEFORE}:{path}"], capture_output=True, check=True).stdout.decode("utf-8")

for name in NAMES:
    assert (hold / name).is_dir() and not (pub / name).exists(), name
    shutil.move(str(hold / name), str(pub / name))
hide = {d.name for d in hold.iterdir() if d.is_dir()}

def hidden(href):
    p = unquote(href).replace("https://nusuphd.com", "")
    return (p.strip("/").split("/")[0] if p.startswith("/") else None) in hide

# 새로 연 페이지 안: stage_open 과 같은 규칙(목록 항목은 빼고, 본문 링크는 글자로)
A = re.compile(r'<a\b([^>]*?)\bhref="([^"]+)"([^>]*)>(.*?)</a>', re.S)
def unlink(m):
    if not hidden(m.group(2)): return m.group(0)
    inner = m.group(4); attrs = re.sub(r'\s(?:target|rel|aria-label)="[^"]*"', "", m.group(1) + m.group(3)).strip()
    tag = "g" if re.search(r"<(?:text|circle|path|rect)\b", inner) else "span"
    return f"<{tag}{(' ' + attrs) if attrs else ''}>{inner}</{tag}>"
for name in NAMES:
    f = pub / name / "index.html"; t = f.read_text(encoding="utf-8")
    t = re.sub(r'<a href="([^"]+)"><strong>[^<]*</strong>(?:<span>[^<]*</span>)?</a>', lambda m: "" if hidden(m.group(1)) else m.group(0), t)
    t = re.sub(r'<li><a href="/station/">[^<]*</a></li>', "", t)
    t = re.sub(r'<a href="/station/">역별 출장</a>', "", t)
    t = re.sub(r'\["[^"]*", "[^"]*", "(/[^"]*)"\],?\s?', lambda m: "" if hidden(m.group(1)) else m.group(0), t)
    f.write_text(A.sub(unlink, t), encoding="utf-8")

# 지역 찾기 목록 + 검색 데이터 + 지역 허브 칩
for rel in ("index.html", "area/index.html"):
    f = pub / rel; t = f.read_text(encoding="utf-8"); o = old(f"public/{rel}")
    for name in NAMES:
        url = f"/{name}/"; region = "seoul" if name.startswith("서울-") else "gyeonggi"
        if url in t: continue
        card = re.search(r'<a href="%s"><strong>[^<]*</strong>(?:<span>[^<]*</span>)?</a>' % re.escape(url), o).group(0)
        t = re.sub(r'(<div class="region-grid dong-grid" data-panel="%s"[^>]*>.*?)(</div>)' % region, lambda m: m.group(1) + card + m.group(2), t, count=1, flags=re.S)
        entry = re.search(r'\["[^"]*", "[^"]*", "%s"\]' % re.escape(url), o).group(0)
        last = list(re.finditer(r'\["[^"]*", "[^"]*", "/%s-[^"]*"\]' % name.split("-")[0], t))[-1]
        t = t[:last.end()] + ", " + entry + t[last.end():]
        chip = re.search(r'<div class="hub"><h3>(?:<a [^>]*>)?([^<]*)(?:</a>)?</h3><p class="chips[^"]*">(?:(?!</p>).)*?(<a href="%s">([^<]*)</a>)' % re.escape(url), o, re.S)
        if chip:
            t = re.sub(r'(<div class="hub"><h3><span>%s</span></h3><p class="chips[^"]*">(?:(?!</p>).)*?)<span>%s</span>' % (re.escape(chip.group(1)), re.escape(chip.group(3))),
                       lambda m: m.group(1) + chip.group(2), t, count=1, flags=re.S)
    for region in ("seoul", "gyeonggi"):
        m = re.search(r'<div class="region-grid dong-grid" data-panel="%s"[^>]*>(.*?)</div>' % region, t, re.S)
        t = re.sub(r'(data-tab="%s"[^>]*>[^<]*<small>)\d+곳' % region, lambda x: x.group(1) + f"{m.group(1).count('<a ')}곳", t, count=1)
    f.write_text(t, encoding="utf-8")

# 사이트맵: 마지막 동 페이지 뒤에
f = pub / "sitemap.xml"; t = f.read_text(encoding="utf-8"); o = old("public/sitemap.xml")
for name in NAMES:
    loc = f"https://nusuphd.com{quote('/' + name + '/')}"
    if loc in t: continue
    line = re.search(r"<url><loc>%s</loc>.*?</url>" % re.escape(loc), o).group(0)
    last = list(re.finditer(r"<url><loc>https://nusuphd\.com/%[^<]*</loc>.*?</url>", t))[-1]
    t = t[:last.end()] + "\n" + line + t[last.end():]
f.write_text(t, encoding="utf-8")

# 옛 영문 주소 301
f = root / "src" / "redirects.json"; mp = json.loads(f.read_text(encoding="utf-8")); full = json.loads(old("src/redirects.json"))
mp.update({k: v for k, v in full.items() if v.strip("/") in NAMES})
f.write_text(json.dumps(mp, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

bad = [(n, unquote(h)) for n in NAMES for h in re.findall(r'href="([^"]+)"', (pub / n / "index.html").read_text(encoding="utf-8")) if hidden(h)]
assert not bad, bad[:3]
for rel in ("index.html", "area/index.html", "sitemap.xml"):
    t = (pub / rel).read_text(encoding="utf-8")
    assert all(f"/{n}/" in unquote(t) for n in NAMES), rel
print("opened", NAMES, "held", len(hide), "redirects", len(mp))

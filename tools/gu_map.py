"""하위 주소 사이트 첫 화면(구 페이지) 지도 — 동 페이지 지도와 같은 저스트 방식.
옅은 회색 바탕 + 흰 경계선, 그 구의 행정동을 법정동(공릉1동·공릉2동 → 공릉동)으로 묶어 파스텔 면 + 굵은 이름(동 페이지 링크),
둘레 구·시는 회색 이름.  python -I tools/gu_map.py <public> <하위 폴더 예: _sub/nowon> <hjd.geojson> <시도 예: 서울특별시> <구 예: 노원구>
경계: 통계청 SGIS(공공누리 제1유형) · 가공 vuski/admdongkor (CC BY 4.0). geojson 은 저장소에 두지 않음(34MB)."""
import sys, json, re, math, html, pathlib

pub, sub, gjp, SIDO, GU = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
gj = json.loads(pathlib.Path(gjp).read_text(encoding="utf-8"))
FILL = ["#f0dcae", "#bfe3dc", "#c8eba8", "#dcd2f2", "#f7cdb9", "#f3e6a8", "#cfe0f3", "#e8d3c0"]
W = H = 440

feats = []
for f in gj["features"]:
    pr = f["properties"]
    if not pr.get("sidonm", "").startswith(("서울", "경기", "인천")): continue
    g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    xs = [p[0] for poly in polys for p in poly[0]]; ys = [p[1] for poly in polys for p in poly[0]]
    sgg = re.sub(r"(시)(.+구)$", r"\1", pr["sggnm"])
    feats.append({"name": pr["adm_nm"].split(" ")[-1], "sido": pr["sidonm"], "sgg": sgg, "polys": polys, "bb": (min(xs), min(ys), max(xs), max(ys))})

mine = [f for f in feats if f["sido"] == SIDO and f["sgg"] == GU]
assert mine, (SIDO, GU)
legal = lambda n: re.sub(r"(본|[\d·]+)동$", "동", n)              # 상계3·4동·중계본동 → 상계동·중계동
groups = {}
for f in mine: groups.setdefault(legal(f["name"]), []).append(f)

pts = [p for f in mine for poly in f["polys"] for p in poly[0]]
lat0 = sum(p[1] for p in pts) / len(pts); kx = math.cos(math.radians(lat0))
minx = min(p[0] for p in pts) * kx; maxx = max(p[0] for p in pts) * kx; miny = min(p[1] for p in pts); maxy = max(p[1] for p in pts)
span = max(maxx - minx, maxy - miny) * 1.22; sc = W / span; cxm, cym = (minx + maxx) / 2, (miny + maxy) / 2
X = lambda lo: round(W / 2 + (lo * kx - cxm) * sc, 1)
Y = lambda la: round(H / 2 - (la - cym) * sc, 1)
box = ((cxm - span / 2) / kx, cym - span / 2, (cxm + span / 2) / kx, cym + span / 2)

def path(f):
    d = []
    for poly in f["polys"]:
        for ring in poly:
            out, last = [], None
            for lo, la in ring:
                p = (X(lo), Y(la))
                if last is None or abs(p[0] - last[0]) + abs(p[1] - last[1]) >= 1.4: out.append(p); last = p
            if len(out) >= 3: d.append("M" + "L".join(f"{a:g} {b:g}" for a, b in out) + "Z")
    return "".join(d)

base, side = [], {}
for f in feats:
    b = f["bb"]
    if b[2] < box[0] or b[0] > box[2] or b[3] < box[1] or b[1] > box[3] or f in mine: continue
    base.append(path(f))
    vis = [(X(lo), Y(la)) for poly in f["polys"] for lo, la in poly[0]]
    vis = [(x, y) for x, y in vis if 24 < x < W - 24 and 20 < y < H - 20]
    if vis: side.setdefault(f["sgg"], []).extend(vis)
out = [f'<rect width="{W}" height="{H}" class="dm-bg"/>', f'<path d="{"".join(base)}" class="dm-dong"/>']
taken, labels = [], []
def free(x, y, w, h): return all(x + w / 2 < a or x - w / 2 > c or y + h / 2 < b or y - h / 2 > d for a, b, c, d in taken)
pages = {d.name.split("-")[2]: d.name for d in (pub / sub).iterdir() if d.is_dir() and d.name.count("-") == 3}
for k, (name, fs) in enumerate(sorted(groups.items())):
    out.append(f'<path d="{"".join(path(f) for f in fs)}" fill="{FILL[k % len(FILL)]}" class="dm-area"/>')
    gp = [(X(lo), Y(la)) for f in fs for poly in f["polys"] for lo, la in poly[0]]
    x = sum(p[0] for p in gp) / len(gp); y = sum(p[1] for p in gp) / len(gp); w, h = 15 * len(name) + 6, 20
    for dy in (0, 14, -14, 28, -28):
        if free(x, y + dy, w, h): y += dy; break
    taken.append((x - w / 2, y - h / 2, x + w / 2, y + h / 2))
    t = f'<text x="{x:.0f}" y="{y + 5:.0f}" class="dm-name dm-main">{html.escape(name)}</text>'
    labels.append(f'<a href="/{pages[name]}/">{t}</a>' if name in pages else t)
for sgg, vis in side.items():
    x = sum(p[0] for p in vis) / len(vis); y = sum(p[1] for p in vis) / len(vis); w = 13 * len(sgg)
    if free(x, y, w, 16): taken.append((x - w / 2, y - 8, x + w / 2, y + 8)); out.append(f'<text x="{x:.0f}" y="{y + 4:.0f}" class="dm-sgg">{html.escape(sgg)}</text>')
names = "·".join(sorted(groups))
svg = f'<svg class="dongmap" viewBox="0 0 {W} {H}" role="img" aria-label="동별 지도 — {html.escape(names)}">' + "".join(out + labels) + "</svg>"
ATTR = ('<p class="dm-credit">행정동 경계: 통계청 SGIS(공공누리 제1유형) · 가공 '
        '<a href="https://github.com/vuski/admdongkor" rel="nofollow noopener" target="_blank">vuski/admdongkor</a> (CC BY 4.0)</p>')
fig = f'<figure class="compass dongmap-fig"><figcaption><strong>동별 지도</strong></figcaption>{svg}{ATTR}</figure>'
p = pub / sub / "index.html"; s = p.read_text(encoding="utf-8")
s, n = re.subn(r'<figure class="(?:map |compass dongmap-fig)[^"]*">.*?</figure>', lambda m: fig, s, count=1, flags=re.S)
assert n == 1; p.write_text(s, encoding="utf-8")
print("gu map", GU, {k: len(v) for k, v in groups.items()}, "links", sum(1 for g in groups if g in pages))

"""Expeditie Mediajungle lock-up (E14, 2026-09-09): titel EXPEDITIE (rasterlaag, nano-banana-2 in JUNGLE-letterstijl)
boven, het echte MJ-vectorlogo zonder ® ervoor ingeschoven, bladeren als vector uit het Super Fake Safari-logo erachter.
gebruik: python3 compose_expeditie_logo.py [uit.svg] ['{json-overrides}']   (draai vanuit de repo-root)
"""
import re, sys, json, base64
R = "media/expeditie-mediajungle/references"
OUT = sys.argv[1] if len(sys.argv) > 1 else f"{R}/logo-expeditie-mj.svg"
P = {"pad": 90, "title_w": 940, "title_y": 40, "logo_w": 370, "logo_y": 232, "y0": -10,
     "leaves": [{"x": -40, "y": 60, "h": 350, "rot": -6}, {"x": 1040, "y": 60, "h": 350, "rot": 6, "flip": True}]}
P.update(json.loads(sys.argv[2]) if len(sys.argv) > 2 else {})
TITLE_PNG = f"{R}/expeditie-titel-rgba.png"
import struct
with open(TITLE_PNG, "rb") as fh: fh.read(16); TW, TH = struct.unpack(">II", fh.read(8))
W = 1000.0
title_w = P.get("title_w", 1000); title_x = (W - title_w) / 2; title_y = P.get("title_y", 0)
title_h = title_w * TH / TW
logo_w = P.get("logo_w", 560); logo_x = (W - logo_w) / 2; logo_y = P.get("logo_y", title_y + title_h * 0.72)
LW, LH = 506.84, 303.87; logo_h = logo_w * LH / LW
H = P.get("H", logo_y + logo_h + 10)

# --- bladcluster uit SFS (regio linksonder), volledig ---
sfs = open(f"{R}/sfs-logo-bron.svg").read()
num = re.compile(r'-?\d*\.?\d+(?:e-?\d+)?'); els = []
for m in re.finditer(r'<(path|polygon|polyline)\b[^>]*/>', sfs):
    d = re.search(r'\b(?:d|points)="([^"]+)"', m.group(0))
    if not d: continue
    ns = [float(x) for x in num.findall(d.group(1))]
    if 0 <= ns[0] <= 95 and 170 <= ns[1] <= 295: els.append(m.group(0))
defs_sfs = sfs[sfs.index("<defs>"):sfs.index("</defs>") + 7]
# unieke prefix voor ids/klassen om botsing met het MJ-logo te vermijden
defs_sfs = re.sub(r'id="', 'id="sfs-', defs_sfs).replace("url(#", "url(#sfs-").replace('xlink:href="#', 'xlink:href="#sfs-')
defs_sfs = re.sub(r'\.cls-', '.sfs-cls-', defs_sfs)
leaf = "".join(els).replace("url(#", "url(#sfs-"); leaf = re.sub(r'class="cls-', 'class="sfs-cls-', leaf)
# cluster-bbox ≈ x 2.8..65, y 187..287 → verplaats naar oorsprong
LEAF_BB = (2.8, 187.4, 64.9, 287.4); lw, lh = LEAF_BB[2] - LEAF_BB[0], LEAF_BB[3] - LEAF_BB[1]
def leaf_at(x, y, h, rot=0, flip=False):
    s = h / lh
    t = f"translate({x} {y}) rotate({rot}) scale({-s if flip else s} {s}) translate({-LEAF_BB[0]} {-LEAF_BB[1]})"
    return f'<g transform="{t}">{leaf}</g>'
leaves = "".join(leaf_at(**l) for l in P.get("leaves", [
    {"x": 40, "y": 60, "h": 300, "rot": -8},
    {"x": 960, "y": 60, "h": 300, "rot": 8, "flip": True},
]))

# --- MJ-logo (origineel), ingebed als geneste svg ---
mj = open(f"{R}/logo-mj-bron.svg", encoding="utf-8").read()
mj = mj[mj.index("<svg"):]; mj = re.sub(r'<svg[^>]*>', f'<svg viewBox="0 0 {LW} {LH}" x="{logo_x}" y="{logo_y}" width="{logo_w}" height="{logo_h}">', mj, count=1)
mj = mj.replace('<?xml version="1.0" encoding="UTF-8"?>', "")
if P.get("no_r", True):
    mj = re.sub(r'<path class="cls-45" d="M478\.66,33\.46[^"]*"/>', "", mj)  # ®-teken weg

title_b64 = base64.b64encode(open(TITLE_PNG, "rb").read()).decode()
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{-P.get("pad",0)} {P.get("y0",0)} {W + 2*P.get("pad",0)} {H - P.get("y0",0)}">
  {defs_sfs}
  <g id="bladeren">{leaves}</g>
  <image id="titel-expeditie" x="{title_x}" y="{title_y}" width="{title_w}" height="{title_h}" xlink:href="data:image/png;base64,{title_b64}"/>
  <g id="mj-logo">{mj}</g>
</svg>'''
open(OUT, "w", encoding="utf-8").write(svg); print(OUT, f"H={H:.0f} logo_y={logo_y:.0f}")

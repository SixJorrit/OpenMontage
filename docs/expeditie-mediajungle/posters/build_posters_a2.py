"""DEFINITIEVE posterreeks (stijl A — chatgesprek) op A2 + 3mm afloop.

Pagina 426x600mm, RGB (drukwerkdeal converteert zelf naar CMYK; tekst blijft zo
vector-scherp). Recept per poster: artwork full-bleed, E14-logo (4000px)
rechtsboven, slogan als wit+geel chatballon-duo linksboven in Simple Stamp
(ligaturen uit), witte ballon fit-content, iets lucht tussen staartje en gele
ballon. Missie 4 = stijl A op de staande-Boaz-master (def 2026-09-15).
"""
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path("/Users/jorrit/dev/OpenMontage")
PROJ = ROOT / "projects/expeditie-mediajungle-posters"
OUT = PROJ / "renders/a2"
BUILD = PROJ / "build"
OUT.mkdir(parents=True, exist_ok=True)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
LOGO = (ROOT / "docs/expeditie-mediajungle/references/logo-expeditie-mj-4000.png").as_uri()

R3 = PROJ / "assets/images/round-3"
R4 = PROJ / "assets/images/round-4"

POSTERS = [
    {"id": "poster-missie-1-chatgesprek-A2", "art": R3 / "p1a-jeep-bubbles-logozone.png",
     "wit": "Houd het gezellig<br>en sociaal online.", "geel": "Dat is chill, dat is fijn!",
     "geel_nowrap": True},
    {"id": "poster-missie-2-chatgesprek-A2", "art": R3 / "p2-tent-think-first-logozone.png",
     "wit": "Eerst denken,<br>dan verzenden.", "geel": "Dat scheelt een hoop ellende!",
     "geel_nowrap": True},
    {"id": "poster-missie-3-chatgesprek-A2", "art": R4 / "p3c-hammock-sky-final.png",
     "wit": "Gebruik je scherm<br>gezond bewust.", "geel": "Dat geeft je lichaam<br>kracht én rust!",
     "geel_nowrap": False},
    {"id": "poster-missie-4-chatgesprek-A2", "art": R3 / "p3-staand-logozone.png",
     "wit": "Laat je niet pushen,<br>laat je niet foppen", "geel": "bij een potje online shoppen!",
     "geel_nowrap": True},
]

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  @page {{ size: 426mm 600mm; margin: 0; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ width: 426mm; height: 600mm; }}
  body {{ position: relative; overflow: hidden;
         font-family: "Simple Stamp", "Baloo 2", sans-serif;
         font-variant-ligatures: none; font-feature-settings: "liga" 0, "clig" 0; }}
  .art {{ position: absolute; inset: 0; width: 426mm; height: 600mm;
         object-fit: cover; object-position: 50% 0%; }}
</style></head>
<body>
  <img class="art" src="{art}">
  <img src="{logo}" style="position:absolute; top:16mm; right:16mm; width:142mm;">
  <div style="position:absolute; top:24mm; left:20mm;">
    <div style="position:relative; width:fit-content; background:#FFF9EC; border-radius:14mm;
                padding:14mm 18mm; box-shadow:0 4mm 8mm rgba(0,0,0,0.30);
                transform:rotate(-1.5deg); color:#4A2C17; font-size:17mm; line-height:1.15;">
      {wit}
      <div style="position:absolute; left:28mm; bottom:-9.2mm; width:0; height:0;
                  border-left:10mm solid transparent; border-right:3mm solid transparent;
                  border-top:10mm solid #FFF9EC;"></div>
    </div>
    <div style="position:relative; width:fit-content; background:#F5C518; border-radius:14mm;
                padding:14mm 18mm; margin:16mm 0 0 32mm; {nowrap}
                box-shadow:0 4mm 8mm rgba(0,0,0,0.30); transform:rotate(1.2deg);
                color:#4A2C17; font-size:17mm; line-height:1.15;">
      {geel}
      <div style="position:absolute; right:28mm; bottom:-9.2mm; width:0; height:0;
                  border-right:10mm solid transparent; border-left:3mm solid transparent;
                  border-top:10mm solid #F5C518;"></div>
    </div>
  </div>
</body></html>
"""

import sys
only = sys.argv[1:] or None
for p in POSTERS:
    if only and p["id"] not in only:
        continue
    jpg = BUILD / (Path(p["art"]).stem + "-a2.jpg")
    Image.open(p["art"]).convert("RGB").save(jpg, quality=95)
    html_path = PROJ / f"{p['id']}.html"
    html_path.write_text(HTML.format(
        art=jpg.as_uri(), logo=LOGO, wit=p["wit"], geel=p["geel"],
        nowrap="white-space:nowrap;" if p["geel_nowrap"] else ""))
    pdf_path = OUT / f"{p['id']}.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}", html_path.as_uri()], check=True, capture_output=True)
    subprocess.run(["pdftoppm", "-r", "150", "-png", "-singlefile", str(pdf_path),
                    str(OUT / (p["id"] + "-150dpi"))], check=True)
    subprocess.run(["pdftoppm", "-r", "60", "-png", "-singlefile", str(pdf_path),
                    str(OUT / (p["id"] + "-preview"))], check=True)
    print("built", p["id"])
print("done ->", OUT)

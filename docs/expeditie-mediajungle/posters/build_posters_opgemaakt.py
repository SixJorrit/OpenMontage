"""Opgemaakte posters: E14-logo linksboven + missietekst (Baloo 2 Medium) als laag
over de kale logozone-masters. Niet-destructief: masters blijven onaangetast.

Nummering 2026-09-11: missie 3 = gezond schermgebruik (nog geen poster);
online shoppen = missie 4.
"""
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path("/Users/jorrit/dev/OpenMontage")
PROJ = ROOT / "projects/expeditie-mediajungle-posters"
IMG = PROJ / "assets/images/round-3"
OUT = PROJ / "renders/opgemaakt"
BUILD = PROJ / "build"
OUT.mkdir(parents=True, exist_ok=True)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
LOGO = (ROOT / "docs/expeditie-mediajungle/references/logo-expeditie-mj-2000.png").as_uri()

BROWN = "#4A2C17"
WHITE = "#FFFFFF"

POSTERS = [
    {
        "id": "poster-missie-1-def",
        "art": "p1a-jeep-bubbles-logozone.png",
        "color": BROWN,
        "shadow": "0 0.5mm 1.6mm rgba(255,246,227,0.55)",
        "par1": ["Houd het gezellig", "en sociaal online."],
        "par2": ["Dat is chill,", "dat is fijn!"],
    },
    {
        "id": "poster-missie-2-def",
        "art": "p2-tent-think-first-logozone.png",
        "color": WHITE,
        "shadow": "0 0.6mm 2mm rgba(0,0,0,0.45)",
        "par1": ["Eerst denken,", "dan verzenden."],
        "par2": ["Dat scheelt een", "hoop ellende!"],
    },
    {
        "id": "poster-missie-4-def",
        "art": "p3-staand-logozone.png",
        "color": BROWN,
        "shadow": "0 0.5mm 1.6mm rgba(255,246,227,0.55)",
        "par1": ["Laat je niet pushen,", "laat je niet foppen"],
        "par2": ["bij een potje", "online shoppen!"],
    },
]

TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  @page {{ size: 216mm 303mm; margin: 0; }}
  * {{ margin: 0; padding: 0; }}
  html, body {{ width: 216mm; height: 303mm; }}
  body {{ position: relative; overflow: hidden;
         font-family: "Baloo 2 Medium", "Baloo 2", "Arial Rounded MT Bold", sans-serif; }}
  .art {{ position: absolute; inset: 0; width: 216mm; height: 303mm;
         object-fit: cover; object-position: 50% 0%; }}
  .logo {{ position: absolute; top: 9mm; left: 9mm; width: 104mm; }}
  .tekst {{ position: absolute; top: 55mm; left: 12mm; width: 112mm;
           color: {color}; font-weight: 500; font-size: 9.2mm; line-height: 1.18;
           text-shadow: {shadow}; }}
  .tekst p + p {{ margin-top: 4mm; }}
</style></head>
<body>
  <img class="art" src="{art}">
  <img class="logo" src="{logo}">
  <div class="tekst">
    <p>{par1}</p>
    <p>{par2}</p>
  </div>
</body></html>
"""

for p in POSTERS:
    jpg = BUILD / (Path(p["art"]).stem + ".jpg")
    Image.open(IMG / p["art"]).convert("RGB").save(jpg, quality=95)
    html_path = PROJ / f"{p['id']}.html"
    html_path.write_text(TEMPLATE.format(
        art=jpg.as_uri(), logo=LOGO, color=p["color"], shadow=p["shadow"],
        par1="<br>".join(p["par1"]), par2="<br>".join(p["par2"]),
    ))
    pdf_path = OUT / f"{p['id']}.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}", html_path.as_uri()], check=True, capture_output=True)
    subprocess.run(["pdftoppm", "-r", "300", "-png", "-singlefile", str(pdf_path), str(OUT / p["id"])], check=True)
    subprocess.run(["pdftoppm", "-r", "72", "-png", "-singlefile", str(pdf_path), str(OUT / (p["id"] + "-preview"))], check=True)
    print("built", p["id"])
print("done ->", OUT)

"""Maak de drie A4-posters op: artwork full-bleed + scherpe typografielaag.

Pagina: 216x303mm (A4 + 3mm afloop rondom), 300 dpi.
Typografie: Baloo 2 (systeemfont), slogans boven, footerband met mj-logo-clean.png
+ 'MISSIE X' onderin. Output: PDF (drukker) + PNG (300 dpi) per poster.
"""
import subprocess
from pathlib import Path

ROOT = Path("/Users/jorrit/dev/OpenMontage")
PROJ = ROOT / "projects/expeditie-mediajungle-posters"
IMG = PROJ / "assets/images"
OUT = PROJ / "renders"
OUT.mkdir(exist_ok=True)
LOGO = (ROOT / "docs/expeditie-mediajungle/references/mj-logo-clean.png").as_uri()

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

BROWN = "#4A2C17"
YELLOW = "#F5C518"
TEAL = "#2FB8A8"
CREAM = "#FFF6E3"

POSTERS = [
    {
        "id": "poster-1-missie-1",
        "art": "poster-1-jeep.png",
        "object_position": "50% 0%",   # crop onderin: daar zit het meegebakken logo
        "line1": "Ook zo klaar met haat online?",
        "line2": "Zeg wat aardigs, das pas fijn!",
        "missie": "MISSIE 1",
    },
    {
        "id": "poster-2-missie-2",
        "art": "poster-2-tent.png",
        "object_position": "50% 0%",   # donkere band bovenin = slogan-zone
        "line1": "Eerst denken, dan verzenden,",
        "line2": "dat scheelt een hoop ellende!",
        "missie": "MISSIE 2",
    },
    {
        "id": "poster-3-missie-3",
        "art": "poster-3-cocos-v3.png",
        "object_position": "50% 100%",  # crop bovenin: schoenen onderin vrijhouden
        "line1": "Wees een baas! Laat je niet foppen",
        "line2": "tijdens het online shoppen!",
        "missie": "MISSIE 3",
        "font_size": "11.0mm",
    },
]

TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  @page {{ size: 216mm 303mm; margin: 0; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ width: 216mm; height: 303mm; }}
  body {{ position: relative; overflow: hidden; font-family: "Baloo 2", "Arial Rounded MT Bold", sans-serif; }}

  .art {{ position: absolute; inset: 0; width: 216mm; height: 303mm;
         object-fit: cover; object-position: {object_position}; }}

  /* Slogan boven: dubbele laag voor een dikke bruine outline achter de vulling */
  .slogan {{ position: absolute; top: 13mm; left: 8mm; right: 8mm;
            text-align: center; transform: rotate(-1.6deg); }}
  .line {{ position: relative; display: block; font-weight: 800; white-space: nowrap;
          font-size: {font_size}; line-height: 1.22; letter-spacing: 0.1mm; }}
  .line .stroke {{ position: absolute; inset: 0;
                  -webkit-text-stroke: 2.4mm {brown}; color: {brown};
                  text-shadow: 0 1.2mm 2.6mm rgba(0,0,0,0.38); }}
  .line .fill {{ position: relative; }}
  .l1 .fill {{ color: {cream}; }}
  .l2 .fill {{ color: {yellow}; }}

  /* Footerband */
  .footer {{ position: absolute; left: -1mm; right: -1mm; bottom: -1mm; height: 25mm;
            background: {brown};
            box-shadow: 0 -1mm 3mm rgba(0,0,0,0.35);
            display: flex; align-items: center; justify-content: center;
            gap: 7mm; padding-bottom: 3mm; }}
  .footer img {{ height: 15.5mm; filter: drop-shadow(0 0 1.4mm rgba(255,246,227,0.5)); }}
  .divider {{ width: 0.6mm; height: 12mm; background: rgba(255,246,227,0.35);
             border-radius: 0.3mm; }}
  .missie-blok {{ display: flex; flex-direction: column; align-items: flex-start;
                 line-height: 1.02; }}
  .expeditie {{ color: {teal}; font-weight: 800; font-size: 4.6mm;
               letter-spacing: 1.7mm; }}
  .missie {{ color: {yellow}; font-weight: 800; font-size: 10.4mm;
            letter-spacing: 0.5mm; }}
</style></head>
<body>
  <img class="art" src="{art}">
  <div class="slogan">
    <span class="line l1"><span class="stroke">{line1}</span><span class="fill">{line1}</span></span>
    <span class="line l2"><span class="stroke">{line2}</span><span class="fill">{line2}</span></span>
  </div>
  <div class="footer">
    <img src="{logo}">
    <div class="divider"></div>
    <div class="missie-blok">
      <span class="expeditie">EXPEDITIE</span>
      <span class="missie">{missie}</span>
    </div>
  </div>
</body></html>
"""

from PIL import Image

BUILD = PROJ / "build"
BUILD.mkdir(exist_ok=True)

for p in POSTERS:
    # JPEG q95 voor de PDF-embed: op 300 dpi visueel identiek, drukbestand blijft klein
    jpg = BUILD / (Path(p["art"]).stem + ".jpg")
    Image.open(IMG / p["art"]).convert("RGB").save(jpg, quality=95)
    html_path = PROJ / f"{p['id']}.html"
    html_path.write_text(TEMPLATE.format(
        art=jpg.as_uri(), logo=LOGO,
        object_position=p["object_position"],
        line1=p["line1"], line2=p["line2"], missie=p["missie"],
        font_size=p.get("font_size", "12.6mm"),
        brown=BROWN, yellow=YELLOW, teal=TEAL, cream=CREAM,
    ))
    pdf_path = OUT / f"{p['id']}.pdf"
    subprocess.run([
        CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}", html_path.as_uri(),
    ], check=True, capture_output=True)
    subprocess.run([
        "pdftoppm", "-r", "300", "-png", "-singlefile",
        str(pdf_path), str(OUT / p["id"]),
    ], check=True)
    # kleine preview voor inspectie
    subprocess.run([
        "pdftoppm", "-r", "72", "-png", "-singlefile",
        str(pdf_path), str(OUT / (p["id"] + "-preview")),
    ], check=True)
    print("built", p["id"])
print("done ->", OUT)

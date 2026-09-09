"""Ronde 2: tekstloze A4-posters — full-bleed artwork, geen typografielaag.

Pagina: 216x303mm (A4 + 3mm afloop), 300 dpi. PDF embedt JPEG q95; PNG via pdftoppm.
"""
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path("/Users/jorrit/dev/OpenMontage")
PROJ = ROOT / "projects/expeditie-mediajungle-posters"
IMG = PROJ / "assets/images/round-2"
OUT = PROJ / "renders/round-2"
BUILD = PROJ / "build"
OUT.mkdir(parents=True, exist_ok=True)
BUILD.mkdir(exist_ok=True)

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

POSTERS = [
    {"id": "poster-1a-jeep-bubbels", "art": "p1a-jeep-bubbles-v2.png"},
    {"id": "poster-1b-jeep-telefoonhart", "art": "p1b-jeep-phone-heart-final.png"},
    {"id": "poster-2-tent-eerst-denken", "art": "p2-tent-think-first.png"},
    {"id": "poster-3-cocos-koopjes", "art": "p3-cocos-scale-fix-final.png"},
]

TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  @page {{ size: 216mm 303mm; margin: 0; }}
  * {{ margin: 0; padding: 0; }}
  html, body {{ width: 216mm; height: 303mm; }}
  body {{ position: relative; overflow: hidden; }}
  .art {{ position: absolute; inset: 0; width: 216mm; height: 303mm;
         object-fit: cover; object-position: 50% 0%; }}
</style></head>
<body><img class="art" src="{art}"></body></html>
"""

for p in POSTERS:
    jpg = BUILD / (Path(p["art"]).stem + ".jpg")
    Image.open(IMG / p["art"]).convert("RGB").save(jpg, quality=95)
    html_path = PROJ / f"{p['id']}.html"
    html_path.write_text(TEMPLATE.format(art=jpg.as_uri()))
    pdf_path = OUT / f"{p['id']}.pdf"
    subprocess.run([
        CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}", html_path.as_uri(),
    ], check=True, capture_output=True)
    subprocess.run(["pdftoppm", "-r", "300", "-png", "-singlefile", str(pdf_path), str(OUT / p["id"])], check=True)
    subprocess.run(["pdftoppm", "-r", "72", "-png", "-singlefile", str(pdf_path), str(OUT / (p["id"] + "-preview"))], check=True)
    print("built", p["id"])
print("done ->", OUT)

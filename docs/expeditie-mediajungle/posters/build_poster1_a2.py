"""Poster 1 (missie 1, stijl A chatgesprek) op A2 + 3mm afloop, drukklaar.

Pagina 426x600mm (A2 = 420x594 + 3mm rondom), 300 dpi. Artwork ~200 dpi op dit
formaat (4k-bron, prima op posterkijkafstand); ballonnen, tekst en logo (4000px)
renderen op volle scherpte. Fixes t.o.v. het opzetje: witte ballon past zich aan
de tekst aan (fit-content) en er zit iets meer ruimte tussen het staartje van de
witte ballon en de gele ballon.
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
ART = PROJ / "assets/images/round-3/p1a-jeep-bubbles-logozone.png"

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
      Houd het gezellig<br>en sociaal online.
      <div style="position:absolute; left:28mm; bottom:-9.2mm; width:0; height:0;
                  border-left:10mm solid transparent; border-right:3mm solid transparent;
                  border-top:10mm solid #FFF9EC;"></div>
    </div>
    <div style="position:relative; width:fit-content; background:#F5C518; border-radius:14mm;
                padding:14mm 18mm; margin:16mm 0 0 32mm; white-space:nowrap;
                box-shadow:0 4mm 8mm rgba(0,0,0,0.30); transform:rotate(1.2deg);
                color:#4A2C17; font-size:17mm; line-height:1.15;">
      Dat is chill, dat is fijn!
      <div style="position:absolute; right:28mm; bottom:-9.2mm; width:0; height:0;
                  border-right:10mm solid transparent; border-left:3mm solid transparent;
                  border-top:10mm solid #F5C518;"></div>
    </div>
  </div>
</body></html>
"""

jpg = BUILD / "p1a-logozone-a2.jpg"
Image.open(ART).convert("RGB").save(jpg, quality=95)
html_path = PROJ / "poster-missie-1-a2.html"
html_path.write_text(HTML.format(art=jpg.as_uri(), logo=LOGO))
pdf_path = OUT / "poster-missie-1-chatgesprek-A2.pdf"
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={pdf_path}", html_path.as_uri()], check=True, capture_output=True)
subprocess.run(["pdftoppm", "-r", "150", "-png", "-singlefile", str(pdf_path),
                str(OUT / "poster-missie-1-chatgesprek-A2-150dpi")], check=True)
subprocess.run(["pdftoppm", "-r", "60", "-png", "-singlefile", str(pdf_path),
                str(OUT / "poster-missie-1-chatgesprek-A2-preview")], check=True)
print("built ->", pdf_path)

"""Drie vrije-hand opzetjes voor poster 1 (lage resolutie previews).

A: slogan als chatballonnen linksboven, logo rechtsboven.
B: slogan op een houten junglebord linksboven, logo erboven.
C: nieuw hero-artwork (ballonnenlucht), logo + tekst groot gecentreerd.
"""
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path("/Users/jorrit/dev/OpenMontage")
PROJ = ROOT / "projects/expeditie-mediajungle-posters"
OUT = PROJ / "renders/opzetjes"
BUILD = PROJ / "build"
OUT.mkdir(parents=True, exist_ok=True)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
LOGO = (ROOT / "docs/expeditie-mediajungle/references/logo-expeditie-mj-2000.png").as_uri()

BASE_CSS = """
  @page { size: 216mm 303mm; margin: 0; }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 216mm; height: 303mm; }
  body { position: relative; overflow: hidden;
         font-family: "Simple Stamp", "Baloo 2", sans-serif;
         font-variant-ligatures: none; font-feature-settings: "liga" 0, "clig" 0; }
  .art { position: absolute; inset: 0; width: 216mm; height: 303mm;
         object-fit: cover; object-position: 50% 0%; }
"""

ART_A = (PROJ / "assets/images/round-3/p1a-jeep-bubbles-logozone.png")
ART_C = (PROJ / "assets/images/round-4/p1c-balloon-sky.png")

OPZETJES = {
    "opzet-a-chatgesprek": {
        "art": ART_A,
        "html": """
  <img class="art" src="{art}">
  <img src="{logo}" style="position:absolute; top:8mm; right:8mm; width:72mm;">
  <div style="position:absolute; top:12mm; left:10mm; width:118mm;">
    <div style="position:relative; background:#FFF9EC; border-radius:7mm; padding:7mm 9mm;
                box-shadow:0 2mm 4mm rgba(0,0,0,0.30); transform:rotate(-1.5deg);
                color:#4A2C17; font-size:8.6mm; line-height:1.15;">
      Houd het gezellig<br>en sociaal online.
      <div style="position:absolute; left:14mm; bottom:-4.6mm; width:0; height:0;
                  border-left:5mm solid transparent; border-right:1.5mm solid transparent;
                  border-top:5mm solid #FFF9EC;"></div>
    </div>
    <div style="position:relative; background:#F5C518; border-radius:7mm; padding:7mm 9mm;
                margin:7mm 0 0 16mm; width:100mm; white-space:nowrap;
                box-shadow:0 2mm 4mm rgba(0,0,0,0.30); transform:rotate(1.2deg);
                color:#4A2C17; font-size:8.6mm; line-height:1.15;">
      Dat is chill, dat is fijn!
      <div style="position:absolute; right:14mm; bottom:-4.6mm; width:0; height:0;
                  border-right:5mm solid transparent; border-left:1.5mm solid transparent;
                  border-top:5mm solid #F5C518;"></div>
    </div>
  </div>
""",
    },
    "opzet-b-junglebord": {
        "art": ART_A,
        "html": """
  <img class="art" src="{art}">
  <img src="{logo}" style="position:absolute; top:8mm; left:9mm; width:88mm;">
  <div style="position:absolute; top:48mm; left:10mm; width:112mm; transform:rotate(-2.2deg);
              background:linear-gradient(180deg,#8a5a30 0%,#7a4c26 30%,#6d421f 100%);
              border:2.2mm solid #4A2C17; border-radius:4mm; padding:8mm 9mm 9mm;
              box-shadow:0 2.5mm 5mm rgba(0,0,0,0.4), inset 0 1mm 2mm rgba(255,235,200,0.35);
              color:#FFF3DC; font-size:8.8mm; line-height:1.2; text-align:center;
              text-shadow:0 0.6mm 1mm rgba(0,0,0,0.4);">
    Houd het gezellig en sociaal online.<br>Dat is chill, dat is fijn!
    <div style="position:absolute; top:2.5mm; left:4mm; width:3mm; height:3mm;
                border-radius:50%; background:#3a2211;"></div>
    <div style="position:absolute; top:2.5mm; right:4mm; width:3mm; height:3mm;
                border-radius:50%; background:#3a2211;"></div>
    <div style="position:absolute; bottom:2.5mm; left:4mm; width:3mm; height:3mm;
                border-radius:50%; background:#3a2211;"></div>
    <div style="position:absolute; bottom:2.5mm; right:4mm; width:3mm; height:3mm;
                border-radius:50%; background:#3a2211;"></div>
  </div>
""",
    },
    "opzet-c-ballonnenlucht": {
        "art": ART_C,
        "html": """
  <img class="art" src="{art}">
  <img src="{logo}" style="position:absolute; top:14mm; left:50%; transform:translateX(-50%); width:128mm;">
  <div style="position:absolute; top:74mm; left:50%; transform:translateX(-50%); width:170mm;
              text-align:center; color:#4A2C17; font-size:10.6mm; line-height:1.22;
              text-shadow:0 0 2mm rgba(255,250,235,0.95), 0 0 5mm rgba(255,250,235,0.8);">
    Houd het gezellig<br>en sociaal online.<br>
    <span style="font-size:12.4mm;">Dat is chill, dat is fijn!</span>
  </div>
""",
    },
}

TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{css}</style></head>
<body>{body}</body></html>
"""

for pid, spec in OPZETJES.items():
    jpg = BUILD / (Path(spec["art"]).stem + ".jpg")
    Image.open(spec["art"]).convert("RGB").save(jpg, quality=95)
    html_path = PROJ / f"{pid}.html"
    html_path.write_text(TEMPLATE.format(css=BASE_CSS,
                                         body=spec["html"].format(art=jpg.as_uri(), logo=LOGO)))
    pdf_path = OUT / f"{pid}.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}", html_path.as_uri()], check=True, capture_output=True)
    subprocess.run(["pdftoppm", "-r", "100", "-png", "-singlefile", str(pdf_path), str(OUT / pid)], check=True)
    print("built", pid)
print("done ->", OUT)

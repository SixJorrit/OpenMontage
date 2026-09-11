"""Vrije-hand opzetjes voor alle missies: A (chatballonnen) en C (hero-lucht).

Output: previews op 100dpi in renders/opzetjes/ + één deelbare feedbackplaat.
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

R3 = PROJ / "assets/images/round-3"
R4 = PROJ / "assets/images/round-4"

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

def bubbel_html(b1_lines, b2_text, b2_width, b2_font="8.2mm"):
    b1 = "<br>".join(b1_lines)
    return f"""
  <img class="art" src="{{art}}">
  <img src="{{logo}}" style="position:absolute; top:8mm; right:8mm; width:72mm;">
  <div style="position:absolute; top:12mm; left:10mm; width:120mm;">
    <div style="position:relative; background:#FFF9EC; border-radius:7mm; padding:7mm 9mm;
                box-shadow:0 2mm 4mm rgba(0,0,0,0.30); transform:rotate(-1.5deg);
                color:#4A2C17; font-size:8.6mm; line-height:1.15; width:fit-content;">
      {b1}
      <div style="position:absolute; left:14mm; bottom:-4.6mm; width:0; height:0;
                  border-left:5mm solid transparent; border-right:1.5mm solid transparent;
                  border-top:5mm solid #FFF9EC;"></div>
    </div>
    <div style="position:relative; background:#F5C518; border-radius:7mm; padding:7mm 9mm;
                margin:7mm 0 0 16mm; width:{b2_width}; white-space:nowrap;
                box-shadow:0 2mm 4mm rgba(0,0,0,0.30); transform:rotate(1.2deg);
                color:#4A2C17; font-size:{b2_font}; line-height:1.15;">
      {b2_text}
      <div style="position:absolute; right:14mm; bottom:-4.6mm; width:0; height:0;
                  border-right:5mm solid transparent; border-left:1.5mm solid transparent;
                  border-top:5mm solid #F5C518;"></div>
    </div>
  </div>
"""

def hero_html(lines_small, line_big, color, glow, big_font="12.4mm"):
    small = "<br>".join(lines_small)
    return f"""
  <img class="art" src="{{art}}">
  <img src="{{logo}}" style="position:absolute; top:14mm; left:50%; transform:translateX(-50%); width:128mm;">
  <div style="position:absolute; top:74mm; left:50%; transform:translateX(-50%); width:176mm;
              text-align:center; color:{color}; font-size:10.6mm; line-height:1.22;
              text-shadow:{glow};">
    {small}<br>
    <span style="font-size:{big_font}; white-space:nowrap;">{line_big}</span>
  </div>
"""

GLOW_LICHT = "0 0 2mm rgba(255,250,235,0.95), 0 0 5mm rgba(255,250,235,0.8)"
GLOW_DONKER = "0 0.6mm 2mm rgba(0,0,20,0.55), 0 0 4mm rgba(0,0,20,0.4)"

OPZETJES = {
    "opzet-m2-a-chatgesprek": {
        "art": R3 / "p2-tent-think-first-logozone.png",
        "html": bubbel_html(["Eerst denken,", "dan verzenden."],
                            "Dat scheelt een hoop ellende!", "108mm"),
    },
    "opzet-m4-a-chatgesprek": {
        "art": R3 / "p3-staand-logozone.png",
        "html": bubbel_html(["Laat je niet pushen,", "laat je niet foppen"],
                            "bij een potje online shoppen!", "108mm"),
    },
    "opzet-m2-c-maanlucht": {
        "art": R4 / "p2c-moon-sky.png",
        "html": hero_html(["Eerst denken,", "dan verzenden."],
                          "Dat scheelt een hoop ellende!", "#FFFFFF", GLOW_DONKER, "11.4mm"),
    },
    "opzet-m3-c-hangmat": {
        "art": R4 / "p3c-hammock-sky.png",
        "html": hero_html(["Gebruik je scherm", "gezond bewust."],
                          "Dat geeft je lichaam kracht én rust!", "#4A2C17", GLOW_LICHT, "10.2mm"),
    },
    "opzet-m4-c-parachutes": {
        "art": R4 / "p4c-parachute-sky.png",
        "html": hero_html(["Laat je niet pushen,", "laat je niet foppen"],
                          "bij een potje online shoppen!", "#4A2C17", GLOW_LICHT, "11.4mm"),
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
print("done")

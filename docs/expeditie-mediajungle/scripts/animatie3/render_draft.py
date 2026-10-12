# -*- coding: utf-8 -*-
"""Animatie 3 — Remotion-render van de ExpeditieMJ-compositie met de props uit compose_prep_a3, daarna
een masterpass (statische gain naar I=-16 LUFS + true-peak-limiter -1,5 dBTP) en een shotlabel-napass (PNG-overlay per shotvenster).
    PYTHONPATH=. .venv/bin/python projects/expeditie-mj-animatie3/render_draft.py <draftnr> [--lowres]
--lowres: Remotion --scale=0.5 (640x360), lichtere encode; bedoeld voor snelle reviewdrafts. Bestandsnaam krijgt -360p.
"""
import json, pathlib, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
PROJ = pathlib.Path("projects/expeditie-mj-animatie3").resolve()
args = [a for a in sys.argv[1:] if not a.startswith("--")]; LOW = "--lowres" in sys.argv
DRAFT = args[0] if args else "1"; SUF = "-360p" if LOW else ""; SC = 0.5 if LOW else 1.0
REND = PROJ / "renders"; REND.mkdir(exist_ok=True); LAB = PROJ / "previews/draft-labels"; LAB.mkdir(parents=True, exist_ok=True)
props = PROJ / "artifacts/remotion_props.json"
raw = REND / f"animatie3-DRAFT{DRAFT}{SUF}-raw.mp4"; clean = REND / f"animatie3-DRAFT{DRAFT}{SUF}-clean.mp4"; labeled = REND / f"animatie3-DRAFT{DRAFT}{SUF}-shotlabels.mp4"
cmd = ["npx", "remotion", "render", "src/index.tsx", "ExpeditieMJ", str(raw), f"--props={props}", "--log=error"]
if LOW: cmd += ["--scale=0.5", "--crf=26"]
subprocess.run(cmd, cwd="remotion-composer", check=True); print("render:", raw)
# masterpass: meten, dan lineair corrigeren
TI, TTP, TLRA = -16.0, -1.5, 11.0
err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(raw), "-af", f"loudnorm=I={TI}:TP={TTP}:LRA={TLRA}:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
m = json.loads(err[err.rindex("{"):err.rindex("}") + 1])
# loudnorm valt bij LRA > doel of te hoge piek terug op dynamische modus (pompt); daarom statische gain + true-peak-limiter
gain = TI - float(m["input_i"]); lim = 10 ** (TTP / 20)
ln = f"volume={gain:.2f}dB,aresample=192000,alimiter=limit={lim:.4f}:attack=2:release=50:level=disabled,aresample=48000"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", ln, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(clean)], check=True)
print(f"master: in I={m['input_i']} TP={m['input_tp']} LRA={m['input_lra']} -> statische gain {gain:+.2f} dB + limiter {TTP} dBTP")
raw.unlink()
wins = json.load(open(PROJ / "artifacts/draft_label_windows.json"))
try: font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(34 * SC))
except Exception: font = ImageFont.load_default()
inputs = ["-i", str(clean)]; fc = []; prev = "[0:v]"; off = int(24 * SC)
for i, w in enumerate(wins, 1):
    text = w["shot"].replace("shot_", ""); png = LAB / f"{text}{SUF}.png"
    if not png.exists():
        im = Image.new("RGBA", (int(150 * SC), int(52 * SC)), (0, 0, 0, 150)); ImageDraw.Draw(im).text((int(14 * SC), int(8 * SC)), text, font=font, fill=(255, 255, 255, 255)); im.save(png)
    inputs += ["-i", str(png)]
    fc.append(f"{prev}[{i}:v]overlay={off}:{off}:enable='between(t,{w['start']:.3f},{w['end']:.3f})'[v{i}]"); prev = f"[v{i}]"
subprocess.run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", ";".join(fc), "-map", prev, "-map", "0:a", "-c:v", "libx264", "-crf", "24" if LOW else "19", "-preset", "veryfast" if LOW else "medium", "-c:a", "copy", str(labeled)], check=True)
print("labels:", labeled)

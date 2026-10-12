# -*- coding: utf-8 -*-
"""Audioketen v2 (2026-10-12): filmaudio van álle regels en zinsdelen uit opname 2, op 44,1 kHz.
Verschil met split_recording.py (dat blijft de bron voor de 16k-referenties):
  - geen loudnorm per regel (dynamische modus op korte clips pompt en vlakt de opname-dynamiek af);
    in plaats daarvan één statische gain PER SPREKER, gemeten over al het materiaal van die spreker (in de opname
    staat Boaz ~6 LU zachter dan Femke); binnen een stem blijven de verhoudingen zoals opgenomen;
  - ook de zinsdelen (s02p12, s02p3, s06p1, s06p2, s07p1, s07p2) op 44,1 kHz — v1 gebruikte daarvoor de 16k-
    referentiebestanden als filmaudio (dof, bandbreedte 8 kHz);
  - knippen, blokkoppeling en atempo identiek aan v1 (door Jorrit goedgekeurd), dus de timing en de bestaande
    warps blijven gelden.
Schrijft assets/audio/lines/film/<id>.wav en film/levels.json.
    PYTHONPATH=. .venv/bin/python projects/expeditie-mj-animatie3/split_film_audio.py
"""
import json, pathlib, subprocess, importlib.util, sys
PROJ = pathlib.Path("projects/expeditie-mj-animatie3"); L = PROJ / "assets/audio/lines"; F = L / "film"; TMP = L / "_tmp_film"
F.mkdir(parents=True, exist_ok=True); TMP.mkdir(exist_ok=True)
TARGET_I = -16.0

# hergebruik BLOCKS/LINES/PARTS en de knipfuncties van v1 zonder het v1-script uit te voeren
src = (PROJ / "split_recording.py").read_text()
head = src.split("for d in (N, P, PREV, TMP): d.mkdir")[0]
ns = {}; exec(compile(head, "split_recording_head", "exec"), ns)
SRC, BLOCKS, LINES, PARTS, HEAD, TAIL = ns["SRC"], ns["BLOCKS"], ns["LINES"], ns["PARTS"], ns["HEAD"], ns["TAIL"]
dur = ns["dur"]; azure_words = ns["azure_words"]
def run(cmd): subprocess.run(cmd, check=True)

def lufs(p):
    err = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", str(p), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = float([l for l in err.splitlines() if l.strip().startswith("I:")][-1].split()[1])
    pk = float([l for l in err.splitlines() if l.strip().startswith("Peak:")][-1].split()[1])
    return I, pk
src_I, src_pk = lufs(SRC)
SPK = {}
for sid, (who, text, blocks) in LINES.items(): SPK.setdefault(who, []).extend(b for b, _ in blocks)
GAINS = {}
for who, blks in SPK.items():
    f = TMP / f"spk-{who}.wav"
    flt = ";".join(f"[0:a]atrim={BLOCKS[b][0]:.3f}:{BLOCKS[b][1]:.3f},asetpts=PTS-STARTPTS[a{i}]" for i, b in enumerate(blks))
    flt += ";" + "".join(f"[a{i}]" for i in range(len(blks))) + f"concat=n={len(blks)}:v=0:a=1[o]"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-filter_complex", flt, "-map", "[o]", "-ar", "44100", "-ac", "1", str(f)])
    I, pk = lufs(f); GAINS[who] = TARGET_I - I
    print(f"{who}: I={I} LUFS over blokken {blks} -> gain {GAINS[who]:+.2f} dB")
print(f"opname geheel: I={src_I} LUFS, piek {src_pk} dBFS")
GAIN = 0.0

def piece(a, b, tempo, out):
    af = [f"atrim={a:.3f}:{b:.3f}", "asetpts=PTS-STARTPTS"] + ([f"atempo={tempo}"] if tempo != 1.0 else [])
    run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-af", ",".join(af), "-ar", "44100", "-ac", "1", "-c:a", "pcm_f32le", str(out)])

def assemble(segments, out, gain, pad_min=None):
    files = []
    for i, (a, b, tempo) in enumerate(segments):
        f = TMP / f"seg{i}.wav"; piece(a, b, tempo, f); files.append(f)
        if i < len(segments) - 1:
            gap = max(segments[i + 1][0] - b, 0.05); g = TMP / f"gap{i}.wav"
            run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{gap:.3f}", "-c:a", "pcm_f32le", str(g)]); files.append(g)
    lst = TMP / "list.txt"; lst.write_text("".join(f"file '{f.resolve()}'\n" for f in files))
    raw = TMP / "raw.wav"; run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(raw)])
    d = dur(raw); af = ["afade=t=in:d=0.02", f"afade=t=out:st={max(d - 0.03, 0):.3f}:d=0.03", f"volume={gain:.2f}dB", "alimiter=limit=0.89:attack=1:release=40:level=disabled"]
    if pad_min and d < pad_min: af.append(f"apad=pad_dur={pad_min + 0.1 - d:.2f}")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", ",".join(af), "-ar", "44100", "-ac", "1", "-c:a", "pcm_s24le", str(out)])

def segs_from_blocks(blocks):
    segs = []
    for i, (blk, tempo) in enumerate(blocks):
        a, b = BLOCKS[blk]
        a = a - HEAD if i == 0 else a - 0.03
        b = b + TAIL if i == len(blocks) - 1 else b + 0.03
        segs.append((max(0, a), b, tempo))
    return segs

cut_cache = {}
def split_segs(block, n, which, tempo, full_text):
    if (block, n) not in cut_cache:
        a, b = BLOCKS[block]; tmp = TMP / "blk16.wav"
        run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-ar", "16000", "-ac", "1", str(tmp)])
        words = azure_words(tmp, full_text); cut_cache[(block, n)] = a + (words[n - 1]["t1"] + words[n]["t0"]) / 2
    cut = cut_cache[(block, n)]; a, b = BLOCKS[block]
    return [(max(0, a - HEAD), cut, tempo)] if which == 0 else [(cut, b + TAIL, tempo)]

levels = {"source_I": src_I, "source_peak": src_pk, "gain_db": {k: round(v, 2) for k, v in GAINS.items()}, "files": {}}
for sid, (who, text, blocks) in LINES.items():
    out = F / f"{sid}.wav"; assemble(segs_from_blocks(blocks), out, GAINS[who], pad_min=1.8)
    I, pk = lufs(out); levels["files"][sid] = {"I": I, "peak": pk, "dur": round(dur(out), 3)}
    print(f"{sid:7} {who:6} I={I:6.1f}  piek {pk:5.1f}  {dur(out):.2f}s", flush=True)
for pid, (text, spec) in PARTS.items():
    segs = split_segs(spec[1], spec[2], spec[3], spec[4], LINES["s06"][1]) if isinstance(spec, tuple) else segs_from_blocks(spec)
    out = F / f"{pid}.wav"; assemble(segs, out, GAINS[LINES[pid[:3]][0]], pad_min=1.8)
    I, pk = lufs(out); levels["files"][pid] = {"I": I, "peak": pk, "dur": round(dur(out), 3)}
    print(f"{pid:7}        I={I:6.1f}  piek {pk:5.1f}  {dur(out):.2f}s", flush=True)
(F / "levels.json").write_text(json.dumps(levels, indent=1))
# timingcontrole t.o.v. v1 (warps zijn op v1 gemeten)
for f in sorted(F.glob("*.wav")):
    old = (L / "norm" / f.name) if (L / "norm" / f.name).exists() else (L / "parts" / f.name)
    if old.exists() and abs(dur(old) - dur(f)) > 0.03: print(f"  LET OP {f.name}: duur v1 {dur(old):.3f} vs v2 {dur(f):.3f}")
print("klaar:", F)

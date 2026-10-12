# -*- coding: utf-8 -*-
"""Filmaudio uit de gekozen v4-takes: 44,1k/24-bit, stilte aan kop en staart bijgesneden (0,10 / 0,15 s marge),
één vaste gain per spreker naar -16 LUFS (gemeten over alle gekozen takes van die spreker), zinsdelen geknipt
midden in de pauze tussen de woorden (Azure-woordtijden). Schrijft assets/audio/lines/film-v4/<id>.wav + levels.json.
    PYTHONPATH=. .venv/bin/python projects/expeditie-mj-animatie3/build_v4_film.py s01b=2 s02=2 ..."""
import json, pathlib, subprocess, sys, base64, urllib.request, time
PROJ = pathlib.Path("projects/expeditie-mj-animatie3"); V4 = PROJ / "assets/audio/v4"; OUT = PROJ / "assets/audio/lines/film-v4"; OUT.mkdir(parents=True, exist_ok=True)
TMP = OUT / "_tmp"; TMP.mkdir(exist_ok=True)
env = dict(l.rstrip("\n").split("=", 1) for l in open(".env") if "=" in l and not l.startswith("#"))
src = (PROJ / "split_recording.py").read_text(); ns = {}; exec(compile(src.split("for d in (N, P, PREV, TMP): d.mkdir")[0], "h", "exec"), ns)
LINES, PARTS = ns["LINES"], ns["PARTS"]
CHOICE = dict(a.split("=") for a in sys.argv[1:])
lf = OUT / "levels.json"; levels = json.load(open(lf)) if lf.exists() else {"choice": {}, "files": {}, "gain_db": {}}
levels["choice"].update(CHOICE)
def run(c): subprocess.run(["ffmpeg", "-v", "error", "-y", *c], check=True)
def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip())
def lufs(p):
    e = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", str(p), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float([l for l in e.splitlines() if l.strip().startswith("I:")][-1].split()[1])
def words(wav16, text):
    pa = base64.b64encode(json.dumps({"ReferenceText": text, "GradingSystem": "HundredMark", "Granularity": "Word", "EnableMiscue": True}).encode()).decode()
    url = f"https://{env['AZURE_SPEECH_REGION']}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=nl-NL&format=detailed"
    req = urllib.request.Request(url, data=open(wav16, "rb").read(), headers={"Ocp-Apim-Subscription-Key": env["AZURE_SPEECH_KEY"], "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000", "Pronunciation-Assessment": pa, "Accept": "application/json"})
    for at in range(4):
        try: r = json.load(urllib.request.urlopen(req, timeout=120)); break
        except Exception:
            if at == 3: raise
            time.sleep(8)
    return [((w["Offset"]) / 1e7, (w["Offset"] + w["Duration"]) / 1e7) for w in (r.get("NBest") or [{}])[0].get("Words", []) if w.get("ErrorType") != "Omission" and w.get("Duration")]
nw = lambda t: len(t.replace("’", "'").split())
# 1) per gekozen regel: woordtijden, bijsnijden
info = {}
for sid, k in CHOICE.items():
    who, text, _ = LINES[sid]; f = V4 / sid / f"take{k}.mp3"; w16 = TMP / f"{sid}.wav"
    run(["-i", str(f), "-ar", "16000", "-ac", "1", str(w16)]); ws = words(w16, text)
    assert len(ws) == nw(text), f"{sid}: {len(ws)} woorden herkend, {nw(text)} verwacht"
    info[sid] = {"who": who, "file": f, "words": ws, "a": max(0, ws[0][0] - 0.10), "b": min(dur(f), ws[-1][1] + 0.15)}
# 2) gain per spreker over alle gekozen takes (ook eerder gekozen, uit levels.json)
for who in {i["who"] for i in info.values()}:
    cat = TMP / f"cat-{who}.wav"; fs = [i for i in info.values() if i["who"] == who]
    flt = ";".join(f"[{n}:a]atrim={i['a']:.3f}:{i['b']:.3f},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=mono[a{n}]" for n, i in enumerate(fs)) + ";" + "".join(f"[a{n}]" for n in range(len(fs))) + f"concat=n={len(fs)}:v=0:a=1[o]"
    run(sum((["-i", str(i["file"])] for i in fs), []) + ["-filter_complex", flt, "-map", "[o]", str(cat)])
    levels["gain_db"][who] = round(-16.0 - lufs(cat), 2)
def cut(i, a, b, out, gain):
    d = b - a
    run(["-i", str(i["file"]), "-af", f"atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={max(d - 0.04, 0):.3f}:d=0.04,volume={gain:.2f}dB,alimiter=limit=0.89:attack=1:release=40:level=disabled",
         "-ar", "44100", "-ac", "1", "-c:a", "pcm_s24le", str(out)])
    levels["files"][out.stem] = {"dur": round(dur(out), 3), "I": lufs(out)}
for sid, i in info.items():
    g = levels["gain_db"][i["who"]]; cut(i, i["a"], i["b"], OUT / f"{sid}.wav", g)
    # zinsdelen: woordtelling uit PARTS-tekst, knip midden in de pauze
    for pid, (ptext, _) in PARTS.items():
        if not pid.startswith(sid + "p"): continue
        full = LINES[sid][1]; start_w = full.replace("’", "'").find(ptext.replace("’", "'"))
        assert start_w >= 0, pid
        w0 = nw(full[:start_w]); w1 = w0 + nw(ptext); ws = i["words"]
        a = i["a"] if w0 == 0 else (ws[w0 - 1][1] + ws[w0][0]) / 2
        b = i["b"] if w1 == len(ws) else (ws[w1 - 1][1] + ws[w1][0]) / 2
        cut(i, a, b, OUT / f"{pid}.wav", g)
lf.write_text(json.dumps(levels, indent=1, default=str))
for k, v in sorted(levels["files"].items()): print(f"{k:8} {v['dur']:6.2f}s  {v['I']:6.1f} LUFS")
print("gain:", levels["gain_db"])

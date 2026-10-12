# -*- coding: utf-8 -*-
"""Animatie 3 — v4-stemtakes via de API (Jorrit 2026-10-12: "Eleven v4 is echt veel beter", "via de API").
Tekst = LINES uit split_recording.py (bron van waarheid). Per regel N takes eleven_v4 + acteertag, instellingen als opname 2
(stability 0,30, similarity 0,75, speed 1,05). Gates: Azure-meter (nauwkeurigheid, laagste woord, compleetheid) en F0-mediaan
t.o.v. dezelfde spreker in opname 2. Schrijft assets/audio/v4/<sid>/take<k>.mp3, takes.json en een luisterreel.
    PYTHONPATH=. .venv/bin/python projects/expeditie-mj-animatie3/gen_v4.py Femke [--takes 3] [sid=tag ...]"""
import json, os, pathlib, subprocess, sys, base64, urllib.request, urllib.error, time, numpy as np
PROJ = pathlib.Path("projects/expeditie-mj-animatie3"); OUT = PROJ / "assets/audio/v4"; OUT.mkdir(parents=True, exist_ok=True)
env = dict(l.rstrip("\n").split("=", 1) for l in open(".env") if "=" in l and not l.startswith("#"))
src = (PROJ / "split_recording.py").read_text(); ns = {}
exec(compile(src.split("for d in (N, P, PREV, TMP): d.mkdir")[0], "split_head", "exec"), ns)
LINES, BLOCKS, SRC = ns["LINES"], ns["BLOCKS"], ns["SRC"]
VOICE = {"Femke": "YUdpWWny7k5yb4QCeweX", "Boaz": os.environ.get("BOAZ_VOICE_ID")}
SETTINGS = {"stability": 0.30, "similarity_boost": 0.75, "speed": 1.05}
TAGS = {"s01": "excited", "s01b": "playful", "s02": "worried", "s03": "hesitant", "s04": "distracted", "s05": "slightly frustrated",
        "s06": "convinced", "s07": "enthusiastic", "s08": "friendly"}
INLINE = {"s05": "[slightly frustrated] Maar we moeten nu echt iets vinden. [warm] Zullen we anders afspraken hierover maken over onze telefoon waar we allebei blij mee zijn? [determined] We hebben nog een lange reis te gaan.",
          "s06": "[convinced] Dat lijkt mij een goed idee. [excited] Let's go!"}
args = [a for a in sys.argv[1:] if not a.startswith("--")]; who_sel = args[0]
for a in args[1:]:
    if "=" in a: k, v = a.split("=", 1); TAGS[k] = v; INLINE.pop(k, None)
NT = int(sys.argv[sys.argv.index("--takes") + 1]) if "--takes" in sys.argv else 3
assert VOICE[who_sel], f"geen voice-id voor {who_sel} (zet BOAZ_VOICE_ID)"
def run(c): subprocess.run(c, check=True)
def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip())
def to16(a, b): run(["ffmpeg", "-v", "error", "-y", "-i", str(a), "-ar", "16000", "-ac", "1", str(b)])
def meter(wav16, text):
    pa = base64.b64encode(json.dumps({"ReferenceText": text, "GradingSystem": "HundredMark", "Granularity": "Word", "EnableMiscue": True}).encode()).decode()
    url = f"https://{env['AZURE_SPEECH_REGION']}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=nl-NL&format=detailed"
    req = urllib.request.Request(url, data=open(wav16, "rb").read(), headers={"Ocp-Apim-Subscription-Key": env["AZURE_SPEECH_KEY"],
          "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000", "Pronunciation-Assessment": pa, "Accept": "application/json"})
    for at in range(4):
        try: r = json.load(urllib.request.urlopen(req, timeout=120)); break
        except urllib.error.HTTPError:
            if at == 3: raise
            time.sleep(8 * (at + 1))
    nb = (r.get("NBest") or [{}])[0]; ws = nb.get("Words", [])
    pa_ = nb.get("PronunciationAssessment") or nb
    bad = [w["Word"] for w in ws if w.get("ErrorType") not in (None, "None")]
    accs = [w.get("AccuracyScore", (w.get("PronunciationAssessment") or {}).get("AccuracyScore")) for w in ws]
    accs = [a for a in accs if a is not None]
    sp = [w for w in ws if w.get("ErrorType") != "Omission" and w.get("Duration")]
    return {"acc": pa_.get("AccuracyScore"), "compl": pa_.get("CompletenessScore"), "min_word": min(accs) if accs else 0, "errors": bad,
            "speech_s": round((sp[-1]["Offset"] + sp[-1]["Duration"] - sp[0]["Offset"]) / 1e7, 2) if sp else None}
def f0(wav16):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav16), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(float); win, hop, lo, hi = 640, 160, 16000 // 400, 16000 // 70; out = []
    for i in range(0, len(x) - win, hop):
        fr = x[i:i + win]
        if np.sqrt((fr ** 2).mean()) < 300: continue
        fr = fr - fr.mean(); ac = np.correlate(fr, fr, "full")[win - 1:]
        if ac[0] <= 0: continue
        seg = (ac / ac[0])[lo:hi]; pk = [k for k in range(1, len(seg) - 1) if seg[k] > seg[k - 1] and seg[k] >= seg[k + 1] and seg[k] > 0.5]
        if not pk: continue
        top = max(seg[k] for k in pk); k = min(k for k in pk if seg[k] >= 0.85 * top) + lo; out.append(16000 / k)
    return float(np.median(out)) if out else None
# F0-baseline uit opname 2 voor deze spreker
tmp = OUT / "_tmp"; tmp.mkdir(exist_ok=True); base = []
for sid, (w, text, blocks) in LINES.items():
    if w != who_sel: continue
    for b, _ in blocks:
        a, e = BLOCKS[b]; f = tmp / f"b{b}.wav"; run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-ss", f"{a}", "-to", f"{e}", "-ar", "16000", "-ac", "1", str(f)])
        v = f0(f); base.append(v) if v else None
F0B = float(np.median(base)); print(f"F0-baseline {who_sel} (opname 2): {F0B:.0f} Hz", flush=True)
key = env["ELEVENLABS_API_KEY"]; report = {}
for sid, (w, text, blocks) in LINES.items():
    if w != who_sel: continue
    d = OUT / sid; d.mkdir(exist_ok=True); prompt = INLINE.get(sid, f"[{TAGS[sid]}] {text}"); report[sid] = {"text": text, "prompt": prompt, "takes": []}
    start = len(list(d.glob("take*.mp3"))) + 1
    for k in range(start, start + NT):
        body = {"text": prompt, "model_id": "eleven_v4", "language_code": "nl", "voice_settings": SETTINGS}
        req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE[w]}?output_format=mp3_44100_192", data=json.dumps(body).encode(),
                                     headers={"xi-api-key": key, "Content-Type": "application/json"})
        f = d / f"take{k}.mp3"; f.write_bytes(urllib.request.urlopen(req, timeout=180).read())
        w16 = tmp / f"{sid}-{k}.wav"; to16(f, w16); m = meter(w16, text); fz = f0(w16)
        ok = (m["acc"] or 0) >= 90 and m["min_word"] >= 60 and not m["errors"] and fz and abs(fz / F0B - 1) <= 0.15
        t = {"take": k, "file": f.name, "dur": round(dur(f), 2), **m, "f0": round(fz or 0), "f0_dev": round((fz or 0) / F0B - 1, 3), "gate": "OK" if ok else "FAIL"}
        report[sid]["takes"].append(t)
        print(f"{sid} take{k}: {t['dur']:5.2f}s  meter {m['acc']}  laagste woord {m['min_word']}  fouten {m['errors'] or '-'}  F0 {t['f0']} ({t['f0_dev']:+.0%})  {t['gate']}", flush=True)
    (d / "takes.json").write_text(json.dumps(report[sid], ensure_ascii=False, indent=1))
# luisterreel: per regel opname 2, dan de takes; aankondiging met 1 s stilte ertussen
sil = tmp / "sil.wav"; run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "1.0", str(sil)])
lst = []
for sid in report:
    for f in [PROJ / "assets/audio/lines/film" / f"{sid}.wav"] + sorted((OUT / sid).glob("take*.mp3")):
        n = tmp / f"n-{sid}-{f.stem}.wav"; run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-af", "loudnorm=I=-16:TP=-1.5", "-ar", "44100", "-ac", "1", str(n)]); lst += [n, sil]
(tmp / "reel.txt").write_text("".join(f"file '{p.resolve()}'\n" for p in lst))
reel = PROJ / f"previews/v4-takes-{who_sel}.mp3"
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "reel.txt"), "-c:a", "libmp3lame", "-q:a", "2", str(reel)])
print("reel:", reel)

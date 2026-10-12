# -*- coding: utf-8 -*-
"""Gratis sync-fix (2026-10-12): Sync 3 houdt het mondritme van Seedance' kloonstem aan. Daarom wordt de v4-filmregel per
woordgroep op de woordtijden van de kloonstem gelegd: spraakdelen hooguit ±10% in tempo (atempo), pauzes vrij langer/korter.
Woorden v4 <-> kloon gekoppeld op tekst (difflib). Uitvoer: lines/film-v4-sync/<shot>.wav, clip-relatief (begint op clip-t=0),
plus artifacts/sync-retime.json met de restafwijking per woord.
    PYTHONPATH=. .venv/bin/python projects/expeditie-mj-animatie3/retime_to_clone.py [shot ...]"""
import json, subprocess, sys, pathlib, base64, urllib.request, time, difflib, re
P = pathlib.Path("projects/expeditie-mj-animatie3"); V = P / "assets/video/units"; F = P / "assets/audio/lines/film-v4"; O = P / "assets/audio/lines/film-v4-sync"; O.mkdir(exist_ok=True)
TMP = O / "_tmp"; TMP.mkdir(exist_ok=True)
env = dict(l.rstrip("\n").split("=", 1) for l in open(".env") if "=" in l and not l.startswith("#"))
sel = json.load(open(P / "assets/audio/lines/selection.json")); parts = {p["part"]: p["text"] for s in sel.values() for p in s.get("parts", [])}
SH = {"1B": ("g02t", "s01"), "1C": ("g20", "s01b"), "3AB": ("g24", "s02p12"), "4A": ("g10t", "s03"), "4B": ("g11u", "s04"), "4D": ("g13s", "s05"),
      "4F": ("g14w", "s06p1"), "5B": ("g16v", "s07p1"), "5D": ("g18w", "s08")}
import os
GAP = float(os.environ.get('A3_GAP', 0.06)); TMIN, TMAX, PMIN = 0.90, 1.10, 0.03
def run(c): subprocess.run(["ffmpeg", "-v", "error", "-y", *c], check=True)
def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)
def words(wav, ref):
    w16 = TMP / "w16.wav"; run(["-i", str(wav), "-ar", "16000", "-ac", "1", str(w16)])
    pa = base64.b64encode(json.dumps({"ReferenceText": ref, "GradingSystem": "HundredMark", "Granularity": "Word", "EnableMiscue": True}).encode()).decode()
    url = f"https://{env['AZURE_SPEECH_REGION']}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=nl-NL&format=detailed"
    for at in range(4):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, data=w16.read_bytes(), headers={"Ocp-Apim-Subscription-Key": env["AZURE_SPEECH_KEY"], "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000", "Pronunciation-Assessment": pa, "Accept": "application/json"}), timeout=120)); break
        except Exception: time.sleep(6)
    return [(re.sub(r"\W", "", w["Word"].lower()), w["Offset"] / 1e7, (w["Offset"] + w["Duration"]) / 1e7) for w in (r.get("NBest") or [{}])[0].get("Words", []) if w.get("ErrorType") != "Omission" and w.get("Duration")]
report = json.load(open(P / "artifacts/sync-retime.json")) if (P / "artifacts/sync-retime.json").exists() else {}
for shot in (sys.argv[1:] or list(SH)):
    u, lid = SH[shot]; text = parts.get(lid) or sel[lid]["text"]; src = F / f"{lid}.wav"; clip_d = dur(V / u / "clip.mp4")
    vw = words(src, text); cw = words(V / u / "stems/vocals.wav", text)
    sm = difflib.SequenceMatcher(a=[w[0] for w in vw], b=[w[0] for w in cw], autojunk=False)
    m = {}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size): m[blk.a + k] = blk.b + k
    # woordgroepen in de v4-regel
    groups = [[0]]
    for i in range(1, len(vw)):
        (groups[-1].append(i) if vw[i][1] - vw[i - 1][2] < GAP else groups.append([i]))
    segs = []; cursor = 0.0; resid = []; prev_end_v = 0.0
    for gi, g in enumerate(groups):
        sv, ev = vw[g[0]][1], vw[g[-1]][2]
        mi = [i for i in g if i in m]
        if mi:   # doel: eerste en laatste gekoppelde woord van de groep op de kloontijden
            tc0 = cw[m[mi[0]]][1] - (vw[mi[0]][1] - sv)
            tc1 = cw[m[mi[-1]]][2] + (ev - vw[mi[-1]][2])
        else:
            tc0, tc1 = cursor + (sv - prev_end_v), cursor + (sv - prev_end_v) + (ev - sv)
        k = min(max((ev - sv) / max(tc1 - tc0, 0.05), TMIN), TMAX)   # atempo-factor (>1 = sneller)
        if mi:   # plaatsing met de kleinste afwijking over alle gekoppelde woorden (mediaan), niet alleen het eerste woord
            cands = sorted(cw[m[i]][1] - (vw[i][1] - sv) / k for i in mi); tc0 = cands[len(cands) // 2]
        start = max(tc0, cursor + (PMIN if gi else 0.0)); out_d = (ev - sv) / k
        a = max(0.0, sv - (0.08 if gi == 0 else 0.03)); b = min(dur(src), ev + (0.15 if gi == len(groups) - 1 else 0.03))
        segs.append((start - (sv - a) / k, a, b, k)); cursor = start + out_d
        for i in g:
            if i in m: resid.append(round((start + (vw[i][1] - sv) / k) - cw[m[i]][1], 3))
        prev_end_v = ev
    # opbouwen: elk stuk op zijn eigen tijd in een stille track van clip-lengte
    total = segs[-1][0] + (segs[-1][2] - segs[-1][1]) / segs[-1][3] + 0.02   # niet opvullen tot het clipeinde (anders onnodige eindframe-freeze)
    # stukken los renderen (trim + atempo) en zelf op de tijdlijn leggen: ffmpeg verloor adelay na atempo in één filterketen
    import numpy as np
    SR = 44100; track = np.zeros(int(round(total * SR)) + SR, np.float32)
    for j, (t, a, b, k) in enumerate(segs):
        af = f"atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS" + (f",atempo={k:.4f}" if abs(k - 1) > 0.005 else "") + ",afade=t=in:d=0.01"
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-af", af, "-ar", str(SR), "-ac", "1", "-f", "f32le", "-"], capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.float32); i0 = max(0, int(round(t * SR)))
        if i0 + len(x) > len(track): track = np.pad(track, (0, i0 + len(x) - len(track)))
        track[i0:i0 + len(x)] += x
    track = track[:int(round(total * SR))]
    out = O / f"{shot}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s24le", str(out)], input=track.tobytes(), check=True)
    med = sorted(abs(x) for x in resid)[len(resid) // 2] if resid else None
    report[shot] = {"unit": u, "line": lid, "groups": len(groups), "tempo": [round(s[3], 3) for s in segs], "resid": resid, "resid_median": med,
                    "resid_max": max((abs(x) for x in resid), default=None), "matched": f"{len(m)}/{len(vw)}", "out": str(out), "over_clip_end": round(total - clip_d, 2), "dur": round(total, 3)}
    print(f"{shot:4} groepen {len(groups):2} tempo {report[shot]['tempo']} | rest mediaan {med:.2f}s max {report[shot]['resid_max']:.2f}s | gekoppeld {report[shot]['matched']} | voorbij clipeinde {report[shot]['over_clip_end']:+.2f}s", flush=True)
(P / "artifacts/sync-retime.json").write_text(json.dumps(report, indent=1))

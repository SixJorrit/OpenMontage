# -*- coding: utf-8 -*-
"""Beoordeling van de testronde: per clip audio door de Azure-meter (R2-vraag),
framegrabs voor visuele vergelijking, en duur/fps-feiten. Kosten komen apart uit
atlascost.py / model-usage."""
import json, base64, pathlib, subprocess, urllib.request

ROOT = pathlib.Path("projects/expeditie-mediajungle-animaties")
TESTS = ROOT / "assets/video/model-tests"
BASELINE = ROOT / "assets/video/shots/attempts/fix1-2A/attempt-1-solo-medium.mp4"
REF_TEXT = "Help, hij doet het niet!"

env = dict(l.rstrip("\n").split("=", 1) for l in open(".env") if "=" in l and not l.startswith("#"))

def meter(wav):
    pa = base64.b64encode(json.dumps({"ReferenceText": REF_TEXT, "GradingSystem": "HundredMark",
        "Granularity": "Word", "EnableMiscue": True}).encode()).decode()
    url = (f"https://{env['AZURE_SPEECH_REGION']}.stt.speech.microsoft.com/speech/recognition/"
           f"conversation/cognitiveservices/v1?language=nl-NL&format=detailed")
    req = urllib.request.Request(url, data=open(wav, "rb").read(), headers={
        "Ocp-Apim-Subscription-Key": env["AZURE_SPEECH_KEY"],
        "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
        "Pronunciation-Assessment": pa, "Accept": "application/json"})
    resp = json.load(urllib.request.urlopen(req, timeout=60))
    nb = (resp.get("NBest") or [{}])[0]
    return nb.get("AccuracyScore"), (nb.get("Display") or resp.get("DisplayText")), \
        [(w.get("Word"), w.get("AccuracyScore")) for w in nb.get("Words", [])]

def probe(clip):
    out = subprocess.run(["ffprobe", "-v", "quiet", "-select_streams", "v:0", "-show_entries",
        "stream=r_frame_rate,width,height:format=duration", "-of", "json", str(clip)],
        capture_output=True, text=True).stdout
    j = json.loads(out)
    st = (j.get("streams") or [{}])[0]
    return {"fps": st.get("r_frame_rate"), "res": f"{st.get('width')}x{st.get('height')}",
            "duur": round(float(j.get("format", {}).get("duration", 0)), 2)}

def has_audio(clip):
    out = subprocess.run(["ffprobe", "-v", "quiet", "-select_streams", "a", "-show_entries",
        "stream=codec_type", "-of", "csv=p=0", str(clip)], capture_output=True, text=True).stdout
    return "audio" in out

rows = []
clips = [("BASELINE-2.5-pilot", BASELINE)] + \
        sorted((d.name, d / "clip.mp4") for d in TESTS.iterdir() if (d / "clip.mp4").exists())
for naam, clip in clips:
    d = clip.parent
    info = probe(clip)
    rij = {"kandidaat": naam, **info}
    # frames voor visuele vergelijking (eerste, midden, laatste)
    for tag, t in (("f0", 0.1), ("f2", info["duur"] / 2), ("f4", max(info["duur"] - 0.15, 0))):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(clip),
                        "-frames:v", "1", str(d / f"{naam}-{tag}.png")])
    # audio -> meter
    if has_audio(clip):
        wav = d / "clip-audio.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-vn",
                        "-ar", "16000", "-ac", "1", str(wav)])
        try:
            acc, disp, words = meter(wav)
            rij["meter_accuracy"] = acc
            rij["meter_herkend"] = disp
            rij["meter_woorden"] = words
        except Exception as e:
            rij["meter_fout"] = str(e)[:150]
    else:
        rij["meter_accuracy"] = None
        rij["meter_herkend"] = "(clip heeft geen audiospoor)"
    rows.append(rij)
    print(json.dumps(rij, ensure_ascii=False), flush=True)

(TESTS / "eval.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
print("\neval.json geschreven")

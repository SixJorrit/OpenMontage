# -*- coding: utf-8 -*-
"""Testronde vraag 4 + R2-proefclip (vraag 1). Plafond $15 (Jorrit, 2026-08-21).

Eén identiek shot (pilot 2A: Boaz solo in de hut, droog weer) per kandidaat, met de
ElevenLabs-v3-regel van Bram als referentie-audio waar het model dat ondersteunt.
Sequentieel (parallelle submits gaven eerder valse 402's). Elke poging wordt gelogd,
ook mislukkingen.
"""
import json, pathlib, subprocess, time, traceback
from tools.tool_registry import registry

ROOT = pathlib.Path("projects/expeditie-mediajungle-animaties")
SB = ROOT / "assets/images/style-bible"
AUDIO = ROOT / "assets/audio/tts-test/v3_boaz_bram_help_padded.mp3"
DEST = ROOT / "assets/video/model-tests"
DEST.mkdir(parents=True, exist_ok=True)

PROMPT = (ROOT / "assets/video/shots/attempts/fix1-2A/attempt-1-solo-medium.json")
PROMPT = json.loads(PROMPT.read_text())["prompt"]
assert "doet het niet" not in PROMPT.lower(), "regeltekst in de prompt"

REFS = [SB / "boaz-face-neutral-smile.png", SB / "boaz-body-front-headless.png",
        SB / "location-hut-day-dry.png"]
GEO = SB / "geometry-hut-empty.mp4"
for p in REFS + [GEO, AUDIO]:
    assert p.exists(), p

ad = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "default=nw=1:nk=1", str(AUDIO)], capture_output=True, text=True).stdout.strip())
assert ad >= 1.8, f"referentie-audio {ad}s onder 1,8s"

registry.discover()
atlas = registry._tools["atlas_video"]
kling = registry._tools["kling_official_video"]

CANDIDATES = [
    # (slug, model-id, resolutie, audio meegeven)
    ("seedance-2.5-R2", "bytedance/seedance-2.5/reference-to-video", "720p", True),
    ("seedance-2.0",    "bytedance/seedance-2.0/reference-to-video", "720p", True),
    ("minimax-h3",      "minimax/h3/reference-to-video",             "768P", True),
    ("gemini-omni-std", "google/gemini-omni-flash/reference-to-video", "720p", True),
    ("gemini-omni-dev", "google/gemini-omni-flash/reference-to-video-developer", "720p", True),
]

def log(slug, payload):
    d = DEST / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "log.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

atlas_calls = 0
for slug, model, res, with_audio in CANDIDATES:
    d = DEST / slug
    d.mkdir(parents=True, exist_ok=True)
    out = d / "clip.mp4"
    if out.exists():
        print(f"[{slug}] bestaat al, overslaan", flush=True)
        continue
    params = {"operation": "reference_to_video", "model": model, "duration": 4,
              "resolution": res, "aspect_ratio": "16:9", "prompt": PROMPT,
              "reference_images": [str(p) for p in REFS],
              "reference_videos": [str(GEO)],
              "output_path": str(out)}
    if with_audio:
        params["reference_audios"] = [str(AUDIO)]
    print(f"[{slug}] submit -> {model} 4s {res}", flush=True)
    t0 = time.time()
    try:
        r = atlas.execute(params)
        atlas_calls += 1
    except Exception as e:
        # onduidelijk of er gesubmit is: tel hem WEL mee voor de natelling
        atlas_calls += 1
        log(slug, {"model": model, "success": False, "error": traceback.format_exc(),
                   "params_media": {"refs": len(REFS), "geo": True, "audio": with_audio},
                   "seconds": round(time.time() - t0)})
        print(f"[{slug}] EXCEPTIE na {time.time()-t0:.0f}s: {e}", flush=True)
        continue
    dt = round(time.time() - t0)
    if not r.success:
        err = str(r.error)
        log(slug, {"model": model, "success": False, "error": err, "seconds": dt,
                   "params_media": {"refs": len(REFS), "geo": True, "audio": with_audio}})
        print(f"[{slug}] FOUT na {dt}s: {err[:200]}", flush=True)
        # één hertry zonder audio/geometrie als het een validatiefout op media lijkt
        if with_audio and any(w in err.lower() for w in ("audio", "reference", "unsupported", "invalid")):
            params.pop("reference_audios", None)
            print(f"[{slug}] hertry zonder referentie-audio", flush=True)
            t0 = time.time()
            r = atlas.execute(params)
            atlas_calls += 1
            dt = round(time.time() - t0)
            if not r.success:
                log(slug, {"model": model, "success": False, "error": str(r.error), "seconds": dt,
                           "retry": "zonder audio", "params_media": {"refs": len(REFS), "geo": True, "audio": False}})
                print(f"[{slug}] hertry ook FOUT na {dt}s: {str(r.error)[:200]}", flush=True)
                continue
        else:
            continue
    dd = r.data or {}
    log(slug, {"model": model, "success": True, "seconds": dt,
               "output": dd.get("output_path"), "source_url": dd.get("source_url"),
               "prediction_id": dd.get("prediction_id"), "cost_tracker": r.cost_usd,
               "audio_in_call": "reference_audios" in params,
               "prompt": PROMPT})
    print(f"[{slug}] OK na {dt}s -> {out}", flush=True)

# Kling official (trial-units, geen cash; geen referentie-audio ondersteund)
slug = "kling-v3"
d = DEST / slug
d.mkdir(parents=True, exist_ok=True)
out = d / "clip.mp4"
if not out.exists():
    kp = {"operation": "reference_to_video", "model_name": "kling-v3", "duration": "4",
          "aspect_ratio": "16:9", "resolution": "720p", "prompt": PROMPT,
          "reference_image_paths": [str(p) for p in REFS],
          "output_path": str(out)}
    print(f"[{slug}] submit -> kling-v3 reference_to_video (geen audio-ondersteuning)", flush=True)
    t0 = time.time()
    try:
        r = kling.execute(kp)
        dt = round(time.time() - t0)
        if r.success:
            dd = r.data or {}
            log(slug, {"model": "kling-v3", "success": True, "seconds": dt,
                       "output": dd.get("output_path"), "cost_tracker": r.cost_usd,
                       "audio_in_call": False, "prompt": PROMPT})
            print(f"[{slug}] OK na {dt}s -> {out}", flush=True)
        else:
            log(slug, {"model": "kling-v3", "success": False, "seconds": dt, "error": str(r.error)})
            print(f"[{slug}] FOUT na {dt}s: {str(r.error)[:200]}", flush=True)
    except Exception as e:
        log(slug, {"model": "kling-v3", "success": False, "error": traceback.format_exc()})
        print(f"[{slug}] EXCEPTIE: {e}", flush=True)

print(f"\nKLAAR. Atlas-calls gedaan (natellen tegen model-usage): {atlas_calls}", flush=True)

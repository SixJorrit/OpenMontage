# -*- coding: utf-8 -*-
"""Wan 3.0 nakomertest (2026-08-26, binnen het $15-plafond van de testronde).
Zelfde protocol als de eerdere ronde: shot-2A (solo, hut, droog, v3-Bram-regel) en
het complexe two-shot (regenpad, SPEAKER LOCK, v3-Femke-regel). 720p, sequentieel."""
import json, pathlib, subprocess, time, traceback
from tools.tool_registry import registry

ROOT = pathlib.Path("projects/expeditie-mediajungle-animaties")
SB = ROOT / "assets/images/style-bible"
DEST = ROOT / "assets/video/model-tests"

def prompt_of(log_path):
    return json.loads(pathlib.Path(log_path).read_text())["prompt"]

TESTS = [
    {
        "slug": "wan-3.0-2A",
        "prompt": prompt_of(ROOT / "assets/video/shots/attempts/fix1-2A/attempt-1-solo-medium.json"),
        "verboden": "doet het niet",
        "duration": 4,
        "images": [SB / "boaz-face-neutral-smile.png", SB / "boaz-body-front-headless.png",
                   SB / "location-hut-day-dry.png"],
        "videos": [SB / "geometry-hut-empty.mp4"],
        "audios": [ROOT / "assets/audio/tts-test/v3_boaz_bram_help_padded.mp3"],
    },
    {
        "slug": "wan-3.0-complex",
        "prompt": prompt_of(DEST / "complex-seedance-2.5/log.json"),
        "verboden": "rekening met elkaar",
        "duration": 10,
        "images": [SB / "femke-face-neutral-smile.png", SB / "femke-body-front-headless.png",
                   SB / "boaz-face-neutral-smile.png", SB / "boaz-body-front-headless.png",
                   SB / "location-jungle-path-day-rain.png"],
        "videos": [],
        "audios": [ROOT / "assets/audio/tts-test/v3_femke_reis_vol.mp3"],
    },
]

registry.discover()
atlas = registry._tools["atlas_video"]
calls = 0
for t in TESTS:
    assert t["verboden"] not in t["prompt"].lower(), f"regeltekst in prompt van {t['slug']}"
    for p in t["images"] + t["videos"] + t["audios"]:
        assert p.exists(), p
    d = DEST / t["slug"]
    d.mkdir(parents=True, exist_ok=True)
    out = d / "clip.mp4"
    if out.exists():
        print(f"[{t['slug']}] bestaat al, overslaan", flush=True)
        continue
    params = {"operation": "reference_to_video", "model": "alibaba/wan-3.0/reference-to-video",
              "duration": t["duration"], "resolution": "720p", "aspect_ratio": "16:9",
              "prompt": t["prompt"],
              "reference_images": [str(p) for p in t["images"]],
              "reference_videos": [str(p) for p in t["videos"]],
              "reference_audios": [str(p) for p in t["audios"]],
              "output_path": str(out)}
    print(f"[{t['slug']}] submit -> wan-3.0 {t['duration']}s 720p "
          f"({len(t['images'])} beelden, {len(t['videos'])} video, {len(t['audios'])} audio)", flush=True)
    t0 = time.time()
    try:
        r = atlas.execute(params)
        calls += 1
    except Exception:
        calls += 1
        (d / "log.json").write_text(json.dumps({"model": "alibaba/wan-3.0/reference-to-video",
            "success": False, "error": traceback.format_exc(),
            "seconds": round(time.time() - t0)}, ensure_ascii=False, indent=2))
        print(f"[{t['slug']}] EXCEPTIE na {time.time()-t0:.0f}s", flush=True)
        continue
    dt = round(time.time() - t0)
    payload = {"model": "alibaba/wan-3.0/reference-to-video", "success": bool(r.success),
               "seconds": dt, "duration": t["duration"], "prompt": t["prompt"]}
    if r.success:
        dd = r.data or {}
        payload.update({"output": dd.get("output_path"), "source_url": dd.get("source_url"),
                        "prediction_id": dd.get("prediction_id")})
        print(f"[{t['slug']}] OK na {dt}s", flush=True)
    else:
        payload["error"] = str(r.error)
        print(f"[{t['slug']}] FOUT na {dt}s: {str(r.error)[:250]}", flush=True)
    (d / "log.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"KLAAR. Atlas-calls: {calls} (natellen tegen model-usage)", flush=True)

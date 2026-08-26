# -*- coding: utf-8 -*-
"""Bevestigingstest (Jorrit, 2026-08-21): één complexer shot op minimax-h3 en seedance-2.5.
Twee personages, regen-weerslot, alleen Femke spreekt (volledige 5A2-regel als v3-audio, meter 94).
Sequentieel; binnen het $15-plafond van de testronde."""
import json, pathlib, subprocess, time, traceback
from tools.tool_registry import registry

ROOT = pathlib.Path("projects/expeditie-mediajungle-animaties")
SB = ROOT / "assets/images/style-bible"
AUDIO = ROOT / "assets/audio/tts-test/v3_femke_reis_vol.mp3"
DEST = ROOT / "assets/video/model-tests"

PROMPT = """GLOBAL STYLE
Stylized 3D CG in the language of a modern animated feature film, matching the supplied character and location plates exactly in material, colour and proportion. Deliberately not photorealistic: simplified sculpted forms, hand-painted-feeling surfaces, clean readable silhouettes. 16:9. No camera shake, no lens flare, no on-screen text.

SCENE
Femke and Boaz walk side by side along the rain-soaked jungle path towards the camera, heading for the distant broken television mast. Femke talks to Boaz while they walk; she is thoughtful and encouraging. Boaz listens, glances at her and nods once. Only Femke speaks.

CHARACTERS
FEMKE is the girl in the supplied character plates: her head plate carries her face in a neutral and a smiling version, her body plate carries her wardrobe and silhouette. Keep her exact face, hair, wardrobe and accessories in every frame.
BOAZ is the boy in the supplied character plates: 15 to 16 years old with deep warm dark brown skin, black spiky hair with a pale zigzag highlight, a small ear stud, an amber-yellow shirt with a large 07, teal headphones resting around his neck, teal-blue jeans and purple sneakers. Keep his exact face, hair, wardrobe and accessories in every frame.

LOCATION
The jungle path in the supplied plate: a muddy track between dense oversized jungle leaves, puddles on the ground, mist between the trees. Keep the layout and mood of that plate.

WEATHER
Heavy tropical rain falls for the entire shot: visible rain streaks, drops splashing in the puddles, wet glossy leaves, both characters lightly soaked. WEATHER LOCK: the rain is identical in intensity from the first frame to the last; it never stops or fades.

FIRST FRAME AND BLOCKING
Medium two-shot on FEMKE and BOAZ walking towards the camera, both framed from the knees up, side by side, both faces clearly visible from the very first frame. Femke is on the left, Boaz on the right. SPEAKER LOCK: only FEMKE's mouth moves, exactly following the supplied audio; BOAZ's mouth stays closed for the whole shot, he reacts only with his eyes and one nod. They keep walking at a calm steady pace for the whole shot and nobody else appears.

OPTICS / CAMERA
One 35mm lens. The camera slowly dollies backwards at exactly the walking pace so the framing on both characters stays constant. LENS LOCK: no zoom and no focal change; the framing at the last frame is identical to the framing at the first frame.

PHYSICS
Hair and fabric respond to the walking motion and the rain with a small delay. Rain and splashes obey gravity. Nothing else moves on its own.

LIGHTING
Overcast rain light, soft and silver-grey, with gentle rim light separating both characters from the dark green jungle. Both faces stay clearly lit in every frame.

AUDIO
The supplied audio clip is FEMKE'S OWN RECORDED VOICE speaking her line in this scene. Use that recording itself as the dialogue: reproduce exactly the words, the pronunciation, the accent and the timing that are in that audio file, without re-speaking or re-wording anything. Her mouth matches that recording frame for frame, and the line begins within the first second of the shot. Underneath it, rain and quiet jungle ambience. No music, no other voices.

POSITIVE LOCKS
SOLO PAIR LOCK: exactly 2 people are in frame for the whole shot. FACE LOCK: both faces are fully visible, front or three-quarter to the camera, in every single frame; the camera never moves behind them. FRAMING LOCK: this stays a medium two-shot for the whole duration. Both characters keep the exact appearance of their supplied plates. WEATHER LOCK: heavy rain holds identically from the first frame to the last."""

assert "rekening met elkaar" not in PROMPT.lower(), "regeltekst in de prompt"
assert "gezellig" not in PROMPT.lower(), "regeltekst in de prompt"

REFS = [SB / "femke-face-neutral-smile.png", SB / "femke-body-front-headless.png",
        SB / "boaz-face-neutral-smile.png", SB / "boaz-body-front-headless.png",
        SB / "location-jungle-path-day-rain.png"]
for p in REFS + [AUDIO]:
    assert p.exists(), p
ad = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "default=nw=1:nk=1", str(AUDIO)], capture_output=True, text=True).stdout.strip())
assert 1.8 <= ad <= 30.2, ad

registry.discover()
atlas = registry._tools["atlas_video"]

for slug, model, res in [
    ("complex-minimax-h3", "minimax/h3/reference-to-video", "768P"),
    ("complex-seedance-2.5", "bytedance/seedance-2.5/reference-to-video", "720p"),
]:
    d = DEST / slug
    d.mkdir(parents=True, exist_ok=True)
    out = d / "clip.mp4"
    if out.exists():
        print(f"[{slug}] bestaat al, overslaan", flush=True)
        continue
    params = {"operation": "reference_to_video", "model": model, "duration": 10,
              "resolution": res, "aspect_ratio": "16:9", "prompt": PROMPT,
              "reference_images": [str(p) for p in REFS],
              "reference_audios": [str(AUDIO)], "output_path": str(out)}
    print(f"[{slug}] submit -> {model} 10s {res} (5 beelden + audio {ad:.2f}s)", flush=True)
    t0 = time.time()
    try:
        r = atlas.execute(params)
    except Exception:
        (d / "log.json").write_text(json.dumps({"model": model, "success": False,
            "error": traceback.format_exc(), "seconds": round(time.time() - t0)},
            ensure_ascii=False, indent=2))
        print(f"[{slug}] EXCEPTIE na {time.time()-t0:.0f}s", flush=True)
        continue
    dt = round(time.time() - t0)
    payload = {"model": model, "success": bool(r.success), "seconds": dt, "duration": 10,
               "audio_in_call": True, "prompt": PROMPT}
    if r.success:
        dd = r.data or {}
        payload.update({"output": dd.get("output_path"), "source_url": dd.get("source_url"),
                        "prediction_id": dd.get("prediction_id"), "cost_tracker": r.cost_usd})
        print(f"[{slug}] OK na {dt}s", flush=True)
    else:
        payload["error"] = str(r.error)
        print(f"[{slug}] FOUT na {dt}s: {str(r.error)[:200]}", flush=True)
    (d / "log.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

print("KLAAR (2 Atlas-calls gepland; natellen tegen model-usage)", flush=True)

# -*- coding: utf-8 -*-
"""Retakeronde 4 (go Jorrit 2026-10-12): zeven Seedance-2.5 reference-to-video drafts (480p, draft=true) op basis van de oude
prompts met alleen de goedgekeurde wijzigingen (artifacts/shots-compact-retake4.md) + vaste zitplaatsregel.
Schrijft units/<nieuw>/{log.json, draft.mp4}. Afmaken op 1080p gebeurt later per goedgekeurde draft (draft-complete).
    PYTHONPATH=. .venv/bin/python projects/expeditie-mj-animatie3/retake4.py [--dry-run] [shot ...]"""
import json, pathlib, sys, time, re, concurrent.futures as cf
sys.path.insert(0, str(pathlib.Path.cwd()))
from tools import atlas_client
PROJ = pathlib.Path("projects/expeditie-mj-animatie3"); V = PROJ / "assets/video/units"; C3 = PROJ / "assets/images/canon-3d"
FV4 = PROJ / "assets/audio/lines/film-v4"; DRY = "--dry-run" in sys.argv
TARA_OLD = str(C3 / "location-tara-tenten-dusk.png"); TARA_NEW = str(C3 / "location-tara-tenten-dusk-zondertent.png")
SEAT = ("SEATING LOCK: Femke is the driver and sits behind the steering wheel in every frame; the steering wheel is on her side only. "
        "Boaz sits in the front passenger seat right next to her, never touches the steering wheel and never sits in the back. "
        "The jeep has rear seats, but they stay empty; nobody sits in the back.")
FRONTROW = ("Both sit in the FRONT row, shoulder to shoulder, both clearly visible through the windscreen; the rear part of the jeep is an empty open "
            "cargo area with no seats and nobody in it.")
R = {  # shot: (oude unit, nieuwe unit, nieuwe SCENE-tekst, audio, plaat vervangen)
 "2B": ("g04t", "g04u", "Side tracking shot: the camera travels alongside the yellow jeep as it drives from frame-right to frame-left along the jungle track. "
        "Femke sits at the steering wheel on the side nearest to the camera, both hands on the wheel, eyes on the track. Boaz sits beyond her in the front passenger seat, "
        "looks ahead and points at something in the distance. On a low branch in the foreground frame-right sits a colourful toucan; as the jeep passes, it takes off "
        "and flies up out of frame. Exactly one bird. No cuts.", None, False),
 "2C": ("g05t", "g05u", "The camera lies very low on the sandy jungle track, looking along it. For the first second only the empty track is visible while a long green snake "
        "slithers across it in the foreground from frame-left to frame-right and disappears into the ferns; the sound of an engine approaches. Then the yellow jeep appears "
        "in the background with its HEADLIGHTS ON and drives straight towards the camera without slowing down or braking. Through the windscreen, Femke is clearly at the "
        "steering wheel on the frame-right side, both hands on the wheel; Boaz sits in the passenger seat on the frame-left side and, as the jeep comes close, pulls a silly "
        "face at the camera. The jeep drives right over the camera: the bumper passes overhead, the underside of the vehicle and the wheels pass left and right of the lens, "
        "the image goes dark for a moment and then shows the sky and leaves again. Meanwhile, in the bushes frame-right, a single bright camera flash goes off, as if a hidden "
        "animal took a photo. The sun sits very low and orange behind the trees. No cuts.", None, False),
 "2E": ("g22", "g22b", "This shot is a front three-quarter view from the passenger side, not a side view. The yellow jeep drives slowly along the darkening jungle track "
        "towards frame-left-front. Boaz sits in the front passenger seat nearest to the camera, fast asleep, his head resting against the open window frame and lolling "
        "with the bumps, his tongue hanging out of his mouth. Beyond him Femke sits at the steering wheel, both hands on the wheel, eyes on the track. No cuts.", None, False),
 "2F": ("g23", "g23b", "This shot is a front three-quarter view from the passenger side, not a side view. The yellow jeep drives along the jungle track in the last evening "
        "light towards frame-left-front. Boaz sits in the front passenger seat nearest to the camera and hangs his head out of the open passenger window like a happy dog, "
        "mouth open, hair blown back by the wind. Beyond him Femke sits at the steering wheel, both hands on the wheel, glances at him and laughs, then looks back at the track. No cuts.", None, False),
 "4B": ("g11t", "g11u", "Frontal medium two-shot of the cab of the parked jeep, seen through the windscreen over the hood: Boaz frame-left in the passenger seat, Femke frame-right "
        "at the wheel, both fully visible, both doors closed and both side windows present. Boaz holds a smartphone in both hands, thumbs tapping constantly, eyes locked on "
        "the screen, the cool glow of the screen on his face; he shakes his head slightly while speaking and never looks up. The back of the phone faces the camera: a plain "
        "dark phone case with a small camera lens, no screen, no picture and no light on the back; the screen faces Boaz only and is never visible to the camera. Femke looks "
        "at him, waiting, one hand still on the wheel, mouth closed. The jeep stands completely still.", FV4 / "s04.wav", False),
 "4G5A": ("g25", "g25b", None, None, True),
 "5B": ("g16u", "g16v", "Medium two-shot from the same side as the arrival, closer: Femke (frame-right) and Boaz (frame-left) stand side by side next to the front-left corner "
        "of the parked jeep, facing the camera; the yellow jeep fills the left edge of frame, Tara's round thatched hut with its big TARA'S TENTEN sign stands diagonally "
        "behind them to the right, its window glowing warm. The background is the jungle clearing from the supplied Tara dusk plate: dense dark jungle plants and tall trees "
        "behind and around the hut, the evening sky visible only high up between the leaves; no plain sky backdrop. There is no tent anywhere. Both faces are lit warmly by "
        "the hut window and the spill of the headlights. Boaz addresses the viewer directly with a small explanatory hand gesture. Femke looks into the camera and smiles.", FV4 / "s07p1.wav", True),
 "2Bv2": ("g04t", "g04v", "This shot is a front three-quarter view from the passenger side, not a side view. The yellow jeep drives along the sunlit jungle track "
        "towards frame-left-front in golden late-afternoon light. Through the windscreen: Femke sits at the steering wheel on the far side, both hands on the wheel, eyes on "
        "the track; Boaz sits in the front passenger seat nearest to the camera, looks ahead and points at something in the distance with an excited grin. On a low branch "
        "in the foreground frame-right sits a colourful toucan; as the jeep passes, it takes off and flies up out of frame. Exactly one bird. No cuts.", None, False),
 "2Fv2": ("g23", "g23c", "This shot is a front three-quarter view from the passenger side, not a side view. The yellow jeep drives along the jungle track in the last "
        "evening light towards frame-left-front. The steering wheel is on the far side of the cab, in front of Femke, and she holds it with both hands the whole time. "
        "Boaz sits in the front passenger seat nearest to the camera and hangs his head out of the open passenger window like a happy dog, mouth open, hair blown back by "
        "the wind; he rests both forearms on the window sill on the outside of the door, and his hands never come near the steering wheel. Femke glances at him and laughs, "
        "then looks back at the track. No cuts.", None, False),
 "2Bv3": ("g04t", "g04w", "FRONTAL VIEW, not a side view: the camera is in front of the yellow jeep, low on the sunlit jungle track, and slowly travels backwards "
        "while the jeep drives towards it at a steady pace, golden late-afternoon light behind it. Through the windscreen both sit in the FRONT seats, side by side, both "
        "clearly visible: Femke frame-right behind the steering wheel, both hands on the wheel, eyes on the track; Boaz frame-left in the front passenger seat, looking past "
        "the camera and pointing at something in the distance with an excited grin. The rear seats behind them stay empty. On a low branch in the foreground frame-right sits "
        "a colourful toucan; as the jeep comes closer it takes off and flies up out of frame. Exactly one bird. No cuts.", None, False),
 "2Fv3": ("g23", "g23d", "FRONTAL VIEW, not a side view: the camera is in front of the yellow jeep on the jungle track in the last evening light and slowly travels "
        "backwards while the jeep drives towards it. Through the windscreen both sit in the FRONT seats: Femke frame-right behind the steering wheel, holding it with both "
        "hands the whole time, glancing at Boaz and laughing; Boaz frame-left in the front passenger seat leans his head and shoulders out of his open side window on the "
        "frame-left side like a happy dog, mouth open, hair blown back by the wind, both forearms resting on the outside of his door; his hands never come near the steering "
        "wheel. The rear seats behind them stay empty. No cuts.", None, False),
}
LINES = json.load(open(PROJ / "assets/audio/lines/selection.json"))
line_texts = [v["text"] for v in LINES.values()]
def no_line_text(p):
    for t in line_texts:
        w = re.sub(r"[^\w\s']", "", t).split()
        for i in range(len(w) - 2):
            frag = " ".join(w[i:i + 3])
            assert frag.lower() not in p.lower(), f"regeltekst in prompt: {frag}"
def dur(p):
    import subprocess; return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)
def build(shot):
    old, new, scene, audio, swap = R[shot]; d = json.load(open(V / old / "log.json")); p = d["prompt"]
    i = p.find("\nSCENE\n"); j = p.find("\nCHARACTERS\n")
    if scene is None:
        scene = p[i + 7:j].strip() + " There is no tent anywhere in the clearing; only the hut, its signs and the low wooden fence."
    if shot.startswith("2") or shot == "4B": scene = scene + "\n\n" + SEAT + (" " + FRONTROW if shot.endswith("v2") else "")
    prompt = p[:i] + "\nSCENE\n" + scene + "\n" + p[j:]
    refs = [TARA_NEW if (swap and r == TARA_OLD) else r for r in d["refs"]]
    for r in refs: assert pathlib.Path(r).exists(), r
    no_line_text(prompt)
    duration = d["duration"]
    if audio:
        ad = dur(audio); assert 1.8 <= ad <= 30.2; import math; duration = max(4, math.ceil(ad + 0.5))
    return {"shot": shot, "old": old, "unit": new, "prompt": prompt, "refs": refs, "audio": str(audio) if audio else None, "duration": duration}
targets = [a for a in sys.argv[1:] if not a.startswith("--")] or list(R)
jobs = [build(s) for s in targets]
tot = 0
for jb in jobs:
    c = 0.134 * jb["duration"]; tot += c
    print(f"{jb['shot']:5} -> {jb['unit']:5} {jb['duration']:2d}s  ${c:.2f}  refs {len(jb['refs'])}  audio {pathlib.Path(jb['audio']).name if jb['audio'] else '-'}  plaat {'zonder tent' if any('zondertent' in r for r in jb['refs']) else '-'}")
print(f"totaal drafts: ${tot:.2f}")
if DRY:
    (PROJ / "artifacts/prompts-retake4.json").write_text(json.dumps(jobs, ensure_ascii=False, indent=1)); raise SystemExit(0)
key = atlas_client.get_api_key()
def run(jb):
    D = V / jb["unit"]; D.mkdir(exist_ok=True); t0 = time.time()
    payload = {"model": "bytedance/seedance-2.5/reference-to-video", "prompt": jb["prompt"], "duration": jb["duration"], "ratio": "16:9",
               "generate_audio": True, "draft": True, "reference_images": [atlas_client.upload_media(r, key) for r in jb["refs"]]}
    if jb["audio"]: payload["reference_audios"] = [atlas_client.upload_media(jb["audio"], key)]
    log = {**jb, "model": payload["model"], "draft": True}
    try:
        pid = atlas_client.submit(atlas_client.GENERATE_VIDEO_ENDPOINT, payload, key); log["prediction_id"] = log["draft_id"] = pid
        (D / "log.json").write_text(json.dumps(log, ensure_ascii=False, indent=1)); print(f"{jb['shot']}: ingediend {pid}", flush=True)
        data = atlas_client.poll(pid, key, interval=6.0, timeout=2400.0); log["source_url"] = data["outputs"][0]
        if data.get("draft_id"): log["draft_id"] = data["draft_id"]
        atlas_client.download(log["source_url"], D / "draft.mp4"); log["success"] = True
    except Exception as e:
        log["success"] = False; log["error"] = str(e)[:600]
    log["seconds"] = round(time.time() - t0); (D / "log.json").write_text(json.dumps(log, ensure_ascii=False, indent=1))
    print(f"{jb['shot']}: {'klaar' if log['success'] else 'FOUT ' + log['error'][:200]} ({log['seconds']}s)", flush=True); return log
with cf.ThreadPoolExecutor(4) as ex: results = list(ex.map(run, jobs))
print("ALLES KLAAR", sum(r["success"] for r in results), "/", len(results))

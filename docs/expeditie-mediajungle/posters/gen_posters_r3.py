"""Ronde 3: poster 2 gebaar/oogjes-edit + nieuwe poster 3 (postbusje, verwachting vs. werkelijkheid)."""
import json
import pathlib
import sys
import time

sys.path.insert(0, "/Users/jorrit/dev/OpenMontage")
from tools.tool_registry import registry  # noqa: E402

registry.discover()
tool = registry._tools["atlas_image"]

SB = "docs/expeditie-mediajungle/style-bible"
REF = "docs/expeditie-mediajungle/references"
D2 = "projects/expeditie-mediajungle-posters/assets/images/round-2"
OUT = "projects/expeditie-mediajungle-posters/assets/images/round-3"
pathlib.Path(OUT).mkdir(parents=True, exist_ok=True)

STYLE = (
    "Stylized 3D CG in the language of a modern animated feature film, deliberately NOT "
    "photorealistic: simplified sculpted forms, gently exaggerated proportions, "
    "hand-painted-feeling surface textures, clean readable silhouettes, soft global "
    "illumination, a warm cinematic key light with a cool rim, matching the supplied "
    "character plates exactly in face, material, colour and proportion."
)

FEMKE = (
    "FEMKE (exactly as in the supplied plates): a 15 to 16 year old girl with red-orange "
    "hair in a ponytail carrying one pale zigzag streak, turquoise rectangular glasses, "
    "green eyes, freckles across her nose and cheeks; a dark navy T-shirt with the colourful "
    "printed MEDIA JUNGLE logo, teal cropped jeans with rolled cuffs, white high-top sneakers "
    "with purple laces, a dark purple smartwatch on the left wrist."
)

BOAZ = (
    "BOAZ (exactly as in the supplied plates): a 15 year old boy with deep warm dark brown "
    "skin, black spiky hair carrying a pale zigzag highlight, a small stud in one ear, warm "
    "brown eyes; an amber-yellow V-neck long-sleeve shirt with a large 07 across the chest, "
    "teal over-ear headphones resting around the neck, teal-blue slim jeans, purple sneakers."
)

POSTER_ZONES = (
    "POSTER LAYOUT: this is a vertical movie-poster frame. The top fifth of the frame is "
    "calm and simple scenery (sky or soft canopy, no important detail). The bottom sixth of "
    "the frame is plain calm ground scenery with no important detail. All characters and key "
    "action sit in the middle of the frame, fully visible, nothing important cropped by the "
    "edges. The artwork fills the entire frame edge to edge — no flat empty colour bands."
)

JOBS = [
    {
        "id": "p2-gesture-eyes-edit",
        "mode": "edit-existing",
        "inputs": [f"{D2}/p2-tent-think-first.png"],
        "output": f"{OUT}/p2-tent-think-first-v2.png",
        "prompt": (
            "Fix two things in this image and change nothing else.\n\n"
            "1. THE BOY'S GESTURE, clearer and more exaggerated: raise his right hand higher, "
            "up beside his head, as a big open 'STOP, hold on!' palm facing the viewer, "
            "fingers spread wide, eyebrows raised high and mouth slightly open as if saying "
            "'ho!'. He still lies on his belly in the tent entrance looking at the girl's "
            "phone. Keep his face exactly the same person.\n\n"
            "2. THE GLOWING ANIMAL EYES: remove the dark creature shapes with eyes sitting in "
            "the FOREGROUND bushes at the bottom left and bottom right of the frame. Instead, "
            "keep only a few small pairs of colourful glowing cartoon eyes peeking out DEEP in "
            "the dark background bushes, half hidden, further away from the tent — curious, "
            "not scary.\n\n"
            "Keep everything else exactly the same: the girl with her phone and hovering "
            "finger, the thought bubble with the question mark, the tent with the lantern, "
            "the moon, the drizzle, the jungle, colours and lighting."
        ),
    },
    {
        "id": "p3-pakketbusje",
        "mode": "generate",
        "inputs": [
            f"{SB}/femke-face-neutral-smile.png",
            f"{SB}/femke-body-front-headless.png",
            f"{SB}/boaz-face-neutral-smile.png",
            f"{SB}/boaz-body-front-headless.png",
            f"{SB}/prop-jeep-reward.png",
            f"{REF}/building--step4--mall.png",
            f"{SB}/location-jungle-path-after-rain.png",
        ],
        "output": f"{OUT}/p3-pakketbusje.png",
        "prompt": f"""{STYLE}

SCENE: {FEMKE} {BOAZ}

A parcel delivery moment on a jungle clearing. A boxy toy-like DELIVERY VAN in the same sculpted vehicle language as the supplied jeep plate — but a different vehicle: a compact cream-coloured panel van with teal and red accents, matching the brand colours of the supplied shop plate, with "COCO'S KOOPJES" painted in playful red letters on its side. The van is parked at the left on the jungle road, rear doors open, a few plain brown cardboard parcels visible inside. No driver, nobody in the van — exactly two people in the whole image.

STORY IN THE IMAGE — expectation versus reality: in the middle Femke kneels or stands at a freshly opened brown cardboard parcel, torn open, packing straw spilling out. She holds up her smartphone with the screen toward the viewer: on the screen is a picture of gleaming GOLDEN luxury headphones, shiny and perfect — what she ordered. But in the opened parcel lies the delivered reality: a sad, flimsy FAKE version of those headphones, crooked cardboard-and-tape build, dull grey, one earpiece hanging loose. Femke's expression is baffled disappointment: eyebrows up, mouth open in a small 'huh?'. Boaz crouches on the other side of the parcel and holds ONE ordinary magnifying glass with a single round lens ABOVE THE PARCEL, inspecting the shipping label on the box, his face fully visible beside the glass with a sceptical, investigative frown — the glass is aimed at the label, not at his eye.

A couple more unopened plain brown parcels sit stacked beside them.

SETTING: dense jungle in the leaf language of the supplied jungle plate, warm daylight, mossy stones by the road.

{POSTER_ZONES}

FRAME: the only readable text in the image is "COCO'S KOOPJES" on the van's side and the MEDIA JUNGLE logo on the girl's shirt. The shipping label and the phone screen carry no readable letters. No other words, no captions, no title, no logo band. No watermarks, no border, exactly two people.""",
    },
]

only = sys.argv[1:] or None
for job in JOBS:
    if only and job["id"] not in only:
        continue
    result = None
    for attempt in range(3):
        result = tool.execute({
            "prompt": job["prompt"],
            "model": "google/nano-banana-2/edit",
            "generation_mode": "edit",
            "image_paths": job["inputs"],
            "aspect_ratio": "2:3",
            "resolution": "4k",
            "output_path": job["output"],
        })
        if result.success:
            break
        print(f"{job['id']} attempt {attempt+1} failed: {result.error}", flush=True)
        time.sleep(45)
    print(job["id"], "->", "OK" if result.success else f"FAILED: {result.error}", flush=True)
    logpath = "projects/expeditie-mediajungle-posters/artifacts/generation_log.json"
    log = json.load(open(logpath))
    log.append({"id": job["id"], "round": 3, "model": "google/nano-banana-2/edit",
                "prompt": job["prompt"], "reference_images": job["inputs"],
                "success": result.success,
                "cost_usd": 0.16 if result.success else None,
                "output": job["output"] if result.success else None,
                "error": result.error})
    json.dump(log, open(logpath, "w"), indent=2, ensure_ascii=False)

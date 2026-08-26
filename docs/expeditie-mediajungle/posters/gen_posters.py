"""Genereer de 3 Expeditie Mediajungle posterartworks (missie 1-3) via atlas_image.

Model: google/nano-banana-2/edit — het gelockte style-bible model.
Referenties: style-bible karakterplaten + canon-art (jeep, tent, Coco's Koopjes).
Tekstzones (boven/onder) blijven rustig; slogans + MJ-logo worden later als
scherpe typografielaag gecomposit. In-scene tekst (bordje, tassen) gaat wél mee.
"""
import json
import sys

sys.path.insert(0, "/Users/jorrit/dev/OpenMontage")
from tools.tool_registry import registry  # noqa: E402

registry.discover()
tool = registry._tools["atlas_image"]

SB = "docs/expeditie-mediajungle/style-bible"
REF = "docs/expeditie-mediajungle/references"
OUT = "projects/expeditie-mediajungle-posters/assets/images"

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
    "green eyes, freckles across her nose and cheeks; a dark navy T-shirt with a colourful "
    "printed jungle logo, teal cropped jeans with rolled cuffs, white high-top sneakers "
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
    "calm and simple (sky or soft canopy, no important detail) — reserved for a title. The "
    "bottom sixth of the frame is simple ground with no important detail — reserved for a "
    "logo. All characters and key action sit in the middle of the frame, fully visible, "
    "nothing important cropped by the edges."
)

FRAME = "FRAME: no text, no letters, no labels, no watermarks, no border, exactly two people."

JOBS = [
    {
        "id": "poster-1-jeep",
        "prompt": f"""{STYLE}

SCENE: {FEMKE} {BOAZ}

Femke and Boaz proudly pose with their chunky yellow expedition jeep from the supplied jeep plate (same body, wheels, black roll cage and trim) on a jungle trail. The jeep stands in three-quarter front view. Femke sits behind the steering wheel with her head and one arm out of the open side window, laughing brightly at the camera. Boaz sits relaxed and confident on the hood of the jeep, his feet resting on the front bumper, arms loosely crossed, a proud grin at the camera. Both look straight into the camera radiating confidence — they are clearly thrilled with the jeep.

SETTING: a lush dense jungle exactly in the leaf language of the supplied jungle plate: big sculpted banana and monstera leaves, ferns and mossy stones framing the scene left and right, a warm sunny break of golden daylight on the jeep and the kids, deep green jungle behind them.

{POSTER_ZONES}

{FRAME}""",
        "refs": [
            f"{SB}/femke-face-neutral-smile.png",
            f"{SB}/femke-body-front-headless.png",
            f"{SB}/boaz-face-neutral-smile.png",
            f"{SB}/boaz-body-front-headless.png",
            f"{SB}/prop-jeep-reward.png",
            f"{SB}/location-jungle-path-after-rain.png",
        ],
    },
    {
        "id": "poster-2-tent",
        "prompt": f"""{STYLE}

SCENE: {FEMKE} {BOAZ}

Night in the jungle. A cosy dark-green wedge camping tent from the supplied tent plate stands on a small clearing. Femke and Boaz both poke their heads out of the open tent entrance side by side, lying on their bellies, each resting their chin on their hands with elbows propped on the ground, smiling calmly at the camera. Only their heads and hands are visible in the tent opening; a warm faint lantern glow comes from inside the tent.

SETTING: it is dark; a big stylized moon glows between the clouds and a light drizzle of rain falls, leaving soft drips on the tent canvas. In the dark bushes around the clearing several pairs of colourful cartoon animal eyes peek out — pairs of glowing eyes in different colours, curious not scary. Big sculpted jungle leaves in the leaf language of the supplied jungle plates frame the scene, wet and glossy in the moonlight.

{POSTER_ZONES}

{FRAME}""",
        "refs": [
            f"{SB}/femke-face-neutral-smile.png",
            f"{SB}/boaz-face-neutral-smile.png",
            f"{REF}/reward--2--tent.png",
            f"{SB}/location-hut-exterior-rain.png",
            f"{SB}/location-jungle-path-day-rain.png",
        ],
    },
    {
        "id": "poster-3-cocos",
        "prompt": f"""{STYLE}

SCENE: {FEMKE} {BOAZ}

Femke and Boaz stand in front of the jungle shop from the supplied shop plate: the same boxy shop with a red central tower, big teal glass windows and a cream sign band reading "COCO'S KOOPJES" in playful red letters, remade in the same stylized 3D CG language. Next to the shop entrance stands a small wooden sign that reads exactly: "KOOP JE LOCO, ZO HELP JE COCO!". Boaz stands closest to the shop, leaning forward and inspecting the shop through a large magnifying glass, one eye comically enlarged behind the lens, a sceptical investigative look on his face. Femke stands beside him beaming with joy, carrying two big overfull paper shopping bags with "COCO'S KOOPJES" printed on them, colourful gadgets and rolled-up goodies sticking out of the bags. In the background on the jungle road their chunky yellow expedition jeep from the supplied jeep plate is parked.

SETTING: dense jungle surrounds the shop in the leaf language of the supplied jungle plate, warm daylight, a few mossy stones by the path.

{POSTER_ZONES}

FRAME: no text anywhere except the shop sign "COCO'S KOOPJES", the wooden sign "KOOP JE LOCO, ZO HELP JE COCO!" and the bag print "COCO'S KOOPJES". No watermarks, no border, exactly two people.""",
        "refs": [
            f"{SB}/femke-face-neutral-smile.png",
            f"{SB}/femke-body-front-headless.png",
            f"{SB}/boaz-face-neutral-smile.png",
            f"{SB}/boaz-body-front-headless.png",
            f"{REF}/building--step4--mall.png",
            f"{SB}/prop-jeep-reward.png",
            f"{SB}/location-jungle-path-after-rain.png",
        ],
    },
]

log = []
only = sys.argv[1:] or None
for job in JOBS:
    if only and job["id"] not in only:
        continue
    out = f"{OUT}/{job['id']}.png"
    result = tool.execute({
        "prompt": job["prompt"],
        "model": "google/nano-banana-2/edit",
        "generation_mode": "edit",
        "image_paths": job["refs"],
        "aspect_ratio": "2:3",
        "resolution": "4k",
        "output_path": out,
    })
    entry = {
        "id": job["id"],
        "model": "google/nano-banana-2/edit",
        "aspect_ratio": "2:3",
        "resolution": "4k",
        "reference_images": job["refs"],
        "prompt": job["prompt"],
        "success": result.success,
        "cost_usd": (result.data or {}).get("estimated_cost_usd") if result.success else None,
        "output": out if result.success else None,
        "error": result.error,
    }
    log.append(entry)
    print(job["id"], "->", "OK" if result.success else f"FAILED: {result.error}")

logpath = "projects/expeditie-mediajungle-posters/artifacts/generation_log.json"
try:
    existing = json.load(open(logpath))
except Exception:
    existing = []
existing.extend(log)
json.dump(existing, open(logpath, "w"), indent=2, ensure_ascii=False)
print("log ->", logpath)

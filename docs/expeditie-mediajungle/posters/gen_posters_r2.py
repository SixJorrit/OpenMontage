"""Ronde 2: posterartworks zonder opmaaklaag, inhoudelijk aangesloten op de slogans.

Vier beelden: 1a (bubbels), 1b (telefoon-hart), 2 (twijfelmoment), 3 (fop-contrast
+ schaal-fix). Geen slogans/logo-band; in-scene canon-tekst en -logo's blijven wél
(Coco's Koopjes-bord, tassen, MJ-logo op shirt en jeep-deur).
Model: google/nano-banana-2/edit (gelockt style-bible-model), 2:3, 4k.
"""
import json
import sys

sys.path.insert(0, "/Users/jorrit/dev/OpenMontage")
from tools.tool_registry import registry  # noqa: E402

registry.discover()
tool = registry._tools["atlas_image"]

SB = "docs/expeditie-mediajungle/style-bible"
REF = "docs/expeditie-mediajungle/references"
OUT = "projects/expeditie-mediajungle-posters/assets/images/round-2"

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
    "calm and simple (sky or soft canopy, no important detail) — reserved for a title that "
    "will be added later. The bottom sixth of the frame is plain ground or scenery with no "
    "important detail — also reserved. All characters and key action sit in the middle of "
    "the frame, fully visible, nothing important cropped by the edges."
)

NO_TEXT_BASE = (
    "FRAME: no words, no letters, no captions, no title, no logo band or banner anywhere — "
    "not at the top, not at the bottom. The only graphic marks allowed are the MEDIA JUNGLE "
    "logo as it appears on the girl's shirt and on the jeep's door in the supplied plates. "
    "No watermarks, no border, exactly two people."
)

JEEP = (
    "their chunky yellow expedition jeep from the supplied jeep plate (same body, wheels, "
    "black roll cage and trim, MEDIA JUNGLE logo on the door)"
)

CHAR_REFS = [
    f"{SB}/femke-face-neutral-smile.png",
    f"{SB}/femke-body-front-headless.png",
    f"{SB}/boaz-face-neutral-smile.png",
    f"{SB}/boaz-body-front-headless.png",
]

JOBS = [
    {
        "id": "p1a-jeep-bubbles",
        "prompt": f"""{STYLE}

SCENE: {FEMKE} {BOAZ}

Femke and Boaz proudly pose with {JEEP} on a jungle trail. The jeep stands in three-quarter front view. Femke sits behind the steering wheel with her head and one arm out of the open side window, laughing brightly at the camera. Boaz sits relaxed and confident on the hood, his feet resting on the front bumper, a proud grin at the camera.

STORY IN THE IMAGE: around the two kids float a few glossy sculpted 3D chat-bubble icons containing only symbols — a red heart in one, a thumbs-up in another, a small yellow star in a third. The bubbles are bright, rounded and friendly, like reactions drifting up around them. BEHIND the jeep the jungle they came from is darker and unfriendly: thorny vines, gnarled shadowy bushes and two or three pairs of narrow angry glowing eyes deep in the gloom. The kids and the jeep are bathed in warm golden light — they have clearly left the dark part behind them.

SETTING: lush dense jungle in the leaf language of the supplied jungle plate: big sculpted banana and monstera leaves, ferns and mossy stones, a sunny break of daylight on the jeep and the kids.

{POSTER_ZONES}

{NO_TEXT_BASE} The chat bubbles contain only the heart, thumbs-up and star symbols — no letters.""",
        "refs": CHAR_REFS + [
            f"{SB}/prop-jeep-reward.png",
            f"{SB}/location-jungle-path-after-rain.png",
        ],
    },
    {
        "id": "p1b-jeep-phone-heart",
        "prompt": f"""{STYLE}

SCENE: {FEMKE} {BOAZ}

Femke and Boaz proudly pose with {JEEP} on a sunny jungle trail. The jeep stands in three-quarter front view. Femke sits behind the steering wheel with her head and one arm out of the open side window, laughing warmly. Boaz sits relaxed on the hood, his feet resting on the front bumper, and holds up a smartphone with the screen facing the camera: on the screen is one single large red heart symbol, nothing else. He grins proudly at the camera as if he just sent something kind. Femke looks at the phone and laughs with delight.

SETTING: lush dense jungle in the leaf language of the supplied jungle plate: big sculpted banana and monstera leaves, ferns and mossy stones framing the scene, warm golden daylight on the jeep and the kids.

{POSTER_ZONES}

{NO_TEXT_BASE} The phone screen shows only the single large heart symbol — no letters, no interface text.""",
        "refs": CHAR_REFS + [
            f"{SB}/prop-jeep-reward.png",
            f"{SB}/location-jungle-path-after-rain.png",
        ],
    },
    {
        "id": "p2-tent-think-first",
        "prompt": f"""{STYLE}

SCENE: {FEMKE} {BOAZ}

Night in the jungle. A cosy dark-green wedge camping tent from the supplied tent plate stands on a small clearing, a warm faint lantern glow from inside. Femke and Boaz both poke their heads and shoulders out of the open tent entrance side by side, lying on their bellies.

STORY IN THE IMAGE: Femke holds a smartphone in front of her, one index finger hovering hesitantly just above the screen, about to tap — but pausing. Above her head floats a small sculpted 3D thought bubble containing only a large question mark. Boaz looks at her phone and raises one hand in a gentle calm "hold on, wait" gesture, eyebrows raised. The moment reads clearly: think first before you send.

SETTING: it is dark; a big stylized moon glows between the clouds and a light drizzle of rain falls, leaving soft drips on the tent canvas. In the dark bushes around the clearing several pairs of colourful cartoon animal eyes peek out — curious, not scary. Big sculpted jungle leaves in the leaf language of the supplied jungle plates frame the scene, wet and glossy in the moonlight.

{POSTER_ZONES}

{NO_TEXT_BASE} The thought bubble contains only the question mark; the phone screen shows only a soft glow — no letters, no interface text.""",
        "refs": [
            f"{SB}/femke-face-neutral-smile.png",
            f"{SB}/boaz-face-neutral-smile.png",
            f"{REF}/reward--2--tent.png",
            f"{SB}/location-hut-exterior-rain.png",
            f"{SB}/location-jungle-path-day-rain.png",
        ],
    },
    {
        "id": "p3-cocos-scale-fix",
        "prompt": f"""{STYLE}

SCENE: {FEMKE} {BOAZ}

Femke and Boaz stand in front of the jungle shop from the supplied shop plate, remade in the same stylized 3D CG language. SCALE LOCK: the shop is a full-size building exactly as proportioned in the supplied shop plate — its teal glass doorway is more than twice as tall as the characters, the cream sign band reading "COCO'S KOOPJES" in playful red letters sits high above their heads on the facade, and the red central tower rises far above that. The characters reach no higher than the bottom quarter of the building.

STORY IN THE IMAGE: Femke beams with joy, carrying two big overfull paper shopping bags with "COCO'S KOOPJES" printed on them; out of the bags stick shiny gold-glinting gadgets and trinkets that look too good to be true, a couple of them carrying small bright red discount stickers showing only a percent symbol. Boaz stands beside her leaning toward one of the shiny gadgets, inspecting the small dangling price tag on it through ONE ordinary magnifying glass with a SINGLE round lens and a single handle held in front of his eye — through the lens his eye appears comically enlarged — with a sceptical, investigative frown. Next to the shop entrance stands a small wooden sandwich-board sign that reads exactly: "KOOP JE LOCO, ZO HELP JE COCO!". In the background on the jungle road their chunky yellow expedition jeep from the supplied jeep plate is parked.

SETTING: dense jungle surrounds the shop in the leaf language of the supplied jungle plate, warm daylight, mossy stones by the path.

{POSTER_ZONES}

FRAME: the only readable text in the image is the facade sign "COCO'S KOOPJES", the wooden sign "KOOP JE LOCO, ZO HELP JE COCO!", the bag print "COCO'S KOOPJES", the percent symbols on the stickers, and the MEDIA JUNGLE logo on the girl's shirt. No other words, no captions, no title, no logo band at the top or bottom. No watermarks, no border, exactly two people.""",
        "refs": CHAR_REFS + [
            f"{REF}/building--step4--mall.png",
            f"{SB}/prop-jeep-reward.png",
            f"{SB}/location-jungle-path-after-rain.png",
        ],
    },
]

import pathlib
pathlib.Path(OUT).mkdir(parents=True, exist_ok=True)

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
        "round": 2,
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
    print(job["id"], "->", "OK" if result.success else f"FAILED: {result.error}", flush=True)

logpath = "projects/expeditie-mediajungle-posters/artifacts/generation_log.json"
try:
    existing = json.load(open(logpath))
except Exception:
    existing = []
existing.extend(log)
json.dump(existing, open(logpath, "w"), indent=2, ensure_ascii=False)
print("log ->", logpath)

"""Defect-herstel ronde 2: banden vullen (p1a/p1b), sneaker (p1b), gevel-typo (p3)."""
import json
import sys
import time

sys.path.insert(0, "/Users/jorrit/dev/OpenMontage")
from tools.tool_registry import registry  # noqa: E402

registry.discover()
tool = registry._tools["atlas_image"]

D = "projects/expeditie-mediajungle-posters/assets/images/round-2"

FILL_BANDS = (
    "Fix one framing error in this image and change nothing else.\n\n"
    "The picture has flat empty colour bands at the very top and the very bottom of the "
    "frame. Remove them by extending the artwork itself to fill the entire frame edge to "
    "edge: at the top continue the sky and jungle canopy naturally upward; at the bottom "
    "continue the earthy jungle ground, mud and foliage naturally downward. The extended "
    "areas stay calm and simple, with no important new detail.\n\n"
    "Keep everything else exactly the same: both characters, their poses and faces, the "
    "jeep with its MEDIA JUNGLE door logo, the girl's shirt logo, all floating icons, the "
    "jungle, colours and lighting. Do not add any words, captions or logos."
)

JOBS = [
    {
        "id": "p1a-jeep-bubbles-v2",
        "input": f"{D}/p1a-jeep-bubbles.png",
        "output": f"{D}/p1a-jeep-bubbles-v2.png",
        "prompt": FILL_BANDS,
    },
    {
        "id": "p1b-jeep-phone-heart-v2",
        "input": f"{D}/p1b-jeep-phone-heart.png",
        "output": f"{D}/p1b-jeep-phone-heart-v2.png",
        "prompt": FILL_BANDS + (
            "\n\nAlso fix one wardrobe error: the boy's lifted left sneaker is white-pink; "
            "make it the same purple sneaker as his other foot, matching the supplied plates."
        ),
    },
    {
        "id": "p3-cocos-scale-fix-v2",
        "input": f"{D}/p3-cocos-scale-fix.png",
        "output": f"{D}/p3-cocos-scale-fix-v2.png",
        "prompt": (
            "Fix one spelling error in this image and change nothing else.\n\n"
            "The big cream facade sign at the top reads \"COCO'S KOIPJES\". Correct it to "
            "read exactly \"COCO'S KOOPJES\" in the same playful red letters, same size, "
            "same placement on the sign.\n\n"
            "Keep everything else exactly the same: both characters, poses, faces, the "
            "magnifying glass with the enlarged eye, the shopping bags and their "
            "\"COCO'S KOOPJES\" print, the percent stickers, the wooden sign with "
            "\"KOOP JE LOCO, ZO HELP JE COCO!\", the girl's shirt logo, the jeep, the "
            "building, the jungle, colours and lighting."
        ),
    },
]

log = []
only = sys.argv[1:] or None
for job in JOBS:
    if only and job["id"] not in only:
        continue
    result = None
    for attempt in range(4):
        result = tool.execute({
            "prompt": job["prompt"],
            "model": "google/nano-banana-2/edit",
            "generation_mode": "edit",
            "image_paths": [job["input"]],
            "aspect_ratio": "2:3",
            "resolution": "4k",
            "output_path": job["output"],
        })
        if result.success:
            break
        print(f"{job['id']} attempt {attempt+1} failed: {result.error}", flush=True)
        time.sleep(60)
    log.append({
        "id": job["id"], "round": 2, "model": "google/nano-banana-2/edit",
        "prompt": job["prompt"], "reference_images": [job["input"]],
        "success": result.success,
        "cost_usd": (result.data or {}).get("estimated_cost_usd") if result.success else None,
        "output": job["output"] if result.success else None,
        "error": result.error,
    })
    print(job["id"], "->", "OK" if result.success else f"FAILED: {result.error}", flush=True)

logpath = "projects/expeditie-mediajungle-posters/artifacts/generation_log.json"
existing = json.load(open(logpath))
existing.extend(log)
json.dump(existing, open(logpath, "w"), indent=2, ensure_ascii=False)
print("log ->", logpath)

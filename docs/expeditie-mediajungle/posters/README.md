# Posters missie 1–3 (A4) — 2026-08-26

Drie campagneposters in de gelockte 3D-stijl van de animatiereeks. Goedgekeurde route:

1. **Artwork**: `atlas_image` → `google/nano-banana-2/edit` (het style-bible-model), 2:3, 4k,
   met de style-bible-karakterplaten + canon-art (jeep, tent, Coco's Koopjes) als
   `reference_images`. In-scene tekst (bordje, tassen, gevelnaam) genereert mee; slogans en
   logo uitdrukkelijk NIET — die zone's blijven rustig (`POSTER_ZONES`-blok in de prompt).
   Prompts en referenties: `generation_log.json`, generator: `gen_posters.py`.
2. **Typografie**: als scherpe laag eroverheen via `build_posters.py` — HTML (216×303mm =
   A4 + 3mm afloop) → headless Chrome print-PDF (300 dpi) → `pdftoppm` PNG. Slogans in
   **Baloo 2 ExtraBold** (staat als user-font in `~/Library/Fonts`; anders via Google Fonts
   te halen), MJ-kleuren `#F5C518`/`#4A2C17`/`#2FB8A8`, footerband met het échte
   `../references/mj-logo-clean.png` + "MISSIE X". PDF embedt JPEG q95 (drukbestand ~3MB).

| bestand | wat |
|---|---|
| `poster-1-jeep.png` | master missie 1: Femke achter het stuur, Boaz op de motorkap |
| `poster-2-tent.png` | master missie 2: hoofden uit de tent, nacht/maan/regen/oogjes |
| `poster-3-cocos-v3.png` | master missie 3: Coco's Koopjes; v3 = lens-fix-edit + lokale shirtlogo-patch |
| `generation_log.json` | alle generaties incl. afgekeurde tussenstappen en prompts |
| `gen_posters.py` / `build_posters.py` | artwork-generator en A4-opmaakbuild (paden wijzen naar de lokale werkmap `projects/expeditie-mediajungle-posters/`) |

Afgekeurde versies (v1 dubbele lens, v2 verminkt shirtlogo) staan met diagnose in de lokale
werkmap onder `rejected/` — zie ook providerkennis §6 (nano-banana-edits vervormen kleine
tekst elders in het beeld; lokaal terugpatchen, niet regenereren).

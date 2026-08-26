# Handoff — Expeditie Mediajungle, animatie 2 (pilot)

Opgeschoond 2026-08-21 na de troubleshoot-sessie. Dit bestand beschrijft **alleen de staat van
deze productie**. De oude versie (370 regels, met interne correcties) staat in
`archive/HANDOFF-2026-08-21-voor-opschoning.md`.

Waar de rest staat:

| wat | waar |
|---|---|
| Providerkennis (tarieven, Seedance-gedrag, Kling, ElevenLabs, Azure-meter) | `skills/seedance-reference-audio-limits.md` |
| De route- en stembesluiten voor animatie 1, 3 en 4 | `TROUBLESHOOT-FINDINGS.md` + `artifacts/decision_log.json` (d-034 t/m d-037) |
| De briefing van de reeks | `BRIEFING-4-animaties.md` |

**De film is af en beoordeeld. Er wordt niets meer gerepareerd aan animatie 2** (instructie
Jorrit, troubleshoot-sessie). Animatie 1, 3 en 4 beginnen vers, op de nieuwe route.

---

## 1. Wat er ligt

| bestand | wat |
|---|---|
| `renders/animatie-2-fixronde2.mp4` | **de definitieve film**, 66,5s, 1280x720, 24fps. Alle negen feedbackpunten geadresseerd |
| `renders/animatie-2-fixronde1.mp4` | tussenversie met alleen de gratis fixes |
| `renders/animatie-2-compleet.mp4` | de oorspronkelijk beoordeelde versie, 60,4s |
| `assets/video/cut-v3/` | montageclips van de definitieve film + `assembly_report.json` |
| `assets/video/shots/attempts/` | alle afgekeurde generaties met prompt en diagnose (bewaren) |
| `assets/images/style-bible/` | de gelockte referentieset — **gaat ongewijzigd mee in alle vier films** |
| `assets/audio/lines/v2/` | de regelbestanden van de pilotroute (historisch; nieuwe films genereren regels via ElevenLabs) |
| `assets/audio/tts-test/` | de stemroute-tests van 2026-08-21 (v2/v3-vergelijking, casting, meterijking) |
| `artifacts/` | script, scene_plan, asset_manifest, edit_decisions, render_report, final_review, decision_log (37 entries) |
| `scripts-fixronde/` | de 25 sessiescripts, incl. `atlascost.py` (echte factuur uitlezen) |
| `feat/expeditie-mj-atelier-composition` | compositiecode (`ExpeditieMJ.tsx`), commit `7fba96d`, gepusht naar `fork` |

Checkpoints: `assets` staat op `awaiting_human`, `compose` op `in_progress` (het contract laat
compose niet sluiten zolang assets niet is goedgekeurd; het compose-werk is op verzoek van
Jorrit vooruit gedaan). De gate hoeft voor deze afgeronde pilot niet alsnog gepasseerd te
worden tenzij Jorrit dat wil.

## 2. Bekende, geaccepteerde afwijkingen in de definitieve film

- `shot_4B` toont een andere tempel en een grijzere stijl dan de ankerplaat — met
  vergelijkingsbeeld voorgelegd en bewust geaccepteerd door Jorrit.
- `shot_3B`, `shot_4C`, `shot_6B` zijn hertimed aan de rand van de band (+13 tot +14,6%).
- De vier Kling-lipsyncshots (2A, 2B, 2C, 5C) hebben 31–34% dubbelframes door de
  30fps-omweg, en de gekloonde stem staat op -44 dB onder de mix. Beide zijn de aanleiding
  geweest voor de nieuwe route (d-034/d-036); in deze film blijven ze zoals ze zijn.

## 3. Budget (werkelijke factuurcijfers)

| dag | Atlas werkelijk |
|---|---|
| 2026-08-19 (fase 0) | $3,06 |
| 2026-08-20 (fase 1) | $82,92 |
| 2026-08-21 (fixronde 1) | $0,00 |
| 2026-08-21 (fixronde 2) | $11,48 |

**Project totaal: $97,46** (waarvan ~$2,09 op het aparte project
`expeditie-mediajungle-intro`). Kling loopt op een trial pack: 97,3 van 100 units over, nul
cash. De troubleshoot-sessie van 2026-08-21 kostte $0 aan Atlas.

De oude cost logs (`cost_log.json`, `cost_log_fase1.json`) tellen structureel te laag —
alleen `cost_log_fixronde2.json` en de Atlas-API zelf zijn betrouwbaar. Reken nieuwe rondes
met **$0,373/s** (720p24) en tel calls na via `model-usage`; zie de projectskill §1.

## 4. Wat de volgende productiesessie moet weten

1. **Stemroute** (d-034/d-035): alle regels via ElevenLabs `eleven_v3` + emotietag, per take
   door de Azure-meter, retake onder drempel. Casting: Matanga = Hans Claesen, Femke = Ruth,
   Boaz = Bram. Details en ijkcijfers in de projectskill §4.
2. **SFX** (d-036): ambiance en effecten apart genereren via `music_gen` (`generate_sfx`);
   clipaudio gaat niet meer de mix in.
3. **Muziek** (d-037): pas op het allerlaatst; `music: null` in de props.
4. **Dialoogshots met spreker in beeld** (d-039): **R1-plus** — mode B met de v3-regel als
   referentie-audio, kloonstem weg, v3-regel als filmaudio; bij een ratio buiten 0,86–1,16
   eerst een andere/versnelde v3-take (audio is elastisch) in plaats van beeld hertimen.
   Spraakspannen meten met Azure word-timestamps, niet met whisper. R2 (kloonstem) is
   verworpen na beluistering; Kling-lipsync is alleen nog een noodgreep.
5. **Videomodel** (d-038): **seedance-2.5** voor de hele reeks, geen modellenmix. Testronde
   2026-08-21 kostte $7,93 van plafond $15; uitslagen en clips in
   `assets/video/model-tests/` en `TROUBLESHOOT-FINDINGS.md`, vraag 4.

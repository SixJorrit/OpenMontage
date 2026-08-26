# Handoff — animatie 2 opnieuw, met alle geleerde lessen

Geschreven 2026-08-26 aan het eind van de troubleshoot-sessie. **Doel van de nieuwe chat:
animatie 2 (de pilot) opnieuw produceren op de nieuwe route.** De bestaande pilot
(`renders/animatie-2-fixronde2.mp4`) blijft onaangetast staan als vergelijkingsmateriaal.

## Leesvolgorde

1. `AGENT_GUIDE.md` (verplicht, altijd eerst).
2. `docs/expeditie-mediajungle/README.md` — de route in vijf regels.
3. `skills/seedance-reference-audio-limits.md` in deze projectmap — de providerkennis
   (Layer 2; lees vóór elke generatie).
4. Bij twijfel over het waarom: `docs/expeditie-mediajungle/TROUBLESHOOT-FINDINGS.md` en
   `artifacts/decision_log.json` (d-034 t/m d-039 zijn bindend).

## Werkruimte

- Start een **nieuw project-workspace** (bijv. `expeditie-mj-animatie2-v2`) via
  `init_project` + `python -m backlot open` — overschrijf niets in
  `projects/expeditie-mediajungle-animaties/`.
- **Hergebruik als startpunt**: `artifacts/script.json` en `artifacts/scene_plan.json`
  van de pilot (het verhaal en de negen regels zijn goedgekeurd), de **gelockte style
  bible** (`assets/images/style-bible/` — ongewijzigd overnemen, niets regenereren) en de
  referencesmap. Alle gates opnieuw doorlopen; scene_plan mag wijzigen waar de nieuwe
  route dat vraagt (continuity locks, master-takes, off-screen staging).

## De route (bindend, samengevat)

1. **Spraak**: ElevenLabs `eleven_v3` + emotietag per regel. Casting: verteller Matanga =
   Hans Claesen (`FpLGR2n1CcG1v7SHJFsa`), Femke = Ruth (`YUdpWWny7k5yb4QCeweX`), Boaz =
   Bram (`2GJZCZIWrWiGFDntCFaz`). Elke take door de Azure-meter (drempel: regel <90 of
   woord <60 → retake); mens luistert het eindresultaat één keer na. Nooit whisper voor
   woordtrouw. Let op: de tts-tool schrijft raw PCM bij `pcm_16000`.
2. **Videomodel**: seedance-2.5, geen modellenmix. Reken **$0,373/s** (720p24, gemeten);
   nooit `model_catalog`/`estimate_cost`.
3. **Dialoogshots** (spreker in beeld): mode B — v3-regel als `reference_audios`,
   regeltekst NIET in de prompt (assert!), kloonstem weggooien, v3-regel = filmaudio. Ratio
   buiten 0,86–1,16? Eerst een andere/versnelde v3-take genereren, niet het beeld
   hertimen. Spraakspannen meten met Azure word-timestamps. Geen Kling (30fps-schade;
   alleen gedocumenteerde noodgreep). Lange regels waar mogelijk over beeld zonder spreker.
4. **Audio-mix**: clipaudio gaat NOOIT de mix in. Ambiance en SFX per scène genereren via
   `music_gen` (`generate_sfx`). **Muziek: `music: null`** — komt pas op het allerlaatst
   (d-037).
5. **Continuïteit**: per scène een blokkeringscontract (wie links/rechts, kijkrichtingen,
   camera-as) als CONTINUITY LOCK in élke shotprompt. Scènes met personages samen in
   beeld: overweeg een **master-take** (4–30s, zelfde prijs/s) en knip zelf met punch-ins
   1,2–1,3x. Doorlopende actie: frame-chaining (`return_last_frame` → `image_path`).
6. **Bewaar per generatie de `source_url`** (24u geldig) en archiveer afgekeurde
   generaties met prompt + diagnose. Draai generaties op de achtergrond met ruime timeout
   (praktijk 100–569s); een lokaal gekilde poll is NIET verloren — haal het resultaat op
   via de prediction-id.

## Budgetafspraken (Jorrit)

- **Vraag een budgetplafond vóór de eerste betaalde call** en presenteer eerst een raming
  op de gemeten tarieven. Ter referentie: de pilot (66,5s film) kostte $97,46 mét alle
  omwegen; een schone rerun zonder omwegen zou grofweg $35–50 aan generaties moeten
  kosten plus marge voor retakes — maar begroot het zelf per scene_plan.
- Tel na elke ronde je eigen calls na tegen het **requestaantal** in
  `/public/v1/model-usage` (`docs/expeditie-mediajungle/scripts/atlascost.py`); saldo en
  dagbucket lopen achter.
- ElevenLabs loopt op Jorrits Pro-credits, Azure op de gratis F0-tier, Kling op trial-units.

## Inventaris nieuw aangeleverd materiaal (2026-08-26, `assets/references/`)

- **`apng/` — 16 geanimeerde sprites (APNG, 36 frames, transparante achtergrond).** Twee
  families: de gebouwstappen (tent, camera, greenscreen, lanparty, fishing, kraan, tempel
  1251x1169) en zeven boom-assets (losse palm, drie palmen, palm-met-schermen,
  palm-met-camera, groep schermen, rij schermen, jungle-camera). **Doel (bevestigd door
  Jorrit, 2026-08-26): dit is canon-materiaal waarváán gegenereerd wordt** — dezelfde
  route als de karakters en de jeep in de pilot (canon-plaat → evt. promotie naar de style
  bible → `reference_images` in de generatie), zodat de gegenereerde wereld deze
  elementen bevat (schermen in de jungle, de gebouwstappen als locaties). Praktisch:
  Seedance eet stilstaande referenties, dus trek per APNG een representatief frame
  (`ffmpeg -i asset.png -frames:v 1 still.png`); de animatieframes zelf blijven daarnaast
  beschikbaar voor de compositielaag waar dat direct past. De vaste regel "genereer geen
  art die het project al bezit" betekent hier: verzin geen éigen schermen-bomen of
  gebouwen — gebruik déze als anker.
- **`icon--check.svg`, `icon--expeditie.svg`** — vectoriconen voor overlays/UI-momenten.
- Verder aanwezig: canon-platen (Femke, Boaz, tempel, jeep, eiland, bomen),
  `mj-logo-clean.png`, de statische vectorart-set (platforms, rewards, deco,
  gebouwstappen) en oude audio uit de pilotroute (die audio is vervangen door de
  v3-stemroute; niet meer gebruiken als filmaudio).

## Wat er beter moet dan de pilot (de meetlat)

De negen feedbackpunten van de pilot zijn bekend terrein; de nieuwe route lost de
onderliggende oorzaken op. Extra aandachtspunten uit de eindbeoordeling: shotconsistentie
binnen scènes (het continuïteitsprotocol is er speciaal voor), geen hoorbare tweede stem,
gelijkmatige framecadans (geen Kling), en 100% scriptgetrouwe Nederlandse spraak
(meter + luisterronde als bewijs).

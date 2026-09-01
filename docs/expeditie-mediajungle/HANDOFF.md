# HANDOFF — stand na de redo van animatie 2 (v2), 2026-08-28

Vervangt de pilot-handoff. **Animatie 2 is af en opgeleverd**:
`projects/expeditie-mj-animatie2-v2/renders/expeditie-mediajungle-animatie-2-v2.mp4`
(75,8s, 1280x720/24, met muziek). Echte factuur van de hele redo: **~$69** (nageteld via
`model-costs`, 26–28 aug), tegenover $97,46 voor de pilot. Alle 39+14 besluiten in
`projects/expeditie-mj-animatie2-v2/artifacts/decision_log.json` (r-001 t/m r-014 + geïmporteerde
d-034 t/m d-039).

## Volgende sessies: animatie 1, 3 en 4

**Jorrit levert eerst aangepaste scripts/storyboards aan** (aangekondigd 2026-08-28; komt in
een nieuwe chat). Begin dus niet vanuit de oude shotlists — wacht op zijn materiaal en run
daarna de gates gewoon opnieuw. Alles hieronder is het herbruikbare *proces*, niet de inhoud.

## De bewezen route (lees ook providerkennis.md, secties 6+)

1. **Workspace**: nieuw project via `init_project` + `python -m backlot open`. Style bible
   ongewijzigd hergebruiken; canon-vectorart eerst promoveren naar 3D-stijl via
   `google/nano-banana-2/edit` (vector-still + style-bible-plaat als stijlanker, $0,12/beeld) —
   nooit vectors direct als reference (stijlbreuk).
2. **Stemmen (route A2, r-006/r-009)**: eleven_v3 + emotietag (casting: Hans Claesen/Ruth/Bram),
   meter ≥90/woord ≥60, **F0-registergate** (±10% t.o.v. goedgekeurde takes van die stem),
   loudnorm I=-16 op élke filmtake. Zo nodig vooraf atempo ~0,88-0,90 (die versie = filmaudio
   én seedance-referentie); cumulatieve atempo boven ~0,85 houden.
3. **Video**: seedance-2.5 via `atlas_video`, $0,373/s gemeten, 720p24.
   **Duurregel: dialoogshot = audioduur + 0,5–1,0s, nooit ruimer.** Referentiebeelden ≥300px
   hoog. Audio-entries 1,8–30,2s (korte regels padden). Regeltekst nooit in de prompt (assert).
   Geen licht-metaforen in acting-prompts; EYES LOCK bij emotioneel acteren.
4. **Gates per dialooggeneratie**: kloon-meter ≥93 woordperfect én mondspan-ratio — 0,95–1,05
   voor close-ups, 0,86–1,16 voor medium/wide. Fail op ratio met goed beeld → **deterministisch
   repareren** (per-segment audio op de mondpauzes; of per-segment beeld-hertiming — beide
   bewezen en door Jorrit geaccepteerd), nooit opnieuw gokken. Alleen beeldfouten = retake.
   Reken ~15% retakemarge.
5. **Audio-architectuur (r-004/r-008)**: Seedance-clipaudio behouden in mensloze shots (goede
   ambiance, wel naluisteren op verzonnen spraak - "bitch-ass"-incident); beds
   (`music_gen`-ambience) onder dialoogshots; beds per scène doorlopend (cumulatieve
   bron-offsets, zachte bed-koppen overslaan); alle audio-lassen in spreekpauzes met fades.
   Muziek pas op het allerlaatst via `music_gen` + `musicEnvelope` in de compositie.
6. **Compositie**: Remotion `ExpeditieMJ` (atelier), per-shot voorbewerkte MP4's in
   `remotion-composer/public/<clipdir>/`, props met title/error/rewardWindow + envelope.
   Drafts altijd met **shotnummers in beeld** (PNG-overlay-napass) — Jorrits reviewvorm.
7. **Operatie**: generaties sequentieel op de achtergrond (100–740s praktijk); gestrande poll →
   prediction-id (endpoint kan ~30 min 401 geven terwijl public-API werkt); calls natellen via
   `model-costs`/`model-usage`; afgekeurde generaties archiveren in attempt-mappen met diagnose.
8. **Gemini Omni**: alleen previz/schermcontent/timecoded beats — nooit eindbeeld of video-edit
   op gelockte identiteit (herstijlt karakters, gemeten).

## Reviewritme met Jorrit (werkte goed)

Draft → feedback per shotnummer → gerichte fixes (gratis waar het kan) → nieuwe draft.
Budget per ronde vooraf laten accorderen (plafond-revisies in het decision_log). Previews
altijd met de échte filmaudio (nooit kale kloonstem laten beoordelen) en met labels.

## Werkscripts (herbruikbaar, in projects/expeditie-mj-animatie2-v2/)

`generate_units.py` (batchgeneratie met asserts/logging/checkpoints), `ratio_check.py`
(lipsync-gate), `compose_prep_v3.py` (per-shot bak: beds/VO/accenten/offsets),
`retakes_round*.py` (retake-patronen), F0-meting: zie providerkennis §"v3-takes driften".

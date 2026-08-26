# Providerkennis Expeditie Mediajungle — Seedance/Atlas, Kling, ElevenLabs, Azure

Duurzame, gemeten providerkennis die over de vier films heen geldt. Opgeschoond 2026-08-21
(troubleshoot-sessie); de ongeredigeerde geschiedenis staat in
`archive/seedance-reference-audio-limits-2026-08-21-voor-opschoning.md`. Productiebesluiten
staan niet hier maar in `artifacts/decision_log.json` (d-034 t/m d-037) en
`TROUBLESHOOT-FINDINGS.md`.

---

## 1. Kosten en kostenmeting (Atlas)

**Het gemeten tarief is de enige meter.** Voor `bytedance/seedance-2.5/reference-to-video` op
720p24, uit de factuur van 2026-08-21:

- **$0,373 per seconde** (≈ 39.800 output-tokens/s, ≈ $9,37 per miljoen tokens)
- Seedance factureert op **output-tokens**; `model-usage` geeft letterlijk `video: null`.
- `model_catalog` noemt $0,134/s — **2,8x te laag**. `atlas_video.estimate_cost()` rekent
  daarmee en is dus onbruikbaar (openstaande taak-chip). Alle vier de gecontroleerde
  modelpagina's hadden een fout tarief.
- nano-banana-2 rekent per resolutietier; 2752x1536 is de **2k-tier van $0,12** per beeld,
  niet de geadverteerde $0,08.
- **Referentiemateriaal is gratis** (input/input_audio/input_image tellen 0) en
  `generate_audio` kost niets extra.

**Controleprotocol na elke betaalde ronde:**

1. Tel je eigen calls na tegen het **requestaantal** in `GET /public/v1/model-usage`. Dat is
   het enige betrouwbare signaal; saldo en dagbucket lopen achter.
2. Een **lokaal gekilde of getimeoute submit wordt server-side afgemaakt en gefactureerd**
   (gemeten: 9 eigen calls, 10 op de factuur, ~$1,49 verschil). Draai elke generatie op de
   achtergrond met ruime timeout; `estimate_runtime` zegt 180s, de praktijk was 100–569s.
3. Een submit die vóór generatie wordt geweigerd (400/402) kost niets.
4. Lees echte kosten met `GET /public/v1/model-costs` (`scripts-fixronde/atlascost.py`).

**HTTP 402 betekent niet altijd "tegoed op":** parallelle submits (20–27s na elkaar) vriezen
elk hun eigen tegoed vast en worden geweigerd terwijl er saldo staat. Bij een 402: eerst het
echte saldo lezen (`GET /public/v1/balance`), dan **de gelijktijdigheid verlagen** en opnieuw
proberen; pas daarna aan bijvullen denken.

**HTTP 401 op de `model/*`-endpoints betekent niet "key ongeldig":** op 2026-08-26 gaven
`generateImage`/`prediction` ~25 minuten lang 401 unauthorized terwijl dezelfde key op
`/public/v1/balance` gewoon werkte en er saldo stond. Storing aan Atlas-kant; herstelde
vanzelf. Diagnose bij een 401: eerst balance-endpoint proberen — werkt die, dan is het een
storing en is een retry-loop (interval ~2 min) de juiste reactie, geen key-rotatie. Let op:
een submit die vlak vóór de storing wegging kan wél zijn aangenomen (poll gaf 401 op een
bestaand prediction-id); check achteraf `model-costs` op spookkosten.

## 2. Seedance 2.5 reference-to-video — gedrag

### Referentie-audio: 1,8–30,2s per entry

`InvalidParameter.DurationTooShort: Duration must be between 1.8s and 30.2s` slaat op de
audio-entry, niet op de clipduur. Korte regels padden met stilte
(`ffmpeg -af "apad=pad_dur=1.1"`); de spraak blijft even kort. Controleer elke entry vóór
submit.

### Het model spreekt ná, het kopieert niet

Referentie-audio conditioneert stemkleur en mondanimatie, maar het model **rendert de spraak
opnieuw** (cross-correlatie 0,52 sluit pass-through uit; een regel van 0,68s werd 1,02s). Twee
gevolgen:

1. **Woordfouten zijn mogelijk** ("natulet" voor "natuurlijk") — de gegenereerde stem is nooit
   per constructie scriptgetrouw. Verificatie: zie §4.
2. **Spreektempo heeft een ondergrens**: korte uitingen rekt het sterk op (0,76s → 1,18s),
   lange volgt het redelijk. Korte regels zijn dus het moeilijke geval. Gemeten ratio's
   (opname/generatie) liepen van 0,70 tot 1,06; hertimen is alleen onzichtbaar binnen de band
   **0,86–1,16**.

### Regeltekst niet in de prompt (procesregel met een assert)

Bindend sinds d-023: de regeltekst staat niet in de prompt (ook niet indirect in een
SCENE-beschrijving). Zet er een assert op in het generatiescript — die heeft echte fouten
gevangen en kost niets. **Bewijskracht eerlijk:** de drie shots mét regeltekst waren ook de
drie slechtst synchroniserende (0,78–0,87), maar een herhaalde generatie zonder regeltekst
bleef op 0,80 — het ratio-effect is dus níet bewezen; het blijft een procesregel, geen
gemeten oorzaak.

### Kadering en camerabeweging worden genegeerd

Vier van vier generaties leverden medium-totaal waar een medium shot gevraagd was (hoofd op
1/6–1/8 van de kaderhoogte i.p.v. 1/4), FRAMING/LENS LOCK ten spijt; één deed een push-in bij
`Camera movement: static`. Wat wél hielp: `no zoom, no push in, no pull back and no focal
change; the framing at the last frame is identical to the framing at the first frame`.
**Praktijkregel:** haal de definitieve kadering in de montage met een punch-in van 1,2–1,3x,
bepaald op een echt frame van de generatie. Een push-in van het model is dan gratis winst.

### Het inputframe verslaat de prompt

Regenachtige locatieplaten geven regen, wat de weerinstructie ook zegt. Voor elke weerstand
een eigen plaat. De geometrieclip is wél te overrulen door een droge plaat.

### Karakterlijst en staging moeten symmetrisch zijn

Wie in kader hoort, staat in de referentieset; wie niet, gaat eruit — beide kanten op. Twee
subjecten met kaderposities in `FIRST FRAME AND BLOCKING` bij een gevraagde solo levert een
verkeerde voorgrond op ($1,36 leergeld) of een verzonnen personage ($0,54). Gebruik `SOLO
LOCK` + `FRAMING LOCK`.

### Continuïteit tussen shots: contract + master-take + chaining

Staging verspringt tussen losse generaties als de prompts geen scène-breed contract delen.
Drie gereedschappen (protocol in `TROUBLESHOOT-FINDINGS.md`, vraag 6):

1. **CONTINUITY LOCK**: het scène-blokkeringsblok (wie links/rechts, kijkrichtingen,
   camera-as / 180-gradenregel) letterlijk herhalen in elke shotprompt van de scène.
   Links/rechts-plaatsing wordt exact opgevolgd (2/2 gemeten, seedance én minimax) — in
   tegenstelling tot kaderhoogte en camerabeweging.
2. **Master-take**: seedance-2.5 genereert 4–30s (`-1` = auto) tegen hetzelfde tarief per
   seconde; één doorlopende take per scène en zelf knippen met punch-ins geeft gratis
   continuïteit en houdt de cut-timing bij de monteur. Punch-ins kosten resolutie
   (overweeg 1080p-esr); een mislukte lange take is een grotere schadepost.
3. **Frame-chaining**: `return_last_frame` op shot A en dat frame als `image_path` (eerste
   frame) van shot B — posities/licht/weer kloppen op de las. Alleen bij gelijke
   camerapositie; fouten planten zich voort door de keten.

### Groeperen = interne timing uit handen geven

Meerdere shots in één generatie: het model legt zelf de interne cuts (gemeten 1,750s/3,958s
waar 3,3s/1,7s gepland was). Overlay-timing wordt dan gokwerk. Meet de cuts achteraf met
scenedetectie; nooit schatten.

### Herknipte audio is niet vrij verplaatsbaar

Na generatie vormt de referentie-audio een paar met de mondanimatie. Een kop of staart
herknippen verschuift de ratio (gemeten: 0,99 → 0,76). Alleen koppen herknippen waar de
generatie niet op leunt. Controleer of een knip in een stiltegat valt met
`silencedetect=noise=-40dB:d=0.04` — whisper rapporteert voor elke schone opname onzet 0,000
en vindt dit dus nooit.

## 3. Kling official (lipsync) — LEGACY, alleen relevant als terugvaloptie

> Sinds d-034/d-036 is Kling geen onderdeel meer van de hoofdroute. Deze kennis blijft staan
> voor het geval een shot er alsnog om vraagt.

- **Uitvoer is altijd 30fps** — geen fps-parameter in tool of API. Terug naar 24 met
  nearest-frame geeft 31–34% dubbelframes (gemeten met mpdecimate); echte hertiming
  (`minterpolate`) kost scherpte. Meet de dubbelframe-ratio vóór montage als afkeurgate.
- `advanced_lip_sync` eist **≥2000ms gecropte audio**; padden met stilte. `sound_insert_time`
  is waar het **bestand** begint op de tijdlijn, niet de spraak.
- `identify_face` vindt de gestileerde 3D-gezichten betrouwbaar (face_id "0", $0,02);
  hergebruik `session_id` + `face_id`.
- Kling kan **niet bij lokale bestanden**: het vraagt een publieke `video_url`. Atlas'
  `source_url` is **24 uur geldig** — bewaar hem in het generatielog, anders is een shot een
  dag later niet meer te bewerken.
- `original_audio_volume=0` verwijdert óók de ambiance uit de clip. (Met d-036 — losse
  SFX-generatie — is dat geen probleem meer.)
- Het account loopt op een **trial pack** (100 units; 4 lipsyncs + 4 detecties = 2,7 units,
  nul cash). `kling_lip_sync.estimate_cost` ($0,32/shot) klopt niet voor dit account.
- `kling_tts` ondersteunt alleen `zh`/`en` — geen Nederlands.

## 4. Spraak genereren en verifiëren (de route sinds d-034/d-035)

### Generatie: ElevenLabs `eleven_v3` met emotietags

- Casting: verteller **Matanga = Hans Claesen** (`FpLGR2n1CcG1v7SHJFsa`, Vlaams), **Femke =
  Ruth** (`YUdpWWny7k5yb4QCeweX`), **Boaz = Bram** (`2GJZCZIWrWiGFDntCFaz`). De kloon
  "Mediajungle Dave" in het account wordt niet gebruikt.
- **Korte regels zonder tag jagen**: "Wat doet er niet?" werd 0,64s en verloor "niet"
  (meter 56–85 over drie takes). Met `[nervous]`: 1,76s, meter 98. **Tag is verplicht** en
  hoort als acteerrichting in het script-artefact. Stability 0,5 (1,0 dempt tags en bleef op
  85).
- De `elevenlabs_tts`-tool schrijft bij `output_format: pcm_16000` **raw PCM**, ook met een
  `.mp3`-extensie in het pad. Converteren: `ffmpeg -f s16le -ar 16000 -ac 1 -i in out.wav`.
- API-keys hebben scopes; nodig: `text_to_speech`, `voices_read` (en `user_read` voor
  quota-checks; `add_voice_from_voice_library` alleen om library-stemmen toe te voegen).

### Verificatie: Azure Pronunciation Assessment — nooit whisper

**Whisper is in beide richtingen onbetrouwbaar voor woordtrouw** (normaliseert "natulet" weg;
verzint "Helep, ik doe dat niet" op een correcte opname). Alleen bruikbaar voor "zit er
NL-spraak in en waar begint die".

De meter: REST short-audio op
`https://northeurope.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=nl-NL&format=detailed`
met header `Pronunciation-Assessment` = base64 van
`{"ReferenceText": <letterlijke regel zonder tags>, "GradingSystem": "HundredMark",
"Granularity": "Word", "EnableMiscue": true}`; audio als WAV PCM 16kHz mono. Resource:
`openmontage-speech` (northeurope, **gratis F0**: 5 STT-uren/maand, PA valt daaronder; zelfde
`AZURE_SPEECH_KEY` als `azure_tts`/`azure_stt`).

- IJkpunten: correcte regels scoren 96–99; dezelfde audio tegen een fout script zakte naar 83
  met dips (74/75/18) op de gemanipuleerde passage.
- **Beperking:** de `ErrorType`-labels (Omission/Insertion) blijven leeg; het signaal zit in
  scoredips. Grove-fouten-detector, geen bewijs.
- **Drempelregel: regel-accuracy < 90 óf enig woord < 60 → retake of naluisteren.** Eén
  volledige luisterronde op de eindmix blijft altijd staan.
- Let op: **Azure West Europe accepteert geen nieuwe klanten** (`RequestDisallowedByAzure`);
  nieuwe resources in northeurope zetten. De portal-wizard toont die fout pas laat en het
  foutpaneel lijkt eerst leeg.

## 5. Proces-valkuilen (agent)

- Wachtlussen op `ps aux | grep` matchen hun eigen commandoregel: wacht op bestanden, niet op
  processen.
- `CostTracker._load` overschrijft het plafond uit de constructor met de waarde uit het
  logbestand — eerder een verkeerd "resterend" gerapporteerd.
- Controleer generatiescripts met `ast.parse` vóór het draaien; een tekstvervanging laat
  makkelijk een oud fragment staan.

## 6. Nano Banana 2 (Atlas) — chirurgische beeldedits

`google/nano-banana-2/edit` (max 14 referenties, tot 4k; toolschatting $0,08/beeld maar de
échte prijs is per resolutietier — zie §1: 2k mat $0,12, de 4k-tier ligt vermoedelijk hoger;
alleen `model-costs` telt) is het gelockte style-bible-model. Bij de postersessie
(2026-08-26, 4 beelden op 4k) geleerd:

- **Een "verander alleen X"-edit hergenereert stilletjes ook tekst elders in het beeld.**
  De lens-fix op poster 3 repareerde het vergrootglas correct, maar verminkte en passant
  het MEDIA JUNGLE-logo op Femke's shirt tot wartaal — ondanks een expliciete
  keep-everything-lock in de prompt. Grote bordteksten overleefden wél; klein logotype niet.
- **Remedie: lokaal terugpatchen, niet opnieuw genereren.** Edit-output is vrijwel
  pixel-uitgelijnd met de input (basisdiff ~2%), dus een gefeatherde PIL-patch van het
  intacte gebied uit de vorige versie is gratis, deterministisch en onzichtbaar.
  Controleer na élke edit alle tekstdragende gebieden op ware grootte.
- Nederlandse in-scene tekst (bordje, tassen, gevelnaam) genereert het model foutloos mee
  als de exacte string in de prompt staat; poster-slogans en het merk-logo horen als échte
  typografielaag bovenop (Baloo 2 staat lokaal geïnstalleerd; MJ-kleuren #F5C518/#4A2C17/#2FB8A8).

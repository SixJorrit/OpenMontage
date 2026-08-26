# Troubleshoot-bevindingen — sessie 2026-08-21

Antwoorden op de vijf vragen uit `TROUBLESHOOT-HANDOFF.md`. Groeit per vraag; vraag 5 (opschonen) verwerkt dit document later in de definitieve instructieset.

## Vraag 3 — Nederlandse spraak die het script 100% volgt: OPGELOST (route staat, casting open)

**Gekozen route (Jorrit, deze sessie): ElevenLabs `eleven_multilingual_v2` + Azure Pronunciation Assessment als verificatiemeter + gericht naluisteren.**

### Wat er is vastgesteld

- `kling_tts` (de enige eerder geconfigureerde TTS) ondersteunt alleen `zh`/`en` (`tools/_kling/schemas.py:102`). Nederlands was onmogelijk met de oude configuratie.
- De "eigen opname" uit de pilotroute was zelf al ElevenLabs-uitvoer (bevestigd door Jorrit). Het account (Pro-abonnement) bestaat nog, met projectstemmen: `Mediajungle Dave` (kloon, nl, id zNLstS0OsdlQdVvyKKij), `Matanga (TEST)` (nl, id wRpvYm2PkhHVdXejrZ84), `[NL] CHIP NEW` (id h6uBOiAjLKklte8hdYio), `[EN] Chip` (kloon, id JOd7sMmNCOqoGAVpTaSm). Op 2026-08-18 is `Ruth - Professional female voiceover` (id YUdpWWny7k5yb4QCeweX) gebruikt voor missieteksten, model `eleven_multilingual_v2`.
- **Modelkeuze: `eleven_v3`** (Jorrit, 2026-08-21: "de nieuwe engine, stemmen klinken veel beter" — vervangt het v2-advies uit de Layer 3-skill, dat verouderd is). Gemeten v3-gedrag op de korte regel "Wat doet er niet?" (Ruth): zonder tag jaagt v3 erdoorheen (0,64s; "niet" herkend op 0–50; accuracy 56–85 over drie takes), mét emotietag `[nervous]` is het 1,76s, accuracy 98. **Protocol: v3 + emotietag per regel + meter verplicht per take; onder drempel = retake (credits verwaarloosbaar); de tag hoort bij het script-artefact als acteerrichting.** De meter bewaakt ook dat de tagtekst niet wordt uitgesproken (referentietekst = regel zonder tag). Stability: 0,5 voor tagresponsiviteit; 1,0 is stabieler maar dempt tags en haalde alsnog maar 85 op de korte regel.
- ElevenLabs-API-keys hebben scopes: de key heeft minimaal `text_to_speech`, `voices_read` (en liefst `user_read`) nodig. Een beperkte key geeft 401 `missing_permissions`.
- De `elevenlabs_tts`-tool schrijft bij `output_format: pcm_16000` **raw PCM** naar het opgegeven pad, ook met een `.mp3`-naam. Converteren: `ffmpeg -f s16le -ar 16000 -ac 1 -i in.pcm out.wav`.

### De verificatiemeter (vervangt whisper voor woordtrouw)

Azure Speech **Pronunciation Assessment**, REST short-audio, `nl-NL`, met `ReferenceText` = de letterlijke scriptregel. Endpoint: `https://northeurope.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=nl-NL&format=detailed`, header `Pronunciation-Assessment` = base64 JSON `{ReferenceText, GradingSystem: HundredMark, Granularity: Word, EnableMiscue: true}`. Audio: WAV PCM 16kHz mono.

Gemeten op de drie historisch beruchte pilotregels (2026-08-21):

| regel | stem | AccuracyScore | gevlagde woorden |
|---|---|---|---|
| "Het internet natuurlijk!" | Daan (professional) | 97 | geen |
| "Dat wordt een hele reis…" (lang) | Mediajungle Dave (kloon) | 96 | geen |
| "Onze eerste missie…" (langst) | Ruth (professional) | 97 | geen |

Negatieve controle (zelfde audio, expres fout script met 'rekenen' i.p.v. 'rekening', weggelaten en toegevoegde woorden): accuracy zakt naar **83**, gemanipuleerde passage scoort 74/75/18.

**Beperkingen van de meter, eerlijk:** de `ErrorType`-labels (Omission/Insertion) bleven op `None` ondanks `EnableMiscue: true`; het signaal zit in de score-dips, niet in nette labels. De meter is een grove-fouten-detector, geen bewijs. Drempelregel: **regel-accuracy < 90 óf enig woord < 60 → naluisteren.** Eén volledige luisterronde op de eindmix blijft staan.

**Whisper blijft ongeschikt voor woordtrouw** (beide richtingen) — alleen bruikbaar voor "zit er NL-spraak in en waar begint die".

### Infrastructuur

- Azure Speech-resource: `openmontage-speech`, resourcegroep `openmontage`, regio **northeurope**, tier **Free F0** ($0; 0,5M TTS-tekens + 5 STT-uren/maand — PA valt onder STT-uren). Aangemaakt 2026-08-21 op abonnement "Azure subscription 1" (jorrit@mediajungle.eu).
- **West Europe accepteert geen nieuwe klanten** (`RequestDisallowedByAzure`, aka.ms/locationineligible) — daarom northeurope. De portal-wizard toont deze fout pas na doorklikken op "View error details" (paneel laadt traag; lijkt eerst leeg).
- `.env`: `ELEVENLABS_API_KEY`, `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION=northeurope` gevuld; `azure_tts`, `azure_stt`, `elevenlabs_tts` op AVAILABLE.

### Casting (vastgelegd door Jorrit, 2026-08-21)

- **Femke = Ruth** (`YUdpWWny7k5yb4QCeweX`, "Ruth - Professional female voiceover")
- **Boaz = Bram** (`2GJZCZIWrWiGFDntCFaz`, "Bram - Calm and reliable")
- **Verteller (Matanga) = Hans Claesen - Engaging Storyteller** (`FpLGR2n1CcG1v7SHJFsa`, Vlaams accent; uit de publieke library toegevoegd aan het account, ook in collectie "Mediajungle")
- Getest op echte pilotregels: accuracy 97–99, niets gevlagd (`assets/audio/tts-test/`).
- Let op: er staat ook een oudere `Matanga (TEST)` (`wRpvYm2PkhHVdXejrZ84`) in het account — NIET de vertellerstem; de FpLG…-ID is de juiste.
- Toevoegen van een library-stem via API vraagt keypermissie `add_voice_from_voice_library`; via de UI kan het altijd.
- **Dave vervalt** (Jorrit, 2026-08-21: "ik weet niet waar Dave vandaan komt, die mag je vergeten"). De kloon `Mediajungle Dave` in het account wordt niet gebruikt. Casting is hiermee compleet: verteller Matanga, Femke, Boaz.
- Kanttekening kloonstemmen: het riskantste geval voor woordtrouw; de meter + naluisteren is daar het dragende deel.

### Kosten deze sessie

- Atlas: 0 calls, $0. ElevenLabs: ~360 tekens van het Pro-tegoed (verwaarloosbaar). Azure: $0 (F0).

## Vraag 2 — muziek eerst weglaten: BEVESTIGD

`music: null` in de props volstaat; `ExpeditieMJ.tsx` slaat de Audio-laag over. Geen actie nu. Bijeffect blijft (zie handoff §2): zonder muziek is de tweede stem uit vraag 1 beter hoorbaar — volgorde 3 → 1 aanhouden.

## Vraag 1 — framecadans + tweede stem: tweede stem OPGELOST; dialoogroute wacht op de R2-proefclip (Jorrit, 2026-08-21: "R2 eerst testen", betaalde tests nog niet)

### Tweede stem: structureel oplosbaar, geen meting meer nodig

De oorzaak (handoff §1B): clipaudio was de **enige** SFX-bron en bevat ambiance + kloonstem, onscheidbaar. Dat "enige" is vervallen: de ElevenLabs-key ontgrendelt ook `music_gen`, en die heeft een **`generate_sfx`-operatie** (ElevenLabs sound effects). Nieuwe route: **clipaudio volledig weglaten** uit de mix; ambiance en SFX (jungle, regen, TV-glitch) apart genereren per scène. Geen kloonstem in de mix = geen tweede stem, geen duckvensters, geen -44dB-compromis. Kost ElevenLabs-credits per SFX (verwaarloosbaar t.o.v. video).

### Framecadans: Kling heeft géén fps-knop

`kling_lip_sync` (toolschema geverifieerd) accepteert geen fps; uitvoer is altijd 30fps. De open handoff-vraag is daarmee beantwoord: de 30→24-omweg is niet binnen Kling te repareren. Wil je Kling toch houden, dan zijn de opties: echte hertiming (`minterpolate`, kost scherpte op beweging) i.p.v. nearest-frame, plus een **dupe-ratio-gate vóór montage** (mpdecimate-telling per shot; >±5% bij een bewegend shot = afkeuren) — die gate is triviaal te bouwen.

### De routes voor sprekende personages in beeld (alleen relevant voor animatie 3/4; animatie 1 is verteller-gedreven en heeft dit probleem helemaal niet)

- **R1 — mode B met TTS-regel als referentie-audio + hertimen** (bewezen pilotroute, nu met ElevenLabs-audio i.p.v. opname): woorden per constructie goed (de TTS-regel ís de filmaudio), cadans natief 24fps, geen Kling. Nadeel: de hertimingsmachinerie (band 0,86–1,16) blijft bestaan.
- **R2 — Seedance-kloonstem accepteren, bewaakt door de meter**: reference_audios = TTS-regel, de gegenereerde stem blijft de filmaudio (perfecte sync, geen hertimen, geen Kling), en elke regel gaat door Azure PA + naluisteren; fail = shot regenereren. Nadeel: woordtrouw hangt aan meter + oor (zachtere garantie dan R1), en het regeneratierisico is onbekend (pilotdata: fouten kwamen voor). Onbekende: kloont Seedance een TTS-stem beter/slechter dan een opname — alleen met een betaalde proefclip te meten.
- **R3 — Kling-lipsync op TTS-audio**: blijft mogelijk als redmiddel per shot, maar 30fps-cadans + Jorrits uitgesproken voorkeur tegen lipsync-achteraf (d-023).
- **R4 — kaderdiscipline**: sprekers zoveel mogelijk buiten beeld/van achteren; regel kan per definitie niet fout. Blijft de goedkoopste verdediging, combineerbaar met alle routes.

**Aanbeveling:** R1 als hoofdroute + R4 waar het script het toelaat; clipaudio overal vervangen door gegenereerde SFX. R2 alleen als Jorrit de hertimingsmachinerie per se kwijt wil — dan eerst één betaalde proefclip in de testronde van vraag 4.

## Vraag 4 — goedkopere videomodellen: TESTRONDE GEDRAAID (2026-08-21, plafond $15, besteed $3,91)

### Uitslag (één identiek shot per kandidaat: pilot-2A-prompt, zelfde referentieset + geometrieclip, v3-Bram-regel als referentie-audio)

| kandidaat | beeld t.o.v. style bible | meter op clipstem* | opmerkingen |
|---|---|---|---|
| **minimax-h3** | zeer sterk: geometrie en props vrijwel exact, garderobe compleet; gezicht wijkt af, zigzag-highlight ontbreekt | **99** | goedkoopste (cat. $0,10/s), levert 1344x768 24fps; 370s generatietijd |
| **seedance-2.0** | sterk on-model, zigzag-highlight aanwezig | 62 ("het" viel weg) | cat. $0,112/s; 225s |
| **seedance-2.5 (R2-proef)** | de bekende kwaliteit | 90 (volledige zin, op de drempel) | basislijn $0,373/s gemeten; 270s |
| **gemini-omni-std** | zachter; props uit geometrieclip deels genegeerd | 30 (spraak grotendeels afwezig) | cat. $0,135/s; wel snelst (76s) |
| gemini-omni-dev | **afgevallen**: eist precies één video_clip (editing-modaliteit, geen reference-to-video zoals wij het nodig hebben) | — | 2 weigeringen, niet gefactureerd |
| kling-v3-omni | beeld sterk (props + zigzag compleet, 1080p 24fps geleverd) maar **acting fout** (lachend i.p.v. gefrustreerd) | geen audio-ondersteuning | promptlimiet 2500 tekens (ingekorte prompt = ongelijke vergelijking); trial-units, $0 cash |

*De meter op clip-mixen (stem + ambiance) is indicatief: de goedgekeurde pilotbaseline scoort er zelf maar 30. Menselijk oor beslist; de clips staan in `assets/video/model-tests/` en zijn aan Jorrit gestuurd.

### Beluistering door Jorrit (2026-08-21)

- **Minimax overtuigt zeker.** Seedance-2.5 met v3-stem "ook heel sterk".
- **De pilotbaseline bleek bij herbeluistering een Engelse stem met een Duits accent te hebben** — de gekloonde stem drift dus niet alleen op woorden maar zelfs op taal/accent. Extra bewijs tegen de oude kloonroute (d-015/d-023-tijdperk).
- Vervolgopdracht: één complexer shot op **beide** finalisten (minimax-h3 en seedance-2.5): two-shot Femke+Boaz in zware regen, SPEAKER LOCK (alleen Femke spreekt, de volledige 5A2-regel als v3-audio, meter 94), 10s. Uitslag hieronder zodra gedraaid.

### Bevestigingstest "complex shot" (2026-08-21, uitslag)

Two-shot Femke+Boaz lopend op het regenpad, 10s, SPEAKER LOCK, volledige 5A2-regel (v3, Ruth, meter 94) als referentie-audio, 5 referentiebeelden. Beide op dezelfde prompt:

| | complex-minimax-h3 | complex-seedance-2.5 |
|---|---|---|
| stem-meter op clipaudio | **94** — volledige lange zin, niets laag | **75** — woordsalade in het midden ("rekening hele houden om het reis te reis"), 'rekening' op 15 |
| beeld | beide personages on-model, regen aanwezig; **kadering wijder dan gevraagd** (full body i.p.v. knees-up), shirtlogo verhaspeld | **kadering trouw** (knees-up), MEDIA JUNGLE-logo exact, regen subtieler |
| levering | 1344x768, 24fps, 10,1s | 1280x720, 24fps, 10,1s |

**Conclusie:** de historische woordfout van Seedance reproduceert op de moeilijke regel (75), terwijl minimax-h3 hem óók in het complexe shot vlekkeloos naspreekt (94, boven de drempel van 90). De sterktes zijn complementair: minimax wint op spraak en prijs, seedance op kader- en logotrouw. NB: de seedance-clip strandde lokaal op een DNS-storing tijdens het pollen en is via de prediction-id alsnog opgehaald — de bekende regel "een gekilde poll betekent niet dat de generatie weg is" werkte hier in ons voordeel; `recovered_source_url.txt` staat in de testmap.

### Eindafrekening testronde

Dag 2026-08-21 compleet (`partial: false`): $19,41 totaal − $11,48 (fixronde 2) = **$7,93 voor de hele testronde** (plafond $15). 16 requests = 10 (fixronde 2) + 6 gefactureerde testgeneraties; de 2 gemini-dev-weigeringen kostten niets. Kling: trial-units, $0 cash. Saldo na afloop: $19,61. Seedance-aandeel herleidbaar: 14s × $0,373 ≈ $5,22; de overige ~$2,71 verdeeld over seedance-2.0 (4s), minimax (14,5s) en gemini (4,5s) — minimax factureert daarmee aantoonbaar in de buurt van zijn catalogusprijs (~$0,10/s), dus **ruwweg 3,5–4x goedkoper dan seedance-2.5**.

### EINDBESLUIT (Jorrit, 2026-08-21 — d-038/d-039)

- **Videomodel: seedance-2.5** voor de hele reeks. "Seedance is wel echt beter"; geen modellenmix (kwaliteitsverschil zichtbaar). Minimax' spraakvoordeel weegt niet op tegen kaderdrift en logoverhaspeling.
- **Dialoogmechaniek: R1-plus.** R2 verworpen ("de dialoog is echt niet goed"). Mode B met de v3-regel als referentie-audio, kloonstem weggooien, v3-regel als filmaudio — met drie verbeteringen t.o.v. de pilotmachinerie:
  1. **Elastische audio**: valt een shot buiten de hertimingsband (0,86–1,16), genereer dan eerst een andere v3-take of gebruik de `speed`-parameter (0,7–1,2) van `elevenlabs_tts` — de audio beweegt naar de mond toe, in plaats van het beeld naar een vaste opname. Takes verschillen fors in tempo (gemeten: 0,64s vs 1,76s op dezelfde regel), dus dit is een echte knop.
  2. **Tweede stem bestaat niet meer**: clipaudio gaat niet de mix in (d-036), dus de kloonstem in de clip is irrelevant geworden — geen duckvensters.
  3. **Spraakspannen meten met Azure word-timestamps** (detailed-format geeft per woord Offset/Duration) in plaats van whisper — betrouwbaarder trimvenster en ratiometing.
  - R4 (sprekers buiten beeld waar gemotiveerd) blijft de goedkoopste verdediging; Kling-lipsync is alleen nog een gedocumenteerde noodgreep.

### R2-verdict (vraag 1, dialoogroute)

De seedance-2.5-kloon van de v3-stem haalt meter-90 met de volledige zin — precies op de drempel, niet ruim erboven. **Opvallendste bevinding: minimax-h3 sprak de v3-regel vrijwel perfect na (99), door de ambiance heen.** Als het oor dat bevestigt, is R2 mogelijk levensvatbaarder op minimax dan op seedance. Besluit ligt bij Jorrit na beluistering.

### Kosten en natelling

14 requests op 2026-08-21 = 10 (fixronde 2) + 4 geslaagde testgeneraties; de 2 gemini-dev-weigeringen zijn niet gefactureerd (pre-generatie). Ronde: **$3,91** (dagbucket $15,39 − $11,48 fixronde 2; bucket nog partial bij afsluiting). Per-model-uitsplitsing geeft de API niet; seedance-2.5 is per token herleidbaar (~$1,49), de rest gezamenlijk ~$2,42. Saldo na de ronde: $23,62.

### Nakandidaat: Wan 3.0 (geparkeerd, 2026-08-26)

Uitgebracht 24-08 (ná de testronde). Lijstprijs 720p $0,10/s — op papier ~3,7x goedkoper dan seedance-2.5, mét reference-gestuurde generatie, audio-invoer en 2–30s clips. Nog niet testbaar zonder frictie: Atlas heeft hem (nog) niet, OpenRouter geeft alleen tekst + first-frame door (geen referentieset, geen audio — ongeschikt voor ons protocol), en de native DashScope-route vraagt Alibaba-accountverificatie met btw-nummer. **Afspraak: bij de start van elke volgende productie de Atlas-catalogus checken; zodra Wan 3.0 daar staat, de klaarliggende testscripts draaien (~$1,50).** Ontbrekende last-frame-support (OpenRouter) is geen bezwaar: ons protocol gebruikt alleen first-frame-conditioning; eindframes trekken we zelf met ffmpeg.

### Oorspronkelijk protocol (uitgevoerd zoals gepland)

### Testprotocol (klaar om te draaien zodra er een plafond is)

- **Basislijn:** seedance-2.5 op 720p24 = **$0,373/s gemeten**. De catalogusprijzen zijn 2,8x te laag en alleen bruikbaar als volgorde-indicatie. Enige geldige meting per kandidaat: één clip genereren en daarna `/public/v1/model-costs` lezen (`scripts-fixronde/atlascost.py`).
- **Kandidaten** (ondersteunen reference-to-video; cataloguswaarde alleen als sortering): `minimax/h3` ($0,10/s cat.), `bytedance/seedance-2.0` ($0,112/s cat.), `google/gemini-omni-flash` developer-route ($0,112–0,12/s cat.) en standaard ($0,125–0,14/s cat.), plus `kling_official_video` (nieuw beschikbaar via KLING_API_KEY; ongeprijsd, mogelijk trial-units i.p.v. cash).
- **Methode:** één identiek shot per kandidaat — zelfde prompt, zelfde style-bible-referentieset (tot 8 beelden + geometrieclip), zelfde duur (~4s, 720p24). Beoordelen naast de seedance-2.5-versie op: karaktertrouw aan de gelockte platen, weerslot, kaderstabiliteit. Daarna de factuurdelta.
- **Meeliftend in dezelfde ronde: de R2-proefclip van vraag 1** (Seedance 2.5 met een ElevenLabs-v3-regel als reference_audios; de gegenereerde kloonstem door de meter halen). Dat beslist de dialoogroute.
- **Uitvoeringsregels:** generaties op de achtergrond met ruime timeout (praktijk 100–569s); calls natellen tegen het requestaantal in `model-usage`; mislukte generaties archiveren met prompt en diagnose.
- **Raming:** ±$1,50 per kandidaat-clip + R2-proefclip; 5 kandidaten + R2 + marge ≈ $10–15.

## Nagekomen vraag 6 — shotconsistentie binnen een scène (Jorrit, 2026-08-21)

Klacht: shots binnen een scène zijn onderling inconsistent (staging/posities verspringen tussen shots — het genoemde links/rechts-voorbeeld is illustratief, het gaat om het idee). Oorzaak: pilotprompts waren per shot, zonder scène-breed blokkeringscontract, dus het model koos per shot opnieuw.

**Protocol voor animatie 1, 3 en 4 (drie technieken, gecombineerd):**

1. **Scène-blokkeringscontract** (standaard, alle scènes): per scène één keer in het `scene_plan` vastleggen wie links/rechts staat, kijkrichtingen en aan welke kant van de handelingsas de camera blijft (180-gradenregel); dat blok als CONTINUITY LOCK letterlijk herhalen in elke shotprompt van de scène. Gemeten: links/rechts-plaatsing wordt door seedance-2.5 én minimax exact opgevolgd (beide complexe testclips).
2. **Master-take + punch-ins** (scènes met personages samen in beeld): één doorlopende take per scène (seedance-2.5 kan 4–30s, ook `-1`=auto) en in de montage knippen met punch-ins 1,2–1,3x. Continuïteit fysiek gegarandeerd, cut-timing bij ons (les g_scene1: nooit het model interne cuts laten leggen), kost per seconde hetzelfde als losse shots. Nadelen: één camera-as, resolutieverlies bij punch-ins (optie: 1080p-esr), grotere schadepost bij een mislukte take.
3. **Frame-chaining** (doorlopende actie over een cut): `return_last_frame` op shot A, dat frame als `image_path` (eerste frame) van shot B. Alleen voor zelfde camerapositie; let op foutvoortplanting.

## Vraag 5 — instructies reviewen en opschonen: GEDAAN (2026-08-21)

- **`skills/seedance-reference-audio-limits.md`** herschreven van 13 gegroeide secties naar één geordende projectskill (kosten/meting, Seedance-gedrag, Kling als gemarkeerde LEGACY-terugval, de nieuwe spraak+verificatieroute, proces-valkuilen). Verouderde cijfers ($0,340/s; $0,32/shot Kling) en dubbelingen verwijderd; de bewijskracht-caveat bij de regeltekst-assert behouden.
- **`HANDOFF.md`** teruggebracht van 370 naar ~90 regels: alleen productiestaat van animatie 2 (wat ligt waar, geaccepteerde afwijkingen, echte budgetcijfers, wat de volgende sessie moet weten). De zichzelf corrigerende paragrafen (§3/§3b, §2 vs §6) zijn weg; routes staan nu op één plek.
- **Verwijderde claims** (stonden fout of misleidend in de oude docs): de "afwijking mond versus woorden 20 ms"-meting (berustte op twee elkaar opheffende whisperfouten — niet als fundament herbruikbaar); de $0,340/s; de suggestie dat het regeltekst-ratio-effect bewezen is.
- **Archief:** de ongeredigeerde originelen staan in `archive/` (beide met datum in de naam). Niets is vernietigd.
- **`artifacts/decision_log.json`**: d-034 (stemroute v3 + casting, vervangt d-023 als bron van regels), d-035 (Azure PA-meter, vervangt whisper), d-036 (SFX gegenereerd, vervangt d-026-mix), d-037 (muziek uitgesteld). Schema-gevalideerd, 37 entries.
- **Bewust behouden ondanks "dood gewicht"-verwachting:** de hertimingskennis (band 0,86–1,16, spreektempo-ondergrens, herknip-regels) — die is pas dood als de R2-test slaagt; tot die tijd is R1 de terugvalroute.

# Posters missie 1–3 (A4)

## DEFINITIEVE KEUZES (vastgelegd 2026-09-11)

**Let op de hernummering (2026-09-11): online shoppen = missie 4.** Missie 3 = gezond
schermgebruik ("Gebruik je scherm gezond bewust. Dat geeft je lichaam kracht én rust!") —
daar is nog géén poster voor gemaakt.

| missie | definitieve master (in `round-3/`) | concept | slogan |
|---|---|---|---|
| 1 | `p1a-jeep-bubbles-logozone.png` | jeep met hart/duim/ster-bubbels, boze oogjes in de doornstruiken erachter | "Houd het gezellig en sociaal online. Dat is chill, dat is fijn!" |
| 2 | `p2-tent-think-first-logozone.png` | tent bij nacht, vinger boven verzendknop, denkwolkje, "HO!"-gebaar | "Eerst denken, dan verzenden. Dat scheelt een hoop ellende!" |
| 4 | `p3-staand-logozone.png` | pakketbusje; Boaz stáánd naast de doos met tablet (fop-webshop) in de rechterhand | "Laat je niet pushen, laat je niet foppen bij een potje online shoppen!" |

**Opgemaakte variant** (logo + slogan als niet-destructieve laag over de kale master):
`build_posters_opgemaakt.py` — E14-logo linksboven (104mm), tekst eronder in **Baloo 2
Medium**, wit met dunne bruine contour (1,15mm stroke-laag) + zachte schaduw, géén
missie-label. Output lokaal in `renders/opgemaakt/poster-missie-{1,2,4}-def.{pdf,png}`.

De niet-gekozen varianten (1b telefoonhart; poster 3 knielend met/zonder vergrootglas)
blijven in `round-3/` staan als alternatief, maar zijn géén deliverable. Print-klare
A4-uitsneden van de definitieve masters: lokale werkmap `renders/logozone/`
(`poster-1a-bubbels-logozone`, `poster-2-tent-logozone`, `poster-3-staand-logozone`,
PDF + 300dpi-PNG); regenereerbaar via `build_posters_r2.py`-patroon.

## VASTE LAYOUTREGEL — logozone linksboven (2026-09-09, geldt ook voor alle toekomstige posters)

Elke poster-master houdt **linksboven een open, rustige contrastzone van ruwweg 55% breed ×
30% hoog**: open lucht (dag: licht/nevelig, nacht: egale donkere lucht), geen bladeren,
lianen of belangrijke objecten. **Jorrit/het team plaatst daar zélf het Expeditie MJ-logo en
de missietekst** — de agent bakt géén logo of tekst in de deliverables. Bij nieuwe
generaties: neem het `POSTER_ZONES`-blok uit `gen_posters_r3.py` en vervang de top-regel
door deze linksboven-eis (let op de les: nooit het woord "reserved" gebruiken — dat geeft
platte kleurbanden; vraag om "calm open sky as full scenery"). Bestaande masters zijn
bijgewerkt als `round-3/*-logozone.png` (topstrip-edits, 16:9, gefeatherd teruggeplakt).

## Ronde 3 — feedbackronde poster 2 en 3 (2026-09-09)

Masters in `round-3/`; deze vervangen de ronde-2-versies van poster 2 en 3:

| bestand | wat er veranderde |
|---|---|
| `p2-tent-think-first-final.png` | Boaz' "HO!"-gebaar overdreven (grote open handpalm), oog-wezentjes uit de voorgrond naar de achtergrondstruiken, shirtlogo = officieel logo (crop-edit) |
| `p3-pakketbusje-final.png` | **nieuw concept**: Coco's Koopjes-pakketbusje, verwachting (gouden koptelefoon op Femke's telefoon) vs. werkelijkheid (karton-en-tape-namaak in het pakket), Boaz' vergrootglas op het verzendlabel i.p.v. voor zijn oog (oog-gag was te eng), koptelefoon-canon hersteld en onderband gevuld via crop-edits |
| `p3-pakketbusje-tablet-loep-final.png` | variant: Boaz met tablet die de fop-webshop toont (letterloze layout: gouden koptelefoon, %-badge, sterren) én het vergrootglas op het scherm |
| `p3-pakketbusje-tablet-final.png` | variant: idem maar zonder vergrootglas — tablet met beide handen vast |
| `p3-pakketbusje-staand-final.png` | variant: Boaz stáát naast de doos, tablet in de rechterhand (letterloos scherm), blik omlaag op het pakket; Femke's telefoon-hand via masker uit het origineel behouden, schermtekst lokaal weggewerkt (per-kolom rood-band-vulling) |

Script: `gen_posters_r3.py`. De crop-edit-route (uitsnede → herstel met referentie →
gefeatherd terugplakken) was opnieuw de betrouwbare weg voor logotype, wardrobe-adds
en bandvulling; full-frame edits alleen voor pose/compositie.

## Ronde 2 — tekstloos + inhoudelijk op de slogan (2026-09-09)

Op verzoek: **geen opmaaklaag** (geen slogans, geen logo-band) — in-scene canon-tekst en
-logo's blijven wél (Coco's-bord, tassen, MJ-logo op shirt/jeep-deur). Elke scène draagt nu
zelf de boodschap; masters in `round-2/`:

| bestand | missie / concept |
|---|---|
| `p1a-jeep-bubbles-v2.png` | 1: hart/duim/ster-bubbels rond de jeep, boze oogjes in doornstruiken erachter |
| `p1b-jeep-phone-heart-final.png` | 1 (variant): Boaz toont telefoon met één groot hart |
| `p2-tent-think-first.png` | 2: Femke's vinger boven de verzendknop, denkwolkje met vraagteken, Boaz gebaart "wacht" |
| `p3-cocos-scale-fix-final.png` | 3: winkel op echte schaal, gouden fop-koopjes met %-stickers, vergrootglas-inspectie |

Scripts: `gen_posters_r2.py` (generatie), `fix_r2.py` (defect-edits), `build_posters_r2.py`
(tekstloze A4-build). Lessen van deze ronde (ook in providerkennis §6):

- "Reserved for a title"-taal in een prompt levert **letterlijke platte kleurbanden** op —
  vraag om "calm simple scenery", nooit om gereserveerde zones.
- Full-frame edits blijven klein logotype slopen; de betrouwbare route is een **crop-edit**
  (probleemgebied uitsnijden, alleen dat laten herstellen — met `mj-logo-clean.png` als
  extra referentie voor logo's — en gefeatherd terugplakken). Aspect 2:1 bestaat niet bij
  nano-banana; 16:9 wel (mislukte submits met executionTime 0 worden niet gefactureerd).

## Ronde 1 — met typografielaag (2026-08-26)

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

# Shopify-pagina Expeditie Mediajungle — plan en conceptcopy (2026-09-09)

Doel: informatie voor scholen, verkoop, teasen met animatie en poster.
Canon: Femke en Boaz uit de animatiereeks. Noor/de Ruis (verhaalbijbel 2026-01) is oud en wordt genegeerd.

## Bestaande template (theme Bingo-sparta-02, view `expeditie-mediajungle` op /pages/about-us)

Kopie van de Educatieplatform-demopagina. Secties nu:

| # | sectie | huidige inhoud | voorstel |
|---|---|---|---|
| 1 | bingo_slideshow (hero) | "Ontdek het Educatieplatform tijdens een demo" + laptopbeeld | Expeditie MJ-logo lock-up + poster-artwork; kop + CTA |
| 2 | text_with_image | Van losse producten naar één platform | **Wat is Expeditie Mediajungle** (leerlijn, 10 missies, SLO) |
| 3 | text_with_image (zonder beeld) | Wat kun je verwachten in 15–20 min | **Zo werkt een missie** (animatie → opdrachten → beloning) + animatiefragment |
| 4 | text_with_image | "Complete leerlijn… beschikbaar vanaf augustus 2026" | **Voor de leerkracht** (minimale voorbereiding, ontzorgd, po/so/sbo) |
| 5 | text_with_image (zonder beeld) | Benieuwd? Binnen één werkdag contact | **CTA**: demo aanvragen / bestellen |
| 6 | bingo_testimonials | Zaan Primair e.a. | behouden (of weglaten als ze niet over Expeditie gaan) |
| 7 | section_partners | logo's | behouden |
| 8 | bingo_newsletter | nieuwsbrief | behouden |

Toe te voegen: een videosectie (theme-sectie "Video" of custom liquid met Shopify-gehoste MP4) en een postergalerij (image-with-text of collage). Te controleren in de editor zodra die laadt.

## Conceptcopy (NL, zakelijke stem richting scholen)

### Hero
**Kop:** Expeditie Mediajungle
**Sub:** Digitale geletterdheid als ontdekkingsreis voor groep 7 en 8
**Tekst:** Femke en Boaz zitten vast op een eiland. Het internet ligt plat en alleen jouw klas kan helpen. Tien missies, tien beloningen, één schooljaar lang digitaal geletterd worden.
**CTA:** Vraag een demo aan · Bekijk de intro

### Wat is Expeditie Mediajungle
Een complete leerlijn digitale geletterdheid en mediawijsheid voor groep 7/8 in het po, so en sbo, gebouwd op de SLO-kerndoelen. De klas gaat als expeditieteam op reis door de Mediajungle. Elke maand een missie van 45 tot 60 minuten, met een korte animatie als start, opdrachten in de klas en een beloning die het verhaal verder brengt.

- Dekt de SLO-kerndoelen 22, 23 en 24 (praktische vaardigheden, maken, de gedigitaliseerde wereld)
- Tien missies per schooljaar, in vaste volgorde met een doorlopend verhaal
- Leerling, school én ouder doen mee
- Plus-werk voor snelle leerlingen

### Zo werkt een missie
1. **Kijk.** Een animatie van ongeveer een minuut zet het probleem neer. Boaz: "Help, hij doet het niet!"
2. **Doe.** De klas werkt aan opdrachten rond het mediathema van de maand.
3. **Verdien.** Lukt het, dan krijgen Femke en Boaz wat ze nodig hebben voor de volgende etappe: een jeep, een tent, een winkelwagentje.

[hier: fragment animatie missie 1, ±20–30 s, met poster-still als cover]

### Voor de leerkracht
- Minimale voorbereiding: alles staat klaar in het Mediajungle Educatieplatform
- Werkvormen on- en offline, geschikt voor po, so en sbo
- Ouderbetrokkenheid ingebouwd (ouder/kindavond, gesprekswaaiers)
- Wist je dat scholen vanaf augustus 2027 verplicht werken aan de kerndoelen digitale geletterdheid?

### Kom mee op expeditie (CTA)
Expeditie Mediajungle is onderdeel van het Mediajungle Educatieplatform. [Beschikbaarheid en prijs: in te vullen door Jorrit.]
Knoppen: Vraag een vrijblijvende demo aan · Bestel het Educatieplatform

## Assets uit de repo (webexport te maken)

| asset | bron | webversie |
|---|---|---|
| logo lock-up | references/logo-expeditie-mj.svg (+ PNG 2000/4000) | PNG 1600 px transparant + SVG |
| poster missie 1 (jeep) | posters/round-2/p1a-jeep-bubbles-v2.png of poster-1-jeep.png | WebP 1600 px |
| poster missie 2 (tent) | posters/round-3/p2-tent-think-first-final.png | WebP 1600 px |
| animatiefragment | projects/expeditie-mj-animatie2-v2/renders/expeditie-mediajungle-animatie-2-v2.mp4 (75,8 s) | knip 20–30 s, H.264 1280x720, + poster-still |
| thumbnail | renders/thumbnail-jeep.png | 1280x720 |

## Status 2026-09-09: gepubliceerd

Template `templates/page.expeditie-mediajungle.json` weggeschreven via de Admin API (client-credentials-app
"Mediajungle content", scopes write_themes/write_files/write_content; credentials in `~/.zshrc.local`).
Live op https://mediajungle.eu/pages/about-us?view=expeditie-mediajungle (eigen handle nog te kiezen door Jorrit).
Origineel in `backup/`, definitieve JSON in `page.expeditie-mediajungle.json`, webexports in `export/`.
Assets in Shopify Files: hero-expeditie-1920x730.jpg, logo-expeditie-mj-1600.png, poster-1-jeep.jpg,
poster-2-tent.jpg, poster-3-cocos.jpg (staande variant), animatie-missie1-cover.jpg, animatie-missie1-fragment.mp4 (33 s).
Let op theme-eigenaardigheid: sectie `section-video` toont niets als het veld "Video (YouTube embed)" leeg is,
ook met een Shopify-video; er staat daarom een HTML-comment in dat veld.

## Ronde 2 (2026-09-09, na feedback Jorrit)

- Hero: tweede knop (`btnOrangeOutline`) via custom_css in SimpleStamp + afgeronde outline gezet.
- Video vervangen door `animatie-missie1-teaser.mp4` (32 s, 9 segmenten uit animatie 2: eiland, storing, Boaz,
  mast, jungle, Jeep-beloning, slot). Filter in scratch `teaser.filter`; segmenten (s): 0-3.2, 5.9-9.9, 12.9-15.0,
  24.0-28.9, 36.8-40.4, 40.6-43.0, 47.0-50.0, 64.4-69.6, 69.6-73.4. Tent-scène volgt zodra animatie 3 bestaat.
- Postergalerij toont nu klaslokaal-mockups (`mockup-p1..3-classroom.jpg`, 16:9). Achtergronden gegenereerd met
  `google/nano-banana-2/text-to-image` (2 beelden, 2k, $0,24 totaal; goedgekeurd door Jorrit), posters erin
  gemonteerd met ffmpeg (schaduw, geen perspectief nodig: wand recht van voren). Bronnen + log in `export/mockup-bronnen/`.
- Ronde 2b: klasmockups vervangen door staande 3:4-versies (`mockup-p1..3-klas.jpg`) op geleefde klaswanden
  (`classroom-c.png` prikbord/slinger/kist, `classroom-d.png` okergele wand/plank/radiator; nano-banana-2 3:4 2k,
  $0,24, goedgekeurd). Poster op ~35% van de beeldhoogte, vrij aan de wand. Eerste liggende mockups (16:9) blijven als
  `mockup-p*-classroom.jpg` in export/ maar zijn niet meer in gebruik.

## Ronde 3 (2026-09-11, feedback Jorrit)

- Copy: doelgroep = "groep 1 tot en met 8" (nooit alleen 7/8); missiestappen kijk, ontdek, doe, verdien; geen beloningen noemen.
- Jeep-beloning in de teaser mag blijven (Jorrit 2026-09-11).
- Klaslokaal-mockups (AI én Pexels-stock) afgekeurd: AI "druipt eraf" / te kleuterachtig, stock lijkt niet op een NL basisschool.
  Pexels-zoektocht (125 treffers) staat in scratch; licentie gecheckt: commercieel gebruik + bewerking toegestaan, credit niet verplicht.
- Definitief: `mockup-p1..3-wand.jpg` — volledige poster close-up op kale warme wand (Pillow, `wallmock.py` in scratch; wand
  procedureel, geen foto), galerij 3:4. Pexels-key staat nu in .env (PEXELS_API_KEY) voor later gebruik.

## Ronde 4 (2026-09-15): feedback Robert verwerkt — zie tekstvoorstel-r4.md
Gepubliceerd: hero zonder verhaal, "Wat is" met Femke/Boaz-introductie en nieuwe bullets, kijk-ontdek-doe-verdien + themavoorbeelden,
posterblok = opgemaakte definitieve posters missie 1/2/4 (`mockup-missie-{1,2,4}-wand.jpg`, geen bijschriften), leerkrachtblok met
digitale/fysieke werkvormen, thuis-formulering, start groep 7-8 + rest vanaf 2027-2028. Hulpscripts nu duurzaam in `scripts/`.

## Ronde 5 (2026-09-15): slop-ronde + nieuwe posters
- Hero-subkop: "Digitale geletterdheid als ontdekkingstocht voor de basisschool. Femke en Boaz nemen je klas mee in tien missies."
- Blok 2 bullets ongewijzigd (Jorrit), Femke/Boaz-uitleg blijft. Blok 3: "introduceert het thema", themazin ingekort, extra demo-knop.
- Leerkracht: SLO-bullet i.p.v. herhaling, slopzin "ben je er klaar voor" weg. Slotblok: demo-vraag, platformzin met tekstlink bóven de knop.
- Galerij: vier A2-chatgesprekposters (missie 1-4) op wandmockup (`mockup-missie-{1..4}-a2-wand.jpg`), 4 kolommen (2 op mobiel), kop "Elke missie een poster voor in de klas".
  Missie 4 A2 gerenderd via `build_posters_a2.py`. Bronnen: `projects/expeditie-mediajungle-posters/renders/a2/*-150dpi.png`.

## Ronde 6 (2026-09-15): eigen URL, home, platform
- Bestaande (ongepubliceerde) pagina `expeditie-mediajungle` (aangemaakt 2026-09-09) gepubliceerd met templateSuffix
  `expeditie-mediajungle` → **https://mediajungle.eu/pages/expeditie-mediajungle** (oude ?view=-URL werkt ook nog).
- Home (`config/settings_data.json`, back-up in backup/): slide "Nieuw! Startpakket" (image_C9Dxhw) verwijderd; nieuwe slide
  `image_expeditie` op positie 1 (hero-still, "Nieuw: Expeditie Mediajungle", knop "Bekijk de expeditie").
- Educatieplatform (`templates/page.platform.json`, back-up in backup/): 4e onderdeel "Expeditie Mediajungle" in de opsomming,
  nieuw blok "Nieuw: Expeditie Mediajungle" met jeep-still, en "Offerte aanvragen" → "Vraag een vrijblijvende demo aan" (ClickUp-formulier).
- Galerij: poster 3 (hangmat) verwijderd op verzoek; drie kaarten (missie 1, 2, 4).
- Menu: thema rendert geen geneste menu-items; bewust niet aangepast.

## Ronde 7 (2026-09-16): trailer
- Videosectie toont nu `expeditie-trailer-v3.mp4` (59 s; animatie 2 + LinkedIn-kaarttour + eindkaart "Gratis onderdeel van het
  Mediajungle Educatieplatform"), kop "Bekijk de trailer". Bouw: `projects/expeditie-mediajungle-trailer/build_trailer.py`.
  Kaartbron is 640p (LinkedIn); originele schermopname nog inwisselen als Jorrit die aanlevert.

## Zorgeditie (2026-09-25): preview gebouwd, nog niet gepubliceerd
- Sjabloon `templates/page.expeditie-mediajungle-zorg.json` staat in het thema, nog aan geen pagina gekoppeld.
  Preview: https://mediajungle.eu/pages/about-us?view=expeditie-mediajungle-zorg . Bron + builder: `zorg/`.
- Hergebruikt: hero-still, logo, trailer v3 (bevat geen schoolzin, gecontroleerd via transcript), posters missie 1/2/4.
- Nieuw in Shopify Files: `handreiking-mediawijsheid-lvb-zorg.pdf`, `logo-asvz.png`. Ambiq en De Lovie bewust nog niet getoond.
- Demo: zelfde ClickUp-formulier (heeft Sector = Zorg). Beschikbaarheid 1 oktober niet in de hero (Jorrit).
- Nog te doen na "ja, publiceer": pagina /pages/expeditie-mediajungle-zorg publiceren; links vanaf zorgblokken op home en platform,
  trainingenpagina (opleiding Aandachtsfunctionaris) en één regel op de onderwijspagina.
- **Gepubliceerd 2026-09-25:** https://mediajungle.eu/pages/expeditie-mediajungle-zorg . Ingangen: kaart "Zorg en ondersteuning" op home
  (settings_data, blok item_UbetjU) en platform (item_TVRVYf), opleiding Aandachtsfunctionaris op /pages/workshops-trainingen
  ("Daarmee kun je ook direct starten met…"), slotblok onderwijspagina ("Werk je in de zorg?"). Back-ups in backup/, gepushte versies in live/.
  Partnerkop: "Deze organisaties zijn al op expeditie" (alleen ASVZ tot Ambiq/De Lovie akkoord).
- 2026-09-25: kaart 'In de klas en BSO' (home, item_igQwJ7) en 'Onderwijs' (platform, item_pdE8Ah) linken naar /pages/expeditie-mediajungle.

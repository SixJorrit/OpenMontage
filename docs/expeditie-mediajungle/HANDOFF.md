# HANDOFF — stand na animatie 3, 2026-10-12

**Animatie 3 (missie 2, de tent) is af**: `projects/expeditie-mj-animatie3/renders/expeditie-mediajungle-animatie-3.mp4`
(1280x720/24, ~1:59, **zonder muziek** — besluit Jorrit). Intro 0A is nog het afgeknipte eilandshot uit animatie 2 en
wordt later vervangen. Volledige geschiedenis, kosten en elke feedbackronde: `projects/expeditie-mj-animatie3/artifacts/review-notes.md`.
Animatie 2 v2 (2026-08-28) staat in `projects/expeditie-mj-animatie2-v2/`; die gebruikt nog de oude dialoogroute en
v3-stemmen (Boaz moet daar later opnieuw).

Deze route **vervangt** de dialoogroute A2 van animatie 2 (warp/ratio-gates). Lees providerkennis.md §7 voor de metingen.

## De route (animatie 3, bewezen)

1. **Workspace**: nieuw project via `init_project` + Backlot. Style bible ongewijzigd; canon-vectorart eerst promoveren
   naar 3D via `google/nano-banana-2/edit` ($0,12). Platen controleren op elementen die het verhaal verklappen
   (Tara-plaat bevatte de beloningstent → tent eruit geëdit).
2. **Overleg vóór geld**: script → vragen over locaties/staging → compact overzicht per shot (wat gebeurt er, wie waar,
   camera, audio) → Jorrits akkoord → **expliciete "ga" per betaalde ronde** met kosten vooraf. Plafond per ronde.
3. **Stemmen**: `eleven_v4` via de API (`gen_v4.py`), casting **Femke = Ruth** (YUdpWWny7k5yb4QCeweX), **Boaz = Bram**
   (2GJZCZIWrWiGFDntCFaz); stab 0,30 / sim 0,75 / speed 1,05 + acteertag per regel. 3 takes per regel, Azure-meter
   (≥90, laagste woord ≥60) — Jorrit kiest (animatie 3: Femke take 2, Boaz take 1). Filmaudio: `build_v4_film.py`
   (44,1k, één vaste gain per spreker, zinsdelen geknipt in de woordpauzes). Nooit loudnorm per regel, nooit 16k-referenties als filmaudio.
4. **Video**: seedance-2.5 reference-to-video via Atlas, **eerst `draft: true` (480p, $0,134/s)**, controle, Jorrits akkoord,
   dan `draft-complete` (1080p, $0,263/s; zelfde beweging, gemeten). v4-regel als referentie-audio bij dialoogshots.
   Regeltekst nooit in de prompt. **Cabineshots altijd frontaal door de voorruit** (Femke frame-rechts aan het stuur,
   Boaz frame-links); zijaanzichten met beide inzittenden zetten Boaz achterin (de jeep-referenties tonen een achterbank).
   SEATING LOCK in elke cabineprompt. **Eigen gate vóór elke draft**: ingezoomd op stuur, zitplaatsen, achtergrond.
5. **Lipsync**: Sync 3 (`sync/lipsync-v3`, Atlas, $0,22/s) op een **uitsnede van alleen het gezicht van de spreker**
   (1024px, alleen het spreekvenster ±0,5 s), mond terug met het *union*-masker (vaste hoofd-relatieve vorm incl. kaak/kin,
   bovengrens net onder de neus), Lanczos-schaling: `crop_lipsync.py prep|submit|paste`. Gezichtsankers per shot handmatig
   (meerdere ankers voor draaiende hoofden). **Veed niet gebruiken** (ook niet als tussenstap) — besluit Jorrit.
6. **Sync**: Sync 3 houdt het mondritme van Seedance' eigen kloonstem aan. Meet daarom **op geluid**: woordtijden van de
   kloonstem (Demucs-vocals) vs. de v4-regel (Azure). Leg de v4-regel per woordgroep op dat ritme (`retime_to_clone.py`:
   spraak ±10% tempo, pauzes vrij), daarna Sync 3 op de bijgestelde audio. Doel: mediaan ≤0,12 s per woord.
7. **Audio**: Seedance-clipaudio is de basis (ook onder dialoog): kloonstem eruit met Demucs (`separate_clip_audio.py`,
   lokaal, gratis), achtergrond op eenheidsgain; eigen sfeerbanden/SFX alleen als dunne laag. Elke bron op een gemeten
   doelniveau (LVL in `compose_prep_a3.py`); master = statische gain naar -16 LUFS + limiter -1,5 dBTP. Geen muziek
   tenzij Jorrit erom vraagt (animatie 3: "voegt niet zoveel toe").
8. **Montage**: Remotion `ExpeditieMJ` met `transitionIn` per shot. Overgangen = **zachte schaduwwipe** (variant B,
   `bandWipes.tsx`, look "shadow", 70 px), klok-wipe voor de beloning. **Nooit praten tijdens een overgang**: compose
   kort de wipe in vóór een lipsyncshot, schuift regels zonder lipsync naar ná de wipe, en houdt het laatste beeld vast
   tot de regel uit is. Beloningsburst pas als de klok-wipe rond is.
9. **Drafts**: `render_draft.py <nr> --lowres` (360p, ~90 s) met **shotnummers in beeld**; eindversie zonder `--lowres`.

## Reviewritme met Jorrit

Draft → feedback per shotnummer in één ronde → analyse en voorstel met kosten → "ga" → fix → nieuwe draft.
Gratis eerst. Altijd met de échte filmaudio. Meet zelf vóór oplevering (bestuurder, sync op geluid, overgangen).

## Werkscripts (in projects/expeditie-mj-animatie3/, kopie in docs/expeditie-mediajungle/scripts/animatie3/)

`gen_v4.py`, `build_v4_film.py` (stemmen) · `retake4.py`, `complete4.py` (Seedance draft → 1080p) ·
`separate_clip_audio.py` (Demucs) · `crop_lipsync.py`, `run_lipsync_batch.sh` (Sync 3) · `retime_to_clone.py` (sync) ·
`compose_prep_a3.py` (A3_FILM, A3_LIPSYNC, A3_VO_SYNC, TRANSITIONS, LVL) · `render_draft.py`.
Let op: macOS-zsh splitst `$var` niet in woorden — lussen met meerdere argumenten onder `bash -c` draaien.

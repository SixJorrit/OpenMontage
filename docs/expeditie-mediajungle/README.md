# Expeditie Mediajungle — productiedossier

Repo-getrackte kopie van het kennisdossier voor de animatiereeks Expeditie Mediajungle,
vastgesteld in de troubleshoot-sessie van 2026-08-21. De werkkopie leeft in
`projects/expeditie-mediajungle-animaties/` (gitignored, alleen op de productiemachine);
**deze map is de duurzame kopie voor alle toekomstige animaties.** Bij wijzigingen in de
werkkopie: hierheen synchroniseren en committen naar de fork (`SixJorrit/OpenMontage`) —
nooit naar upstream pushen.

| bestand | wat |
|---|---|
| `TROUBLESHOOT-FINDINGS.md` | het volledige routedossier: alle zes vragen, metingen, besluiten en protocollen |
| `providerkennis.md` | duurzame providerkennis (Seedance/Atlas-tarieven en -gedrag, Kling-legacy, ElevenLabs-stemroute, Azure-verificatiemeter, continuïteitsprotocol) |
| `HANDOFF.md` | productiestaat van animatie 2 (de pilot) op het moment van afronden |
| `decision_log.json` | het besluitenlog van de pilot, 39 entries, incl. d-034 t/m d-039 (de route voor de reeks) |
| `scripts/` | de herbruikbare testscripts: modelvergelijking, beoordeling (meter + frames), en `atlascost.py` (echte Atlas-factuur uitlezen) |

## De route in vijf regels (details in de findings)

1. **Spraak**: ElevenLabs `eleven_v3` + emotietag per regel; casting verteller Matanga =
   Hans Claesen, Femke = Ruth, Boaz = Bram. Meter: Azure Pronunciation Assessment
   (northeurope, gratis F0) tegen de letterlijke regel; drempel <90/woord<60 → retake.
   Nooit whisper voor woordtrouw.
2. **Dialoogshots** (d-039): mode B met de v3-regel als referentie-audio, kloonstem weg,
   v3-regel = filmaudio; bij ratio buiten 0,86–1,16 een andere/versnelde v3-take, niet het
   beeld hertimen.
3. **Videomodel** (d-038): seedance-2.5, geen modellenmix. Reken met de gemeten $0,373/s
   (720p24), nooit met `model_catalog`/`estimate_cost`.
4. **Audio-mix**: clipaudio nooit in de mix; ambiance/SFX los genereren via `music_gen`
   (d-036). Muziek pas op het allerlaatst (d-037).
5. **Continuïteit**: CONTINUITY LOCK (scène-blokkeringscontract in elke shotprompt) +
   master-take met punch-ins voor scènes met personages samen in beeld + frame-chaining
   voor doorlopende actie.

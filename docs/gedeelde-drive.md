# Werken met de gedeelde drive

De code staat in git; eindproducten (projectmappen, renders, posters, exports,
referentiebeeld) staan op de gedeelde Google Drive van Mediajungle:

```
Mediajungle Projecten / 03. Projecten / OpenMontage /
├── projects/   # werkmappen van de pipeline (checkpoints, assets, renders)
└── media/      # losse eindproducten en bronbeeld buiten een project (o.a. fonts/)
```

In de repo zijn `projects` en `media` symlinks naar die mappen. Iedereen heeft
de drive op een ander pad (het pad bevat je eigen e-mailadres), dus die links
maak je zelf aan. Daarna verwijst alles naar dezelfde relatieve paden.

## Eenmalig instellen

1. Installeer **Google Drive for desktop** en log in met je Mediajungle-account.
2. Zet in Finder de map `OpenMontage` op **Beschikbaar offline** (rechtermuisknop).
   Anders haalt Drive bestanden pas op als een render ze nodig heeft; dat is traag
   en kan halverwege mislukken.
3. Clone de repo (zonder de oude grote bestanden uit de historie):

   ```bash
   git clone --filter=blob:limit=1m https://github.com/SixJorrit/OpenMontage.git
   ```

4. Maak de links, vanuit de repo-map:

   ```bash
   make shared-drive
   ```

   Vindt het script de drive niet (bijvoorbeeld bij een andere taalinstelling),
   zet dan in `.env`:

   ```
   OPENMONTAGE_SHARED_DIR=/Users/<jij>/Library/CloudStorage/GoogleDrive-<jij>@mediajungle.eu/Shared drives/Mediajungle Projecten/03. Projecten/OpenMontage
   ```

   Controleren: `python3 scripts/link_shared_drive.py --status`.

5. Installeer de fonts uit `media/fonts/` (dubbelklikken) als je zelf posters of
   de trailer bouwt.

## Afspraken

- **Eén persoon per project tegelijk.** Werken twee mensen tegelijk in dezelfde
  projectmap, dan maakt Drive dubbele versies van checkpoints en loopt de
  pipeline in de war. Spreek af wie een project "heeft".
- **Alleen relatieve paden.** Schrijf `projects/<id>/...` of `media/...`, nooit
  `/Users/<naam>/...`. Scripts draai je vanuit de repo-map.
- **Vóór je een project overdraagt:** `make check-paths`. Staan er nog absolute
  paden in, dan herschrijft `make fix-paths` wat kan. Wat overblijft wijst naar
  bronmateriaal buiten repo en drive (bijvoorbeeld een Dropbox) en moet je zelf
  naar `media/` verhuizen.
- **Geen eindproducten in git.** Ook niet onder `docs/`.

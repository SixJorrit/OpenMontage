# OpenMontage installeren (nieuwe collega)

Drie delen: wat Jorrit vooraf regelt, de opdracht die je in Claude Code plakt,
en hoe je daarna zelf de API-sleutels invult.

## 1. Vooraf (Jorrit)

- **Toegang tot de gedeelde drive** `Mediajungle Projecten` (Google Drive).
- **Sleutels delen via een wachtwoordmanager**, niet via mail, WhatsApp of Slack.
  Nodig: ElevenLabs, Atlas Cloud en Azure Speech. Liefst een eigen sleutel
  per persoon waar de dienst dat toelaat (ElevenLabs, Atlas Cloud; Azure heeft
  per resource twee sleutels, geef de tweede). Dan kun je er één intrekken zonder de ander te raken en zie je wie
  wat verbruikt.
- **Schrijfrechten op GitHub** (collaborator op `SixJorrit/OpenMontage`) als de
  collega zelf wijzigingen moet kunnen pushen. Clonen kan zonder.

## 2. Opdracht voor Claude Code

Open Claude Code in je thuismap en plak dit:

```text
Help me OpenMontage op mijn Mac te installeren, de versie van Mediajungle. Werk stap voor stap, controleer elke stap en stop met uitleg als iets mislukt.

Belangrijk: vraag mij nooit om API-sleutels in deze chat te plakken, en lees, toon of kopieer het bestand .env nooit (ook niet met cat, grep of een script). Sleutels vul ik zelf in.

1. Controleer wat er al is: Homebrew, git, python3 (3.10 of nieuwer), nvm met Node 22, ffmpeg. Ontbreekt Homebrew, stop dan en leg uit hoe ik het zelf installeer (daar is mijn wachtwoord voor nodig).
   - Node: installeer Node 22 via nvm en maak het de standaard (nvm install 22, nvm alias default 22). Ontbreekt nvm, installeer dat eerst.
   - ffmpeg: we hebben de volledige versie nodig: brew install ffmpeg-full. Staat er al een gewone ffmpeg, doe dan brew unlink ffmpeg en brew link --force ffmpeg-full. Controleer dat ffmpeg -filters het filter "subtitles" toont.
   - Staat git user.name of user.email nog niet ingesteld, vraag me dan mijn naam en e-mailadres en stel ze in.
2. Controleer dat Google Drive for desktop draait en dat deze map bestaat: ~/Library/CloudStorage/GoogleDrive-*/Shared drives/Mediajungle Projecten/03. Projecten/OpenMontage (op een Nederlandstalige Mac kan "Shared drives" "Gedeelde drives" heten). Bestaat hij niet, stop dan: dan heb ik nog geen toegang.
3. Clone de repo in ~/dev (maak die map als hij er niet is):
   git clone --filter=blob:limit=1m https://github.com/SixJorrit/OpenMontage.git
   Ga in ~/dev/OpenMontage staan en controleer dat de branch "mediajungle" is.
4. Draai make setup.
5. Draai make shared-drive en daarna python3 scripts/link_shared_drive.py --status. De links projects en media moeten allebei "ok" zijn.
6. Kopieer de fonts: cp media/fonts/*.ttf ~/Library/Fonts/
7. Draai make test en vat de uitkomst samen.
8. Lees docs/gedeelde-drive.md en vat de afspraken voor mij samen in een paar zinnen.
9. Vertel me tot slot welke handmatige stappen ik nog moet doen: de map OpenMontage in Finder op "Beschikbaar offline" zetten, en de API-sleutels invullen volgens deel 3 van docs/nieuwe-collega-setup.md. Vul die sleutels niet zelf in.
```

## 3. API-sleutels invullen (zelf doen)

De sleutels komen in het bestand `.env` in de repo. Dat bestand gaat nooit naar
GitHub. Gebruik hiervoor het script `scripts/set_env_key.py`: het leest de
sleutel van je klembord, schrijft hem in `.env` en wist daarna het klembord.
De sleutel verschijnt niet op je scherm en niet in de chat.

Per sleutel:

1. Kopieer de sleutel uit de wachtwoordmanager.
2. Typ in Claude Code, **met het uitroepteken vooraan**, bijvoorbeeld:

   ```text
   ! python3 scripts/set_env_key.py ELEVENLABS_API_KEY
   ```

   Het uitroepteken laat de opdracht direct in de terminal draaien; Claude doet
   er zelf niets mee. Je ziet alleen iets als
   `ELEVENLABS_API_KEY toegevoegd in .env (51 tekens). Klembord gewist.`

Doe dat voor elk van deze sleutels (de naam steeds na `set_env_key.py`):

| Naam | Waarvoor |
|---|---|
| `ATLASCLOUD_API_KEY` | video en beeld via Atlas Cloud (Seedance, Sync, nano-banana, Wan) |
| `ELEVENLABS_API_KEY` | stemmen |
| `AZURE_SPEECH_KEY` | uitspraakcontrole (Azure Pronunciation Assessment) |

Andere sleutels uit `.env.example` zijn voor deze productie niet nodig.

Deze instelling is niet geheim; die typ je er gewoon achter:

```text
! python3 scripts/set_env_key.py AZURE_SPEECH_REGION northeurope
```

Controleren wat er is ingevuld (alleen de namen, nooit de waarden):

```text
! python3 scripts/set_env_key.py --status
```

Vraag Claude daarna: *"Draai make preflight en vertel me welke providers nu
beschikbaar zijn."*

**Werk je liever in een gewone Terminal** (zonder Claude): laat het uitroepteken
weg. Het script vraagt de sleutel dan zelf, zonder hem te tonen.

**Let op:** betaalde diensten (Atlas, ElevenLabs) kosten geld per
aanroep. Laat Claude vóór elke betaalde ronde de verwachte kosten noemen en
geef pas daarna akkoord.

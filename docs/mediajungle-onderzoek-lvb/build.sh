#!/bin/zsh
# Rendert de opgegeven HTML-bestanden (zonder .html) naar PDF (A4) en PNG-previews (150 dpi).
# Afbeeldingen uit assets/ worden bij het bouwen ingesloten, zodat de PDF altijd compleet is.
# Uitvoer gaat naar de gedeelde drive (media/, zie docs/gedeelde-drive.md), niet naar git.
set -e
cd "$(dirname "$0")"
OUT="$PWD/../../media/mediajungle-onderzoek-lvb"
mkdir -p "$OUT"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
mkdir -p .build
for f in ${@:-infographic factsheet infographic-implementatie factsheet-implementatie dias-lvb dias-implementatie}; do
  [ -f "$f.html" ] || continue
  python3 - "$f" <<'PY'
import base64, re, sys
f = sys.argv[1]
s = open(f + ".html").read()
s = re.sub(r'src="(assets/[^"]+\.png)"',
           lambda m: 'src="data:image/png;base64,' + base64.b64encode(open(m.group(1), "rb").read()).decode() + '"', s)
s = s.replace('href="slides.css"', 'href="../slides.css"')
open(".build/" + f + ".html", "w").write(s)
PY
  "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=8000 \
    --run-all-compositor-stages-before-draw --print-to-pdf="$OUT/$f.pdf" "file://$PWD/.build/$f.html" 2>/dev/null
  if [[ $f == dias-* ]]; then
    # dia's: losse PNG's in 4K (3840x2160) om in een presentatie te plaatsen
    pdftoppm -png -scale-to-x 3840 -scale-to-y 2160 "$OUT/$f.pdf" "$OUT/$f"
  else
    pdftoppm -r 150 -png "$OUT/$f.pdf" "$OUT/preview-$f"
  fi
done

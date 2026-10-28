#!/bin/zsh
# render.sh in.svg out.png breedte   -> transparante PNG via Chrome headless
set -e
IN="$1"; OUT="$2"; W="$3"
VB=$(grep -o 'viewBox="[^"]*"' "$IN" | head -1 | sed 's/viewBox="//;s/"//')
H=$(python3 -c "import sys; x,y,w,h=map(float,'$VB'.split()); print(round($W*h/w))")
HTML="${OUT%.png}.html"
printf '<!doctype html><html><head><style>html,body{margin:0;padding:0;background:transparent;overflow:hidden}img{display:block;width:%spx;height:%spx}</style></head><body><img src="file://%s"></body></html>' "$W" "$H" "$IN" > "$HTML"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --default-background-color=00000000 --window-size="$W,$H" --screenshot="$OUT" "file://$HTML" >/dev/null 2>&1
rm -f "$HTML"; echo "$OUT ${W}x${H}"

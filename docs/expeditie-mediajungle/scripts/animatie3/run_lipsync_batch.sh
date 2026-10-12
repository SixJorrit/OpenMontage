#!/bin/bash
# Sync 3 uitsnede-lipsync voor een lijst shots, max 4 tegelijk; daarna terugplakken met het union-masker.
set -a; . ./.env; set +a
one() {
  s=$1
  PYTHONPATH=. .venv/bin/python -u projects/expeditie-mj-animatie3/crop_lipsync.py $s submit sync3 2>&1 | grep -E "ingediend|klaar|Error|Traceback" | sed "s/^/[$s] /"
  PYTHONPATH=. .venv/bin/python projects/expeditie-mj-animatie3/crop_lipsync.py $s paste sync3 2>&1 | tail -1 | sed "s/^/[$s] /"
}
n=0
for s in "$@"; do one $s & n=$((n+1)); if [ $n -ge 4 ]; then wait -n; n=$((n-1)); fi; done
wait; echo "ALLES KLAAR"

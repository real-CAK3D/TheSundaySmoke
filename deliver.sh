#!/usr/bin/env bash
# After Ganja files The Sunday Smoke: draw the funnies, print the issue, rebuild the pages and ring the Newsstand's bell.
set -u
D="$HOME/.hermes/garden/sunday-smoke"; PY="$HOME/.hermes/hermes-agent/venv/bin/python"; T=$(TZ=America/New_York date +%F)
F="$D/drafts/$T.json"; [ -f "$F" ] || { echo "no Sunday Smoke draft for $T"; exit 0; }
"$PY" "$D/draw_funnies.py" "$F"
cd "$D" && "$PY" "$D/render_sunday.py" "$F" || exit 1
HEAD=$("$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["cover"]["title"])' "$F" 2>/dev/null)
"$PY" "$HOME/.hermes/garden/newsstand/notify.py" "💨 The Sunday Smoke is here" "${HEAD:-The week, rolled up} — plus the funnies" "/sunday-smoke/"

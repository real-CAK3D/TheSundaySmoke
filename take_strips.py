#!/usr/bin/env python3
"""Take the day's comic strips from Ganja's Double Wide draft, draw them, and keep them for Sunday.

Usage: take_strips.py ~/.hermes/garden/doublewide/drafts/<date>.json
Writes strips/<date>.json (the scripts + drawn image paths); The Sunday Smoke prints the whole week's strips on Sunday."""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
ed = json.load(open(sys.argv[1]))
fun = ed.get("funnies") or {}
if not fun.get("strips"):
    sys.exit(print("no strips today") or 0)
os.makedirs(os.path.join(ROOT, "strips"), exist_ok=True)
out = os.path.join(ROOT, "strips", ed["date"] + ".json")
if not os.path.exists(out):
    json.dump({"date": ed["date"], "funnies": fun}, open(out, "w"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, os.path.join(ROOT, "draw_funnies.py"), out], check=False)
print("strips kept for Sunday:", out)

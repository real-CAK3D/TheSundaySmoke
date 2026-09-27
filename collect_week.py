#!/usr/bin/env python3
"""Input for THE SUNDAY SMOKE: the whole week in one place (printed for Ganja by the job's script).

Reads the last 7 Double Wide drafts, the collector's data files, B.I.G's catalogs, approved-job follow-ups and the
calendar facts; saves the 7-day forecast for the paper's weather box.
"""
import datetime as dt, glob, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))           # The Sunday Smoke
DW = os.path.expanduser("~/.hermes/garden/doublewide")       # its source: the week's Double Wides
sys.path.insert(0, DW)
import collect_inputs as ci   # noqa: E402  (The Double Wide's collector: weather, calendar, moon)

SITE, DW_SITE, H, TZ = os.path.join(ROOT, "site"), os.path.join(DW, "site"), ci.H, ci.TZ


def load(p):
    try:
        return json.load(open(p))
    except Exception:
        return {}


def week_weather(today):
    os.makedirs(os.path.join(SITE, "data"), exist_ok=True)
    cfg = json.load(open(f"{H}/garden/homie/lewiston_weather_ac_config.json"))["location"]
    fc = ci.get_json(f"https://api.weather.gov/gridpoints/{cfg['nws_grid']}/forecast")["properties"]["periods"]
    days = []
    for i, p in enumerate(fc):
        if p.get("isDaytime") or (i == 0 and not days):
            nxt = fc[i + 1] if i + 1 < len(fc) and not fc[i + 1].get("isDaytime") else None
            days.append({"name": p["name"], "high": p["temperature"], "low": nxt["temperature"] if nxt else None, "short": p["shortForecast"]})
    json.dump({"days": days[:7]}, open(os.path.join(SITE, "data", "weather-week-%s.json" % today), "w"))
    return days[:7]


def main():
    now = dt.datetime.now(TZ)
    today = now.date()
    days = [(today - dt.timedelta(days=i)).isoformat() for i in range(7, 0, -1)] + [today.isoformat()]
    print("THE SUNDAY SMOKE — edition date %s (covering %s to %s)\n" % (today, days[0], days[-1]))
    try:
        wk = week_weather(today.isoformat())
        print("WEATHER, NEXT 7 DAYS (printed automatically): " + "; ".join("%s %s°/%s° %s" % (d["name"], d["high"], d["low"], d["short"]) for d in wk))
    except Exception as e:
        print("WEATHER: unavailable (%s)" % type(e).__name__)
    print("PORTRAITS available (agent names): " + ", ".join(ci.portraits()))

    print("\n=== THE WEEK'S DOUBLE WIDES ===")
    for d in days:
        ed = load(os.path.join(DW, "drafts", d + ".json"))
        if not ed:
            continue
        h = ed.get("headline") or {}
        print("\n--- %s: HEADLINE: %s — %s" % (d, h.get("title"), h.get("dek") or ""))
        for s in ed.get("sections") or []:
            for st in s.get("stories") or []:
                print("  [%s] %s (%s): %s" % (s.get("name"), st.get("title"), st.get("agent"), str(st.get("body") or "")[:260].replace("\n", " ")))
        for b in ed.get("police_blotter") or []:
            print("  BLOTTER %s %s: %s" % (b.get("time"), b.get("agent"), b.get("text")))
        for j in ed.get("job_listings") or []:
            print("  JOB LISTING: %s — %s" % (j.get("title"), j.get("ask")))
        for c in ed.get("coming_up") or []:
            print("  COMING UP (as of %s): %s — %s" % (d, c.get("when"), c.get("what")))

    print("\n=== FOLLOW-UPS ON APPROVED JOBS ===")
    for d in days:
        for k, v in load(os.path.join(DW, "jobs", d + ".json")).items():
            if v.get("status") in ("approved", "done", "clipped"):
                print("- %s: %s — %s %s" % (d, v.get("title"), v.get("status"), v.get("result") or ""))

    print("\n=== TOKENS & PAY (the Weekly Ledger prints automatically; quote a highlight) ===")
    total, agents = 0, {}
    for d in days[:-1]:
        u = load(os.path.join(DW_SITE, "data", "usage-%s.json" % d))
        total += u.get("total") or 0
        for k, v in (u.get("by_agent") or {}).items():
            agents[k] = agents.get(k, 0) + v
    print("Tokens this week: %.1fM. Top agents: %s" % (total / 1e6, ", ".join("%s %.0fk" % (k, v / 1000) for k, v in sorted(agents.items(), key=lambda kv: -kv[1])[:6])))
    pays = sorted(glob.glob(os.path.join(DW_SITE, "data", "payroll-20*.json")))
    if pays:
        p = load(pays[-1])
        print("Payroll week to date: " + "; ".join("%s $%.2f" % (r["agent"], r.get("week", 0)) for r in p.get("rows") or []))

    print("\n=== B.I.G's CATALOGS THIS WEEK ===")
    for d in days:
        m = load(os.path.join(DW_SITE, "data", "market-%s.json" % d))
        for it in m.get("items") or []:
            print("- %s %s: %s (%s)" % (d, it.get("item_no"), it.get("title"), it.get("price")))

    print("\n=== CALENDAR FACTS (use for 'week_ahead.calendar') ===")
    for f in ci.coming_up_facts():
        print("- " + f)
    try:
        keys = subprocess.run([f"{H}/hermes-agent/venv/bin/python", f"{H}/scripts/hermes_agent_token_watchdog.py", "--summary"],
                              capture_output=True, text=True, timeout=120).stdout.strip()
        print("\nLOGINS & KEYS:\n" + keys)
    except Exception:
        pass
    try:
        name, illum, nf, nn = ci._moon(now)
        print("SKY: moon is %s (%d%% lit); next full moon %s, next new moon %s" % (name, illum, nf.strftime("%a %b %-d"), nn.strftime("%a %b %-d")))
    except Exception:
        pass

    last = sorted(glob.glob(os.path.join(ROOT, "drafts", "20*.json")))
    if last:
        prev = load(last[-1])
        print("\nLAST SUNDAY'S FUNNIES (don't repeat these gags): " + "; ".join(s.get("title", "") for s in (prev.get("funnies") or {}).get("strips") or []))
    r = subprocess.run(["ssh", "-n", "-o", "BatchMode=yes", "cak3d",
                        "tail -c 6000 '%s/The Gardiner/Handoffs/Daily Recaps/%s.md' 2>/dev/null" % (ci.VAULT, (today - dt.timedelta(days=1)).isoformat())],
                       capture_output=True, text=True, timeout=60)
    print("\n=== THE GARDINER'S LATEST DAILY RECAP ===\n" + (r.stdout.strip() or "(none)"))


if __name__ == "__main__":
    main()

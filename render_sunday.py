#!/usr/bin/env python3
"""Render THE SUNDAY SMOKE — the Garden's weekly paper (Sundays): the week in review, the week ahead,
things to do around town, the weekly ledger and THE FUNNIES.

Usage: render_sunday.py drafts/<date>.json   -> site/issues/<date>.html, then build_sunday.py refreshes home + archives.
Uses its own copy of The Double Wide's flipbook (flipbook.py) with its own masthead and stylesheet.
"""
import datetime as dt, glob, json, os, sys

import flipbook as fb
from flipbook import e, mug, para, story, page, strips_block, SEAL, back_codes

fb.CSS_FILE = "sunday-smoke.css"
ROOT = fb.ROOT
SITE = fb.SITE
DW_DATA = os.path.expanduser("~/.hermes/garden/doublewide/site/data")   # the week's numbers come from The Double Wide


def load(path):
    try:
        return json.load(open(path))
    except Exception:
        return {}


def cover(no, d, teaser):
    return page("The Sunday Smoke", (
        '<div class="gum"><span>SUNDAY EDITION · ALL THE WEEK FIT TO READ</span></div>'
        '<div class="pc-top"><a class="seal" href="/" aria-label="Back to The Corner Chronicle" title="Back to The Corner Chronicle">%s</a><div class="ear">No. %s<br>%s<br><b>%s</b><br>%s</div></div>'
        '<div class="flag"><div class="est">EST. 2026 · THE GARDEN · LEWISTON, ME</div><h1>The<br>Sunday Smoke</h1><div class="motto">The whole week, rolled up</div></div>'
        '<div class="pc-band"><span>WEEK IN REVIEW</span><span>THE WEEK&#39;S FUNNIES</span><span>AROUND TOWN</span></div>'
        '<div class="pc-teaser"><div class="kicker">This week\'s big story</div><b>%s</b></div>'
        '<div class="pc-open">Unfold the paper ›</div>') % (SEAL, e(no), d.strftime("%a"), d.strftime("%b %-d"), d.strftime("%Y"), e(teaser)),
        " hardcover")


def back(date, no):
    return page("Back Page", (
        '<div class="gum"><span>SUNDAY EDITION · THE GARDEN</span></div>'
        '<div class="pb-body"><a class="seal" href="/" aria-label="Back to The Corner Chronicle" title="Back to The Corner Chronicle">%s</a><h2 class="pb-title">The Sunday Smoke</h2>'
        '<p>Put together by Ganja from the week\'s Double Wides.<br>The funnies: every strip drawn this week, all in one place.</p>'
        '%s<p class="pb-code">%s · No. %s</p><p><a href="../funnies.html">The funnies archive ›</a> · <a href="../archive.html">Back issues ›</a></p></div>')
        % (SEAL, back_codes("https://github.com/real-CAK3D/TheSundaySmoke", "TheSundaySmoke"), date, e(no)), " hardcover back")


def week_ledger(date):
    """Tokens per day for the last 7 days + this week's payroll, from The Double Wide's data files."""
    d = dt.date.fromisoformat(date)
    days = [(d - dt.timedelta(days=i)).isoformat() for i in range(7, 0, -1)]
    tot, agents = [], {}
    for x in days:
        u = load(os.path.join(DW_DATA, "usage-%s.json" % x))
        tot.append((x, u.get("total") or 0))
        for k, v in (u.get("by_agent") or {}).items():
            agents[k] = agents.get(k, 0) + v
    top = max([v for _, v in tot] + [1])
    bars = "".join('<div class="wk-bar"><span style="height:%d%%"></span><b>%s</b><i>%s</i></div>'
                   % (max(2, round(v / top * 100)) if v else 0, fb._k(v), dt.date.fromisoformat(x).strftime("%a")) for x, v in tot)
    ag = sorted(agents.items(), key=lambda kv: -kv[1])[:10]
    mx = ag[0][1] if ag else 1
    agent_rows = "".join('<li>%s<span class="tk-name">%s</span><span class="tk-meter"><span style="width:%d%%"></span></span><b>%s</b></li>'
                         % (mug(k, "mug xs"), e(k), max(3, round(v / mx * 100)), fb._k(v)) for k, v in ag)
    pay = {}
    for f in sorted(glob.glob(os.path.join(DW_DATA, "payroll-20*.json"))):
        if os.path.basename(f)[8:18] <= date:
            pay = load(f)
    pay_rows = "".join('<tr><td>%s<span>%s</span></td><td class="pay">$%.2f</td><td>$%.2f</td></tr>'
                       % (mug(r["agent"], "mug xs"), e(r["agent"]), r.get("week", 0), r.get("month", 0))
                       for r in sorted(pay.get("rows") or [], key=lambda r: -r.get("week", 0)))
    return ('<div class="box ledger"><h2>The Weekly Ledger</h2><p class="small">Tokens, pay and who carried the week — %s to %s</p>'
            '<div class="wk-chart">%s</div><p class="center"><b>%s tokens</b> this week</p>'
            '<div class="tk-grid two"><div class="tk-list"><h4>Tokens by agent</h4><ul>%s</ul></div>'
            '<div><h4>Payroll — week to date</h4><table class="paytab"><thead><tr><th>Agent</th><th>Week</th><th>Month</th></tr></thead>'
            '<tbody>%s</tbody></table></div></div></div>'
            % (days[0], days[-1], bars, fb._k(sum(v for _, v in tot)), agent_rows or "<li>—</li>",
               pay_rows or '<tr><td colspan="3">No payroll yet.</td></tr>'))


def week_strips(date):
    """The week's daily strips (kept by take_strips.py), Monday through Sunday."""
    d = dt.date.fromisoformat(date)
    out = []
    for i in range(6, -1, -1):
        day = (d - dt.timedelta(days=i)).isoformat()
        fun = load(os.path.join(ROOT, "strips", day + ".json")).get("funnies") or {}
        if fun.get("strips"):
            out.append((day, fun))
    return out


def week_weather(date):
    days = load(os.path.join(SITE, "data", "weather-week-%s.json" % date)).get("days") or []
    if not days:
        return ""
    return ('<div class="box weather wk"><h2>The Week\'s Weather</h2><div class="wx-days seven">%s</div></div>'
            % "".join('<div class="wx-day"><div class="wx-dname">%s</div><div class="wx-icon">%s</div><div class="wx-hl"><b>%s°</b>%s</div>'
                      '<div class="wx-short">%s</div></div>'
                      % (e(str(x.get("name", ""))[:3].upper()), fb.wx_icon(x.get("short")), e(x.get("high")),
                         (" / %s°" % e(x.get("low"))) if x.get("low") is not None else "", e(x.get("short"))) for x in days[:7]))


def render(ed):
    date = ed["date"]
    d = dt.date.fromisoformat(date)
    no = (d - dt.date(2026, 9, 27)).days // 7 + 1
    cv = ed.get("cover") or {}
    nums = "".join("<li><b>%s</b> %s</li>" % (e(k), e(v)) for k, v in (ed.get("numbers") or {}).items())
    pages = [page("Page One", '<div class="front"><div class="front-lead">%s</div><aside class="front-side">%s%s</aside></div>'
                  % (story(cv, lead=True), week_weather(date),
                     ('<div class="box"><h2>The Week in Numbers</h2><ul class="nums">%s</ul></div>' % nums) if nums else ""))]
    rev = "".join('<li class="wr-day"><div class="wr-when">%s</div>%s<div><b>%s</b><div>%s</div></div></li>'
                  % (e(x.get("day")), mug(x.get("agent"), "mug sm"), e(x.get("title")), e(x.get("text")))
                  for x in ed.get("week_in_review") or [] if isinstance(x, dict))
    pages.append(page("The Week in Review", '<div class="box review"><h2>The Week in Review</h2><ul class="wr">%s</ul></div>' % (rev or "<li>A quiet week.</li>")))
    wa = ed.get("week_ahead") or {}
    plan = "".join('<li>%s<div><b>%s</b><div>%s</div></div></li>' % (mug(x.get("agent"), "mug xs"), e(x.get("title")), e(x.get("text")))
                   for x in wa.get("plan") or [] if isinstance(x, dict))
    cal = "".join('<li><span class="cu-when">%s</span>%s<span>%s</span></li>' % (e(x.get("when")), mug(x.get("agent"), "mug xs"), e(x.get("what")))
                  for x in wa.get("calendar") or [] if isinstance(x, dict))
    pages.append(page("The Week Ahead", '<div class="board"><div class="box plan"><h2>Plan for the Week</h2><ul class="plan-list">%s</ul></div>'
                      '<div class="box coming"><h2>On the Calendar</h2><ul class="cu">%s</ul></div></div>'
                      % (plan or "<li>Nothing planned — a free week.</li>", cal or "<li>Nothing on the calendar.</li>")))
    ev = "".join('<a class="event" %s><div class="ev-when">%s</div><div><b>%s</b><div class="small">%s%s</div><div>%s</div></div>%s</a>'
                 % (('href="%s" target="_blank" rel="noopener"' % e(x["url"])) if str(x.get("url", "")).startswith("https://") else "",
                    e(x.get("when")), e(x.get("title")), e(x.get("where")), (" · " + e(x.get("cost"))) if x.get("cost") else "",
                    e(x.get("text")), '<span class="ev-go">›</span>' if x.get("url") else "")
                 for x in ed.get("events") or [] if isinstance(x, dict))
    pages.append(page("Around Town", '<div class="box events"><h2>Around Town This Week</h2><p class="small">Lewiston · Auburn · nearby — tap one for details</p>%s</div>'
                      % (ev or '<p class="small">No events found this week.</p>')))
    for day, fun in week_strips(date):   # every strip drawn this week, one page per day
        pages.append(page("The Funnies — %s" % dt.date.fromisoformat(day).strftime("%A"),
                          '<div class="fn-dayhead">%s</div>' % e(dt.date.fromisoformat(day).strftime("%A, %B %-d")) + strips_block(fun), " comic-page"))
    pages.append(page("The Weekly Ledger", week_ledger(date)))
    col = ed.get("column") or {}
    if col.get("body"):
        pages.append(page("From the Porch", '<div class="box column"><h2>From the Porch</h2>%s</div>' % story(col)))
    pages = [cover(no, d, cv.get("title") or "")] + pages + [back(date, no)]
    return fb.book(pages, date=date, no=no, lists={}, paper="The Sunday Smoke", motto="The whole week, rolled up",
                   gum="SUNDAY EDITION · ALL THE WEEK FIT TO READ · FUNNIES INSIDE", price="PRICE: TWO PINCHES",
                   delivered="DELIVERED SUNDAY BY GANJA", flap="Sunday edition · Compiled by The Gardiner · Rolled by Ganja", body_class="pub-sun")


def preview(today=None):
    """Between Sundays: the cover, what's coming, and every strip drawn so far this week."""
    today = today or dt.date.today()
    sunday = today + dt.timedelta(days=(6 - today.weekday()) % 7 or 7) if today.weekday() == 6 else today + dt.timedelta(days=(6 - today.weekday()) % 7)
    no = (sunday - dt.date(2026, 9, 27)).days // 7 + 1
    strips = week_strips(today.isoformat())
    n = sum(len(f.get("strips") or []) for _, f in strips)
    pages = [page("Coming Sunday", '<div class="box"><h2>The next Sunday Smoke: %s</h2><p>Every Sunday at 7 AM Ganja rolls up the week: what happened, '
                  'what\'s coming, things to do around town, the weekly ledger — and every comic strip drawn that week.</p>'
                  '<p><b>%d strip%s saved up so far</b> — they\'re on the next pages.</p><p><a href="funnies.html">The funnies archive ›</a> · '
                  '<a href="archive.html">Back issues ›</a> · <a href="/">🏠 The Corner Chronicle</a></p></div>'
                  % (e(sunday.strftime("%A, %B %-d")), n, "" if n == 1 else "s"))]
    for day, fun in strips:
        pages.append(page("The Funnies — %s" % dt.date.fromisoformat(day).strftime("%A"),
                          '<div class="fn-dayhead">%s</div>' % e(dt.date.fromisoformat(day).strftime("%A, %B %-d")) + strips_block(fun), " comic-page"))
    pages = [cover(no, sunday, "Coming %s — %d strip%s saved up so far" % (sunday.strftime("%A, %B %-d"), n, "" if n == 1 else "s"))] + pages + [back(sunday.isoformat(), no)]
    html = fb.book(pages, date=sunday.isoformat(), no=no, lists={}, paper="The Sunday Smoke", motto="The whole week, rolled up",
                   gum="SUNDAY EDITION · ALL THE WEEK FIT TO READ · FUNNIES INSIDE", price="PRICE: TWO PINCHES",
                   delivered="DELIVERED SUNDAY BY GANJA", flap="Sunday edition · Compiled by The Gardiner · Rolled by Ganja", body_class="pub-sun")
    return html.replace('href="../', 'href="').replace('src="../', 'src="'), n, sunday


def main():
    ed = json.load(open(sys.argv[1]))
    dt.date.fromisoformat(ed["date"])
    os.makedirs(os.path.join(SITE, "issues"), exist_ok=True)
    open(os.path.join(SITE, "issues", ed["date"] + ".html"), "w").write(render(ed))
    print("rendered The Sunday Smoke %s" % ed["date"])
    if "--no-build" not in sys.argv:
        import subprocess
        subprocess.run([sys.executable, os.path.join(ROOT, "build_sunday.py")], check=False)


if __name__ == "__main__":
    main()

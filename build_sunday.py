#!/usr/bin/env python3
"""The Sunday Smoke's pages around the issues: home (the newest issue), back issues and the funnies archive.
Also keeps the agents' portraits in step with The Double Wide's copies."""
import datetime as dt, glob, json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "site")
DW = os.path.expanduser("~/.hermes/garden/doublewide")
sys.path.insert(0, ROOT)
import flipbook as fb   # noqa: E402
from flipbook import e, strips_block   # noqa: E402

fb.CSS_FILE = "sunday-smoke.css"


def load(p):
    try:
        return json.load(open(p))
    except Exception:
        return {}


def nice(day):
    return dt.date.fromisoformat(day).strftime("%A, %B %-d, %Y")


def shell(title, body, cls="stand pub-sun"):
    css = open(os.path.join(ROOT, fb.CSS_FILE)).read()
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#1f3a5f">'
            '<link rel="icon" href="/icons/icon-192.png"><link rel="apple-touch-icon" href="/icons/icon-192.png">'
            '<link href="https://fonts.googleapis.com/css2?family=Abril+Fatface&family=UnifrakturMaguntia&family=Patrick+Hand+SC'
            '&family=Oswald:wght@400;600;700&family=Old+Standard+TT:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">'
            '<style>%s</style><script src="/app.js" defer></script></head><body class="%s">%s</body></html>' % (e(title), css, cls, body))


def topbar(title, sub):
    return ('<header class="stand-top"><a class="stand-home" href="./" aria-label="This week\'s paper">📰</a><div><h1>%s</h1>'
            '<div class="stand-sub">%s</div></div><a class="stand-home" href="archive.html" aria-label="Back issues">🗂</a></header>' % (e(title), e(sub)))


def issues():
    d = os.path.join(SITE, "issues")
    return sorted((f[:-5] for f in os.listdir(d) if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.html", f)), reverse=True) if os.path.isdir(d) else []


def sync_portraits():
    os.makedirs(os.path.join(SITE, "img", "funnies"), exist_ok=True)
    for f in glob.glob(os.path.join(DW, "site", "img", "*.png")):
        dest = os.path.join(SITE, "img", os.path.basename(f))
        if not os.path.exists(dest) or os.path.getmtime(dest) < os.path.getmtime(f):
            shutil.copy2(f, dest)


def build_funnies():
    """Every strip ever printed: the Sunday Smoke's, plus the ones that ran in The Double Wide before the funnies moved here."""
    rows = []
    for f in glob.glob(os.path.join(ROOT, "strips", "*.json")):   # the daily strips kept for Sunday
        m = re.fullmatch(r"(\d{4}-\d{2}-\d{2})\.json", os.path.basename(f))
        fun = load(f).get("funnies") or {}
        if m and fun.get("strips"):
            rows.append((m.group(1), "The Sunday Smoke", fun))
    for f in glob.glob(os.path.join(DW, "drafts", "*.json")):
        m = re.fullmatch(r"(\d{4}-\d{2}-\d{2})\.json", os.path.basename(f))
        fun = load(f).get("funnies") or {}
        if not (m and (fun.get("strips") or fun.get("panels"))):
            continue
        for s in fun.get("strips") or []:   # bring the drawn strip images over from The Double Wide
            img = str(s.get("image") or "")
            src = os.path.join(DW, "site", img.replace("../", "")) if img else ""
            if src and os.path.exists(src):
                dest = os.path.join(SITE, "img", "funnies", "dw-" + os.path.basename(src))
                if not os.path.exists(dest):
                    shutil.copy2(src, dest)
                s["image"] = "../img/funnies/dw-" + os.path.basename(src)
        rows.append((m.group(1), "The Double Wide", fun))
    rows.sort(key=lambda r: (r[0], r[1] == "The Sunday Smoke"), reverse=True)
    secs = "".join('<section class="fn-day"><h2 class="cat-date">%s <small>%s</small></h2>%s</section>' % (nice(d), src, strips_block(fun))
                   for d, src, fun in rows)
    html = shell("The Funnies Archive", '%s<main class="paper funnies-archive">%s</main>'
                 % (topbar("The Funnies", "every strip, newest first"), secs or '<p class="small">No funnies yet.</p>'))
    open(os.path.join(SITE, "funnies.html"), "w").write(html.replace('src="../img/', 'src="img/').replace('href="../img/', 'href="img/'))


def build_archive():
    items = "".join('<li><a href="issues/%s.html">%s</a></li>' % (x, nice(x)) for x in issues())
    body = ('%s<main class="paper"><div class="box arch"><h2>The Sunday Smoke</h2><ul class="archive">%s</ul></div>'
            '<div class="box arch"><h2>Also</h2><ul class="archive"><li><a href="funnies.html">😂 The funnies archive</a></li>'
            '<li><a href="/double-wide/">🗞 The Double Wide</a> <span class="small">(daily)</span></li><li><a href="/">🏪 The Newsstand</a></li></ul></div></main>'
            % (topbar("Back Issues", "every Sunday Smoke"), items or "<li>The first Sunday Smoke comes this Sunday.</li>"))
    open(os.path.join(SITE, "archive.html"), "w").write(shell("The Sunday Smoke — Back Issues", body))


def build_index():
    eds = issues()
    if eds:
        pg = open(os.path.join(SITE, "issues", eds[0] + ".html")).read()
        open(os.path.join(SITE, "index.html"), "w").write(pg.replace('href="../', 'href="').replace('src="../', 'src="'))
        ed = load(os.path.join(ROOT, "drafts", eds[0] + ".json"))
        json.dump({"paper": "The Sunday Smoke", "date": eds[0], "title": (ed.get("cover") or {}).get("title") or "", "url": "issues/%s.html" % eds[0],
                   "issues": eds[:10]}, open(os.path.join(SITE, "latest.json"), "w"), ensure_ascii=False)
    else:
        body = ('%s<main class="paper"><div class="box"><h2>The first Sunday Smoke is on its way</h2><p>Every Sunday at 7 AM Ganja rolls up the week: '
                'what happened, what\'s coming, things to do around town, the weekly ledger — and the funnies.</p>'
                '<p><a href="funnies.html">Read the funnies archive while you wait ›</a></p></div></main>' % topbar("The Sunday Smoke", "the whole week, rolled up"))
        open(os.path.join(SITE, "index.html"), "w").write(shell("The Sunday Smoke", body))
        n = sum(len((load(f).get("funnies") or {}).get("strips") or []) for f in glob.glob(os.path.join(ROOT, "strips", "*.json")))
        json.dump({"paper": "The Sunday Smoke", "date": dt.date.today().isoformat(), "title": "First issue this Sunday — %d strip%s saved up so far" % (n, "" if n == 1 else "s"),
                   "url": "", "issues": []}, open(os.path.join(SITE, "latest.json"), "w"))


if __name__ == "__main__":
    for step in (sync_portraits, build_funnies, build_archive, build_index):
        try:
            step()
        except Exception as ex:
            print("sunday: %s failed: %s: %s" % (step.__name__, type(ex).__name__, ex))
    print("sunday pages built")

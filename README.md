# The Sunday Smoke

The Garden's Sunday paper: the whole week rolled up — week in review, the week ahead, things to do around town, the weekly ledger (tokens + pay) and **the funnies**: 1-2 strips are written with The Double Wide every day, drawn as real inked newspaper strips, saved up, and printed together every Sunday. Dressed as a black ribbed King pack with gold lettering.

Part of the Garden's papers, all read through **[The Newsstand](https://github.com/real-CAK3D/NewsStand)** — one home-screen app that mounts every paper under one private (Tailscale-only) HTTPS address: [The Double Wide](https://github.com/real-CAK3D/TheDoubleWide) (daily), [The Re-Up](https://github.com/real-CAK3D/TheRe-Up) (want ads), [The Sunday Smoke](https://github.com/real-CAK3D/TheSundaySmoke) (Sundays), [Roach Clips](https://github.com/real-CAK3D/RoachClips) (Tuesdays) and [The Green Thumb](https://github.com/real-CAK3D/TheGreenThumb) (the directory). The papers are written by [Hermes](https://github.com/NousResearch/hermes-agent) agents running on a small Oracle VM called The Garden.

## Files

| File | What it does |
|---|---|
| `render_sunday.py` | Prints an issue from Ganja's JSON draft as a turn.js flipbook. |
| `collect_week.py` | The week's material for Ganja (reads The Double Wide's drafts and data). |
| `draw_funnies.py` | Draws each strip script as one comic-strip image (gpt-image-2 via the Codex login) with fixed character looks. |
| `take_strips.py` | Takes the day's strips from The Double Wide's draft, draws them and keeps them for Sunday. |
| `build_sunday.py` | Home page, back issues and the funnies archive. |
| `flipbook.py` | A copy of The Double Wide's flipbook renderer, restyled by `sunday-smoke.css`. |
| `prompts/sunday_prompt.txt` | Ganja's instructions and the issue schema. |
| `deliver.sh` | Draw → print → ring the Newsstand's bell. |
| `gardenweb.py` | The small shared web-server kit every Garden paper carries its own copy of. |

## Running

Runs Sundays at 07:00 Eastern through the Garden's relay; served at `/sunday-smoke/` under the Newsstand. Each project is Linux-first (`%-d` date formatting) and expects a Hermes install on the same machine.

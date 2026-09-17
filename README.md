# SITROOM LIVE — setup

This is a real, always-on version of the dashboard. It works because it runs
*outside* Claude entirely — Claude's own published pages are sandboxed and
can't make outbound network calls, so "live" has to be a small pipeline you
host yourself. This one is free (GitHub's free tier covers it):

- `scraper.py` — pulls the public preview page of any Telegram channel
  (`t.me/s/<channel>`, no login/API key needed) and writes `data/alerts.json`.
- `.github/workflows/update.yml` — a GitHub Action that runs the scraper
  every 10 minutes and commits the updated JSON.
- `index.html` — a static page that polls `data/alerts.json` every 30s and
  renders it. No backend needed to *serve* it — GitHub Pages is enough.

## Setup (10 minutes, no server needed)

1. Create a new **public** GitHub repo (Pages needs public on the free tier,
   or use a paid plan for private).
2. Upload all these files, keeping the folder structure
   (`.github/workflows/update.yml` must stay in that exact path).
3. Repo → **Settings → Actions → General → Workflow permissions** → set to
   **"Read and write permissions"**. (Needed so the Action can commit the
   refreshed JSON back to the repo.)
4. Repo → **Settings → Pages** → Source: **Deploy from branch**, branch
   `main`, folder `/ (root)`. Save.
5. Repo → **Actions** tab → run `Update alerts` once manually
   (`workflow_dispatch`) to generate the first `data/alerts.json`.
6. Your live page is now at `https://<you>.github.io/<repo>/`.

From then on, the Action re-scrapes every 10 minutes automatically and the
page picks up new data on its own next poll. No further action needed.

## Adding more channels (e.g. an actual strike-tracker)

Edit the `CHANNELS` dict at the top of `scraper.py`:

```python
CHANNELS = {
    "redalertlb": {"label": "Drone overflight", "type": "drone"},
    "QudsNen":    {"label": "Strikes (Quds News Network)", "type": "strike"},
}
```

Any public Telegram channel works — just use its `@handle` without the `@`.
Different channels format their posts differently, so if a channel's text
comes through garbled, the regex in `scraper.py` (`MSG_RE`) may need a small
tweak — paste me the channel handle and I can adjust it.

## Known limitations

- Telegram's preview markup can change; if the scraper starts returning 0
  items, that's the first thing to check.
- 10-minute polling is a free-tier-friendly default. You can tighten the
  cron in `update.yml` (GitHub won't reliably run more often than ~5 min
  regardless of what you set).
- This is unofficial, volunteer-run source data (drone log currently has
  15 subscribers) — treat as one input, not verified fact.

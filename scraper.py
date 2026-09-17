#!/usr/bin/env python3
"""
Pulls public Telegram channel previews (t.me/s/<channel>) and writes
data/alerts.json. No API key needed — this uses the same public HTML
preview page a browser sees when it can't open the app.

Add/remove channels in CHANNELS below. `type` is just a label you use
to group items in the frontend (e.g. "drone" vs "strike").
"""
import json
import re
import urllib.request
from pathlib import Path

CHANNELS = {
    "redalertlb": {"label": "Drone overflight", "type": "drone"},
    # Example — add a strike-tracking channel the same way:
    # "QudsNen": {"label": "Strikes (Quds News Network)", "type": "strike"},
}

OUT = Path(__file__).parent / "data" / "alerts.json"
MAX_ITEMS = 300

MSG_RE = re.compile(
    r'data-post="[^"]+/(?P<id>\d+)".*?'
    r'tgme_widget_message_text[^>]*>(?P<text>.*?)</div>.*?'
    r'datetime="(?P<time>[^"]+)"',
    re.S,
)
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def fetch(channel: str) -> str:
    url = f"https://t.me/s/{channel}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="ignore")


def parse(html: str, channel: str, meta: dict) -> list[dict]:
    items = []
    for m in MSG_RE.finditer(html):
        text = TAG_RE.sub(" ", m.group("text"))
        text = WS_RE.sub(" ", text).strip()
        if not text:
            continue
        items.append({
            "id": f"{channel}-{m.group('id')}",
            "channel": channel,
            "label": meta["label"],
            "type": meta["type"],
            "text": text,
            "time": m.group("time"),
        })
    return items


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if OUT.exists():
        for it in json.loads(OUT.read_text(encoding="utf-8")):
            existing[it["id"]] = it

    for channel, meta in CHANNELS.items():
        try:
            html = fetch(channel)
            new = parse(html, channel, meta)
            print(f"{channel}: parsed {len(new)} posts")
            for it in new:
                existing[it["id"]] = it
        except Exception as e:
            print(f"WARN: failed to fetch/parse {channel}: {e}")

    merged = sorted(existing.values(), key=lambda x: x["time"], reverse=True)[:MAX_ITEMS]
    OUT.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(merged)} items -> {OUT}")


if __name__ == "__main__":
    main()

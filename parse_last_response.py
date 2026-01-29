#!/usr/bin/env python3
"""Small helper to parse local last_response.html without needing Telegram secrets.

It sets DRY_RUN and dummy TELEGRAM_* env vars so importing the project's
`main` module won't fail or log a critical error. Run this from the project root:

    python .\parse_last_response.py

"""
import os
import json
import pathlib
import sys

# Ensure DRY_RUN so the notifier won't attempt to send messages.
os.environ.setdefault("DRY_RUN", "1")
# Provide harmless dummy Telegram vars to avoid critical checks on import.
os.environ.setdefault("TELEGRAM_TOKEN", "dummy-token")
os.environ.setdefault("TELEGRAM_CHAT_ID", "1")

from main import SeekScraper, SEARCH_KEYWORDS, looks_automated


def main():
    s = SeekScraper()
    p = pathlib.Path("last_response.html")
    if not p.exists():
        print("last_response.html not found in project root.")
        sys.exit(2)

    html = p.read_text(encoding="utf-8")
    jobs = s._parse_response(html)

    print("Found (raw):", len(jobs))
    if not jobs:
        return

    # Normalize keywords for simple title matching
    keys = [k.strip().lower() for k in SEARCH_KEYWORDS if k.strip()]

    filtered = []
    for j in jobs:
        title = (j.get('title') or '').lower()
        # match if any keyword token appears in title
        if any(k in title for k in keys) and not looks_automated(j):
            filtered.append(j)

    print("Found (filtered):", len(filtered))
    if filtered:
        print(json.dumps(filtered, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

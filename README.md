# M&M Quick Codex

**Live site: https://shaftdb.github.io/mnm-guide/** — open that link to use the guide (pick your class and level range in the top bar).

Monsters & Memories quick reference for every class, built to sit in a narrow second-monitor window. Static site in `docs/` (GitHub Pages), built by `build.py` from `content/` and `data/`.

- Rebuild: `python3 build.py` then `python3 tools/linkcheck.py`
- Refresh data: `tools/dump.py`, `tools/batch.py`, `tools/extract.py`, `tools/deepdives.py`, `tools/maps.py` (writes to ignored `raw/`)
- News: data lives in `content/news.json` (id, date ISO, headline, summary, source_url, source_name, tags; no HTML). Add items with `tools/news_add.py new.json --build` (validates fields, checks the link, dedupes by source_url, sorts, rebuilds + link-checks); `tools/news_add.py --check` validates the file. Home shows the newest 5; archive at `news.html`.
- Market prices: data in `content/prices.json` (one dated, sourced observation per entry; never invent prices). `tools/prices_update.py --check` validates; `--add new.json --build` merges, dedupes, stamps dates and rebuilds; `--wiki-refresh` re-checks vendor values via the monstersandmemories.wiki Partner API (needs `MNM_WIKI_PARTNER_KEY`). Page: `market.html` (modules/market.py, static/mod-market.*).
- Seasonal theme: `modules/halloween.py` has `HALLOWEEN = True`; set False to remove the Caves of Irem theme after the season.
- Wiki content CC BY-SA 4.0 (M&M Wiki contributors); map credits on each zone page.
- noindex + robots.txt Disallow: / — not meant for search engines.

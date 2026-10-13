# M&M Quick Codex

**Live site: https://shaftdb.github.io/mnm-guide/** — open that link to use the guide (pick your class and level range in the top bar).

Monsters & Memories quick reference for every class, built to sit in a narrow second-monitor window. Static site in `docs/` (GitHub Pages), built by `build.py` from `content/` and `data/`.

- Rebuild: `python3 build.py` then `python3 tools/linkcheck.py`
- Refresh data: `tools/dump.py`, `tools/batch.py`, `tools/extract.py`, `tools/deepdives.py`, `tools/maps.py` (writes to ignored `raw/`)
- Wiki content CC BY-SA 4.0 (M&M Wiki contributors); map credits on each zone page.
- noindex + robots.txt Disallow: / — not meant for search engines.

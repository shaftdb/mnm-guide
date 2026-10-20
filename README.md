# M&M Quick Codex

**Live site: https://shaftdb.github.io/mnm-guide/** — open that link to use the guide (pick your class and level range in the top bar).

Monsters & Memories quick reference for every class, built to sit in a narrow second-monitor window. Static site in `docs/` (GitHub Pages), built by `build.py` from `content/` and `data/`.

- Rebuild: `python3 build.py` then `python3 tools/linkcheck.py`
- Refresh data: `tools/dump.py`, `tools/batch.py`, `tools/wiki_refresh.py`, `tools/extract.py`, `tools/mnmdb_fetch.py`, `tools/mnmdb_merge.py`, `tools/deepdives.py`, `tools/maps.py` (writes to ignored `raw/`). See "Daily data refresh" below.

## Daily data refresh (the 11 AM run)
Run from the repo root, in this order. Nothing needs a key or login.

```
python3 tools/dump.py              # wiki parse pages (Zones, Classes, Quests, ...) -> raw/parse/; re-fetches only pages whose revision changed
python3 tools/batch.py Quests Merchant "Armor Sets" "Crafted Armor Sets" "Removed Items" "Quest Reward" "Named Mobs"   # category wikitext -> raw/cat_*.json
python3 tools/wiki_refresh.py      # every zone / mob / item page by category AND infobox template, with continuation; refreshes changed revisions
python3 tools/extract.py           # raw/ -> data/*.json (zones, mobs, items, ...)
python3 tools/wiki_refresh.py --report   # no network: content/wiki_audit.json "after" = wiki pages still missing from data/
python3 tools/mnmdb_fetch.py       # mnm-db.com public JSON exports -> raw/mnmdb/ (keeps the old copy if a file fails)
python3 tools/mnmdb_merge.py       # cross-check -> data/mnmdb.json + content/source_conflicts.json (never overwrites wiki values)
python3 build.py && python3 tools/linkcheck.py
for t in tools/test_*.js; do node --experimental-websocket "$t" || echo "FAILED $t"; done
```

- **Rate limits.** Wiki (monstersandmemories.miraheze.org): `tools/wapi.py` waits at least 1 s between requests, sends `maxlag=5`, honours Retry-After and identifies itself as `mnm-quick-codex/1.1 (community guide; https://shaftdb.github.io/mnm-guide/)`. A no-change day is about 150 requests (5 to 6 minutes); `dump.py` uses two threads with a 0.5 s pause. mnm-db.com: 8 files, one at a time, 2 s apart, same User-Agent; its robots.txt allows all agents and has no crawl-delay. Never call its `/api/admin` endpoints (they need a Bearer token).
- **Not automated, on purpose.** monstersandmemories.wiki forbids scraping (Partner API needs `MNM_WIKI_PARTNER_KEY`, which we don't have), so only manual single-page checks. mnmatlas.com's robots.txt bars AI and dataset crawlers, so `data/map_links.json` is edited by hand with a cited source per entry and no guessed coordinates.
- **Check before committing.** `git diff --stat data/ content/`: a big drop in `data/items.json` or `data/zones.json` means a fetch failed, so don't commit it. Read new rows in `content/source_conflicts.json` (count by type at the top). Patch-vs-wiki and wiki-vs-wiki conflicts are entered by hand in `content/source_conflicts_manual.json`; `mnmdb_merge.py` copies them into the `manual` list of `source_conflicts.json` (so regenerating never wipes them) and they show on source-conflicts.html.
- **Commit and hand-off.** Commit `data/`, `content/` and the rebuilt `docs/` on a branch named `data-refresh-YYYY-MM-DD` (message: `Data refresh YYYY-MM-DD: wiki revs + mnm-db`, with item/mob/conflict counts). Don't push. Hand the branch, the counts and any new conflicts or audit gaps to Brewologist for review and publishing.
- News: data lives in `content/news.json` (id, date ISO, headline, summary, source_url, source_name, tags; no HTML). Add items with `tools/news_add.py new.json --build` (validates fields, checks the link, dedupes by source_url, sorts, rebuilds + link-checks); `tools/news_add.py --check` validates the file. Home shows the newest 5; archive at `news.html`.
- Market prices: data in `content/prices.json` (one dated, sourced observation per entry; never invent prices). `tools/prices_update.py --check` validates; `--add new.json --build` merges, dedupes, stamps dates and rebuilds; `--wiki-refresh` re-checks vendor values via the monstersandmemories.wiki Partner API (needs `MNM_WIKI_PARTNER_KEY`). Page: `market.html` (modules/market.py, static/mod-market.*).
- Patch notes: `tools/patch_extract.py` reads cached pages in `tools/pn/` (curl new IDs there, or `--fetch`). Per-class changes go in `content/patch_class_changes.json` (FACT, cited; shown in Class at a glance and as "changed" badges next to matching spells). Announced-but-not-live race/class combos (e.g. Deep Gnome Bard) go in `not_yet_available` in `data/start_audit.json`; they are removed from pickers and rankings and shown as not yet available.
- Seasonal theme: `modules/halloween.py` has `HALLOWEEN = True`; set False to remove the Caves of Irem theme after the season.
- Wiki content CC BY-SA 4.0 (M&M Wiki contributors); map credits on each zone page.
- noindex + robots.txt Disallow: / — not meant for search engines.

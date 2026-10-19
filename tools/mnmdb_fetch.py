#!/usr/bin/env python3
"""Download the public mnm-db.com JSON exports into raw/mnmdb/ (gitignored).

Permission: https://mnm-db.com/robots.txt allows all user agents (AI agents explicitly welcome) with no crawl-delay;
the site publishes these files as static exports. There is no terms page. Approved as a Codex source by Brewologist.
Rules kept here: identify ourselves, one request at a time with >= 2 s between requests, public files only,
NO auth (the site's /api/admin endpoints need a Bearer token: never call them). If a file 404s we keep the previous copy."""
import os, sys, time, json, urllib.request, urllib.error
BASE = 'https://mnm-db.com/'
FILES = ['data.json', 'data-ea.json', 'wiki.json', 'mob-levels.json', 'mob-levels-wiki.json', 'vendors.json', 'spells.json', 'maps.json']
UA = {'User-Agent': 'mnm-quick-codex/1.1 (community guide; https://shaftdb.github.io/mnm-guide/; contact via Brewologist)'}
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'raw', 'mnmdb')
GAP = 2.0
def main():
    os.makedirs(OUT, exist_ok=True); ok = 0
    for i, f in enumerate(FILES):
        if i: time.sleep(GAP)
        try:
            with urllib.request.urlopen(urllib.request.Request(BASE + f, headers=UA), timeout=60) as r: body = r.read()
            json.loads(body)          # only keep valid JSON
            open(os.path.join(OUT, f), 'wb').write(body); ok += 1; print('ok', f, len(body))
        except (urllib.error.URLError, ValueError) as e:
            print('kept previous copy of', f, '-', e)
    json.dump({'fetched': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'files': FILES, 'ok': ok}, open(os.path.join(OUT, '_fetch.json'), 'w'))
    return 0 if ok else 1
if __name__ == '__main__': sys.exit(main())

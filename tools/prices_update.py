#!/usr/bin/env python3
"""Validate, dedupe, date-stamp and (optionally) refresh content/prices.json, the Market page data.

  tools/prices_update.py --check                 validate only (exit 1 on errors)
  tools/prices_update.py                         normalise: parse prices to copper, dedupe, sort, stamp meta.updated
  tools/prices_update.py --add new.json          merge new observations (a JSON list of entries), then normalise
  tools/prices_update.py --wiki-refresh          re-check vendor values through the monstersandmemories.wiki Partner API
                                                 (needs MNM_WIKI_PARTNER_KEY; 1 call/sec, max --max-calls, honours 429 Retry-After)
  add --build to rebuild the site and run tools/linkcheck.py afterwards.

Entry fields: item, kind, price (text like "8 sp 75 cp", "1.25 Gold", "1 sp - 1 sp 50 cp"), source (key of "sources"),
seen (YYYY-MM-DD), confidence (high|medium|low), label (FACT|STRATEGY|UNVERIFIED); optional url, server, where, weight, note,
link (item name to link instead of item), nolink. Derived and overwritten here: cp, cp_max, checked.
Never add a price you did not see in a source. The Tunnel feed is deliberately not fetched (it exposes posters' IPs/PINs).
"""
import argparse, datetime, json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, 'content', 'prices.json')
KINDS = {'vendor_buys': 'Vendor pays', 'vendor_sells': 'NPC sells for', 'player_ask': 'Player asking (WTS)',
         'player_bid': 'Player wants (WTB)', 'player_sale': 'Reported sale', 'report': 'Player report'}
CONF = ('high', 'medium', 'low'); LABELS = ('FACT', 'STRATEGY', 'UNVERIFIED')
UNIT = {'cp': 1, 'c': 1, 'copper': 1, 'sp': 100, 's': 100, 'silver': 100, 'gp': 10000, 'g': 10000, 'gold': 10000}
API = 'https://monstersandmemories.wiki/api/partner/v1/'
TODAY = datetime.date.today().isoformat()

def parse_one(t):
    t = t.strip().lower()
    if not t: return None
    total = 0.0; pos = 0
    for m in re.finditer(r'(\d+(?:\.\d+)?)\s*(copper|silver|gold|cp|sp|gp|c|s|g)\b', t):
        if t[pos:m.start()].strip(' ,+and'): return None
        total += float(m.group(1)) * UNIT[m.group(2)]; pos = m.end()
    if pos == 0 or t[pos:].strip(' ,'): return None
    return int(round(total))

def parse_price(text):
    """'8 sp 75 cp' -> (875, None); '1 sp - 1 sp 50 cp' -> (100, 150). Raises ValueError (platinum is not parsed on purpose)."""
    parts = [p for p in re.split(r'\s+[-\u2013]\s+|\s+to\s+', str(text)) if p.strip()]
    vals = [parse_one(p) for p in parts]
    if not vals or None in vals or len(vals) > 2: raise ValueError('unparseable price %r' % text)
    return (vals[0], vals[1] if len(vals) == 2 else None)

def fmt(cp):
    g, r = divmod(cp, 10000); s, c = divmod(r, 100)
    return ' '.join(x for x in (('%d gp' % g) if g else '', ('%d sp' % s) if s else '', ('%d cp' % c) if c or not (g or s) else '') if x)

def validate(D):
    errs = []
    src = D.get('sources') or {}
    for i, e in enumerate(D.get('entries') or []):
        w = '%d %s' % (i, e.get('item'))
        for k in ('item', 'kind', 'price', 'source', 'seen', 'confidence', 'label'):
            if not e.get(k): errs.append('%s: missing %s' % (w, k))
        if e.get('kind') not in KINDS: errs.append('%s: bad kind %r' % (w, e.get('kind')))
        if e.get('confidence') not in CONF: errs.append('%s: bad confidence %r' % (w, e.get('confidence')))
        if e.get('label') not in LABELS: errs.append('%s: bad label %r' % (w, e.get('label')))
        if e.get('source') not in src: errs.append('%s: unknown source %r' % (w, e.get('source')))
        try:
            d = datetime.date.fromisoformat(str(e.get('seen')))
            if d.isoformat() > TODAY: errs.append('%s: seen date in the future' % w)
        except ValueError: errs.append('%s: seen must be YYYY-MM-DD' % w)
        if e.get('url') and not str(e['url']).startswith('https://'): errs.append('%s: url must be https' % w)
        try: parse_price(e.get('price', ''))
        except ValueError as x: errs.append('%s: %s' % (w, x))
        if e.get('weight') is not None and not isinstance(e['weight'], (int, float)): errs.append('%s: weight must be a number' % w)
    for k, s in src.items():
        if not str(s.get('url', '')).startswith('https://'): errs.append('source %s: url must be https' % k)
    for i, c in enumerate(D.get('camps') or []):
        for k in ('band', 'camp', 'zone', 'items'):
            if not c.get(k): errs.append('camp %d: missing %s' % (i, k))
    return errs

def normalise(D):
    out = {}
    for e in D['entries']:
        e['cp'], cpm = parse_price(e['price'])
        if cpm is None: e.pop('cp_max', None)
        else: e['cp_max'] = cpm
        key = (e['item'].strip().lower(), e['kind'], (e.get('server') or '').lower(), (e.get('where') or '').lower(), e['source'], e['cp'], e.get('cp_max'))
        old = out.get(key)
        if old is None or e['seen'] > old['seen']: out[key] = e  # same observation seen again: keep the newest date
    D['entries'] = sorted(out.values(), key=lambda e: (e['item'].lower(), e['kind'], e['seen']))
    D.setdefault('meta', {})['updated'] = TODAY
    D['meta']['counts'] = {k: sum(1 for e in D['entries'] if e['kind'] == k) for k in KINDS}
    return D

def api_get(path, key):
    req = urllib.request.Request(API + path, headers={'Authorization': 'Bearer ' + key, 'User-Agent': 'mnm-guide prices_update (fan site)'})
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as r: return json.load(r)
        except urllib.error.HTTPError as x:
            if x.code == 429: time.sleep(int(x.headers.get('Retry-After') or 30)); continue
            if x.code == 404: return None
            raise
    return None

def wiki_refresh(D, max_calls):
    key = os.environ.get('MNM_WIKI_PARTNER_KEY')
    if not key:
        print('wiki-refresh skipped: MNM_WIKI_PARTNER_KEY not set (ask a monstersandmemories.wiki Site Admin for a Partner API key)'); return 0
    names = sorted({e.get('link') or e['item'] for e in D['entries'] if e['kind'] == 'vendor_buys' and e['source'] in ('mmwiki-lv', 'mmwiki-api') and not e.get('nolink') and not e.get('where')})
    added = calls = 0
    for nm in names[:max_calls]:
        it = api_get('item/' + urllib.parse.quote(nm, safe=''), key); calls += 1; time.sleep(1.0)
        if not it or it.get('vendorPays') is None: continue
        cp = int(it['vendorPays'])
        same = [e for e in D['entries'] if (e.get('link') or e['item']) == nm and e['kind'] == 'vendor_buys' and e['cp'] == cp and e.get('cp_max') is None]
        if same:
            for e in same: e['checked'] = TODAY
            continue
        D['entries'].append({'item': it.get('name') or nm, 'kind': 'vendor_buys', 'price': fmt(cp), 'source': 'mmwiki-api', 'url': it.get('url') or '',
                             'seen': TODAY, 'checked': TODAY, 'confidence': 'medium', 'label': 'FACT', 'weight': it.get('weight'),
                             'note': 'Partner API vendorPays (players\' ledgers)'}); added += 1
    print('wiki-refresh: %d calls, %d new values' % (calls, added)); return added

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true'); ap.add_argument('--add'); ap.add_argument('--wiki-refresh', action='store_true')
    ap.add_argument('--max-calls', type=int, default=100); ap.add_argument('--build', action='store_true')
    a = ap.parse_args()
    D = json.load(open(PATH, encoding='utf8'))
    if a.add:
        new = json.load(open(a.add, encoding='utf8'))
        for e in (new if isinstance(new, list) else new.get('entries', [])):
            e.setdefault('seen', TODAY); D['entries'].append(e)
    errs = validate(D)
    if errs:
        print('\n'.join('ERROR ' + x for x in errs)); sys.exit(1)
    if a.check:
        print('prices.json OK: %d entries, %d camps' % (len(D['entries']), len(D.get('camps', [])))); return
    normalise(D)
    if a.wiki_refresh:
        wiki_refresh(D, a.max_calls); normalise(D)
    errs = validate(D)
    if errs: print('\n'.join('ERROR ' + x for x in errs)); sys.exit(1)
    with open(PATH, 'w', encoding='utf8') as f: json.dump(D, f, ensure_ascii=False, indent=1); f.write('\n')
    print('prices.json written: %d entries %s' % (len(D['entries']), D['meta']['counts']))
    if a.build:
        subprocess.check_call([sys.executable, 'build.py'], cwd=ROOT); subprocess.check_call([sys.executable, 'tools/linkcheck.py'], cwd=ROOT)

if __name__ == '__main__': main()

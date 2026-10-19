#!/usr/bin/env python3
"""Find and refresh every zone, mob and item page on the M&M wiki, then report what data/*.json is missing.

Fixes the gaps of the older dump.py/batch.py flow (see the "Wiki import audit" changelog entry):
  * pages are found by category AND by infobox template (list=embeddedin), so pages without the expected category are not skipped;
  * every list follows API continuation;
  * the cache is keyed by revision id: a page is re-fetched whenever the wiki has a newer revision (dump.py kept the first copy forever);
  * redirects are resolved and recorded;
  * mob pages (Namedmobpage / MobBox / Mobstatsbox, Category:NPCs, Category:Named Mobs, Category:<Zone> NPCs) are cached for tools/extract.py.

Usage: python3 tools/wiki_refresh.py [--audit-only]   then tools/extract.py, then tools/wiki_refresh.py --report (no network)
Writes raw/parse/<zone>.json (parse output, as dump.py), raw/cat_ItemPages.json, raw/cat_MobPages.json, raw/wiki/_categories.json (Zones list),
and content/wiki_audit.json (counts + every page missing from data/). Polite: >=1 s between requests, maxlag=5 (tools/wapi.py)."""
import json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wapi import api, query_all
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'raw'); DATA = os.path.join(ROOT, 'data')
ZONE_T = ['Template:ZoneDetails', 'Template:Zone']
MOB_T = ['Template:Namedmobpage', 'Template:MobBox', 'Template:Mobstatsbox', 'Template:MobDrops']
ITEM_T = ['Template:Itempage', 'Template:ItemBox', 'Template:Item page', 'Template:ItempageMaster']
NOT_ZONES = ('Starting City',)
def safe(t): return re.sub(r'[^A-Za-z0-9_.-]+', '_', t)
def cat(c): return [m['title'] for m in query_all('categorymembers', cmtitle='Category:' + c, cmlimit=500, cmnamespace=0)]
def emb(t): return [m['title'] for m in query_all('embeddedin', eititle=t, eilimit=500, einamespace=0)]
def info(titles):
    """title -> (lastrevid, resolved title) for every title, following redirects."""
    out = {}
    for i in range(0, len(titles), 50):
        chunk = titles[i:i + 50]
        d = api(action='query', titles='|'.join(chunk), prop='info', redirects=1)
        red = {r['from']: r['to'] for r in d['query'].get('redirects', [])}
        norm = {r['from']: r['to'] for r in d['query'].get('normalized', [])}
        pages = {p['title']: p for p in d['query']['pages']}
        for t in chunk:
            t2 = norm.get(t, t); t3 = red.get(t2, t2); p = pages.get(t3, {})
            out[t] = (p.get('lastrevid'), t3, bool(p.get('missing')))
    return out
def contents(titles):
    out = {}
    for i in range(0, len(titles), 50):
        d = api(action='query', titles='|'.join(titles[i:i + 50]), prop='revisions|categories', rvprop='content|ids|timestamp', rvslots='main', cllimit=500, redirects=1)
        for p in d['query']['pages']:
            if not p.get('revisions'): continue
            r = p['revisions'][0]
            out[p['title']] = {'wt': r['slots']['main']['content'], 'ts': r['timestamp'], 'revid': r['revid'], 'cats': [c['title'][9:] for c in p.get('categories', [])]}
    return out
def load(fn, d):
    try: return json.load(open(fn))
    except Exception: return d
def refresh_set(name, titles, rev):
    fn = os.path.join(RAW, 'cat_%s.json' % name); cache = load(fn, {})
    need = [t for t in titles if rev.get(t) and cache.get(t, {}).get('revid') != rev[t]]
    print(name, len(titles), 'pages,', len(need), 'new or changed', flush=True)
    cache.update(contents(need))
    cache = {t: v for t, v in cache.items() if t in titles}
    json.dump(cache, open(fn, 'w'), ensure_ascii=False)
    return cache, need
def main(audit_only=False):
    t0 = time.time()
    zones = sorted((set(cat('Zones')) | set(x for t in ZONE_T for x in emb(t))) - {''})
    zones = [z for z in zones if not z.startswith(NOT_ZONES)]
    allcats = query_all('allcategories', aclimit=500, acprop='size')
    zone_npc_cats = [c['category'] for c in allcats if c['category'].endswith(' NPCs')]
    mobs = set(cat('NPCs')) | set(cat('Named Mobs')) | set(x for t in MOB_T for x in emb(t))
    for c in zone_npc_cats: mobs |= set(cat(c))
    items = set(cat('All Race Equipment')) | set(cat('Bags & Containers')) | set(x for t in ITEM_T for x in emb(t))
    removed = set(cat('Removed Items'))
    redirects = query_all('allpages', apnamespace=0, apfilterredir='redirects', aplimit=500)
    articles = query_all('allpages', apnamespace=0, apfilterredir='nonredirects', aplimit=500)
    mobs = sorted(mobs - set(zones)); items = sorted((items - removed) - set(mobs) - set(zones))
    rev = {}
    for t, (r, t3, miss) in info(zones + mobs + items).items(): rev[t] = r
    audit = {'generated': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'wiki_articles': len(articles), 'wiki_redirects': len(redirects),
             'zone_pages': len(zones), 'mob_pages': len(mobs), 'item_pages': len(items), 'zone_npc_categories': zone_npc_cats}
    # what data/ currently has (before refresh)
    Z = load(os.path.join(DATA, 'zones.json'), {}); I = load(os.path.join(DATA, 'items.json'), {}); M = load(os.path.join(DATA, 'mobs.json'), {})
    zmobs = {(e.get('name') or '').lower() for z in Z.values() for e in z.get('npcs', []) + z.get('named', [])}
    cached = {}
    for z in zones:
        p = load(os.path.join(RAW, 'parse', safe(z) + '.json'), None)
        cached[z] = p.get('revid') if p and isinstance(p.get('wikitext'), dict) else None
    audit['zones_missing_from_data'] = [z for z in zones if z not in Z]
    audit['zones_stale_cache'] = [{'zone': z, 'cached_rev': cached[z], 'wiki_rev': rev.get(z)} for z in zones if cached[z] and rev.get(z) and cached[z] != rev[z]]
    audit['zone_category_missing'] = [z for z in zones if z not in set(cat('Zones'))]
    audit['mobs_missing_from_data'] = [m for m in mobs if m.lower() not in zmobs and m not in M]
    audit['items_missing_from_data'] = [i for i in items if i not in I]
    audit['items_missing_category'] = sorted(set(items) - set(cat('All Race Equipment')) - set(cat('Bags & Containers')))
    audit['redirects_to_tracked'] = sorted({r['title'] for r in redirects} & (set(zones) | set(mobs) | set(items)))
    os.makedirs(os.path.join(ROOT, 'content'), exist_ok=True); os.makedirs(os.path.join(RAW, 'parse'), exist_ok=True)
    if not audit_only:
        # zones: parse output (rendered HTML + wikitext), re-fetched when the revision changed
        nz = 0
        for z in zones:
            if cached.get(z) == rev.get(z) and cached.get(z): continue
            d = api(action='parse', page=z, prop='text|wikitext|images|links|revid|displaytitle', redirects=1, formatversion=1)
            if 'parse' in d:
                json.dump(d['parse'], open(os.path.join(RAW, 'parse', safe(z) + '.json'), 'w')); nz += 1
        cats = load(os.path.join(RAW, 'wiki', '_categories.json'), {}); cats['Zones'] = zones
        json.dump(cats, open(os.path.join(RAW, 'wiki', '_categories.json'), 'w'), indent=1)
        _, nm = refresh_set('MobPages', mobs, rev)
        _, ni = refresh_set('ItemPages', items, rev)
        audit['refreshed'] = {'zones': nz, 'mobs': len(nm), 'items': len(ni)}
    json.dump(audit, open(os.path.join(ROOT, 'content', 'wiki_audit.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in audit.items()}), 'in %.0fs' % (time.time() - t0))
def local_report():
    """No network: after tools/extract.py, list wiki pages that are still not in data/ (content/wiki_audit.json 'after')."""
    fn = os.path.join(ROOT, 'content', 'wiki_audit.json'); audit = load(fn, {})
    Z = load(os.path.join(DATA, 'zones.json'), {}); I = load(os.path.join(DATA, 'items.json'), {}); M = load(os.path.join(DATA, 'mobs.json'), {})
    zones = load(os.path.join(RAW, 'wiki', '_categories.json'), {}).get('Zones', [])
    mp = load(os.path.join(RAW, 'cat_MobPages.json'), {}); ip = load(os.path.join(RAW, 'cat_ItemPages.json'), {})
    rows = {(e.get('name') or '').strip().lower() for z in Z.values() for k in ('named', 'npcs', 'quest_npcs') for e in z.get(k, [])}
    removed = set(load(os.path.join(RAW, 'cat_Removed_Items.json'), {}))
    nozone = [t for t, m in M.items() if not m['zones']]
    untpl = [t for t, m in M.items() if not m['template'] and t.lower() not in rows]
    audit['after'] = {'zones_missing': [z for z in zones if z not in Z],
                      'mob_pages_not_in_any_zone_table': sorted(t for t in mp if t.lower() not in rows),
                      'mob_pages_without_zone': sorted(nozone), 'mob_pages_without_infobox_or_level': sorted(untpl),
                      'item_pages_missing': sorted(t for t in ip if t not in I and t not in removed)}
    json.dump(audit, open(fn, 'w'), indent=1, ensure_ascii=False)
    print({k: len(v) for k, v in audit['after'].items()})
if __name__ == '__main__':
    if '--report' in sys.argv: local_report()
    else: main('--audit-only' in sys.argv)

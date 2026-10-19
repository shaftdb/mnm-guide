#!/usr/bin/env python3
"""Cross-check data/ (from the Miraheze wiki) against the mnm-db.com exports in raw/mnmdb/ (tools/mnmdb_fetch.py).

Never overwrites a wiki value. Output:
  data/mnmdb.json              per-entry mnm-db facts the guide shows next to wiki data, each labelled with its source file and era
                               (observed drops per mob/item, /con level estimates, vendors and spells the wiki import lacks);
  content/source_conflicts.json every field where the two sources disagree, with both values and links.
Run after tools/extract.py and before build.py."""
import json, os, re, time, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(ROOT, 'raw', 'mnmdb'); D = os.path.join(ROOT, 'data')
SITE = 'https://mnm-db.com/'
def L(f, d=None):
    try: return json.load(open(f, encoding='utf8'))
    except Exception: return d
def nums(s): return [int(x) for x in re.findall(r'\d+', str(s or ''))]
def num(s):
    m = re.search(r'-?\d+(\.\d+)?', str(s if s is not None else ''))
    return float(m.group(0)) if m else None
def norm(s): return re.sub(r'\s+', ' ', str(s or '')).strip().lower()
SLOTMAP = {'boots': 'feet', 'gloves': 'hands', 'neck': 'neck', 'shoulder': 'shoulders', 'bracer': 'wrist', 'earring': 'ear', 'ring': 'finger', 'cloak': 'back', 'belt': 'waist', 'helm': 'head', 'leggings': 'legs'}
def slotnorm(s):
    s = re.sub(r'&\w+;|two handed|one handed|\(.*?\)', ' ', str(s or '').lower())
    return ' '.join(sorted({SLOTMAP.get(x, x) for x in re.findall(r'[a-z]+', s)}))
def main():
    Z = L(os.path.join(D, 'zones.json'), {}); I = L(os.path.join(D, 'items.json'), {}); MER = L(os.path.join(D, 'merchants.json'), {})
    CL = L(os.path.join(D, 'classes.json'), {})
    beta = L(os.path.join(R, 'data.json'), {}); ea = L(os.path.join(R, 'data-ea.json'), {}); wk = L(os.path.join(R, 'wiki.json'), {})
    est = (L(os.path.join(R, 'mob-levels.json'), {}) or {}).get('estimates', {}); vend = (L(os.path.join(R, 'vendors.json'), {}) or {}).get('vendors', [])
    sp = (L(os.path.join(R, 'spells.json'), {}) or {}).get('spells', {})
    conflicts = []
    def C(kind, name, field, ours, theirs, ours_url, file, note=''):
        conflicts.append({'type': kind, 'entity': name, 'field': field, 'wiki': ours, 'wiki_url': ours_url, 'mnmdb': theirs, 'mnmdb_source': SITE + file, 'note': note})
    # our mob rows by lower-case name
    ours = collections.defaultdict(list)
    for z, zd in Z.items():
        for k in ('named', 'npcs', 'quest_npcs'):
            for e in zd.get(k, []):
                n = (e.get('name') or '').strip()
                if n: ours[n.lower()].append((z, e))
    out = {'source': {'name': 'mnm-db.com', 'url': SITE, 'fetched': (L(os.path.join(R, '_fetch.json'), {}) or {}).get('fetched'),
                      'beta_generated': beta.get('generatedAt'), 'ea_generated': ea.get('generatedAt'), 'wiki_mirror_generated': wk.get('generatedAt')},
           'mobs': {}, 'items': {}, 'vendors_extra': [], 'spells_extra': []}
    # ---- mobs: observed drops / zones (player loot ledgers), level estimates, wiki-mirror levels ----
    for era, src, fn in (('beta', beta, 'data.json'), ('early access', ea, 'data-ea.json')):
        for n, m in (src.get('mobs') or {}).items():
            o = out['mobs'].setdefault(n.lower(), {'name': n, 'drops': [], 'zones': {}, 'kills': {}})
            o['kills'][era] = m.get('kills') or m.get('corpses') or 0
            for it, c in (m.get('drops') or {}).items(): o['drops'].append([it, c, m.get('corpses') or 0, era])
            for zz in (m.get('zones') or {}): o['zones'].setdefault(zz, []).append(era)
    for n, e in est.items():
        o = out['mobs'].setdefault(n.lower(), {'name': n, 'drops': [], 'zones': {}, 'kills': {}})
        o['level_est'] = {'level': e.get('level'), 'range': e.get('range'), 'confidence': e.get('confidence', 'rough'), 'from': e.get('from'), 'file': 'mob-levels.json'}
        for z, row in ours.get(n.lower(), []):
            w = nums(row.get('level'))
            lo, hi = (min(w), max(w)) if w else (None, None)
            if w and '?' in str(row.get('level')) and len(w) == 1: hi = 99   # '8-??' / '20?': open-ended, only a lower bound
            if w and e.get('level') and not (lo - 1 <= e['level'] <= hi + 1):
                C('mob', row['name'], 'level', row.get('level'), '%s (%s, /con estimate)' % (e.get('range') or e['level'], e.get('confidence', 'rough')), row.get('page') or Z[z]['url'], 'mob-levels.json', 'zone ' + z)
    for key, m in (wk.get('mobs') or {}).items():
        for z, row in ours.get(key.lower(), []):
            if m.get('zone') and norm(m['zone']) != norm(z): continue
            a, b = nums(row.get('level')), nums(m.get('level'))
            if a and b and (min(a), max(a)) != (min(b), max(b)):
                C('mob', row['name'], 'level', row.get('level'), m.get('level'), row.get('page') or Z[z]['url'], 'wiki.json', 'mnm-db wiki snapshot %s; zone %s' % ((wk.get('generatedAt') or '')[:10], z))
    for o in out['mobs'].values():
        known = {z for z, _ in ours.get(o['name'].lower(), [])}
        o['in_wiki_zones'] = sorted(known)
        o['zones_not_in_wiki'] = sorted(z for z in o['zones'] if z not in known and z in Z)
    # ---- items: who drops it per the ledgers; slot/class/race vs the mnm-db wiki snapshot ----
    for era, src, fn in (('beta', beta, 'data.json'), ('early access', ea, 'data-ea.json')):
        for it in src.get('items') or []:
            n = it.get('name')
            if not n: continue
            o = out['items'].setdefault(n, {'dropped_by': [], 'zones': [], 'in_wiki': n in I})
            for d in it.get('droppedBy') or []:
                o['dropped_by'].append([d.get('mob'), d.get('drops'), d.get('corpses'), d.get('rate'), era])
            o['zones'] = sorted(set(o['zones']) | set(it.get('zones') or []))
    for n, w in (wk.get('items') or {}).items():
        it = I.get(n)
        if not it: continue
        a, b = slotnorm(it.get('slot')), slotnorm(w.get('slot'))
        if a and b and sorted(a.split()) != sorted(b.split()):
            C('item', n, 'slot', it.get('slot'), w.get('slot'), it.get('url'), 'wiki.json', 'mnm-db wiki snapshot %s' % (wk.get('generatedAt') or '')[:10])
        for f, ours_v in (('dmg', it.get('dmg')), ('delay', it.get('delay'))):
            if ours_v and w.get(f) is not None and num(ours_v) is not None and num(w.get(f)) is not None and num(ours_v) != num(w.get(f)):
                C('item', n, f, ours_v, w.get(f), it.get('url'), 'wiki.json', 'mnm-db wiki snapshot %s' % (wk.get('generatedAt') or '')[:10])
    # ---- vendors ----
    mer = {k.lower(): v for k, v in MER.items()}
    for v in vend:
        m = mer.get((v.get('name') or '').lower())
        if not m:
            out['vendors_extra'].append({'name': v['name'], 'zone': v.get('zone'), 'location': v.get('location'), 'sells': v.get('sells') or [], 'source': SITE + 'vendors.json'})
            continue
        a, b = set(m.get('sells') or []), set(v.get('sells') or [])
        if a and b and a != b:
            C('vendor', m['name'], 'sells', sorted(a - b) and ('only in wiki import: ' + ', '.join(sorted(a - b))), sorted(b - a) and ('only in mnm-db: ' + ', '.join(sorted(b - a))), m.get('url'), 'vendors.json',
              'mnm-db vendors generated %s' % ((L(os.path.join(R, 'vendors.json'), {}) or {}).get('generatedAt') or '')[:10])
    # ---- spells: class + level ----
    ourspell = {}
    for cn, c in CL.items():
        for s in c.get('spells') or []:
            ourspell[(norm(s.get('spell name')), cn)] = (s.get('level'), c.get('url'))
    have = {k[0] for k in ourspell}
    for key, s in sp.items():
        for cn, lv in (s.get('classes') or {}).items():
            o = ourspell.get((norm(s.get('name')), cn))
            if o and o[0] and lv and int(o[0]) < 99 and int(o[0]) != int(lv):   # 99 = level not listed on the wiki class page
                C('spell', '%s (%s)' % (s.get('name'), cn), 'level', o[0], lv, o[1], 'spells.json', 'mnm-db spells generated %s' % ((L(os.path.join(R, 'spells.json'), {}) or {}).get('generatedAt') or '')[:10])
        if norm(s.get('name')) not in have:
            out['spells_extra'].append({'name': s.get('name'), 'classes': s.get('classes'), 'skill': s.get('skill'), 'mana': s.get('mana'), 'description': (s.get('description') or '')[:200]})
    for cf in conflicts:
        for k in ('wiki', 'mnmdb'):
            if isinstance(cf[k], list): cf[k] = ', '.join(map(str, cf[k])) or '-'
    conflicts.sort(key=lambda c: (c['type'], c['entity'].lower(), c['field']))
    json.dump(out, open(os.path.join(D, 'mnmdb.json'), 'w'), indent=1, ensure_ascii=False)
    os.makedirs(os.path.join(ROOT, 'content'), exist_ok=True)
    json.dump({'_note': 'Fields where the Miraheze wiki import and mnm-db.com disagree. Both values are kept and shown on the entry; nothing is overwritten. Generated by tools/mnmdb_merge.py.',
               'generated': time.strftime('%Y-%m-%d'), 'count': len(conflicts), 'by_type': dict(collections.Counter(c['type'] for c in conflicts)), 'conflicts': conflicts},
              open(os.path.join(ROOT, 'content', 'source_conflicts.json'), 'w'), indent=1, ensure_ascii=False)
    print('mnm-db: mobs', len(out['mobs']), 'items', len(out['items']), 'vendors_extra', len(out['vendors_extra']), 'spells_extra', len(out['spells_extra']), 'conflicts', len(conflicts), dict(collections.Counter(c['type'] for c in conflicts)))
if __name__ == '__main__': main()

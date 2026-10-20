#!/usr/bin/env python3
"""Check every internal href/src in docs/ resolves to a file (and #anchors exist)."""
import os, re, sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse
ROOT = os.path.join(os.path.dirname(__file__), '..', 'docs')
class P(HTMLParser):
    def __init__(s): super().__init__(); s.links=[]; s.ids=set()
    def handle_starttag(s, t, a):
        a = dict(a)
        if 'id' in a: s.ids.add(a['id'])
        for k in ('href', 'src'):
            if a.get(k): s.links.append(a[k])
pages = {}
for d, _, fs in os.walk(ROOT):
    for f in fs:
        if f.endswith('.html'):
            p = os.path.normpath(os.path.join(d, f)); x = P(); x.feed(open(p, encoding='utf-8').read()); pages[p] = x
bad = []; n = 0
for p, x in pages.items():
    for l in x.links:
        u = urlparse(l)
        if u.scheme or l.startswith('//') or l.startswith('mailto:') or l.startswith('javascript:'): continue
        n += 1
        if l.startswith('/'): bad.append((p, l, 'root-absolute')); continue
        tgt = p if not u.path else os.path.normpath(os.path.join(os.path.dirname(p), unquote(u.path)))
        if os.path.isdir(tgt): tgt = os.path.join(tgt, 'index.html')
        if not os.path.exists(tgt): bad.append((p, l, 'missing')); continue
        if u.fragment and tgt in pages and u.fragment not in pages[tgt].ids: bad.append((p, l, 'no anchor'))
# also check site.css url() refs
for d, _, fs in os.walk(ROOT):
    for f in fs:
        if f.endswith('.css'):
            for m in re.findall(r'url\(([^)]+)\)', open(os.path.join(d, f)).read()):
                m = m.strip('\'"')
                if m.startswith('data:') or '://' in m: continue
                n += 1
                if not os.path.exists(os.path.normpath(os.path.join(d, m))): bad.append((f, m, 'css missing'))
# UX passes 2-6: files the lazy loader fetches by name (not visible as href/src) must exist too
A = os.path.join(ROOT, 'assets'); lazy = set()
for f in os.listdir(A):
    if f.endswith('.js') and (f.startswith('mod-') or f == 'site.js'):
        lazy.update((m, f) for m in re.findall(r'["\']([\w.-]+\.(?:js|css))["\']', open(os.path.join(A, f), encoding='utf-8').read()))
def _walk(v, src):
    if isinstance(v, dict): [_walk(x, src) for x in v.values()]
    elif isinstance(v, list): [_walk(x, src) for x in v]
    elif isinstance(v, str) and re.fullmatch(r'[\w.-]+\.js', v): lazy.add((v, src))
import json
for f in ('quick-data.js', 'trade-data.js', 'walk-data.js', 'hotbar-data.js'):
    fp = os.path.join(A, f)
    if not os.path.exists(fp): continue
    t = open(fp, encoding='utf-8').read(); i = t.find('"lazy":')
    if i >= 0: _walk(json.JSONDecoder().raw_decode(t, i + 7)[0], f)
for p, x in pages.items():
    h = open(p, encoding='utf-8').read(); rp = os.path.relpath(p, ROOT)
    lazy.update((m, rp) for m in re.findall(r'data-lz="([\w.-]+\.js)"', h))
    for band, cities in re.findall(r'class="sc-lz" data-band="([\w-]+)" data-cities="([^"]*)"', h):
        lazy.update(('walk-r-%s-%s.js' % (band, c), rp) for c in cities.split())
lazy.update((f, 'mod-ux.js (theme toggle)') for f in ('mod-ux-light.css', 'mod-ux-contrast.css'))
# UX pass 6: Items / Mobs database pieces (mod-ux-db.js builds idb-c-<n>.js / mdb-c-<n>.js from the index's "chunks" count)
for idx, pfx in (('idb-index.js', 'idb-c-'), ('mdb-index.js', 'mdb-c-')):
    fp = os.path.join(A, idx)
    if not os.path.exists(fp): continue
    m = re.search(r'"chunks":(\d+)', open(fp, encoding='utf-8').read())
    if not m: bad.append((idx, 'chunks', 'no piece count')); continue
    lazy.update(('%s%d.js' % (pfx, i), idx) for i in range(int(m.group(1))))
    if os.path.exists(os.path.join(A, '%s%d.js' % (pfx, int(m.group(1))))): bad.append((idx, '%s%s.js' % (pfx, m.group(1)), 'stale piece beyond the count'))
# UX pass 7: item tooltip pieces (site.js hashes the item name into itip-0..31.js) and hotbar class files (hotbar-data.js lazy.cls)
lazy.update(('itip-%d.js' % i, 'site.js (item tooltips)') for i in range(32))
for f, src in sorted(lazy):
    n += 1
    if not os.path.exists(os.path.join(A, f)): bad.append((src, f, 'lazy asset missing'))
print('lazy-loaded asset references checked: %d' % len(lazy))
for b in bad: print('BAD', os.path.relpath(b[0], ROOT) if os.path.isabs(b[0]) or '/' in b[0] else b[0], b[1], b[2])
print('pages %d, internal links %d, broken %d' % (len(pages), n, len(bad)))
sys.exit(1 if bad else 0)

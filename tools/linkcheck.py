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
for b in bad: print('BAD', os.path.relpath(b[0], ROOT) if os.path.isabs(b[0]) or '/' in b[0] else b[0], b[1], b[2])
print('pages %d, internal links %d, broken %d' % (len(pages), n, len(bad)))
sys.exit(1 if bad else 0)

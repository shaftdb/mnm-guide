#!/usr/bin/env python3
"""Fetch official patch notes (account.monstersandmemories.com/community/patch_notes/N) -> data/patches.json.
Usage: python3 tools/patch_extract.py [--fetch]   (cached HTML in tools/pn/)"""
import re, html, json, os, sys, subprocess
D = os.path.dirname(os.path.abspath(__file__)); PN = os.path.join(D, 'pn')
URL = 'https://account.monstersandmemories.com/community/patch_notes/%d'
if '--fetch' in sys.argv:
    os.makedirs(PN, exist_ok=True)
    for n in range(1, 120):
        f = os.path.join(PN, '%d.html' % n)
        c = subprocess.run(['curl', '-sL', '-o', f, '-w', '%{http_code}', URL % n], capture_output=True, text=True).stdout
        if c != '200' and os.path.exists(f): os.remove(f)
def tx(s): return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s))).strip()
out = []
for f in os.listdir(PN):
    n = int(f.split('.')[0]); t = open(os.path.join(PN, f), encoding='utf8').read()
    i = t.find('id="patch-note-content"')
    if i < 0: continue
    t = t[i:]
    title = tx(re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S).group(1))
    date = tx(re.search(r'</h1>\s*<p[^>]*>(.*?)</p>', t, re.S).group(1))
    secs = []
    j = t.find('<h2'); head = t[:j] if j >= 0 else t
    hi = [tx(x) for x in re.findall(r'<li[^>]*>(.*?)</li>', head, re.S)]
    if [x for x in hi if x]: secs.append({'h': 'Notes', 'items': [x for x in hi if x]})
    for m in re.finditer(r'<h2[^>]*>(.*?)</h2>(.*?)(?=<h2|\Z)', t, re.S):
        items = [tx(x) for x in re.findall(r'<li[^>]*>(.*?)</li>', m.group(2), re.S)]
        items = [x for x in items if x]
        if items: secs.append({'h': tx(m.group(1)), 'items': items})
    out.append({'n': n, 'title': title, 'date': date, 'url': URL % n, 'sections': secs})
out.sort(key=lambda p: -p['n'])
json.dump(out, open(os.path.join(D, '..', 'data', 'patches.json'), 'w'), indent=1, ensure_ascii=False)
print(len(out), 'patches;', sum(len(s['items']) for p in out for s in p['sections']), 'items')

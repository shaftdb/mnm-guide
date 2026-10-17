#!/usr/bin/env python3
"""raw/wiki Skill pages (tools/wikifetch.py Category:Tradeskills) -> data/trades.json"""
import json, glob, re, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
def clean(s):
    s = re.sub(r'\[\[(?:File|Image):[^\]]*\]\]', '', s); s = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', s)
    s = re.sub(r"'''?", '', s); s = re.sub(r'<[^>]+>', ' ', s); s = re.sub(r'\{\{[^}]*\}\}', '', s)
    return re.sub(r'\s+', ' ', s).strip()
def cell(c):
    c = c.strip()
    if '|' in c and not c.startswith('[[') and re.match(r'^[^\[]*?(style|class|colspan|rowspan|align)\s*=', c): c = c.split('|', 1)[1]
    return clean(c)
def links(c): return [re.sub(r'\|.*', '', x) for x in re.findall(r'\[\[([^\]]+)\]\]', c)]
out = {}
for f in glob.glob(os.path.join(R, 'raw', 'wiki', 'Skill *.json')):
    d = json.load(open(f, encoding='utf8')); t = d['text']
    name = d['title'][6:]; info = {}
    for k, v in re.findall(r'^!\s*[^|\n]*\|\s*([^|\n]+?)\s*\n\|\s*(?:style="[^"]*"\s*\|)?\s*(.+)$', t, re.M): info[clean(k)] = clean(v)
    tips = [clean(x) for x in re.findall(r"<div[^>]*>\s*(.*?)\s*</div>", t, re.S) if 'Tip' in x or 'Note' in x]
    body = re.sub(r'^\{\|.*?\n\|\}\n', '', t, count=1, flags=re.S) if t.lstrip().startswith('{|') else t
    paras = [clean(p) for p in re.split(r'\n\s*\n', body.split('==')[0]) if clean(p)]
    tables = []; sec = ''
    for m in re.finditer(r'^(={2,4})\s*(.*?)\s*\1\s*$|^\{\|(.*?)^\|\}', body, re.M | re.S):
        if m.group(2) is not None: sec = clean(m.group(2)); continue
        tb = m.group(0); rows = []; head = []
        for r in re.split(r'^\|-.*$', tb, flags=re.M)[1:] if '|-' in tb else []:
            r = r.strip()
            if r.startswith('!'): head = [cell(x) for x in re.split(r'!!|\|\||\n!', r.lstrip('!'))]; continue
            if r.startswith('|}') or not r.startswith('|'): continue
            raw = re.split(r'\|\||\n\|', r.lstrip('|'))
            if any(cell(x) == 'Example' for x in raw): continue
            rows.append({'c': [cell(x) for x in raw], 'l': [links(x) for x in raw]})
        if not head:
            pre = re.split(r'^\|-.*$', tb, flags=re.M)[0]   # header rows written before the first |- (one ! line per column)
            hl = [l[1:] for l in pre.splitlines() if l.startswith('!')]
            if hl: head = [cell(x) for l in hl for x in re.split(r'!!|\|\|', l)]
        if rows: tables.append({'sec': sec, 'head': head, 'rows': rows})
    out[name] = {'name': name, 'title': d['title'], 'revid': d['revid'], 'ts': d['ts'][:10], 'info': info, 'intro': paras[:2], 'tips': tips[:6], 'tables': tables}
json.dump(out, open(os.path.join(R, 'data', 'trades.json'), 'w', encoding='utf8'), ensure_ascii=False)
print(len(out), 'skills', sum(len(s['tables']) for s in out.values()), 'tables', sum(len(t['rows']) for s in out.values() for t in s['tables']), 'rows')

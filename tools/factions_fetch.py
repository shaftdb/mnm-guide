#!/usr/bin/env python3
"""Fetch wiki faction pages (wikitext via API) -> data/faction_guide.json"""
import json, re, os, urllib.request, urllib.parse
D = os.path.dirname(os.path.abspath(__file__)); API = 'https://monstersandmemories.miraheze.org/w/api.php'
names = list(json.load(open(os.path.join(D, '..', 'data', 'factions.json'))))
def get(titles):
    q = urllib.parse.urlencode({'action': 'query', 'prop': 'revisions', 'rvprop': 'content|ids', 'rvslots': 'main', 'format': 'json', 'titles': '|'.join(titles), 'redirects': 1})
    r = urllib.request.Request(API + '?' + q, headers={'User-Agent': 'mnm-quick-codex/1.0 (community guide)'})
    return json.load(urllib.request.urlopen(r, timeout=60))['query']['pages'].values()
def clean(s):
    s = re.sub(r"<span[^>]*>(.*?)</span>", r"\1", s); s = re.sub(r'<br\s*/?>', ' ', s); s = re.sub(r'<[^>]+>', '', s)
    s = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', s); s = re.sub(r"'''?", '', s)
    return re.sub(r'\s+', ' ', s).strip()
def lst(s):
    out = [clean(x) for x in re.findall(r'^\s*\*\s*(.+)$', s or '', re.M)]
    return [x for x in out if x and x.lower() not in ('none', 'unknown', '-')]
KEYS = ['zones_raise', 'zones_lower', 'quests_raise', 'quests_lower', 'mobs_raise', 'mobs_lower']
res = {}
for i in range(0, len(names), 40):
    for p in get(names[i:i + 40]):
        t = (p.get('revisions') or [{}])[0].get('slots', {}).get('main', {}).get('*', '')
        if not t: continue
        F = {'name': p['title'], 'url': 'https://monstersandmemories.miraheze.org/wiki/' + urllib.parse.quote(p['title'].replace(' ', '_')), 'revid': p['revisions'][0]['revid']}
        if '{{Factionpage' in t:
            m = re.search(r'\|\s*description\s*=(.*?)(?=\n\|\s*\w+\s*=|\n}})', t, re.S); F['desc'] = clean(m.group(1)) if m else ''
            for k in KEYS:
                m = re.search(r'\|\s*%s\s*=(.*?)(?=\n\|\s*\w+\s*=|\n}})' % k, t, re.S); F[k] = lst(m.group(1)) if m else []
        else:
            F['desc'] = clean(t.split('{|')[0].split('{{')[0])
            for k in KEYS:
                m = re.search(r'\{\{\{%s\|\}\}\}\s*\|\s*\{\{\{%s\}\}\}\s*\|(.*?)\}\}' % (k, k), t, re.S); F[k] = lst(m.group(1)) if m else []
        res[p['title']] = F
json.dump(res, open(os.path.join(D, '..', 'data', 'faction_guide.json'), 'w'), indent=1, ensure_ascii=False)
print(len(res), 'factions;', sum(1 for F in res.values() if any(F[k] for k in KEYS)), 'with raise/lower data')

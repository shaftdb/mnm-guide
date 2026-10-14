#!/usr/bin/env python3
"""Cache wiki wikitext: python3 tools/wikifetch.py "Category:Quests" "Category:Tradeskills" ... -> raw/wiki/<title>.json"""
import json, os, sys, time, urllib.request, urllib.parse
API = 'https://monstersandmemories.miraheze.org/w/api.php'; OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw', 'wiki')
H = {'User-Agent': 'mnm-quick-codex/1.0 (community guide)'}
def api(**k):
    k['format'] = 'json'; return json.load(urllib.request.urlopen(urllib.request.Request(API + '?' + urllib.parse.urlencode(k), headers=H), timeout=60))
def members(cat):
    return [m['title'] for m in api(action='query', list='categorymembers', cmtitle=cat, cmlimit=500)['query']['categorymembers']]
def fetch(titles):
    os.makedirs(OUT, exist_ok=True)
    for i in range(0, len(titles), 40):
        for p in api(action='query', prop='revisions|categories', rvprop='content|ids|timestamp', rvslots='main', titles='|'.join(titles[i:i + 40]), cllimit=500, redirects=1)['query']['pages'].values():
            if 'revisions' not in p: continue
            r = p['revisions'][0]
            json.dump({'title': p['title'], 'revid': r['revid'], 'ts': r['timestamp'], 'text': r['slots']['main']['*'], 'cats': [c['title'][9:] for c in p.get('categories', [])]},
                      open(os.path.join(OUT, p['title'].replace('/', '_') + '.json'), 'w'), ensure_ascii=False)
        time.sleep(0.5)
if __name__ == '__main__':
    t = []
    for a in sys.argv[1:]: t += members(a) if a.startswith('Category:') else [a]
    fetch(t); print(len(t), 'pages')

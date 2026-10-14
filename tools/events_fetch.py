#!/usr/bin/env python3
"""Official dated events -> data/events.json.
Sources: official news feed https://monstersandmemories.com/updates?format=rss and
official patch notes https://account.monstersandmemories.com/community/patch_notes/N (title + date only).
Run:  python3 tools/events_fetch.py && python3 build.py"""
import json, re, os, html, datetime, urllib.request
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); H = {'User-Agent': 'mnm-quick-codex/1.0 (community guide)'}
def get(u):
    try: return urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=30).read().decode('utf8', 'replace')
    except Exception: return None
ev = []
rss = get('https://monstersandmemories.com/updates?format=rss') or ''
for it in re.findall(r'<item>(.*?)</item>', rss, re.S):
    d = datetime.datetime.strptime(re.search(r'<pubDate>(.*?)</pubDate>', it).group(1)[5:16], '%d %b %Y').date().isoformat()
    ev.append({'date': d, 'kind': 'news', 'title': html.unescape(re.search(r'<title>(.*?)</title>', it, re.S).group(1)).strip(), 'url': re.search(r'<link>(.*?)</link>', it).group(1).strip()})
miss = 0
for n in range(1, 400):
    t = get('https://account.monstersandmemories.com/community/patch_notes/%d' % n)
    if not t or 'patch-note-content' not in t:
        miss += 1
        if miss > 8: break
        continue
    miss = 0; t = t[t.find('patch-note-content'):]
    title = html.unescape(re.sub(r'\s+', ' ', re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S).group(1))).strip()
    ds = re.sub(r'\s+', ' ', re.search(r'</h1>\s*<p[^>]*>(.*?)</p>', t, re.S).group(1)).strip()
    ev.append({'date': datetime.datetime.strptime(ds, '%B %d, %Y').date().isoformat(), 'kind': 'patch', 'title': title, 'url': 'https://account.monstersandmemories.com/community/patch_notes/%d' % n})
ev.sort(key=lambda e: (e['date'], e['title']), reverse=True)
json.dump({'fetched': datetime.date.today().isoformat(), 'events': ev}, open(os.path.join(R, 'data', 'events.json'), 'w', encoding='utf8'), indent=1, ensure_ascii=False)
print(len(ev), 'events')

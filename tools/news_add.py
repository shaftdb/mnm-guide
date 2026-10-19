#!/usr/bin/env python3
"""Safely append items to content/news.json, then (optionally) rebuild.

Usage:
  tools/news_add.py new_items.json [--build]     # file holds one item or a list of items
  echo '{...}' | tools/news_add.py - [--build]
  tools/news_add.py --check                      # validate the existing file only

Each item: id, date (YYYY-MM-DD), headline, summary (1-2 lines, from the source text only),
source_url (http/https, must answer 2xx/3xx unless --no-fetch), source_name, tags (list of strings).
Dedupes by source_url (and id). No HTML or layout allowed in the data. Exit code 1 on any invalid item.
"""
import json, os, re, subprocess, sys, datetime, urllib.request
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
NEWS = os.path.join(ROOT, 'content', 'news.json')
FIELDS = ['id', 'date', 'headline', 'summary', 'source_url', 'source_name', 'tags']

def validate(it, fetch=True):
    errs = []
    if not isinstance(it, dict): return ['not an object']
    for f in FIELDS:
        if f not in it: errs.append('missing ' + f)
    extra = set(it) - set(FIELDS)
    if extra: errs.append('unknown fields: %s' % ', '.join(sorted(extra)))
    if errs: return errs
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{2,80}', str(it['id'])): errs.append('id must be lowercase slug')
    try: datetime.date.fromisoformat(it['date'])
    except Exception: errs.append('date must be ISO YYYY-MM-DD')
    for f in ('headline', 'summary', 'source_name'):
        v = it[f]
        if not isinstance(v, str) or not v.strip(): errs.append(f + ' empty')
        elif re.search(r'<[a-zA-Z/]', v): errs.append(f + ' contains HTML')
    if isinstance(it['headline'], str) and len(it['headline']) > 120: errs.append('headline > 120 chars')
    if isinstance(it['summary'], str) and len(it['summary']) > 320: errs.append('summary > 320 chars (keep it 1-2 lines)')
    if not re.match(r'^https?://', str(it['source_url'])): errs.append('source_url must be http(s)')
    if not isinstance(it['tags'], list) or not all(isinstance(t, str) and re.fullmatch(r'[a-z0-9-]+', t) for t in it['tags']): errs.append('tags must be a list of lowercase slugs')
    if fetch and not errs:
        try:
            req = urllib.request.Request(it['source_url'], headers={'User-Agent': 'Mozilla/5.0 (mnm-codex news check)'})
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status >= 400: errs.append('source_url HTTP %s' % r.status)
        except Exception as e: errs.append('source_url not reachable: %s' % e)
    return errs

def main(a):
    fetch = '--no-fetch' not in a
    cur = json.load(open(NEWS, encoding='utf8')) if os.path.exists(NEWS) else []
    bad = 0
    for it in cur:
        e = validate(it, fetch=False)
        if e: print('existing %s: %s' % (it.get('id'), '; '.join(e))); bad += 1
    if '--check' in a: return 1 if bad else 0
    src = next((x for x in a if not x.startswith('--')), None)
    if not src: print(__doc__); return 2
    new = json.load(sys.stdin if src == '-' else open(src, encoding='utf8'))
    new = new if isinstance(new, list) else [new]
    urls = {i['source_url'].rstrip('/') for i in cur}; ids = {i['id'] for i in cur}; added = 0
    for it in new:
        e = validate(it, fetch=fetch)
        if e: print('REJECT %s: %s' % (it.get('id') if isinstance(it, dict) else it, '; '.join(e))); bad += 1; continue
        if it['source_url'].rstrip('/') in urls or it['id'] in ids: print('skip duplicate', it['id']); continue
        cur.append({f: it[f] for f in FIELDS}); urls.add(it['source_url'].rstrip('/')); ids.add(it['id']); added += 1; print('added', it['id'])
    cur.sort(key=lambda i: (i['date'], i['id']), reverse=True)
    if added:
        tmp = NEWS + '.tmp'
        with open(tmp, 'w', encoding='utf8') as f: json.dump(cur, f, ensure_ascii=False, indent=2); f.write('\n')
        os.replace(tmp, NEWS)
    print('%d added, %d rejected, %d total' % (added, bad, len(cur)))
    if added and '--build' in a:
        subprocess.check_call([sys.executable, os.path.join(ROOT, 'build.py')], cwd=ROOT)
        subprocess.check_call([sys.executable, os.path.join(ROOT, 'tools', 'linkcheck.py')], cwd=ROOT)
    return 1 if bad else 0

if __name__ == '__main__': sys.exit(main(sys.argv[1:]))

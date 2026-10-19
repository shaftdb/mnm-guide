"""Polite MediaWiki API client for the M&M wiki (monstersandmemories.miraheze.org).
Identifies itself, waits >=1 s between requests, sends maxlag=5, honours Retry-After / maxlag errors, retries with backoff."""
import json, time, urllib.request, urllib.parse, urllib.error
API = 'https://monstersandmemories.miraheze.org/w/api.php'
UA = {'User-Agent': 'mnm-quick-codex/1.1 (community guide; https://shaftdb.github.io/mnm-guide/)'}
MIN_GAP = 1.0
_last = [0.0]
def api(**p):
    p.setdefault('format', 'json'); p.setdefault('maxlag', 5); p.setdefault('formatversion', 2)
    url = API + '?' + urllib.parse.urlencode(p)
    for i in range(6):
        wait = _last[0] + MIN_GAP - time.time()
        if wait > 0: time.sleep(wait)
        _last[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                d = json.load(r)
            if 'error' in d and d['error'].get('code') == 'maxlag':
                time.sleep(5 * (i + 1)); continue
            return d
        except urllib.error.HTTPError as e:
            ra = e.headers.get('Retry-After')
            time.sleep(int(ra) if ra and ra.isdigit() else 3 * (i + 1))
        except Exception:
            time.sleep(3 * (i + 1))
    raise RuntimeError('wiki API failed: ' + url[:200])
def query_all(list_name, **p):
    """Iterate a list= query through every continuation."""
    out = []; cont = {}
    while True:
        d = api(action='query', list=list_name, **p, **cont)
        out += d['query'][list_name]
        if 'continue' not in d: return out
        cont = {k: v for k, v in d['continue'].items()}

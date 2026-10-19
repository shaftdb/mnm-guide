import json,os,sys,re,time
from concurrent.futures import ThreadPoolExecutor
import sys,os; sys.path.insert(0,os.path.dirname(__file__))
from fetch import api,cat
cats=['Zones','Classes','Tradeskills','Factions','Quests','Named Mobs','Races']
titles=set(['Musty\'s New Player Guide','Game Mechanics','Main Page','Shaman Guides','Spell Research','Research','Patch Notes','Starting City by Race, Class, and Deity','Goblin','Deities','Traits','Underdocks'])
memb={}
for c in cats:
    memb[c]=cat(c); titles|=set(memb[c])
json.dump(memb,open('raw/wiki/_categories.json','w'),indent=1)
def revids(ts):
    out={}
    ts=sorted(ts)
    for i in range(0,len(ts),50):
        r=api(action='query',titles='|'.join(ts[i:i+50]),prop='info',redirects=1)
        red={x['from']:x['to'] for x in r['query'].get('redirects',[])+r['query'].get('normalized',[])}
        pages={p['title']:p.get('lastrevid') for p in r['query']['pages'].values()}
        for t in ts[i:i+50]: out[t]=pages.get(red.get(red.get(t,t),red.get(t,t)))
    return out
LIVE=revids(titles)
os.makedirs('raw/parse',exist_ok=True)
def get(t):
    fn='raw/parse/'+re.sub(r'[^A-Za-z0-9_.-]+','_',t)+'.json'
    if os.path.exists(fn):   # re-fetch when the wiki has a newer revision (this used to keep the first copy forever)
        try:
            if json.load(open(fn)).get('revid')==LIVE.get(t): return   # raw/parse/: wikifetch.py owns raw/wiki/
        except Exception: pass
    try:
        r=api(action='parse',page=t,prop='text|wikitext|images|links|revid|displaytitle',redirects=1)
        if 'error' in r: print('ERR',t,r['error'].get('code')); return
        json.dump(r['parse'],open(fn,'w'))
    except Exception as e: print('FAIL',t,e)
with ThreadPoolExecutor(2) as ex: list(ex.map(get,sorted(titles)))
print('done',len(titles))

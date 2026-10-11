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
def get(t):
    fn='raw/wiki/'+re.sub(r'[^A-Za-z0-9_.-]+','_',t)+'.json'
    if os.path.exists(fn): return
    try:
        r=api(action='parse',page=t,prop='text|wikitext|images|links|revid|displaytitle',redirects=1)
        if 'error' in r: print('ERR',t,r['error'].get('code')); return
        json.dump(r['parse'],open(fn,'w'))
    except Exception as e: print('FAIL',t,e)
with ThreadPoolExecutor(4) as ex: list(ex.map(get,sorted(titles)))
print('done',len(titles))

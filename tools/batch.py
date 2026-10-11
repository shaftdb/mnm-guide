import json,sys,os
import sys,os; sys.path.insert(0,os.path.dirname(__file__))
from fetch import api,cat
def wikitexts(titles):
    out={}
    for i in range(0,len(titles),50):
        r=api(action='query',prop='revisions|categories',rvprop='content|timestamp',rvslots='main',cllimit=500,titles='|'.join(titles[i:i+50]),redirects=1)
        for p in r['query']['pages'].values():
            if 'revisions' in p:
                rv=p['revisions'][0]
                out[p['title']]={'wt':rv['slots']['main']['*'],'ts':rv['timestamp'],'cats':[c['title'][9:] for c in p.get('categories',[])]}
    return out
for c in sys.argv[1:]:
    t=cat(c); print(c,len(t),flush=True)
    json.dump(wikitexts(t),open('raw/cat_'+c.replace(' ','_')+'.json','w'))

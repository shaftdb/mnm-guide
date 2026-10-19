import json,sys,urllib.request,urllib.parse,time,os
API='https://monstersandmemories.miraheze.org/w/api.php'
UA={'User-Agent':'mnm-quick-codex/1.1 (community guide; https://shaftdb.github.io/mnm-guide/)'}
def api(**p):
    p['format']='json'; p.setdefault('maxlag',5); time.sleep(0.5)
    u=API+'?'+urllib.parse.urlencode(p)
    for i in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40))
        except Exception as e:
            time.sleep(2+i*3); err=e
    raise err
def cat(c):
    out=[];cont={}
    while True:
        r=api(action='query',list='categorymembers',cmtitle='Category:'+c,cmlimit=500,**cont)
        out+= [m['title'] for m in r['query']['categorymembers']]
        if 'continue' in r: cont={'cmcontinue':r['continue']['cmcontinue']}
        else: return out
if __name__=='__main__':
    for c in sys.argv[1:]:
        print('##',c); print('\n'.join(cat(c)))

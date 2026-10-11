"""Fetch official class deep dives and parse into data/deepdives.json"""
import urllib.request,re,json,os,sys
from html.parser import HTMLParser
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CL=['archer','bard','beastmaster','cleric','druid','elementalist','enchanter','fighter','inquisitor','monk','necromancer','paladin','ranger','rogue','shadow-knight','shaman','spellblade','wizard']
class T(HTMLParser):
    def __init__(s): super().__init__(); s.out=[]; s.skip=0
    def handle_starttag(s,t,a):
        if t in('script','style'): s.skip+=1
        if t in('p','li','h1','h2','h3','h4','br','div'): s.out.append('\n')
        if t=='li': s.out.append('- ')
    def handle_endtag(s,t):
        if t in('script','style'): s.skip-=1
    def handle_data(s,d):
        if not s.skip: s.out.append(d)
def fetch(slug):
    fn=os.path.join(ROOT,'raw','dd',slug+'.html')
    url=f'https://monstersandmemories.com/class-{slug}-deep-dive'
    if not os.path.exists(fn):
        html=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40).read().decode('utf8','replace')
        open(fn,'w').write(html)
    return url,open(fn).read()
def parse(html):
    t=T(); t.feed(html); txt=''.join(t.out)
    lines=[re.sub(r'\s+',' ',l).strip() for l in txt.split('\n')]
    lines=[l for l in lines if l]
    m=[]
    for l in lines:
        if m and m[-1]=='-': m[-1]='- '+l
        else: m.append(l)
    lines=m
    try: i=lines.index('Overview')+1
    except ValueError: i=0
    end=next((k for k in range(i,len(lines)) if lines[k].startswith('Archer - Bard')),len(lines))
    body=lines[i:end]
    overview=[];sections=[];cur=None;k=0
    while k<len(body):
        l=body[k]; nxt=body[k+1] if k+1<len(body) else ''
        if nxt.startswith('- ') and not l.startswith('- ') and len(l)<70:
            if cur is None: cur={'title':'Abilities','paras':[],'entries':[]}; sections.append(cur)
            desc=nxt[2:]; k+=2
            while k<len(body) and body[k].startswith('- ') and not (k+1<len(body) and body[k+1].startswith('- ') and False):
                if k+1<len(body) and body[k+1].startswith('- ') and len(body[k])<70: break
                desc+=' '+body[k][2:]; k+=1
            cur['entries'].append({'name':l,'desc':desc}); continue
        if len(l)<50 and not l.startswith('- ') and not l.endswith('.'):
            cur={'title':l,'paras':[],'entries':[]}; sections.append(cur); k+=1; continue
        if l.startswith('- '):
            if cur is None: cur={'title':'Notes','paras':[],'entries':[]}; sections.append(cur)
            cur['entries'].append({'name':l[2:],'desc':''}); k+=1; continue
        (overview if cur is None else cur['paras']).append(l); k+=1
    return overview,sections
out={}
for s in CL:
    url,html=fetch(s); ov,sec=parse(html)
    out[s]={'url':url,'overview':ov,'sections':sec}
    print(s,len(ov),[ (x['title'],len(x['entries'])) for x in sec][:12])
json.dump(out,open(os.path.join(ROOT,'data','deepdives.json'),'w'),indent=1,ensure_ascii=False)

import json,re,sys
def fn(t): return 'raw/wiki/'+re.sub(r'[^A-Za-z0-9_.-]+','_',t)+'.json'
def load(t): return json.load(open(fn(t)))
def plain(s):
    s=re.sub(r'<ref.*?</ref>','',s,flags=re.S)
    s=re.sub(r'\[\[(?:File|Image):[^\]]*\]\]','',s)
    s=re.sub(r'\[\[([^\]|]*)\|([^\]]*)\]\]',r'\2',s)
    s=re.sub(r'\[\[([^\]]*)\]\]',r'\1',s)
    s=re.sub(r'\[https?://\S+ ([^\]]*)\]',r'\1',s)
    s=re.sub(r"'''?",'',s)
    s=re.sub(r'<br\s*/?>',' ; ',s)
    s=re.sub(r'<[^>]+>','',s)
    s=re.sub(r'\{\{[^{}]*\}\}','',s)
    return re.sub(r'\s+',' ',s).strip()
def links(s): return [m.split('|')[0].strip() for m in re.findall(r'\[\[([^\]]*)\]\]',s) if not m.lower().startswith(('file:','image:','category:'))]
def strip_attr(c):
    # cell "style=..|content"
    if '|' in c and not '[[' in c.split('|')[0] and re.match(r'\s*(style|class|colspan|rowspan|align|width|bgcolor|scope)\s*=',c):
        return c.split('|',1)[1]
    return c
def tables(wt):
    """returns list of (heading, rows[list of raw cells])"""
    out=[];head=''
    lines=wt.split('\n'); i=0; stack=[]
    cur=None
    for ln in lines:
        s=ln.strip()
        m=re.match(r'^(=+)\s*(.*?)\s*\1$',s)
        if m and cur is None: head=plain(m.group(2)); continue
        if s.startswith('{|'):
            stack.append(cur); cur={'head':head,'rows':[],'row':None}; continue
        if cur is None: continue
        if s.startswith('|}'):
            if cur['row'] is not None: cur['rows'].append(cur['row'])
            out.append((cur['head'],cur['rows'])); cur=stack.pop(); continue
        if s.startswith('|-'):
            if cur['row'] is not None: cur['rows'].append(cur['row'])
            cur['row']=[]; continue
        if s.startswith('|+'): continue
        if s.startswith('!') or s.startswith('|'):
            if cur['row'] is None: cur['row']=[]
            body=s[1:]
            parts=re.split(r'\|\||!!',body)
            for p in parts: cur['row'].append(strip_attr(p).strip())
        else:
            if cur['row']: cur['row'][-1]+=' '+s
    return out
def template(wt,name):
    m=re.search(r'\{\{'+name+r'(.*?)\n\}\}',wt,re.S)
    if not m: return {}
    d={}
    for part in re.split(r'\n\|',m.group(1)):
        if '=' in part:
            k,v=part.split('=',1); d[k.strip()]=v.strip()
    return d
if __name__=='__main__':
    d=load(sys.argv[1]); wt=d['wikitext']['*']
    print(template(wt,'ZoneDetails'))
    for h,rows in tables(wt):
        print('## TABLE',h)
        for r in rows: print('  | '+' | '.join(plain(c) for c in r)[:300])

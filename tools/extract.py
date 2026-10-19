"""Turn raw wiki dumps (raw/) into tidy JSON under data/.
Run tools/dump.py + tools/batch.py first (they fetch from the M&M wiki API).
Stdlib only."""
import json,re,os,sys,glob,collections
sys.path.insert(0,os.path.dirname(__file__))
from wt import plain,links,tables,template
from wh import html_tables
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW=os.path.join(ROOT,'raw'); DATA=os.path.join(ROOT,'data')
WIKI='https://monstersandmemories.miraheze.org/wiki/'
def wurl(t): return WIKI+t.replace(' ','_').replace("'",'%27')
def rawpage(t):
    """Parse-API output for a page. raw/parse/ is its own directory now: tools/wikifetch.py writes a different format
    to raw/wiki/<title>.json and silently replaced Rothold, Faelindral and Underdocks there."""
    s=re.sub(r'[^A-Za-z0-9_.-]+','_',t)+'.json'
    for fn in (os.path.join(RAW,'parse',s),os.path.join(RAW,'wiki',s)):
        if os.path.exists(fn):
            d=json.load(open(fn))
            if isinstance(d.get('wikitext'),dict): return d
    return None
def catj(name): return json.load(open(os.path.join(RAW,'cat_'+name.replace(' ','_')+'.json')))

# ---------- generic template parser (handles nesting) ----------
def find_template(wt,name):
    m=re.search(r'\{\{\s*'+re.escape(name)+r'\s*(\||\n|\}\})',wt,re.I)
    if not m: return None
    i=m.start(); depth=0; j=i
    while j<len(wt):
        if wt.startswith('{{',j): depth+=1; j+=2; continue
        if wt.startswith('}}',j):
            depth-=1; j+=2
            if depth==0: break
            continue
        j+=1
    body=wt[m.end()-1 if m.group(1)!='}}' else m.end():j-2]
    # split top-level |
    parts=[];cur='';d=0;k=0
    while k<len(body):
        if body.startswith('{{',k) or body.startswith('[[',k): d+=1;cur+=body[k:k+2];k+=2;continue
        if body.startswith('}}',k) or body.startswith(']]',k): d-=1;cur+=body[k:k+2];k+=2;continue
        if body[k]=='|' and d==0: parts.append(cur);cur='';k+=1;continue
        cur+=body[k];k+=1
    parts.append(cur)
    out={}
    for p in parts:
        if '=' in p:
            a,b=p.split('=',1); out[a.strip().lower()]=b.strip()
    return out

CLASSES=['Archer','Bard','Beastmaster','Cleric','Druid','Elementalist','Enchanter','Fighter','Inquisitor','Monk','Necromancer','Paladin','Ranger','Rogue','Shadow Knight','Shaman','Spellblade','Wizard']
ABBR={'ARC':'Archer','BRD':'Bard','BST':'Beastmaster','CLR':'Cleric','DRU':'Druid','ELE':'Elementalist','ENC':'Enchanter','FTR':'Fighter','INQ':'Inquisitor','MNK':'Monk','NEC':'Necromancer','PAL':'Paladin','RNG':'Ranger','ROG':'Rogue','SHD':'Shadow Knight','SHM':'Shaman','SPB':'Spellblade','WIZ':'Wizard'}
def parse_classes(s):
    s=plain(s or '').upper()
    if not s: return None
    if 'ALL' in s.split() or s.strip()=='ALL': return sorted(ABBR)
    got=[a for a in ABBR if re.search(r'\b'+a+r'\b',s)]
    return got or None

def lvl_num(s):
    """'~16' -> 16, '8+' -> 8, '12-13' -> 12, '' -> None"""
    m=re.search(r'(\d+)',s or '')
    return int(m.group(1)) if m else None

STAT_KEYS=['ac','str','sta','agi','dex','int','wis','cha','hp','mana','hp_regen','mana_regen','haste','spell_haste','ranged_haste','cr','cor','dr','er','fr','mr','pr','hr','dmg','delay']
def item_from(title,rec):
    wt=rec['wt']; ib=find_template(wt,'ItemBox') or {}
    ip=find_template(wt,'Itempage') or {}
    it={'name':title,'url':wurl(title),'wiki_ts':rec['ts'][:10],'cats':rec.get('cats',[])}
    it['slot']=plain(ib.get('slot','')).title() or None
    for k in STAT_KEYS:
        v=plain(ib.get(k,''))
        if v and re.match(r'^[+-]?\d+(\.\d+)?%?$',v): it[k]=v
    for k in ['skill','handed','weight','size','effect','effect1','effect2','effect3','magic','lore','nodrop','cont_capacity','cont_max_size','cont_weight_reduction']:
        v=plain(ib.get(k,''))
        if v: it[k]=v
    it['classes']=parse_classes(ib.get('class'))
    it['class_raw']=plain(ib.get('class',''))
    it['race']=plain(ib.get('race',''))
    # sources
    df=ip.get('dropsfrom','')
    drops=[];zone=None
    for line in df.split('\n'):
        line=line.strip()
        if not line: continue
        ls=links(line)
        if line.startswith('*'):
            for l in ls: drops.append({'zone':zone,'mob':l})
        elif ls: zone=ls[0]
    it['drops']=drops
    it['quests']=links(ip.get('relatedquests',''))
    pc=ip.get('playercrafted','') or ''
    m=re.search(r'\[\[([^\]|]+)[^\]]*\]\]\s*\(Trivial:\s*([^)]*)\)',pc)
    it['crafted']={'skill':m.group(1),'trivial':m.group(2).strip()} if m else ({'skill':None,'trivial':None} if plain(pc) else None)
    it['soldby']=links(ip.get('soldby',''))
    mv=plain(ip.get('merchant_value',''))
    it['merchant_value']=mv or None
    it['notes']=plain(ip.get('notes',''))[:400] or None
    return it

PLACEHOLDERS={'Example NPC','Example Item','Example Quest','Raid Named'}
def ml(v):
    v=plain(v or '').strip()
    return None if v in ('','-','?') else v
def mob_from(title,rec,zones):
    """One wiki mob page (Namedmobpage / Mobstatsbox, or an untemplated page in a '<Zone> NPCs' category)."""
    wt=rec['wt']; tpl='Namedmobpage'; t=find_template(wt,'Namedmobpage')
    if t is None: tpl='Mobstatsbox'; t=find_template(wt,'Mobstatsbox')
    if t is None: tpl=None; t={}
    cats=rec.get('cats',[])
    zs=links(t.get('zone','')) or ([ml(t.get('zone'))] if ml(t.get('zone')) else [])
    zs+=[c[:-5] for c in cats if c.endswith(' NPCs') and c[:-5] not in zs]
    zl={k.lower():k for k in zones}
    zs=[zl.get(x.lower(),x) for x in zs]
    zs=list(dict.fromkeys(x for x in zs if x))
    loot=links(t.get('known_loot','') or t.get('unique drops',''))
    common=links(t.get('common_loot','') or t.get('drops',''))
    return {'name':title,'url':wurl(title),'wiki_ts':rec['ts'][:10],'revid':rec.get('revid'),'template':tpl,'zones':zs,
        'race':ml(t.get('race')),'class':ml(t.get('class')),'level':ml(t.get('level')),'location':ml(t.get('location')),
        'desc':(ml(t.get('description')) or '')[:300] or None,'known_loot':loot,'common_loot':common,
        'factions':ml(t.get('factions')),'named':'Named Mobs' in cats or bool(loot) and tpl=='Namedmobpage','cats':cats}

def main():
    os.makedirs(DATA,exist_ok=True)
    cats=json.load(open(os.path.join(RAW,'wiki','_categories.json')))
    # ---------- zones ----------
    imgmeta=json.load(open(os.path.join(RAW,'img','_meta.json')))
    zones={}; npclevel={}
    for z in cats['Zones']:
        if z.startswith('Starting City'): continue
        d=rawpage(z)
        if not d: continue
        wt=d['wikitext']['*']
        tz=find_template(wt,'ZoneDetails') or {}
        zd={'name':z,'url':wurl(z),'revid':d.get('revid'),'level':plain(tz.get('level','')).strip(' -') or None,
            'monster_types':plain(tz.get('monstertypes','')) or None,
            'adjacent':links(tz.get('adjacentzones','')),'notable':links(tz.get('notablenpc','')),
            'quests':[],'named':[],'npcs':[],'items':[],'intro':'','images':[i for i in d['images'] if i.replace('_',' ') in imgmeta or i in imgmeta]}
        # intro: first plain paragraph
        body=re.sub(r'\{\{ZoneDetails.*?\n\}\}','',wt,flags=re.S)
        for para in body.split('\n'):
            p=plain(para)
            if len(p)>40 and not para.strip().startswith(('{','|','!','=','*','[[File')): zd['intro']=p; break
        # travel list
        m=re.search(r'==\s*Traveling To and From\s*==(.*?)(\n==[^=])',wt,re.S)
        if m: zd['travel']=[plain(l.lstrip('*')) for l in m.group(1).split('\n') if l.strip().startswith('*')]
        for h,rows in html_tables(d['text']['*']):
            if not rows: continue
            mode=None; hdr=[]
            for cells in rows:
                low=[c.lower() for c in cells]
                if not cells or not any(cells): continue
                f=low[0]
                if len(cells)==1 and re.search(r'\b1\.',cells[0]) and ('2.' in cells[0] or 'A.' in cells[0]):
                    zd.setdefault('legend',[]).append(re.sub(r'^.*?\[ edit \]\s*','',cells[0])); continue
                if f.startswith('named npc'): mode='named';hdr=low;continue
                if f.startswith('quest npc'): mode='qnpcs';hdr=low;continue
                if (f.startswith('npcs') or f.startswith('common npc') or f in('npc','name')) and 'level' in low:
                    mode='npcs';hdr=low;area=cells[0].split(' - ',1)[1] if ' - ' in cells[0] else None;continue
                if f=='quest name': mode='quests';hdr=low;continue
                if f=='item name': mode='items';hdr=low;continue
                if f=='location' and 'merchant' in low: mode='merch';hdr=low;continue
                if mode is None: continue
                cells=[c.strip() for c in cells]
                rec=dict(zip(hdr,cells))
                if cells[0] in PLACEHOLDERS: continue
                if mode=='qnpcs':
                    zd.setdefault('quest_npcs',[]).append({'name':cells[0],'race':rec.get('race'),'class':rec.get('class'),'level':rec.get('level'),'location':rec.get('location'),'desc':rec.get('description')})
                    npclevel.setdefault(cells[0].lower(),[]).append((z,rec.get('level'),False,rec.get('location')))
                elif mode in('named','npcs'):
                    name=cells[0]
                    loot=rec.get('known loot') or rec.get('unique loot')
                    e={'name':name,'race':rec.get('race'),'class':rec.get('class'),'level':rec.get('level'),'location':rec.get('location') or (area if mode=='npcs' else None),'loot':loot,'desc':rec.get('description')}
                    if mode=='npcs' and loot and loot not in('-','') and e['desc'] and 'named' in e['desc'].lower(): mode2='named'
                    else: mode2=mode
                    zd[mode2].append(e)
                    if name: npclevel.setdefault(name.lower(),[]).append((z,rec.get('level'),mode2=='named',e['location']))
                elif mode=='quests':
                    zd['quests'].append({'name':cells[0],'reward':rec.get('reward'),'giver':rec.get('quest giver'),'min_level':rec.get('minimum level'),'classes':rec.get('classes')})
                elif mode=='items':
                    zd['items'].append({'name':re.sub(r'\s*-\s*Quest$','',cells[0]),'from':rec.get('drops from'),'slot':rec.get('slot')})
                elif mode=='merch':
                    zd.setdefault('merchants',[]).append({'location':cells[0],'merchant':cells[1] if len(cells)>1 else ''})
        zones[z]=zd
    # ---------- mob pages (tools/wiki_refresh.py -> raw/cat_MobPages.json) ----------
    mobs={}
    mfn=os.path.join(RAW,'cat_MobPages.json')
    if os.path.exists(mfn):
        for t,rec in json.load(open(mfn)).items():
            if t in PLACEHOLDERS: continue
            mobs[t]=mob_from(t,rec,zones)
        for m in mobs.values():
            for z in m['zones']:
                if z not in zones: continue
                zd=zones[z]; rows=[e for k in ('named','npcs','quest_npcs') for e in zd.get(k,[]) if (e.get('name') or '').strip().lower()==m['name'].lower()]
                for e in rows:   # fill blanks only; a zone-table value is never overwritten
                    for k in ('level','location','race','class'):
                        if not ml(e.get(k)) and m.get(k): e[k]=m[k]; e.setdefault('filled_from_mob_page',[]).append(k)
                    e['page']=m['url']
                    if m['known_loot'] and not ml(e.get('loot')): e['loot']=', '.join(m['known_loot'])
                if not rows and (m['template'] or m['level']):
                    e={'name':m['name'],'race':m['race'],'class':m['class'],'level':m['level'],'location':m['location'],'loot':', '.join(m['known_loot']+m['common_loot']) or None,'desc':m['desc'],'page':m['url'],'src':'mob page'}
                    zd['named' if m['named'] else 'npcs'].append(e)
                    npclevel.setdefault(m['name'].lower(),[]).append((z,m['level'],m['named'],m['location']))
        json.dump(mobs,open(os.path.join(DATA,'mobs.json'),'w'),indent=1,ensure_ascii=False)
    json.dump(zones,open(os.path.join(DATA,'zones.json'),'w'),indent=1,ensure_ascii=False)
    # ---------- quests ----------
    qraw=catj('Quests'); quests={}
    for t,rec in qraw.items():
        q=find_template(rec['wt'],'Quest') or {}
        rew=[]
        rq=q.get('quest rewards','')
        rew+=links(rq)
        m=re.search(r'==\s*Rewards?\s*==(.*?)(\n==|\Z)',rec['wt'],re.S)
        if m: rew+=[l for l in links(m.group(1)) if l not in rew]
        quests[t]={'name':t,'url':wurl(t),'wiki_ts':rec['ts'][:10],'zone':plain(q.get('start zone','')) or None,'giver':plain(q.get('quest giver','')) or None,
            'min_level':plain(q.get('minimum level','')) or None,'classes':plain(q.get('classes','')) or None,'rewards':rew,
            'repeatable':'repeatable' in rec['wt'].lower(),'cats':rec.get('cats',[])}
    json.dump(quests,open(os.path.join(DATA,'quests.json'),'w'),indent=1,ensure_ascii=False)
    # ---------- merchants ----------
    mraw=catj('Merchant'); merchants={}
    for t,rec in mraw.items():
        mp=find_template(rec['wt'],'Merchantpage') or {}
        merchants[t]={'name':t,'url':wurl(t),'wiki_ts':rec['ts'][:10],'zone':links(mp.get('zone','')) or [plain(mp.get('zone',''))],
            'location':plain(mp.get('location','')) or None,'sells':links(mp.get('sells','')),
            'buys':[plain(l.lstrip('*')) for l in mp.get('buys','').split('\n') if plain(l.lstrip('*'))]}
    json.dump(merchants,open(os.path.join(DATA,'merchants.json'),'w'),indent=1,ensure_ascii=False)
    soldby=collections.defaultdict(list)
    for m in merchants.values():
        for s in m['sells']: soldby[s].append(m['name'])
    # ---------- armor sets ----------
    sets={}
    for cn in ['Armor Sets','Crafted Armor Sets']:
        for t,rec in catj(cn).items():
            rows=[]
            for h,tr in tables(rec['wt']):
                if not tr: continue
                hdr=[plain(c).lower() for c in tr[0]]
                for r in tr[1:]:
                    cells=[plain(c) for c in r]
                    if len(cells)>=3: rows.append(dict(zip(hdr,cells)))
            sets[t]={'name':t,'url':wurl(t),'crafted':'Crafted Armor Sets' in rec.get('cats',[]) or cn=='Crafted Armor Sets','rows':rows,'wiki_ts':rec['ts'][:10]}
    json.dump(sets,open(os.path.join(DATA,'armor_sets.json'),'w'),indent=1,ensure_ascii=False)
    # ---------- items ----------
    if os.path.exists(os.path.join(RAW,'cat_ItemPages.json')): iraw=catj('ItemPages')
    else:
        iraw=catj('All Race Equipment')
        for extra in ['Bags & Containers']:
            for k,v in catj(extra).items(): iraw.setdefault(k,v)
    mobloot=collections.defaultdict(list)
    for m in mobs.values():
        for it in m['known_loot']+m['common_loot']:
            for z in (m['zones'] or [None]): mobloot[it].append((z,m['name']))
    removed=set(catj('Removed Items'))
    items={}
    qrew=collections.defaultdict(list)
    for q in quests.values():
        for r in q['rewards']: qrew[r].append(q['name'])
    for t,rec in iraw.items():
        if t in removed or 'Removed Items' in rec.get('cats',[]): continue
        it=item_from(t,rec)
        it['soldby']=sorted(set(it['soldby']+soldby.get(t,[])))
        it['quests']=sorted(set(it['quests']+qrew.get(t,[])))
        have={(d['mob'] or '').lower() for d in it['drops']}
        for z,mn in mobloot.get(t,[]):
            if mn.lower() not in have: it['drops'].append({'zone':z,'mob':mn,'via':'mob page'}); have.add(mn.lower())
        # acquisition level estimate from drop mob levels
        lv=[]
        for d in it['drops']:
            for (z,l,named,loc) in npclevel.get((d['mob'] or '').lower(),[]):
                if d['zone'] in (None,z):
                    n=lvl_num(l)
                    if n: lv.append(n)
                    d.setdefault('level',l); d['named']=named; d.setdefault('location',loc)
        it['drop_level']=min(lv) if lv else None
        ql=[lvl_num(quests[q]['min_level']) for q in it['quests'] if q in quests and lvl_num(quests[q]['min_level'])]
        it['quest_level']=min(ql) if ql else None
        items[t]=it
    json.dump(items,open(os.path.join(DATA,'items.json'),'w'),indent=1,ensure_ascii=False)
    # ---------- classes ----------
    classes={}
    for c in CLASSES:
        d=rawpage(c)
        if not d: continue
        wt=d['wikitext']['*']
        cl={'name':c,'url':wurl(c),'revid':d.get('revid')}
        m=re.search(r'=\s*Description\s*=\s*\n(.*?)\n=',wt,re.S); cl['description']=plain(m.group(1)) if m else ''
        m=re.search(r'Class modifier to race base stats:\s*([^\n]*)',wt); cl['modifier']=plain(m.group(1)) if m else None
        m=re.search(r'==\s*Bonus points\s*==\s*\n(.*?)\n=',wt,re.S); cl['bonus_advice']=plain(m.group(1)) if m else None
        m=re.search(r'may wear ([^.]*)\.',plain(wt)); cl['armor']=m.group(1) if m else None
        cl['spells']=[];cl['races']=[];cl['skills']=[]
        for h,rows in html_tables(d['text']['*']):
            if not rows: continue
            hdr=[x.lower() for x in rows[0]]
            if hdr and hdr[0]=='race':
                for r in rows[1:]: cl['races'].append(dict(zip(hdr,r)))
            elif hdr and 'name' in hdr[0] and len(hdr)>=3:
                lv=lvl_num(h)
                for cells in rows[1:]:
                    if not cells or not cells[0]: continue
                    rec=dict(zip(hdr,cells)); rec['level']=lv; rec['section']=h
                    cl['spells'].append(rec)
            elif 'skill' in hdr and 'level' in hdr:
                for r in rows[1:]:
                    rec=dict(zip(hdr,r)); rec['group']=h; cl['skills'].append(rec)
        m=re.search(r'=\s*Class Quests\s*=\s*\n(.*?)\n=',wt,re.S); cl['class_quests']=links(m.group(1)) if m else []
        classes[c]=cl
    json.dump(classes,open(os.path.join(DATA,'classes.json'),'w'),indent=1,ensure_ascii=False)
    # ---------- factions & tradeskills (summaries) ----------
    for key,catn in [('factions','Factions'),('tradeskills','Tradeskills')]:
        out={}
        for t in cats[catn]:
            d=rawpage(t)
            if not d: continue
            wt=d['wikitext']['*']
            paras=[plain(p) for p in re.split(r'\n\s*\n',re.sub(r'\{\{.*?\}\}','',wt,flags=re.S)) if len(plain(p))>30 and not p.strip().startswith(('{|','|','!'))]
            tb=[]
            for h,rows in tables(wt):
                rr=[[plain(x) for x in r] for r in rows if any(plain(x) for x in r)]
                if rr: tb.append({'head':h,'rows':rr[:80]})
            heads=re.findall(r'^=+\s*(.*?)\s*=+\s*$',wt,re.M)
            out[t]={'name':t,'url':wurl(t),'revid':d.get('revid'),'paras':paras[:12],'tables':tb[:8],'heads':heads,'links':[l['*'] for l in d.get('links',[])][:200],
                    'implemented': not bool(re.search(r'\{\{\s*NotImplemented|not (yet )?(fully )?implemented',wt,re.I))}
        json.dump(out,open(os.path.join(DATA,key+'.json'),'w'),indent=1,ensure_ascii=False)
    print('zones',len(zones),'quests',len(quests),'merchants',len(merchants),'items',len(items),'sets',len(sets),'classes',len(classes))
if __name__=='__main__': main()

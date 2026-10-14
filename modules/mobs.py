# Mob lookup module: /mobs.html + assets/mobs-db.js, from wiki zone NPC/named tables and item drop data
def _mobs_db():
    drops = {}
    for nm, it in ITEMS.items():
        for d in it.get('drops', []):
            k = ((d.get('mob') or '').strip().lower(), d.get('zone') or '')
            drops.setdefault(k, set()).add(nm)
    rows = []
    for z, Z in ZONES.items():
        zu = (dungeon_url(z) if z in DUNGEON_ORDER else zone_url(z)).lstrip('/')
        for named, lst in ((1, Z['named']), (0, Z['npcs'])):
            for e in lst:
                n = (e.get('name') or '').strip()
                if not n or not re.search(r'[A-Za-z]', n) or n in ('Raid Named', 'Example Item'): continue
                lv = e.get('level') or ''
                its = set(drops.get((n.lower(), z), set()))
                wl = [x.strip() for x in (e.get('loot') or '').split(',') if x.strip() and x.strip() != '-']
                its |= {x for x in wl if x in ITEMS}
                other = [x for x in wl if x not in ITEMS]
                rows.append([n, lvl_num(lv) or 0, '' if lv.strip() == '-' else lv, z, zu, named, ' / '.join(x for x in (e.get('race'), e.get('class')) if x and x != '-'), '' if e.get('location') in (None, '-') else e['location'], sorted(its), other])
    rows.sort(key=lambda r: (r[1] == 0, r[1], r[0].lower()))
    return rows
def _mobs_page():
    return ('<link rel="stylesheet" href="/assets/mod-mobs.css">'
            '<p>Search mobs and NPCs from the community wiki zone tables <span class="badge fact">fact</span>: level, zone, whether it is a named, and known drops. Drops come from the wiki item pages and the named loot column, and link to the item%s. '
            'A blank drop list means the wiki records none <span class="badge unc">unverified</span>. Some rows are town NPCs rather than hunting targets.</p>'
            '<div class="idb-tools"><input id="mob-q" type="search" placeholder="Mob, zone or item…" aria-label="Search mobs"><label><input type="checkbox" id="mob-named"> Named only</label>'
            '<label><input type="checkbox" id="mob-lvl"> In my level range</label><label><input type="checkbox" id="mob-drop"> Has drops</label></div>'
            '<p id="mob-count" class="dim"></p><div id="mob-out"></div><script>window.MNM_ITEMPAGE=%s;</script><script src="/assets/mobs-db.js"></script><script src="/assets/mod-mobs.js"></script>') % (
        ' in the item database' if any(k == 'items' for _, _, k in NAV) else ' wiki page', 'true' if any(k == 'items' for _, _, k in NAV) else 'false')
_m_prev_bc = build_content
def build_content():
    _m_prev_bc()
    add_page('mobs.html', 'Mob lookup', body_html=_mobs_page(), section='mobs',
             sources=['Wiki zone pages (NPC and named tables)|%sZones' % WIKI, 'Wiki item pages (drop sources)|%sCategory:Items' % WIKI], desc='Mob lookup')
_m_prev_ra = render_all
def render_all():
    _m_prev_ra()
    urls = {n: it.get('url', '') for n, it in ITEMS.items()}
    D = _mobs_db()
    open(os.path.join(OUT, 'assets', 'mobs-db.js'), 'w', encoding='utf8').write('window.MNM_MOBS=' + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + ';window.MNM_IURL=' + json.dumps({n: urls[n] for r in D for n in r[8]}, ensure_ascii=False, separators=(',', ':')) + ';')
NAV.insert(len(NAV) - 1, ('Mobs', '/mobs.html', 'mobs'))

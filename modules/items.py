# Item & drop DB module: page /items.html + docs/assets/items-db.js (data) + static/mod-items.js (UI)
def _items_db():
    rows = []
    for nm, it in sorted(ITEMS.items()):
        src = []
        for d in it.get('drops', []):
            z = d.get('zone') or ''
            zu = (dungeon_url(z) if z in DUNGEON_ORDER else zone_url(z) if z in ZONES else '')
            src.append(['n' if d.get('named') else 'd', d.get('mob') or '', d.get('level') or '', z, zu.lstrip('/'), '' if d.get('location') in (None, '-') else d['location']])
        for q in it.get('quests', []): src.append(['q', q, (QUESTS.get(q, {}) or {}).get('min_level') or '', (QUESTS.get(q, {}) or {}).get('zone') or '', '', ''])
        for m in it.get('soldby', [])[:3]: src.append(['v', m, '', ', '.join(x for x in (MERCH.get(m, {}).get('zone') or []) if x), '', ''])
        seen = {(d.get('mob') or '').lower() for d in it.get('drops', [])}
        for mob, n, corpses, rate, era in (MNMDB.get('items', {}).get(nm) or {}).get('dropped_by', []):   # mnm-db.com loot ledgers
            if not mob: continue
            src.append(['d', mob, '', '', '', '%s of %s corpses (%s)' % (n, corpses, era) + ('' if mob.lower() in seen else ', not on the wiki'), 'mnm-db'])
        if it.get('crafted'): src.append(['c', (it['crafted'] or {}).get('skill') or 'tradeskill', (it['crafted'] or {}).get('trivial') or '', '', '', ''])
        lv = item_level(it)
        x = {}
        c = _conf_for('item', nm)
        if c: x['c'] = c
        rows.append([nm, it.get('url', ''), it.get('slot') or '', ' '.join(class_codes(it)), lv or '', stat_str(it) or '', src, x])
    return rows

def _items_page():
    return ('<link rel="stylesheet" href="/assets/mod-items.css">'
            '<p>Search %d items from the community wiki item pages <span class="badge fact">fact</span> (every page using the wiki item infobox, including quest items, materials and books): slot, classes, level, and where each comes from (dropping mob or named and its zone, quest, vendor or tradeskill). Zone names link to the zone or dungeon guide. '
            'Drops marked <span class="tag">mnm-db</span> are observed loot counts from the <a class="ext" target="_blank" rel="noopener" href="https://mnm-db.com/">mnm-db.com</a> player ledgers; a <span class="tag conf">sources differ</span> flag shows both values where it and the wiki disagree (<a href="/source-conflicts.html">all conflicts</a>). '
            'Item level is the lowest drop or quest level on the wiki, not a required level. Blank sources or levels mean the wiki has none <span class="badge unc">unverified</span>.</p>'
            '<div class="idb-tools"><input id="idb-q" type="search" placeholder="Item, mob, zone or stat…" aria-label="Search items">'
            '<select id="idb-slot" aria-label="Slot"><option value="">Any slot</option>%s</select>'
            '<label><input type="checkbox" id="idb-cls"> Usable by my class</label><label><input type="checkbox" id="idb-lvl"> In my level range</label>'
            '<select id="idb-src" aria-label="Source"><option value="">Any source</option><option value="n">Named drop</option><option value="d">Mob drop</option><option value="q">Quest</option><option value="v">Vendor</option><option value="c">Crafted</option></select></div>'
            '<p id="idb-count" class="dim"></p><div id="idb-out"></div>'
            '<script src="/assets/items-db.js"></script><script src="/assets/mod-items.js"></script>') % (
        len(ITEMS), ''.join('<option>%s</option>' % esc(s) for s in sorted({x for it in ITEMS.values() for x in (it.get('slot') or '').split() if x})))

_items_prev_bc = build_content
def build_content():
    _items_prev_bc()
    add_page('items.html', 'Item & drop database', body_html=_items_page(), section='items',
             sources=['Wiki item pages|%sCategory:Items' % WIKI, 'Wiki zone NPC tables and mob pages (drop sources)|%sZones' % WIKI, 'mnm-db.com loot ledgers and wiki snapshot (cross-check)|https://mnm-db.com/'], desc='Searchable item and drop database')
_items_prev_ra = render_all
def render_all():
    _items_prev_ra()
    open(os.path.join(OUT, 'assets', 'items-db.js'), 'w', encoding='utf8').write('window.MNM_IDB=' + json.dumps(_items_db(), ensure_ascii=False, separators=(',', ':')) + ';')
NAV.insert(len(NAV) - 1, ('Items', '/items.html', 'items'))

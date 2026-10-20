# Mob lookup module: /mobs.html + assets/mobs-db.js, from wiki zone NPC/named tables, wiki mob pages, item drop data,
# and mnm-db.com cross-checks (data/mnmdb.json + content/source_conflicts.json from tools/mnmdb_merge.py; wiki values are never overwritten).
MNMDB = json.load(open(os.path.join(DATA, 'mnmdb.json'), encoding='utf8')) if os.path.exists(os.path.join(DATA, 'mnmdb.json')) else {'mobs': {}, 'items': {}}
SRCCONF = json.load(open(os.path.join(CONTENT, 'source_conflicts.json'), encoding='utf8')).get('conflicts', []) if os.path.exists(os.path.join(CONTENT, 'source_conflicts.json')) else []
MNMDB_URL = 'https://mnm-db.com/'
def _conf_for(kind, name):
    n = (name or '').strip().lower()
    return ['%s: wiki %s / mnm-db %s (%s)' % (c['field'], c['wiki'], c['mnmdb'], c.get('note') or c['mnmdb_source']) for c in SRCCONF if c['type'] == kind and c['entity'].strip().lower() == n]
def _mob_extra(n, page=None):
    o = MNMDB.get('mobs', {}).get(n.strip().lower()) or {}
    x = {}
    if page: x['p'] = page
    if o.get('drops'):
        agg = {}
        for it, c, corpses, era in o['drops']: agg.setdefault(it, []).append('%s/%s %s' % (c, corpses or '?', era))
        x['m'] = [[it, '; '.join(v)] for it, v in sorted(agg.items())]
    if o.get('level_est'): x['e'] = '%s (%s confidence, /con estimate)' % (o['level_est'].get('range') or o['level_est'].get('level'), o['level_est'].get('confidence'))
    c = _conf_for('mob', n)
    if c: x['c'] = c
    return x
def _mobs_db():
    drops = {}
    for nm, it in ITEMS.items():
        for d in it.get('drops', []):
            k = ((d.get('mob') or '').strip().lower(), d.get('zone') or '')
            drops.setdefault(k, set()).add(nm)
    rows = []
    for z, Z in ZONES.items():
        zu = (dungeon_url(z) if z in DUNGEON_ORDER else zone_url(z)).lstrip('/')
        for named, lst in ((1, Z['named']), (0, Z['npcs']), (0, Z.get('quest_npcs', []))):
            for e in lst:
                n = (e.get('name') or '').strip()
                if not n or not re.search(r'[A-Za-z]', n) or n in ('Raid Named', 'Example Item', 'Example NPC'): continue
                lv = e.get('level') or ''
                its = set(drops.get((n.lower(), z), set()))
                wl = [x.strip() for x in (e.get('loot') or '').split(',') if x.strip() and x.strip() != '-']
                its |= {x for x in wl if x in ITEMS}
                other = [x for x in wl if x not in ITEMS]
                x = _mob_extra(n, e.get('page'))
                if e in Z.get('quest_npcs', []): x['q'] = 1
                rows.append([n, lvl_num(lv) or 0, '' if lv.strip() == '-' else lv, z, zu, named, ' / '.join(x for x in (e.get('race'), e.get('class')) if x and x != '-'), '' if e.get('location') in (None, '-') else e['location'], sorted(its), other, x])
    # mnm-db.com only: mobs (or mob + zone pairs) seen in its player loot ledgers but absent from every wiki table and mob page
    for k, o in sorted(MNMDB.get('mobs', {}).items()):
        zs = o.get('zones_not_in_wiki') or ([] if o.get('in_wiki_zones') else [zz for zz in o.get('zones', {}) if zz in ZONES])
        for z in zs:
            zu = (dungeon_url(z) if z in DUNGEON_ORDER else zone_url(z)).lstrip('/')
            x = _mob_extra(o['name']); x['s'] = 'mnm-db'
            le = (MNMDB['mobs'][k].get('level_est') or {})
            rows.append([o['name'], le.get('level') or 0, ('~%s' % (le.get('range') or le.get('level'))) if le else '', z, zu, 0, '', '', sorted({it for it, _ in x.get('m', []) if it in ITEMS}), [], x])
    rows.sort(key=lambda r: (r[1] == 0, r[1], r[0].lower()))
    return rows
def _mobs_page():
    return ('<link rel="stylesheet" href="/assets/mod-mobs.css">'
            '<p>Search mobs and NPCs from the community wiki zone tables and mob pages <span class="badge fact">fact</span>: level, zone, whether it is a named, and known drops. Drops come from the wiki item pages, mob pages and the named loot column, and link to the item%s. '
            'Observed drops (count / corpses looted) come from the <a class="ext" target="_blank" rel="noopener" href="https://mnm-db.com/">mnm-db.com</a> player loot ledgers, marked by era. Where mnm-db and the wiki disagree both values are shown with a <span class="tag conf">sources differ</span> flag (full list: <a href="/source-conflicts.html">source conflicts</a>). '
            'A blank drop list means the wiki records none <span class="badge unc">unverified</span>. Some rows are town NPCs rather than hunting targets.</p>'
            '<div class="idb-tools"><input id="mob-q" type="search" placeholder="Mob, zone or item…" aria-label="Search mobs"><label><input type="checkbox" id="mob-named"> Named only</label>'
            '<label><input type="checkbox" id="mob-lvl"> In my level range</label><label><input type="checkbox" id="mob-drop"> Has drops</label></div>'
            '<p id="mob-count" class="dim"></p><div id="mob-out"></div><script>window.MNM_ITEMPAGE=%s;</script><script src="/assets/mobs-db.js"></script><script src="/assets/mod-mobs.js"></script>') % (
        ' in the item database' if any(k == 'items' for _, _, k in NAV) else ' wiki page', 'true' if any(k == 'items' for _, _, k in NAV) else 'false')
def _conflicts_page():
    by = {}
    for c in SRCCONF: by.setdefault(c['type'], []).append(c)
    o = ['<p>Every field where the <a class="ext" target="_blank" rel="noopener" href="%s">M&amp;M wiki</a> import and <a class="ext" target="_blank" rel="noopener" href="https://mnm-db.com/">mnm-db.com</a> disagree (%d). '
         'Nothing is overwritten: the wiki value stays on the page and the entry carries a <span class="tag conf">sources differ</span> flag with both values. mnm-db\'s wiki snapshot is a few days older than ours, so many of these are recent wiki edits; check in game when it matters <span class="badge unc">unverified</span>.</p>' % (WIKI, len(SRCCONF))]
    for t in ('mob', 'item', 'vendor', 'spell'):
        L = by.get(t, [])
        if not L: continue
        o.append('<h2 id="%s">%s (%d)</h2><div class="tw"><table class="grid sortable filt-text"><thead><tr><th>Entry</th><th>Field</th><th>Wiki</th><th>mnm-db</th><th>Note</th></tr></thead><tbody>%s</tbody></table></div>' % (
            t, {'mob': 'Mobs', 'item': 'Items', 'vendor': 'Vendors', 'spell': 'Spells'}[t], len(L), ''.join(
                '<tr><td>%s</td><td>%s</td><td><a class="ext" target="_blank" rel="noopener" href="%s">%s</a></td><td><a class="ext" target="_blank" rel="noopener" href="%s">%s</a></td><td class="dim">%s</td></tr>' % (
                    esc(c['entity']), esc(c['field']), esc(c.get('wiki_url') or WIKI), esc(str(c['wiki'])), esc(c['mnmdb_source']), esc(str(c['mnmdb'])), esc(c.get('note') or '')) for c in L)))
    MC = json.load(open(os.path.join(CONTENT, 'source_conflicts.json'), encoding='utf8')).get('manual', []) if os.path.exists(os.path.join(CONTENT, 'source_conflicts.json')) else []
    if MC:
        o.append('<h2 id="manual">Patch notes and wiki pages that disagree (%d)</h2><p>Hand-checked conflicts between official patch notes and the wiki, or between two wiki pages (content/source_conflicts_manual.json). Both values are shown and cited; the site text says which one it follows %s.</p>'
                 '<div class="tw"><table class="grid sortable filt-text"><thead><tr><th>Type</th><th>Entry</th><th>Field</th><th>Source A</th><th>Source B</th><th>Note</th></tr></thead><tbody>%s</tbody></table></div>' % (
            len(MC), '<span class="badge unc">unverified</span>', ''.join(
                '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s: <a class="ext" target="_blank" rel="noopener" href="%s">%s</a></td><td>%s: <a class="ext" target="_blank" rel="noopener" href="%s">%s</a></td><td class="dim">%s</td></tr>' % (
                    esc(c['type']), esc(c['entity']), esc(c['field']), esc(c['a_label']), esc(c['a_url']), esc(str(c['a'])), esc(c['b_label']), esc(c['b_url']), esc(str(c['b'])), esc(c.get('note') or '')) for c in MC)))
    return ''.join(o)
_m_prev_bc = build_content
def build_content():
    _m_prev_bc()
    add_page('mobs.html', 'Mob lookup', body_html=_mobs_page(), section='mobs',
             sources=['Wiki zone pages (NPC and named tables)|%sZones' % WIKI, 'Wiki mob pages (Category:NPCs)|%sCategory:NPCs' % WIKI, 'Wiki item pages (drop sources)|%sCategory:Items' % WIKI,
                      'mnm-db.com: player loot ledgers (data.json beta, data-ea.json early access), /con level estimates (mob-levels.json)|https://mnm-db.com/'], desc='Mob lookup')
    add_page('source-conflicts.html', 'Source conflicts (wiki vs mnm-db.com)', body_html=_conflicts_page(), section='mobs',
             sources=['content/source_conflicts.json, generated by tools/mnmdb_merge.py|https://mnm-db.com/', 'M&M Wiki|%s' % WIKI], desc='Where the wiki and mnm-db.com disagree')
_m_prev_ra = render_all
def render_all():
    _m_prev_ra()
    urls = {n: it.get('url', '') for n, it in ITEMS.items()}
    D = _mobs_db()
    open(os.path.join(OUT, 'assets', 'mobs-db.js'), 'w', encoding='utf8').write('window.MNM_MOBS=' + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + ';window.MNM_IURL=' + json.dumps({n: urls[n] for r in D for n in r[8]}, ensure_ascii=False, separators=(',', ':')) + ';')
NAV.insert(len(NAV) - 1, ('Mobs', '/mobs.html', 'mobs'))

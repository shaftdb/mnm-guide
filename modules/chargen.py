# Character creation module: Race + Starting City selectors in the top bar (localStorage mnm-race / mnm-city + URL ?race=&city=&class=),
# /walkthrough.html (new-character walkthrough built from existing zone, quest, faction, spell and item data),
# a Character Creation section on class quick-reference pages (data/chargen/<class>.json when written; start-city/stat tables for all),
# and the site-wide footer credit line.
# Facts: data/chargen/races.json (tools/chargen_extract.py from cached wiki pages). Recommendations in data/chargen/<class>.json are STRATEGY.
_CGD = os.path.join(ROOT, 'data', 'chargen')
CG = json.load(open(os.path.join(_CGD, 'races.json'), encoding='utf8'))
CGC = {}
for _f in sorted(glob.glob(os.path.join(_CGD, '*.json'))):
    if os.path.basename(_f) != 'races.json':
        _d = json.load(open(_f, encoding='utf8')); CGC[_d['class']] = _d
CG_LARGE = CG['large']
CG_FAQ = 'https://monstersandmemories.com/early-access-faq'
CG_CITY_FAQ = {  # official Early Access FAQ wording (FACT)
    'Night Harbor': 'Good and neutral race/faith/class combinations can start here.',
    'Underdocks': 'Some neutral and evil race/faith/class combinations have the option of starting here (a port district far below Night Harbor).',
    'Faelindral': 'Wood Elves and Halflings have the option of starting here.',
    "Ail'Vorith": 'Various evil race/faith/class combinations can start here (deep below the eastern lands of Calafrey).'}

def _cg_combos():
    """class -> race -> [cities] from the wiki start-city table."""
    out = {}
    for race, cl in CG['combos'].items():
        for c, cities in cl.items():
            out.setdefault(c, {})[race] = [x for x in CG['cities'] if x in cities]
    return out
CG_BY_CLASS = _cg_combos()

def _cg_official_races(c):
    return [r.strip() for r in (globals().get('_OFFICIAL') or {}).get(c, {}).get('races', '').split(',') if r.strip()]

# ------------------------------------------------------------------ top bar
RANGEBAR_HTML = RANGEBAR_HTML.replace(
    '<label class="rb-f"><span class="range-lab">Levels</span>',
    '<label class="rb-f cg-f"><span class="range-lab">Race</span><select id="mnm-race" aria-label="Race"></select></label>'
    '<label class="rb-f cg-f"><span class="range-lab">Start</span><select id="mnm-city" aria-label="Starting city"></select></label>'
    '<label class="rb-f"><span class="range-lab">Levels</span>', 1)
TEMPLATE = TEMPLATE.replace('</head>', '<link rel="stylesheet" href="{root}assets/mod-chargen.css">\n</head>', 1).replace(
    '</body>', '<script src="{root}assets/chargen-data.js"></script>\n<script src="{root}assets/mod-chargen.js"></script>\n</body>', 1)
# footer credit: one plain small line, inherits the footer colour
TEMPLATE = TEMPLATE.replace('</footer>', '<div class="foot-credit">Made together by Brewologist &amp; Grok Bot</div></footer>', 1)

def _cg_topdata():
    races = {r: {'al': v.get('alignment'), 'lg': 1 if v.get('large') else 0} for r, v in CG['races'].items()}
    deities = {}
    for race, cl in CG['combos'].items():
        for c, cities in cl.items():
            for city, ds in cities.items(): deities['%s|%s|%s' % (c, race, city)] = ds
    return {'combos': CG_BY_CLASS, 'races': races, 'cities': CG['cities'], 'large': CG_LARGE, 'deities': deities,
            'chargen': {c: _cref(c)['overview'] if '_cref' in globals() else class_url(c) for c in CGC}}

# ------------------------------------------------------------------ helpers
def _cg_badge(l):
    l = (l or '').upper(); cls = {'FACT': 'fact', 'STRATEGY': 'strat'}.get(l, 'unc')
    return '<span class="badge %s">%s</span>' % (cls, esc(l.lower() or 'unverified'))
def _cg_srcs(c):
    D = CGC.get(c, {}); s = ['%s|%s' % (t, u) for t, u in D.get('sources', [])]
    st = CG['_source']['start_table']; s.append('Wiki: Starting City by Race, Class, and Deity (rev %s)|%s' % (st['revid'], st['url']))
    s.append('Official Early Access FAQ (starting areas)|%s' % CG_FAQ)
    seen, out = set(), []
    for x in s:
        if x.split('|')[1] not in seen: seen.add(x.split('|')[1]); out.append(x)
    return out

def chargen_section(c):
    """Character Creation section for class c (FACT tables for every class; STRATEGY blocks from data/chargen/<class>.json)."""
    D = CGC.get(c); rs = CG_BY_CLASS.get(c, {}); code = CABBR[c]
    o = ['<section class="cg-sec" id="character-creation"><h2 id="chargen">Character creation</h2>']
    o.append('<p class="dim">Pick your race and starting city in the top bar (<b>Race</b> / <b>Start</b>); parts of this section follow that pick. '
             '<span class="badge fact">fact</span> = wiki or official page, <span class="badge strat">strategy</span> = this Codex\'s suggestion, <span class="badge unc">unverified</span> = not sourced yet.</p>')
    # races & cities table
    rows = []
    for r in sorted(rs, key=lambda r: (r in CG_LARGE, r)):
        R = CG['races'].get(r, {}); st = (R.get('start') or {}).get(c)
        stats = ' '.join('%s %s' % (k, v) for k, v in (st or {}).get('stats', {}).items() if v is not None) if st else ''
        note = ' <span class="badge unc">large race</span> <span class="dim">valid, but this Codex never defaults to or recommends it</span>' if r in CG_LARGE else ''
        rows.append('<tr data-cg-race="%s"><td><a class="ext" href="%s" target="_blank" rel="noopener">%s</a>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            esc(r), esc(R.get('url', wiki(r))), esc(r), note, esc(R.get('alignment') or '?'), ', '.join(esc(x) for x in rs[r]),
            esc(stats) or '<span class="dim">not on wiki</span>', esc((st or {}).get('bonus') if st and st.get('bonus') is not None else '?')))
    planned = [r for r in _cg_official_races(c) if r not in rs]
    o.append('<h3>Races and starting cities %s</h3>' % _cg_badge('FACT'))
    o.append('<div class="tw"><table class="grid cg-races"><thead><tr><th>Race</th><th>Alignment</th><th>Can start in</th><th>Starting stats (%s)</th><th>Bonus pts</th></tr></thead><tbody>%s</tbody></table></div>' % (esc(c), ''.join(rows)))
    o.append('<p class="dim">From the wiki <a class="ext" href="%s" target="_blank" rel="noopener">start-city table</a> (any deity) and each race page. %s</p>' % (
        esc(CG['_source']['start_table']['url']),
        ('Also listed on the official class page but not playable in Early Access: %s.' % esc(', '.join(planned))) if planned else ''))
    off = set(_cg_official_races(c)); miss = [r for r in rs if off and r not in off]
    if miss: o.append('<p>%s The wiki table allows %s, but the official class page does not list %s.</p>' % (_cg_badge('UNVERIFIED'), esc(c), esc(', '.join(miss))))
    if not D:
        o.append('<p>%s No stat, trait or race recommendations written for %s yet: no sourced data yet. The <a href="/walkthrough.html">walkthrough</a> still works for this class.</p></section>' % (_cg_badge('UNVERIFIED'), esc(c)))
        return ''.join(o)
    # stats
    o.append('<h3>Stat points</h3><p>%s Class modifier: %s. Every listed race gets <b>10 bonus points</b> at creation (wiki race pages).</p>' % (_cg_badge('FACT'), esc(D['class_mod'])))
    M = D.get('mana')
    if M:
        per = ''
        if M.get('stat') == 'INT/WIS':
            per = ''.join('<span data-cg-race="%s" class="cg-res">%s %s: INT %s, WIS %s, so your mana stat is <b>%s</b>.</span>' % (
                esc(r), esc(r), esc(c), st['INT'], st['WIS'], 'INT' if st['INT'] > st['WIS'] else ('WIS' if st['WIS'] > st['INT'] else 'INT or WIS (tied at creation)'))
                for r in rs if r not in CG_LARGE for st in [((CG['races'].get(r, {}).get('start') or {}).get(c) or {}).get('stats')] if st and st.get('INT') and st.get('WIS'))
        o.append('<p>%s Mana: %s %s</p>' % (_cg_badge(M.get('label')), esc(M['text']), per))
    if D.get('wiki_advice'):
        o.append('<details class="cg-facts"><summary>Wiki creation advice for %s %s</summary><p>%s</p><p class="dim">Quoted from the community wiki class page; it is advice, not a game rule.</p></details>' % (esc(c), _cg_badge('FACT'), esc(D['wiki_advice'])))
    o.append('<details class="cg-facts"><summary>What each stat does (wiki) %s</summary><ul class="tight">%s</ul></details>' % (_cg_badge('FACT'), ''.join('<li><b>%s</b>: %s</li>' % (esc(k), esc(v)) for k, v in D['stat_facts'])))
    cards = []
    for b in D['builds']:
        per_race = ''.join('<span data-cg-race="%s" class="cg-res">%s: %s</span>' % (esc(r), esc(r), esc(', '.join(
            '%s %s' % (k, (CG['races'][r]['start'][c]['stats'].get(k) or 0) + b['alloc'].get(k, 0)) for k in ['STR', 'STA', 'DEX', 'AGI', 'INT', 'WIS', 'CHA'])))
            for r in rs if r not in CG_LARGE and (CG['races'].get(r, {}).get('start') or {}).get(c))
        cards.append('<div class="cg-card"><h4>%s %s</h4><p class="cg-alloc">%s</p><p>%s</p><p class="dim">Result: %s</p></div>' % (
            esc(b['name']), _cg_badge('STRATEGY'), esc(' · '.join('+%d %s' % (v, k) for k, v in b['alloc'].items())), esc(b['why']), per_race))
    o.append('<div class="cg-cards">%s</div><p class="dim">%s %s</p>' % (''.join(cards), _cg_badge('UNVERIFIED'), esc(D['build_caveat'])))
    # traits
    tl = []
    for t in D['traits']:
        info = {x['name']: x for x in CG['traits'].get(t['cat'], [])}
        def tdesc(n):
            x = info.get(n.split(' (')[0]); return esc(x['desc']) if x else '<span class="dim">not on Template:Traits</span>'
        rp = ''.join('<p class="cg-racepick" data-cg-race="%s" data-cg-only="1">For a %s: <b>%s</b>.</p>' % (esc(r), esc(r), esc(p)) for r, p in (t.get('race_pick') or {}).items())
        tl.append('<div class="cg-trait"><h4>%s: %s %s</h4><p class="dim">%s</p><p>%s</p>%s<p class="dim">Alternatives: %s</p></div>' % (
            esc(t['cat'].replace(' Traits', '')), esc(t['pick']), _cg_badge('STRATEGY'), tdesc(t['pick']), esc(t['why']), rp, esc(', '.join(t['alt']))))
    o.append('<h3>Traits</h3><p>%s You pick one Major Combat, one Minor Combat, one Major Non-Combat and one Minor Non-Combat trait; your race also grants a racial ability (wiki Traits).</p>%s<p class="dim">%s</p>' % (
        _cg_badge('FACT'), ''.join(tl), esc(D['trait_caveat'])))
    # races pros/cons
    rc = []
    for r, v in D['races'].items():
        R = CG['races'].get(r, {})
        rc.append('<div class="cg-card cg-race" data-cg-race="%s"><h4>%s %s</h4><p class="dim">%s %s · racial: %s · resists: %s · starts (%s): %s</p><p><b>Pros</b></p><ul class="tight">%s</ul><p><b>Cons</b></p><ul class="tight">%s</ul></div>' % (
            esc(r), esc(r), _cg_badge('STRATEGY'), _cg_badge('FACT'), esc(R.get('alignment') or '?'), esc(R.get('racial') or 'not documented'), esc(R.get('resists') or 'not documented'),
            esc(c), esc(', '.join(rs.get(r, []))), ''.join('<li>%s</li>' % esc(x) for x in v['pros']), ''.join('<li>%s</li>' % esc(x) for x in v['cons'])))
    lg = [r for r in rs if r in CG_LARGE]
    o.append('<h3>Race pros and cons</h3><div class="cg-cards">%s</div>%s%s' % (''.join(rc),
        ''.join('<p class="dim">%s: %s</p>' % (esc(r), esc(n)) for r, n in D.get('planned_races', {}).items()),
        ('<p class="dim">Large races (%s) are valid for %s but are never defaulted to or recommended here.</p>' % (esc(', '.join(lg)), esc(c))) if lg else ''))
    # tradeskills
    T = D['tradeskills']; names = {slug(n): n for n in TS_ORDER} if 'TS_ORDER' in globals() else {}
    tli = ''.join('<li><a href="/trades/%s.html">%s</a>: %s</li>' % (s, esc(names.get(s, s)), esc(T['why'].get(s, ''))) for s in T['recommend'])
    o.append('<h3>Tradeskills %s</h3><ul class="tight">%s</ul><p class="dim">%s</p><p><button type="button" class="cg-ts-apply" data-ts=\'%s\'>Use these in my Trades picker</button> <span class="cg-ts-msg dim" aria-live="polite"></span></p>' % (
        _cg_badge('STRATEGY'), tli, esc(T['note']), json.dumps(T['recommend'])))
    # night harbor
    N = D.get('night_harbor')
    if N: o.append(cg_nh_html(N))
    o.append('</section>')
    return ''.join(o)

def cg_nh_html(N):
    li = ''.join('<li><b>%s</b> %s: %s <i>%s</i></li>' % (zlink(x['city']), _cg_badge(x['label']), esc(x['distance']), esc(x['inq'])) for x in N['cities'])
    return ('<h3 id="night-harbor">Starting near Night Harbor</h3><p>%s %s</p><ul>%s</ul><p><b>Best Inquisitor start outside Night Harbor</b> %s %s</p><p class="dim">%s %s Sources: <a class="ext" href="%s" target="_blank" rel="noopener">wiki start-city table</a>, '
            '<a class="ext" href="%s" target="_blank" rel="noopener">official Early Access FAQ</a>, wiki <a class="ext" href="%s" target="_blank" rel="noopener">Underdocks</a> and <a class="ext" href="%s" target="_blank" rel="noopener">Ail\'Vorith</a>.</p>') % (
        _cg_badge('FACT'), esc(N['summary']), li, _cg_badge('STRATEGY'), esc(N['best']), _cg_badge('UNVERIFIED'), esc(N['caveat']), esc(CG['_source']['start_table']['url']), CG_FAQ,
        esc(CG['city_info']['Underdocks']['url']), esc(CG['city_info']["Ail'Vorith"]['url']))

# ------------------------------------------------------------------ walkthrough data
def _cg_dist(start):
    adj = {}
    for z, Z in ZONES.items():
        for a in Z.get('adjacent', []): adj.setdefault(z, set()).add(a); adj.setdefault(a, set()).add(z)
    for z, ci in CG['city_info'].items():
        for a in ci.get('adjacent', []): adj.setdefault(z, set()).add(a); adj.setdefault(a, set()).add(z)
    d = {start: 0}; q = [start]
    while q:
        z = q.pop(0)
        for a in sorted(adj.get(z, ())):
            if a not in d: d[a] = d[z] + 1; q.append(a)
    return d
def _cg_minlvl(s):
    m = re.search(r'\d+', s or ''); return int(m.group()) if m else None
def _cg_walkdata():
    FG = json.load(open(os.path.join(DATA, 'faction_guide.json'), encoding='utf8'))
    zslug = {slug(z): z for z in ZONES}
    zones = {}
    for z, Z in ZONES.items():
        lo, hi, src = _lvl_range(z)
        mobs = {e['name'].lower() for e in Z['npcs'] + Z['named']}
        camps = [[e['name'], e['level'], (e.get('loot') or '').strip('- ')] for e in _zone_named_sorted(Z) if lvl_num(e['level'])][:12]
        raise_, lower = [], []
        for fn, F in FG.items():
            hit = [m for m in F.get('mobs_raise', []) if m.lower() in mobs]
            if hit or z in F.get('zones_raise', []): raise_.append([fn, hit[:3]])
            hl = [m for m in F.get('mobs_lower', []) if m.lower() in mobs]
            if hl or z in F.get('zones_lower', []): lower.append([fn, hl[:3]])
        zones[z] = {'u': zone_url(z), 'lo': lo, 'hi': hi, 'est': 0 if src.startswith('wiki zone') else 1, 'camps': camps, 'fr': raise_[:6], 'fl': lower[:6],
                    'dg': 1 if z in DUNGEON_ORDER else 0}
    cities = {}
    for city in CG['cities']:
        home = [fn for fn in FG if city.lower().replace("'", '') in fn.lower().replace("'", '')]
        cities[city] = {'dist': {k: v for k, v in _cg_dist(city).items() if k in ZONES}, 'home': home, 'faq': CG_CITY_FAQ.get(city, ''),
                        'u': CG['city_info'][city]['url'], 'tr': CG['city_info'][city]['trainers']}
    quests = []
    for n, Q in QUESTS.items():
        if Q.get('zone') not in ZONES: continue
        quests.append([n, Q['url'], Q['zone'], _cg_minlvl(Q.get('min_level')), (Q.get('classes') or 'ALL'), ', '.join(Q.get('rewards') or [])[:160]])
    spells = {c: [[sp.get('spell name'), sp.get('level') or 0, sp.get('location') or ''] for sp in CLASSES[c]['spells'] if sp.get('spell name')] for c in CLASS_LIST}
    items, ix, gear = [], {}, {}
    for c in CLASS_LIST:
        lst = []
        for it, lv, kinds in easy_items(CABBR[c]):
            if lv is None or len(class_codes(it)) >= 18: continue
            nm = it['name']
            if nm not in ix:
                zs = sorted({zslug[s] for s in re.findall(r'/(?:zones|dungeons)/([a-z0-9-]+)\.html', ' '.join(d for _, _, d in acquisitions(it))) if s in zslug})
                ix[nm] = len(items); items.append([nm, it['url'], ', '.join(slots_of(it)), lv, ' '.join(sorted(kinds)), zs, 1 if it.get('magic') else 0])
            lst.append(ix[nm])
        gear[c] = lst
    walk = {}
    for c, D in CGC.items():
        for city, steps in D.get('walk_notes', {}).items(): walk['%s|%s' % (c, city)] = steps
    races = {r: {'al': v.get('alignment'), 'racial': v.get('racial'), 'note': v.get('note'), 'u': v['url']} for r, v in CG['races'].items()}
    return {'bands': [[k, k.replace('-', '\u2013')] for k in RANGE_ORDER], 'zones': zones, 'cities': cities, 'quests': quests,
            'spells': spells, 'items': items, 'gear': gear, 'walk': walk, 'races': races, 'codes': CABBR, 'gearurl': {c: '/gear/%s.html' % ('shaman' if c == 'Shaman' else slug(c)) for c in CLASS_LIST},
            'nh': {c: D['night_harbor'] for c, D in CGC.items() if D.get('night_harbor')}}

def _cg_walk_page():
    return ('<link rel="stylesheet" href="/assets/mod-chargen.css">'
            '<p>A step-by-step plan for a new character, built for the <b>class</b>, <b>race</b>, <b>starting city</b> and <b>level range</b> picked in the top bar (all remembered in this browser and kept in the page link). '
            'Everything listed comes from this Codex\'s wiki data (zones, named camps, quests, factions, spells, gear) and is marked <span class="badge fact">fact</span>; the order and "when to move" advice is <span class="badge strat">strategy</span>. '
            'Where nothing is sourced it says so instead of guessing.</p>'
            '<div id="cg-walk" class="cg-walk" aria-live="polite"><p class="dim">Loading… (needs JavaScript)</p></div>'
            '<script src="/assets/walk-data.js"></script>')

_cg_prev_ra = render_all
def render_all():
    if 'walkthrough' not in [k for _, _, k in NAV]:
        NAV.append(('New-character walkthrough', '/walkthrough.html', 'walkthrough'))
        if 'NAV_GROUPS' in globals(): NAV_GROUPS[0][1].append('walkthrough')
        add_page('walkthrough.html', 'New-character walkthrough', body_html=_cg_walk_page(), section='walkthrough', desc='Step-by-step new character walkthrough by class, race and city',
                 sources=['Wiki: Starting City by Race, Class, and Deity|%s' % CG['_source']['start_table']['url'], 'Official Early Access FAQ (starting areas)|%s' % CG_FAQ,
                          'Wiki zone, quest and faction pages (see each linked page)|%sZones' % WIKI])
        for p in PAGES:
            m = re.match(r'classref/([a-z-]+)/index\.html$', p['path'])
            if m or p['path'] == 'shaman/index.html':
                c = next((x for x in CLASS_LIST if slug(x) == m.group(1)), None) if m else 'Shaman'
                if c:
                    p['body'] += chargen_section(c)
                    if c in CGC:
                        p['sources'] = (p['sources'] or [s.strip() for s in p['meta'].get('sources', '').split(';') if s.strip()]) + _cg_srcs(c)
                    toc = p['ctx'].setdefault('toc', [])
                    if toc: toc.append(('chargen', 'Character creation'))
    _cg_prev_ra()
    open(os.path.join(OUT, 'assets', 'chargen-data.js'), 'w', encoding='utf8').write('window.MNM_CG=' + json.dumps(_cg_topdata(), ensure_ascii=False, separators=(',', ':')) + ';')
    open(os.path.join(OUT, 'assets', 'walk-data.js'), 'w', encoding='utf8').write('window.MNM_WT=' + json.dumps(_cg_walkdata(), ensure_ascii=False, separators=(',', ':')) + ';')

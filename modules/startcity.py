# Start-city routes module: data/startcities/<city>.json (one file per starting city) drives the early leveling path everywhere a
# level band is shown: /leveling.html, class leveling pages, Quick info panels (home page), the class page "Quick info by level" note
# and /walkthrough.html. Every city gets a block; CSS (html[data-sc]) shows only the one picked in the top bar Start selector, so
# nothing silently falls back to Night Harbor. Class- and race-only lines are hidden by html[data-scc] / html[data-scr].
_SCD = os.path.join(ROOT, 'data', 'startcities')
SC = {}
for _f in sorted(glob.glob(os.path.join(_SCD, '*.json'))):
    _d = json.load(open(_f, encoding='utf8')); SC[_d['city']] = _d
SC_CITIES = list(CG['cities'])  # same order as the Start selector
SC_STATUS = {'sourced': ('fact', 'sourced route'), 'partial': ('unc', 'partial route'), 'stub': ('unc', 'no sourced route yet')}

def _sc_srcs(D, keys):
    S = D.get('sources', {}); out = []
    for k in keys or []:
        if k in S:
            t, u = S[k]
            out.append('<a href="%s">%s</a>' % (esc(u), esc(t)) if u.startswith('/') else '<a class="ext" target="_blank" rel="noopener" href="%s">%s</a>' % (esc(u), esc(t)))
    return ('<span class="sc-src">Source: %s</span>' % ', '.join(out)) if out else ''
def _sc_filt(item):
    """attributes + label for class- or race-only lines"""
    a, who = '', []
    if item.get('classes'):
        a += ' data-scc="%s"' % esc(' '.join(slug(c) for c in item['classes'])); who.append(', '.join(item['classes']))
    if item.get('races'):
        a += ' data-scr="%s"' % esc(' '.join(slug(r) for r in item['races'])); who.append(', '.join(item['races']))
    cls = (' sc-fc' if item.get('classes') else '') + (' sc-fr' if item.get('races') else '')
    return cls, a, ('<span class="sc-who">%s only</span> ' % esc(' · '.join(who))) if who else ''
def _sc_tag(t):
    return '<span class="sc-tag %s">%s</span>' % ('sc-rec' if t == 'Recommended' else 'sc-opt', esc(t)) if t else ''
def _sc_qlinks(title):
    l = ['<a class="ext" target="_blank" rel="noopener" href="%s">wiki</a>' % esc(wiki(title))]
    if title in globals().get('QSTEPS', {}): l.append('<a href="/quest-helper.html#q-%s">quest helper</a>' % slug(title))
    return ' · '.join(l)

def sc_quest(D, qid):
    """inline collapsible walkthrough for quest qid of city file D"""
    Q = D['quests'].get(qid)
    if not Q: return ''
    if Q.get('auto'):  # from the wiki walkthrough data used by the quest helper
        t = Q['auto']; q = globals().get('QSTEPS', {}).get(t)
        if not q:
            return '<details class="sc-q"><summary><b>%s</b> %s</summary><p>%s No walkthrough in this Codex\'s wiki data: no sourced data yet.</p><p class="sc-ql">%s</p></details>' % (esc(t), _sc_tag(Q.get('tag')), _cg_badge('UNVERIFIED'), _sc_qlinks(t))
        st = []
        for k, v in q['steps']:
            if k == 'h': st.append('<li class="sc-qh"><b>%s</b></li>' % esc(v))
            elif k == 'xp': st.append('<li class="dim">Experience</li>')
            else: st.append('<li%s>%s%s</li>' % (' class="dim"' if k in ('info', 'fac', 'get') else '', {'get': 'Receive: ', 'fac': 'Faction: ', 'info': 'Note: '}.get(k, ''), esc(v)))
        fac = list(dict.fromkeys(v for k, v in q['steps'] if k == 'fac')); got = [v for k, v in q['steps'] if k == 'get']
        # city files may add sourced detail the wiki walkthrough lacks: where, prereq, turnin, mobs [{item, from}], notes [{label, text, src}];
        # giver (overrides, for a documented giver conflict), faction and rewards (used only when the walkthrough data has none)
        where = esc(q.get('zone') or 'no sourced data yet') + ((' · ' + esc(Q['where'])) if Q.get('where') else '')
        rows = [('Giver', esc(Q.get('giver') or q.get('giver') or 'no sourced data yet')), ('Where', where), ('Level', esc(q.get('min') or 'not listed')),
                ('Classes', esc(', '.join(q['classes'])) if q['classes'] else 'any'), ('Needs first', esc(Q.get('prereq') or 'none listed')),
                ('Faction', esc('; '.join(fac)) if fac else esc(Q.get('faction') or 'no sourced data yet')),
                ('Turn in', esc(Q.get('turnin') or 'see the steps below (wiki walkthrough)')),
                ('Rewards', esc(q.get('rewards') or '; '.join(got) or Q.get('rewards') or 'no sourced data yet'))]
        mobs = ''.join('<li><b>%s</b>: %s</li>' % (esc(m['item']), esc(m['from'])) for m in Q.get('mobs', []))
        notes = ''.join('<p>%s %s %s</p>' % (_cg_badge(n['label']), esc(n['text']), _sc_srcs(D, n['src'])) for n in Q.get('notes', []))
        return ('<details class="sc-q" id="scq-%s-%s"><summary><b>%s</b> %s <span class="dim">lvl %s</span></summary><p class="sc-why">%s %s</p><table class="kv sc-kv">%s</table>'
                '%s<ol class="tight sc-steps">%s</ol>%s%s<p class="sc-ql">%s %s · wiki walkthrough updated %s</p></details>') % (
            esc(D['slug']), esc(qid), esc(t), _sc_tag(Q.get('tag')), esc(q.get('min') or '?'), _cg_badge('STRATEGY'), esc(Q.get('why', '')),
            ''.join('<tr><th>%s</th><td>%s</td></tr>' % r for r in rows), ('<h5>Mobs and items</h5><ul class="tight">%s</ul>' % mobs) if mobs else '',
            ''.join(st) or '<li>no sourced data yet</li>',
            ('<p>%s The wiki marks this quest page as needing more info; missing steps: no sourced data yet.</p>' % _cg_badge('UNVERIFIED')) if q.get('needsinfo') else '',
            notes, _cg_badge('FACT'), _sc_qlinks(t), esc(q.get('ts', '')))
    R = Q.get('rewards', {})
    rows = [('Giver', Q['giver']), ('Where', Q['where']), ('Level', Q['level']), ('Classes', ', '.join(Q['classes']) if Q.get('classes') else 'any'),
            ('Needs first', Q.get('prereq') or 'none listed'), ('Faction', Q.get('faction') or 'no sourced data yet')]
    mobs = ''.join('<li><b>%s</b>: %s</li>' % (esc(m['item']), esc(m['from'])) for m in Q.get('mobs', []))
    steps = ''.join('<li>%s%s</li>' % ((_cg_badge(s['label']) + ' ') if s.get('label') else '', esc(s['text'])) for s in Q['steps'])
    notes = ''.join('<p>%s %s %s</p>' % (_cg_badge(n['label']), esc(n['text']), _sc_srcs(D, n['src'])) for n in Q.get('notes', []))
    return ('<details class="sc-q" id="scq-%s-%s"><summary><b>%s</b> %s <span class="dim">lvl %s</span></summary><p class="sc-why">%s %s</p>'
            '<table class="kv sc-kv">%s</table><h5>Steps %s</h5><ol class="tight sc-steps">%s</ol>%s<p><b>Turn in:</b> %s</p>'
            '<p><b>Rewards:</b> XP: %s · Item: %s · Coin: %s · Faction: %s</p>%s<p class="sc-ql">%s · %s</p></details>') % (
        esc(D['slug']), esc(qid), esc(Q['name']), _sc_tag(Q.get('tag')), esc(Q['level']), _cg_badge('STRATEGY'), esc(Q.get('why', '')),
        ''.join('<tr><th>%s</th><td>%s</td></tr>' % (k, esc(v)) for k, v in rows), _cg_badge(Q.get('label', 'FACT')), steps,
        ('<h5>Mobs and items</h5><ul class="tight">%s</ul>' % mobs) if mobs else '', esc(Q.get('turnin', 'no sourced data yet')),
        esc(R.get('xp', 'no sourced data yet')), esc(R.get('item', 'no sourced data yet')), esc(R.get('coin', 'no sourced data yet')), esc(R.get('faction', 'no sourced data yet')),
        notes, _sc_qlinks(Q['wiki']), _sc_srcs(D, Q.get('src')))

def _sc_trainers(D, city):
    tr = D.get('trainers') or {}; base = CG['city_info'].get(city, {}).get('trainers', {}); out = []
    for c in CLASS_LIST:
        t = tr.get(c)
        if t:
            body = '%s <b>%s</b> (%s)%s %s' % (_cg_badge(t.get('label', 'FACT')), esc(t['npc']), esc(t['where']), (' ' + esc(t['note'])) if t.get('note') else '', _sc_srcs(D, t.get('src')))
        elif base.get(c):
            body = '%s %s <span class="sc-src">Source: wiki %s page</span>' % (_cg_badge('FACT'), ', '.join('<b>%s</b>%s' % (esc(x['npc']), (' (%s)' % esc(x['where'])) if x.get('where') else '') for x in base[c]), esc(city))
        else:
            body = '%s No %s trainer listed on the wiki %s page: no sourced data yet.' % (_cg_badge('UNVERIFIED'), esc(c), esc(city))
        out.append('<li class="sc-fc" data-scc="%s"><span class="sc-who">%s trainer</span> %s</li>' % (slug(c), esc(c), body))
    return ''.join(out)
def _sc_spells(lo, hi, D, city):
    out = []
    for c in CLASS_LIST:
        sp = sorted([(s.get('level') or 0, s.get('spell name')) for s in CLASSES[c]['spells'] if s.get('spell name') and lo <= (s.get('level') or 0) <= hi])
        t = (D.get('trainers') or {}).get(c) or {}; who = t.get('npc') or ', '.join(x['npc'] for x in CG['city_info'].get(city, {}).get('trainers', {}).get(c, [])) or 'your class trainer'
        if sp:
            lv = {}
            for l, n in sp: lv.setdefault(l, []).append(n)
            txt = '; '.join('L%d %s' % (l, ', '.join(ns)) for l, ns in sorted(lv.items()))
            out.append('<li class="sc-fc" data-scc="%s">%s <span class="sc-who">%s spells</span> Buy or train each as you reach its level (%s): %s. <a href="%s">Full list</a></li>' % (
                slug(c), _cg_badge('FACT'), esc(c), esc(who), esc(txt), esc(_cref(c)['spells'] if '_cref' in globals() else '/spells.html')))
        else:
            out.append('<li class="sc-fc" data-scc="%s">%s <span class="sc-who">%s spells</span> No %s spells with a wiki level in %d–%d.</li>' % (slug(c), _cg_badge('FACT'), esc(c), esc(c), lo, hi))
    return ''.join(out)

def _sc_item(D, city, s, seen):
    cls, attrs, who = _sc_filt(s)
    if s.get('trainer'): return _sc_trainers(D, city)
    q = ''
    if s.get('quest'):
        if s['quest'] in seen: q = ' <span class="dim">(walkthrough above)</span>'
        else: seen.add(s['quest']); q = sc_quest(D, s['quest'])
    return '<li class="sc-step%s"%s>%s%s %s %s%s</li>' % (cls, attrs, who, _cg_badge(s['label']), esc(s['text']), _sc_srcs(D, s.get('src')), q)

def sc_route(lo, hi, nhnote=False):
    """route blocks for every start city for levels lo-hi; CSS shows the selected one"""
    o = ['<div class="sc-wrap"><p class="sc-pick">%s No start city picked: choose one in the <b>Start</b> box in the top bar to see its route for levels %d–%d.</p>' % (_cg_badge('UNVERIFIED'), lo, hi)]
    for city in SC_CITIES:
        D = SC.get(city) or {'city': city, 'slug': slug(city), 'status': 'stub', 'bands': [], 'quests': {}, 'sources': {}}
        st = SC_STATUS.get(D['status'], SC_STATUS['stub'])
        h = ['<div class="sc-route" data-sc="%s"><h3 class="sc-h">Start-city route: %s · levels %d–%d <span class="badge %s">%s</span></h3>' % (esc(D['slug']), esc(city), lo, hi, st[0], st[1])]
        bands = [b for b in D['bands'] if b['lo'] <= hi and b['hi'] >= lo]
        if not bands:
            h.append('<p>%s No sourced %s route for levels %d–%d yet: no sourced data yet. The zone lists on this page are for every start city, not a %s route.</p>' % (_cg_badge('UNVERIFIED'), esc(city), lo, hi, esc(city)))
        seen = set()
        for b in bands:
            items = ''.join(_sc_item(D, city, s, seen) for s in b['steps'])
            if D['status'] != 'stub': items += _sc_spells(max(lo, b['lo']), min(hi, b['hi']), D, city)
            h.append('<h4 class="sc-bh">Levels %d–%d: %s</h4><ul class="sc-steps-list">%s</ul>' % (b['lo'], b['hi'], esc(b['title']), items))
        if nhnote and city != 'Night Harbor':
            h.append('<p class="sc-nhnote">%s The class notes below were written for a <b>Night Harbor</b> start (Night Harbor gates, the Night Market forge, Night Harbor camps). You picked %s: use the route above for where to go.</p>' % (_cg_badge('UNVERIFIED'), esc(city)))
        o.append(''.join(h) + '</div>')
    return ''.join(o) + '</div>'

def sc_head():
    """city overview: intro, faction / KoS, travel, money; one block per city"""
    o = ['<div class="sc-wrap sc-headwrap"><p class="sc-pick">%s No start city picked: choose one in the <b>Start</b> box in the top bar.</p>' % _cg_badge('UNVERIFIED')]
    for city in SC_CITIES:
        D = SC.get(city) or {'city': city, 'slug': slug(city), 'status': 'stub', 'intro': [], 'faction': [], 'travel': [], 'money': [], 'sources': {}}
        st = SC_STATUS.get(D['status'], SC_STATUS['stub'])
        def lst(key):
            return ''.join('<li class="sc-step%s"%s>%s%s %s %s</li>' % (_sc_filt(x)[0], _sc_filt(x)[1], _sc_filt(x)[2], _cg_badge(x['label']), esc(x['text']), _sc_srcs(D, x.get('src'))) for x in D.get(key, []))
        h = ['<div class="sc-route" data-sc="%s"><h2 class="sc-h">Starting in %s <span class="badge %s">%s</span></h2>' % (esc(D['slug']), esc(city), st[0], st[1])]
        h.append('<ul class="sc-steps-list">%s</ul>' % (lst('intro') or '<li>%s no sourced data yet</li>' % _cg_badge('UNVERIFIED')))
        for key, title, op in (('faction', 'Faction, KoS and when it is safe to travel', ' open'), ('travel', 'Getting around', ''), ('money', 'Money', '')):
            body = lst(key) or '<li>%s No sourced %s notes for %s yet: no sourced data yet.</li>' % (_cg_badge('UNVERIFIED'), key, esc(city))
            h.append('<details class="call sc-d"%s><summary><b>%s</b></summary><ul class="sc-steps-list">%s</ul></details>' % (op, title, body))
        if D.get('updated'): h.append('<p class="dim">Route data checked %s (%s). Labels: FACT = wiki or official page, STRATEGY = this Codex\'s suggestion, UNVERIFIED = community report, conflicting or missing data.</p>' % (esc(D['updated']), esc(D.get('generated_by', ''))))
        o.append(''.join(h) + '</div>')
    return ''.join(o) + '</div>'

def sc_summary():
    """compact band list per city for the class page 'Quick info by level' note"""
    o = ['<div class="sc-wrap"><p class="sc-pick">Pick your start city in the top bar to see its route by level.</p>']
    for city in SC_CITIES:
        D = SC.get(city) or {'slug': slug(city), 'status': 'stub', 'bands': []}
        li = ''.join('<li>Levels %d–%d: %s</li>' % (b['lo'], b['hi'], esc(b['title'])) for b in D['bands'])
        o.append('<div class="sc-route" data-sc="%s"><p><b>Your start: %s</b> %s</p>%s</div>' % (
            esc(D['slug']), esc(city), '<span class="badge %s">%s</span>' % SC_STATUS.get(D['status'], SC_STATUS['stub']),
            ('<ul class="tight">%s</ul><p class="dim">Each band\'s steps, camps and quest walkthroughs: <a href="/leveling.html">Leveling by band</a> and the <a href="/walkthrough.html">walkthrough</a>.</p>' % li) if li else
            '<p>%s No sourced %s route yet: no sourced data yet.</p>' % (_cg_badge('UNVERIFIED'), esc(city))))
    return ''.join(o) + '</div>'

GENS.update(route=lambda a, ctx: sc_route(*[int(x) for x in a.split(',')[:2]], nhnote='nh' in a.split(',')[2:]),
            schead=lambda a, ctx: sc_head(), scsummary=lambda a, ctx: sc_summary())

# every zones_band (class Quick info panels, class quick pages, class leveling tabs) starts with the start-city route
_sc_prev_zb = zones_band
def zones_band(lo, hi):
    return '<!--sc-route-->' + _sc_prev_zb(lo, hi).replace('<h3>Where to level %d–%d' % (lo, hi), '<h3>All zones for %d–%d (any start city)' % (lo, hi), 1)
_sc_prev_cq = class_quick
def class_quick(cls, lo, hi, shaman_html=None):
    h = _sc_prev_cq(cls, lo, hi, shaman_html)
    return h if '<!--sc-route-->' in h else h.replace('<div class="qi-sec">', '<!--sc-route-nh--><div class="qi-sec">', 2).replace('<!--sc-route-nh-->', '', 1)
def _sc_fill(h, lo, hi):
    return h.replace('<!--sc-route-->', '<div class="qi-sec sc-qi">%s</div>' % sc_route(lo, hi)).replace('<!--sc-route-nh-->', '<div class="qi-sec sc-qi">%s</div>' % sc_route(lo, hi, True))
_sc_prev_cb = g_classbands
def g_classbands(arg, ctx):
    h = _sc_prev_cb(arg, ctx); parts = h.split('<!--sc-route-->'); out = parts[0]
    for (lo, hi), p in zip(BAND_LIST, parts[1:]): out += _sc_fill('<!--sc-route-->', lo, hi) + p
    return out
GENS['classbands'] = g_classbands
_sc_prev_zbm = GENS.get('zones_band_md')
if _sc_prev_zbm:
    def _sc_zbm(arg, ctx):
        lo, hi = [int(x) for x in arg.split(',')]; return _sc_fill(_sc_prev_zbm(arg, ctx), lo, hi)
    GENS['zones_band_md'] = _sc_zbm
_sc_prev_cn = GENS.get('ccampsnote')
if _sc_prev_cn:
    GENS['ccampsnote'] = lambda a, ctx: _sc_prev_cn(a, ctx) + sc_head()
_sc_prev_gcq = GENS.get('classquick')
if _sc_prev_gcq:
    def _sc_gcq(arg, ctx):
        c, lo, hi = [a.strip() for a in arg.split(',')]; return _sc_fill(_sc_prev_gcq(arg, ctx), int(lo), int(hi))
    GENS['classquick'] = _sc_gcq
# Quick info panels: the route is stored once per band (MNM_QUICK.route) and site.js swaps it in for <!--sc-route-->
_sc_prev_wrd = write_range_data
def write_range_data(ranges):
    panels = _sc_prev_wrd(ranges)
    route = {k: sc_route(*[int(x) for x in k.split('-')]) for k in RANGE_ORDER}
    routenh = {k: sc_route(*[int(x) for x in k.split('-')], nhnote=True) for k in RANGE_ORDER}
    with open(os.path.join(OUT, 'assets', 'quick-data.js'), 'a', encoding='utf8') as f:
        f.write('window.MNM_QUICK.route=' + json.dumps(route, ensure_ascii=False, separators=(',', ':')) + ';')
        f.write('window.MNM_QUICK.routenh=' + json.dumps(routenh, ensure_ascii=False, separators=(',', ':')) + ';')
    return panels
# walkthrough data: route per band + city head
_sc_prev_wd = _cg_walkdata
def _cg_walkdata():
    d = _sc_prev_wd(); d['route'] = {k: sc_route(*[int(x) for x in k.split('-')]) for k in RANGE_ORDER}; d['schead'] = sc_head(); return d

def _sc_css():
    r = ['.sc-route,.sc-pick{display:none}', '.sc-route.sc-on{display:block}', 'html:not([data-sc]) .sc-pick{display:block}']
    for city in SC_CITIES: r.append('html[data-sc="%s"] .sc-route[data-sc="%s"]{display:block}' % (slug(city), slug(city)))
    for c in CLASS_LIST: r.append('html[data-scc="%s"] .sc-fc:not([data-scc~="%s"]){display:none}' % (slug(c), slug(c)))
    for rc in CG['races']: r.append('html[data-scr="%s"] .sc-fr:not([data-scr~="%s"]){display:none}' % (slug(rc), slug(rc)))
    return '\n'.join(r) + '\n'
_sc_prev_ra = render_all
def render_all():
    for p in PAGES:
        if re.match(r'classref/[a-z-]+/index\.html$', p['path']) or p['path'] == 'shaman/index.html':
            if p['path'] == 'shaman/index.html': p['body'] += '<h2 id="start-route">Quick info by level: your start-city route</h2>' + sc_summary()
            else: p['body'] = p['body'].replace('level range picked in the top bar.</p>', 'level range picked in the top bar.</p>' + sc_summary(), 1)
    _sc_prev_ra()
    base = open(os.path.join(ROOT, 'static', 'mod-startcity.css'), encoding='utf8').read() if os.path.exists(os.path.join(ROOT, 'static', 'mod-startcity.css')) else ''
    open(os.path.join(OUT, 'assets', 'mod-startcity.css'), 'w', encoding='utf8').write(base + _sc_css())
TEMPLATE = TEMPLATE.replace('</head>', '<link rel="stylesheet" href="{root}assets/mod-startcity.css">\n</head>', 1).replace(
    '<script src="{root}assets/mod-chargen.js"></script>', '<script src="{root}assets/mod-chargen.js"></script>\n<script src="{root}assets/mod-startcity.js"></script>', 1)

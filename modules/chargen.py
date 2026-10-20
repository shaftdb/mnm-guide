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
# Start-city audit (data/start_audit.json): records the wiki/official revisions checked and applies sourced overrides on top of
# the wiki start table (races.json). Each override is labelled and noted; the picker shows the note.
CG_AUDIT = json.load(open(os.path.join(ROOT, 'data', 'start_audit.json'), encoding='utf8'))
CG['_source']['audit'] = {'checked': CG_AUDIT['checked'], 'start_table_revid': CG_AUDIT['start_table']['revid']}
CG_NOTES = {}
for _o in CG_AUDIT.get('overrides', []):
    _cell = CG['combos'].setdefault(_o['race'], {}).setdefault(_o['class'], {})
    if _o['city'] not in _cell: _cell[_o['city']] = list(_o.get('deities') or [])
    CG_NOTES['%s|%s|%s' % (_o['class'], _o['race'], _o['city'])] = [_o.get('label') or 'UNVERIFIED', _o.get('note') or '']
# Combos an official patch note says are announced but not live yet (e.g. Deep Gnome Bard "coming soon", 0.30.3.2): removed from the
# pickers and rankings even if the wiki start table lists them, and shown as "not yet available" with the patch link.
CG_NYA = {}
for _o in CG_AUDIT.get('not_yet_available', []):
    CG['combos'].get(_o['race'], {}).pop(_o['class'], None)
    CG_NYA.setdefault(_o['class'], []).append(_o)
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
    '<label class="rb-f"><span class="range-lab">Levels</span>', 1).replace(
    '</div></div>', '<div class="cg-valid" id="cg-valid" aria-live="polite"></div></div></div>', 1)
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
    return {'combos': CG_BY_CLASS, 'races': races, 'cities': CG['cities'], 'large': CG_LARGE, 'deities': deities, 'notes': CG_NOTES,
            'playable': sorted(CG['combos']), 'audit': {'rev': CG_AUDIT['start_table']['revid'], 'checked': CG_AUDIT['checked'], 'url': CG_AUDIT['start_table']['url']},
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
    o.append(race_rank_html(c))
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


# ------------------------------------------------------------------ "Best races for <Class>" ranking (STRATEGY score built from FACT data)
# Score (0-100, STRATEGY): stat fit 0-50 (weighted by this Codex's builds for the class; -5 per point of weighted-average deficit vs the best race),
# racial ability 0-20 (class-role value of the documented racial; undocumented = 0, UNVERIFIED), vision trait 0-5, city access 0-15, size/upkeep penalties.
RR_ROLE = {'Fighter': 'tank', 'Paladin': 'tank', 'Shadow Knight': 'tank', 'Inquisitor': 'tank',
           'Rogue': 'melee', 'Monk': 'melee', 'Ranger': 'melee', 'Spellblade': 'melee', 'Bard': 'melee', 'Beastmaster': 'melee',
           'Archer': 'ranged', 'Wizard': 'caster', 'Elementalist': 'caster', 'Enchanter': 'caster', 'Necromancer': 'caster',
           'Cleric': 'healer', 'Druid': 'healer', 'Shaman': 'healer'}
# racial -> (value 0-10 by role, one-line reason). STRATEGY judgement on the wiki Template:Traits text.
RR_RACIAL = {
    'Tenacity': ({'tank': 8, 'melee': 6, 'ranged': 6, 'caster': 7, 'healer': 7}, 'mesmerize/incapacitate resistance and a 15 s immunity keep you acting'),
    'Stone Form': ({'tank': 9, 'melee': 7, 'ranged': 5, 'caster': 5, 'healer': 5}, '15 s of +25% AC and -10% physical damage, plus a disease/electric/poison cleanse'),
    'Slippery': ({'tank': 4, 'melee': 5, 'ranged': 8, 'caster': 7, 'healer': 5}, 'root resistance and a 15 s root/snare immunity, best for kiting'),
    'Hide': ({'tank': 3, 'melee': 5, 'ranged': 6, 'caster': 3, 'healer': 3}, 'unseen while still, useful for scouting and escapes'),
    'Sneak': ({'tank': 3, 'melee': 5, 'ranged': 5, 'caster': 3, 'healer': 3}, 'move unseen, useful for scouting and pulling'),
    'Bribe': ({'tank': 4, 'melee': 5, 'ranged': 4, 'caster': 5, 'healer': 4}, 'make a target forget past wrongdoings (a memory blur for bad pulls)'),
    'Ogre Smash': ({'tank': 7, 'melee': 6, 'ranged': 4, 'caster': 4, 'healer': 4}, 'a 2 s AoE stun on nearby targets'),
    'Forage': ({'tank': 2, 'melee': 2, 'ranged': 2, 'caster': 2, 'healer': 2}, 'Forage as a racial, so no trait slot is needed for it'),
}
RR_CLASS_RACIAL = {('Rogue', 'Sneak'): 9, ('Rogue', 'Hide'): 8, ('Ranger', 'Hide'): 7, ('Archer', 'Hide'): 7, ('Monk', 'Bribe'): 6, ('Enchanter', 'Bribe'): 6, ('Bard', 'Bribe'): 6}
RR_RCODE = {'Human': 'HUM', 'Wood Elf': 'ELF', 'Goblin': 'GOB', 'Ogre': 'OGR', 'Gnome': 'GNM', 'Dwarf': 'DWF', 'Deep Dwarf': 'DDF', 'Deep Elf': 'DEF',
            'Deep Gnome': 'DGN', 'Halfling': 'HFL', 'High Elf': 'HIE', 'Troll': 'TRL'}
RR_STATS = ['STR', 'STA', 'DEX', 'AGI', 'INT', 'WIS', 'CHA']

def _rr_racials(R):
    s = re.sub(r'\s*\(as of[^)]*\)', '', R.get('racial') or '')
    return [x.strip() for x in s.split(',') if x.strip()]
def _rr_vision(r):
    code = RR_RCODE.get(r); out = []
    for t in CG['traits'].get('Major Non-Combat Traits', []):
        if t['name'] in ('Infravision', 'Ultravision') and code and code in [x.strip() for x in t['race'].split(',')]: out.append(t['name'])
    return out
def _rr_weights(c):
    D = CGC.get(c) or {}; w = {}
    for i, b in enumerate(D.get('builds', [])):
        for k, v in b['alloc'].items(): w[k] = w.get(k, 0) + v * (2 if i == 0 else 1)
    return w

def race_rank(c):
    """Ranked list for class c: every race on the wiki start-city table for c."""
    rs = CG_BY_CLASS.get(c, {}); role = RR_ROLE.get(c, 'melee'); W_ = _rr_weights(c); D = CGC.get(c) or {}
    def st(r): return (((CG['races'].get(r, {}).get('start') or {}).get(c)) or {}).get('stats') or {}
    def fit(r):
        s = st(r); tw = sum(W_.values())
        if not tw or any(s.get(k) is None for k in W_): return None
        return sum(W_[k] * s[k] for k in W_) / tw
    fits = {r: fit(r) for r in rs}; best = max([f for f in fits.values() if f is not None] or [0])
    # playable-race stat extremes for the weighted stats (for generated pros/cons)
    rows = []
    for r in rs:
        R = CG['races'].get(r, {}); large = r in CG_LARGE; rac = _rr_racials(R); vis = _rr_vision(r); cities = rs[r]
        f = fits[r]; p_stat = None if f is None else max(20.0, 50 - 5 * (best - f))
        rv, rwhy = 0, []
        for n in rac:
            if n in RR_RACIAL:
                v = RR_CLASS_RACIAL.get((c, n), RR_RACIAL[n][0][role]); rv += v; rwhy.append('%s (%s)' % (n, RR_RACIAL[n][1]))
        p_rac = min(20, 2 * rv)
        p_vis = 5 if 'Ultravision' in vis else (4 if 'Infravision' in vis else 0)
        p_acc = min(10, 5 * len(cities)) + (5 if 'Night Harbor' in cities else 0) - (3 if R.get('alignment') == 'Evil' else 0) - (2 if 'KoS' in (R.get('note') or '') else 0)
        p_size = (-10 if large else 0) - (2 if any('Consumption' in n for n in rac) else 0)
        score = round((p_stat or 20) + p_rac + p_vis + p_acc + p_size)
        rows.append(dict(race=r, R=R, large=large, rac=rac, rwhy=rwhy, vis=vis, cities=cities, fit=f, stats=st(r), score=score,
                         parts=[('stats', None if p_stat is None else round(p_stat)), ('racial', p_rac), ('vision', p_vis), ('access', p_acc), ('size/upkeep', p_size)]))
    rows.sort(key=lambda x: (-x['score'], x['large'], x['race']))
    # a large race is never the #1 / default recommendation
    if len(rows) > 1 and rows[0]['large']:
        i = next((j for j, x in enumerate(rows) if not x['large']), None)
        if i: rows.insert(0, rows.pop(i)); rows[1]['demoted'] = True
    for i, x in enumerate(rows):
        x['rank'] = i + 1; s = x['score']
        x['tier'] = 'A' if s >= 75 else 'B' if s >= 62 else 'C' if s >= 50 else 'D'
        x['pros'], x['cons'] = _rr_proscons(c, x, rows, W_)
    return rows

def _rr_proscons(c, x, rows, W_):
    D = CGC.get(c) or {}; r = x['race']; R = x['R']
    have = (D.get('races') or {}).get(r)
    if have: pros, cons = list(have['pros']), list(have['cons'])
    else:
        pros, cons = [], []
        for k in sorted(W_, key=lambda k: -W_[k])[:3]:
            vals = [y['stats'].get(k) for y in rows if y['stats'].get(k) is not None]
            v = x['stats'].get(k)
            if v is None or len(vals) < 2: continue
            if v == max(vals): pros.append('Highest starting %s of the playable %s races (%s).' % (k, c, v))
            if v == min(vals): cons.append('Lowest starting %s of the playable %s races (%s).' % (k, c, v))
        for n in x['rac']:
            if n in RR_RACIAL: pros.append('Racial: %s: %s.' % (n, RR_RACIAL[n][1]))
            elif 'Consumption' in n: cons.append('Increased Consumption Rate (race page): more food and drink.')
        if R.get('resists'): (pros if '-' not in R['resists'] else cons).append('Resistances %s (race page).' % R['resists'])
        cons.append('%s alignment; starts as a %s in %s.' % (R.get('alignment') or 'Unknown', c, ', '.join(x['cities'])))
    if x['large']: cons.insert(0, 'Large race: this Codex never defaults to or recommends it (size can limit where you fit; the wiki does not document the exact effects).')
    if not x['rac'] and not any('racial' in y.lower() and 'not documented' in y.lower() for y in cons): cons.append('Racial ability not documented on the wiki race page: UNVERIFIED.')
    if x['fit'] is None: cons.append('Starting stats for %s %s not on the wiki: UNVERIFIED.' % (r, c))
    vis = x['vis']
    if vis and not any('vision' in p.lower() for p in pros): pros.append('Can take the %s trait (Template:Traits).' % ' or '.join(vis))
    if not vis: cons.append('No Infravision or Ultravision trait available (Template:Traits).')
    return pros, cons

def _rr_why1(c, rows):
    if not rows: return ''
    a = rows[0]; b = rows[1] if len(rows) > 1 else None
    if not b: return '%s is the only race the wiki start-city table allows for %s.' % (a['race'], c)
    pa, pb = dict(a['parts']), dict(b['parts']); bits = []
    lab = {'stats': 'stat fit for the %s builds' % c, 'racial': 'racial value', 'vision': 'vision trait', 'access': 'start-city access'}
    for k in ('stats', 'racial', 'access', 'vision'):
        va, vb = pa.get(k) or 0, pb.get(k) or 0
        if va > vb:
            extra = {'racial': ' (%s)' % ', '.join(a['rac']), 'access': ' (%s)' % ', '.join(a['cities']), 'vision': ' (%s)' % ' / '.join(a['vis'])}.get(k, '')
            bits.append('better %s%s, %s vs %s' % (lab[k], extra, va, vb))
    if (pb.get('size/upkeep') or 0) < (pa.get('size/upkeep') or 0): bits.append('%s loses %s for size/upkeep' % (b['race'], -(pb.get('size/upkeep') or 0)))
    return '%s (score %s) beats #2 %s (%s): %s.' % (a['race'], a['score'], b['race'], b['score'], '; '.join(bits) or 'higher total score')

def _rr_row(c, x):
    R = x['R']; parts = ' · '.join('%s %s' % (k, ('?' if v is None else ('%+d' % v if k == 'size/upkeep' else v))) for k, v in x['parts'])
    facts = '%s · starts in %s · racial: %s · vision: %s%s' % (esc(R.get('alignment') or 'alignment ?'), esc(', '.join(x['cities'])),
        esc(', '.join(x['rac'])) if x['rac'] else 'not documented', esc(' / '.join(x['vis'])) if x['vis'] else 'none', ' · <b>large race</b>' if x['large'] else '')
    return ('<li class="rr-row gb-row%s" data-cg-race="%s"><button type="button" class="gb-pick rr-use" data-class="%s" data-race="%s" aria-label="Set Race to %s">'
            '<span class="gb-rk">#%d</span> <b>%s</b> <span class="rr-tier rr-t%s">Tier %s</span> <span class="gb-sc">%s</span></button>'
            '<div class="gb-why">%s %s</div>'
            '<div class="rr-pc"><div><b>Pros</b> %s<ul class="tight">%s</ul></div><div><b>Cons</b> %s<ul class="tight">%s</ul></div></div>'
            '<div class="gb-ev">Score %s: %s%s</div></li>') % (
        ' rr-large' if x['large'] else '', esc(x['race']), esc(c), esc(x['race']), esc(x['race']), x['rank'], esc(x['race']), x['tier'], x['tier'], x['score'],
        _cg_badge('FACT'), facts, _cg_badge('STRATEGY'), ''.join('<li>%s</li>' % esc(p) for p in x['pros']) or '<li>None flagged</li>',
        _cg_badge('STRATEGY'), ''.join('<li>%s</li>' % esc(p) for p in x['cons']) or '<li>None flagged</li>', x['score'], parts,
        ' · moved below #1 because large races are never the top pick' if x.get('demoted') else '')

def race_rank_html(c, top=3):
    rows = race_rank(c); D = CGC.get(c) or {}
    o = ['<div class="rr" id="best-races"><h3 id="best-races-h">Best races for %s %s</h3>' % (esc(c), _cg_badge('STRATEGY'))]
    if not rows:
        return o[0] + '<p>%s No race on the wiki start-city table for %s: no sourced data yet.</p></div>' % (_cg_badge('UNVERIFIED'), esc(c))
    o.append('<p class="rr-why1"><b>Why #1:</b> %s</p>' % esc(_rr_why1(c, rows)))
    o.append('<p class="gb-ev">Every race the wiki start-city table allows for %s, best to worst. Click a race to set <b>Race</b> in the top bar (Class becomes %s and Start stays valid). '
             'Score = stat fit for this class\'s builds (up to 50, from wiki starting stats) + racial ability value for the role (up to 20) + Infravision/Ultravision trait (up to 5) + start-city access (up to 15: more cities, Night Harbor hub; evil races and KoS notes cost points) − large size and food upkeep. '
             'Tiers: A 75+, B 62+, C 50+, D below. The weights are this Codex\'s judgement %s; the stats, racials, traits and cities are %s.</p>' % (esc(c), esc(c), _cg_badge('STRATEGY'), _cg_badge('FACT')))
    o.append('<ol class="gb-rank rr-list">%s</ol>' % ''.join(_rr_row(c, x) for x in rows[:top]))
    if len(rows) > top:
        o.append('<details class="gb-more rr-more"><summary>Show all %d</summary><ol class="gb-rank rr-list" start="%d">%s</ol></details>' % (len(rows), top + 1, ''.join(_rr_row(c, x) for x in rows[top:])))
    for _o in CG_NYA.get(c, []):
        o.append('<p class="dim cg-nya">%s <b>%s %s: not yet available</b> (%s). %s <a href="%s">Patch note</a></p>' % (_cg_badge(_o.get('label') or 'FACT'),
            esc(_o['race']), esc(c), esc(_o.get('status') or 'coming soon'), esc(_o.get('note') or ''), esc(_o['source'])))
    pl = D.get('planned_races') or {}
    off = [r for r in _cg_official_races(c) if r not in CG_BY_CLASS.get(c, {})]
    names = sorted((set(pl) | set(off)) - {_o['race'] for _o in CG_NYA.get(c, [])})
    if names:
        o.append('<p class="dim">%s Not ranked (not playable in Early Access, no wiki start-city row%s): %s.</p>' % (_cg_badge('UNVERIFIED'),
            '; starting stats and racials not on the wiki' if any(not _rr_racials(CG['races'].get(n, {})) for n in names) else '', esc(', '.join(names))))
    o.append('</div>')
    return ''.join(o)

# ------------------------------------------------------------------ Quick info: compact new-character walkthrough (rendered by mod-chargen.js from walk-data.js)
def qwalk_html(c):
    return ('<div class="cg-qwalk" data-class="%s" aria-live="polite"><p class="dim">New-character walkthrough for your Race and Start picks: loading… (needs JavaScript). '
            'Or open the <a href="/walkthrough.html">full walkthrough</a>.</p></div>') % esc(c)

def _tab_insert(body, label, key, pane_html):
    """Insert a tab (button after the first tab button, pane after the tab bar) into the first .tabs block."""
    m = re.search(r'<div class="tabs"><div class="tabbar"><button class="tab on" data-tab="([^"]+)">.*?</button>', body)
    if not m: return None
    tid = m.group(1).rsplit('-', 1)[0] + '-' + key
    btn = '<button class="tab" data-tab="%s">%s</button>' % (tid, esc(label))
    body = body[:m.end()] + btn + body[m.end():]
    i = body.index('</div>', body.index('<div class="tabbar">')) + len('</div>')
    return body[:i] + '<div class="tabpane" id="%s">%s</div>' % (tid, pane_html) + body[i:]

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
    def _cg_trainers(city):
        # wiki city_info trainers, plus the start-city route's sourced trainers (data/startcities) for classes city_info lacks
        tr = dict(CG['city_info'][city]['trainers'])
        for c, t in ((globals().get('SC') or {}).get(city, {}).get('trainers') or {}).items():
            if c not in tr and t.get('npc'): tr[c] = [{'npc': t['npc'], 'where': t.get('where', '')}]
        return tr
    cities = {}
    for city in CG['cities']:
        home = [fn for fn in FG if city.lower().replace("'", '') in fn.lower().replace("'", '')]
        cities[city] = {'dist': {k: v for k, v in _cg_dist(city).items() if k in ZONES}, 'home': home, 'faq': CG_CITY_FAQ.get(city, ''),
                        'u': CG['city_info'][city]['url'], 'tr': _cg_trainers(city)}
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
            '')

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
                    sec = chargen_section(c)
                    if p['path'] == 'shaman/index.html':
                        nb = _tab_insert(p['body'], 'Character creation', 'cg', sec)
                        p['body'] = (qwalk_html(c) + nb) if nb else (p['body'] + sec)
                    else:
                        p['body'] += sec
                        p['body'] = re.sub(r'(<div class="call note"><div class="call-t">Quick info by level</div><p>.*?</p></div>)', lambda mm: mm.group(1) + qwalk_html(c), p['body'], count=1, flags=re.S)
                    if c in CGC:
                        p['sources'] = (p['sources'] or [s.strip() for s in p['meta'].get('sources', '').split(';') if s.strip()]) + _cg_srcs(c)
                    toc = p['ctx'].setdefault('toc', [])
                    if toc: toc.append(('chargen', 'Character creation'))
        for p in PAGES:
            m = re.match(r'classes/([a-z-]+)\.html$', p['path'])
            c = next((x for x in CLASS_LIST if m and slug(x) == m.group(1)), None)
            if c:
                nb = _tab_insert(p['body'], 'Character creation', 'cg', chargen_section(c))
                if nb:
                    nb = re.sub(r'(<h2 id="[^"]*">%s quick reference by level</h2>\s*<p>.*?</p>)' % re.escape(esc(c)), lambda mm: mm.group(1) + qwalk_html(c), nb, count=1, flags=re.S)
                    jump = '<p class="cg-jump"><a href="#best-races">Best races for %s</a> · <a href="#chargen">stats, traits and tradeskills</a> <span class="dim">(Character creation tab)</span></p>' % esc(c)
                    p['body'] = nb.replace('<div class="tabs">', jump + '<div class="tabs">', 1)
                    if c in CGC: p['sources'] = (p['sources'] or [s.strip() for s in p['meta'].get('sources', '').split(';') if s.strip()]) + _cg_srcs(c)
            if p['path'] == 'shaman/quickinfo.html': p['body'] = qwalk_html('Shaman') + p['body']
    _cg_prev_ra()
    open(os.path.join(OUT, 'assets', 'chargen-data.js'), 'w', encoding='utf8').write('window.MNM_CG=' + json.dumps(_cg_topdata(), ensure_ascii=False, separators=(',', ':')) + ';')
    open(os.path.join(OUT, 'assets', 'walk-data.js'), 'w', encoding='utf8').write('window.MNM_WT=' + json.dumps(_cg_walkdata(), ensure_ascii=False, separators=(',', ':')) + ';')

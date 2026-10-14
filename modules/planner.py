# Group/duo planner module: page /planner.html, rule-based (STRATEGY), evidence from wiki spell lists (FACT)
_ROLE_RULES = [('tank', r'\btank\b'), ('healer', r'heal'), ('crowd control', r'crowd control'), ('puller', r'puller'), ('pet', r'\bpet\b'),
               ('ranged dps', r'ranged|nuker|caster'), ('melee dps', r'melee')]
# (name regex, description regex) - description patterns are kept narrow to avoid false matches
_UTIL = [('Heals', r'\bheal|mend(?!.*\bdead\b)', r'\b(heals?|restores?) (you|your|the|a|an|\d)[^.]{0,30}(hit points|health|hp)|\bheals (the )?target'),
         ('Slow', r'\bslow|lethargy', r'(slows|reduc\w+) (the )?(target|enemy)\W[^.]{0,30}attack speed|attack speed[^.]{0,20}(reduced|slowed|decreased)'),
         ('Mez / mesmerize', r'mesmer|\bmez\b|\blull', r'mesmeriz'),
         ('Root / snare', r'\broot\b|snare|ensnar', r'roots? (the )?target|ensnar|reduc\w+ (the )?target\W?s? movement'),
         ('Haste', r'\bhaste', r'increas\w+ (the )?(target\W?s? |your |group\W?s? )?attack speed'),
         ('Resurrect', r'resurrect|revive', r'resurrect'),
         ('Cure / dispel', r'\bcure|dispel|purif|cleanse', r'\bcures?\b|removes? (a |one )?(detrimental|poison|disease|curse)'),
         ('Invisibility', r'^invisibility|\binvis\b|vanish', r'become[s]? invisible|makes? (the )?(target|you|group) invisible'),
         ('Teleport / gate', r'teleport|portal|\bgate\b|translocat', r'teleports?'),
         ('Run speed', r'spirit of the wolf|speed of', r'increas\w+ (the )?(target\W?s? |your |group\W?s? )?(run|movement) speed'),
         ('Damage shield', r'thorn', r'damage shield'),
         ('Mana regen', r'clarity', r'(restores?|regenerat\w+|increas\w+)[^.]{0,25}mana regen'),
         ('Pet', r'summon (skeleton|companion|elemental|warder|minion|servant|spirit|beast)|animate', r'summons? (a |an |your )?[^.]{0,30}\b(pet|companion|warder)\b'),
         ('Fear', r'^fear|terror', r'\bflee'),
         ('Feign / stealth', r'feign|sneak|^hide$', r'feign death|move silently|hide in the shadows')]
def _planner_data():
    cls = {}
    for c in CLASS_LIST:
        role = CLASS_NOTES.get(c, {}).get('role', '')
        roles = [r for r, rx in _ROLE_RULES if re.search(rx, role, re.I)]
        util = {}
        for sp in CLASSES[c]['spells']:
            txt = (sp.get('spell name') or '') + ' ' + (sp.get('spell description') or '')
            nm = sp.get('spell name') or ''; ds = sp.get('spell description') or ''
            for u, rn, rd in _UTIL:
                if re.search(rn, nm, re.I) or re.search(rd, ds, re.I):
                    lv = sp.get('level') or 0
                    if u not in util or lv < util[u][1]: util[u] = [sp.get('spell name'), lv]
        cls[c] = {'role': role, 'roles': roles, 'util': util, 'url': class_url(c).lstrip('/')}
    bands = []
    for k in RANGE_ORDER:
        lo, hi = map(int, k.split('-'))
        zs = sorted(zones_for_band(lo, hi), key=lambda x: -len(x[1]))[:8]
        bands.append([k, [[z, (dungeon_url(z) if z in DUNGEON_ORDER else zone_url(z)).lstrip('/'), ZONES[z]['level'] or '?', len(cp), z in DUNGEON_ORDER] for z, cp in zs]])
    return {'classes': cls, 'bands': bands, 'utils': [u for u, _, _ in _UTIL]}
def _planner_page():
    return ('<link rel="stylesheet" href="/assets/mod-planner.css">'
            '<p>Pick 2–6 classes to see role coverage, missing utility and zones for a level range. '
            '<span class="badge strat">strategy</span> The coverage verdicts are simple rules of thumb, not tested comps. '
            '<span class="badge fact">fact</span> Each utility shows the first spell that matched it in that class\'s wiki spell list, with its level, so you can check the match. Keyword matching can miss abilities or match the wrong one <span class="badge unc">unverified</span>.</p>'
            '<div id="pl-picks" class="pl-picks"></div><p><label>Levels <select id="pl-band" aria-label="Planner level range"></select></label> <button type="button" id="pl-clear">Clear</button></p>'
            '<div id="pl-out"></div><script>window.MNM_PLAN=%s;</script><script src="/assets/mod-planner.js"></script>') % json.dumps(_planner_data(), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
_planner_prev_bc = build_content
def build_content():
    _planner_prev_bc()
    add_page('planner.html', 'Group & duo planner', body_html=_planner_page(), section='planner',
             sources=['Wiki class pages (spell lists)|%sCategory:Classes' % WIKI, 'Wiki zone pages (mob levels)|%sZones' % WIKI], desc='Group and duo planner')
NAV.insert(len(NAV) - 1, ('Planner', '/planner.html', 'planner'))

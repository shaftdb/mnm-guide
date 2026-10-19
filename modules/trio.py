# Trio plan + group builder module: /trio.html (plan, content/trio.md) and /groups.html (interactive builder).
# Capability evidence is FACT (wiki spell lists in data/classes.json + official class pages in data/official_classes.json);
# scores and verdicts are STRATEGY.
_OFFICIAL = json.load(open(os.path.join(ROOT, 'data', 'official_classes.json'), encoding='utf8'))
_PLAYABLE = ['Deep Elf', 'Deep Gnome', 'Dwarf', 'Gnome', 'Goblin', 'Halfling', 'Human', 'Ogre', 'Wood Elf']  # CoGM races guide (official FAQ), Oct 2026
_LARGE = ['Ogre', 'Troll']
# Start cities per race: community wiki table (Sep 29, 2026) via CoGM; "some" = only some classes
_START = {'Human': ['Night Harbor', 'Underdocks (some)'], 'Wood Elf': ['Night Harbor', 'Faelindral'], 'Halfling': ['Night Harbor', 'Faelindral'],
          'Dwarf': ['Night Harbor'], 'Gnome': ['Night Harbor', 'Underdocks (some)'], 'Goblin': ['Underdocks'], 'Ogre': ['Night Harbor', 'Underdocks (some)'],
          'Deep Elf': ["Underdocks", "Ail'vorith"], 'Deep Gnome': ['Underdocks']}
_CAPS = [('tank', 'Tank'), ('heal', 'Heals'), ('dps', 'DPS'), ('cc', 'Crowd control'), ('pull', 'Pulling'), ('buffs', 'Buffs'),
         ('self', 'Self-sufficiency'), ('sustain', 'Low downtime'), ('rez', 'Resurrect')]
_SP_RULES = {
    'heal': r'restor\w*[^.]{0,25}\bHealth\b|Health Regeneration',
    'cc': r'mesmeriz|incapacitat|stunn|\bcharms?\b|\bimmobiliz|\bflee',
    'pull': r'feign death|clearing all threat|aggro radius',
    'buffs': r'(your target|your party|your group|target party member|nearby group|their)[^.]{0,60}increas|increas\w+ their',
    'self': r'^summon (food|drink|cloth bandage|arrows)|^gate$|^soulbind|movement speed[^.]{0,30}(35 minutes|1 hour)|^ring of|^circle of|portal|exodus|^invisibility$',
    'sustain': r'mana regeneration[^.]{0,30}(party|group)|(party|group)[^.]{0,60}mana regeneration|enlightenment|converting[^.]{0,30}mana|blood pact|death pact',
    'rez': r'(revive|resurrect|reanimate|redeem|resuscitate|reawaken)\w* a target corpse',
}
_TRAIT_RULES = {
    'tank': r'off-?tank|off\u2011tank|pet to tank|capable tank|tank,? holding aggro',
    'self': r'self-sufficien|self-reliance|draw food|teleport|forage',
    'sustain': r'cannibalize|redistribut\w+ stolen mana|mana regeneration|no mana cost|portion of mana|life-drain|drains life',
    'buffs': r'strongest physical buff|powerful buffs|buff them, their companion, and party|passive divine aura',
    'pull': r'feign death|puller',
    'cc': r'premier crowd-control|crowd control|charm',
}
def _trio_caps():
    out = {}
    for c in CLASS_LIST:
        O = _OFFICIAL.get(c, {}); roles = O.get('roles', ''); traits = O.get('traits', [])
        ev = {k: [] for k, _ in _CAPS}
        for sp in CLASSES[c]['spells']:
            nm = sp.get('spell name') or ''; ds = sp.get('spell description') or ''; lv = sp.get('level') or 0
            if 'beast corpse' in ds: continue
            for k, rx in _SP_RULES.items():
                hit = re.search(rx, nm if k == 'self' else nm + ' - ' + ds, re.I)
                if k == 'self' and not hit: hit = re.search(r'(target|party|group)[^.]{0,40}Movement Speed by[^.]{0,30}(35 minutes|1 hour)', ds, re.I)
                if hit:
                    if k == 'buffs' and re.search(r'decreas|lower|reduc|enemy|enemies|terrify|damage every|received by|threat', ds, re.I): continue
                    if k == 'heal' and re.search(r'\bpet\b|companion', ds, re.I): continue
                    ev[k].append([nm, lv, 'w'])
        for t in traits:
            for k, rx in _TRAIT_RULES.items():
                if re.search(rx, t, re.I): ev[k].append([t[:140], 0, 'o'])
        for k in ev:  # dedupe by name, keep lowest level, cap list
            seen = {}
            for e in sorted(ev[k], key=lambda e: e[1]):
                seen.setdefault(e[0], e)
            ev[k] = list(seen.values())[:6]
        def nsp(k): return len([e for e in ev[k] if e[2] == 'w'])
        sc = {}
        sc['tank'] = 2 if re.search(r'\bTank\b', roles) else (1 if ev['tank'] else 0)
        sc['heal'] = 2 if 'Healer' in roles else (1 if nsp('heal') else 0)
        sc['dps'] = 2 if 'DPS' in roles else 1
        sc['cc'] = 2 if re.search(r'Crowd Control|\bCC\b', roles) or nsp('cc') >= 4 else (1 if ev['cc'] else 0)
        sc['pull'] = 2 if 'Puller' in roles or any(re.search('feign', e[0], re.I) for e in ev['pull']) else (1 if ev['pull'] else 0)
        sc['buffs'] = 2 if any(e[2] == 'o' for e in ev['buffs']) or nsp('buffs') >= 6 else (1 if nsp('buffs') >= 2 else 0)
        sc['self'] = 2 if len(ev['self']) >= 4 else (1 if ev['self'] else 0)
        sc['sustain'] = 2 if ev['sustain'] else 0
        sc['rez'] = 2 if ev['rez'] else 0
        races = [r.strip() for r in O.get('races', '').split(',') if r.strip()]
        out[c] = {'roles': roles, 'url': O.get('url', ''), 'page': class_url(c).lstrip('/'), 'sc': sc, 'ev': ev,
                  'races': [r for r in races if r in _PLAYABLE], 'planned': [r for r in races if r not in _PLAYABLE],
                  'solo': bool(re.search(r'strongest solo|performs well solo|capable of soloing|excels at solo', ' '.join(traits), re.I)),
                  'nomana': c in ('Monk', 'Rogue', 'Fighter', 'Archer')}
    return out
_TRIO_RECS = [
    {'name': 'Iron Trio (recommended)', 'cls': ['Shadow Knight', 'Shaman', 'Monk'], 'races': ['Human', 'Human', 'Human'], 'fourth': 'Enchanter', 'fourth_race': 'Gnome',
     'why': 'Two feign-death pullers, Shaman slow, haste, run speed, food and water, plate tank with lifetaps; no ammo or reagents.'},
    {'name': 'Anti-magic dungeon trio', 'cls': ['Inquisitor', 'Shaman', 'Necromancer'], 'races': ['Human', 'Human', 'Gnome'], 'fourth': 'Monk', 'fourth_race': 'Human',
     'why': 'Inquisitor party haste aura and incapacitates, Necro pet as a second tank plus feign death and root.'},
    {'name': 'Rez and travel trio', 'cls': ['Paladin', 'Druid', 'Monk'], 'races': ['Human', 'Halfling', 'Human'], 'fourth': 'Enchanter', 'fourth_race': 'Gnome',
     'why': 'Paladin rez from L16, Druid ports, party wolf form and charm, Monk pulls.'},
    {'name': 'Buy-nothing trio', 'cls': ['Shadow Knight', 'Shaman', 'Elementalist'], 'races': ['Human', 'Human', 'Gnome'], 'fourth': 'Enchanter', 'fourth_race': 'Gnome',
     'why': 'Elementalist summons food, water, bandages and arrows; Shaman covers buffs and heals.'},
]
def _groups_page():
    data = {'caps': _CAPS, 'classes': _trio_caps(), 'start': _START, 'large': _LARGE, 'recs': _TRIO_RECS}
    return ('<link rel="stylesheet" href="/assets/mod-groups.css">'
            '<p>Pick 1 or 2 classes to get every possible pair or third ranked best to worst (click one to fill it), or pick 3 plus an optional 4th to see what the group covers and every 4th ranked. <span class="badge fact">fact</span> Each score lists its evidence: wiki spells with their level (W), or lines from the official class page (O). '
            '<span class="badge strat">strategy</span> The 0–2 scores, verdicts, money rating and suggested 4th are rules of thumb. Keyword matching can miss abilities <span class="badge unc">unverified</span>. '
            'For the full plan, see the <a href="/trio.html">trio plan</a>.</p>'
            '<h2 id="recommended">Recommended groups</h2><div id="gb-recs" class="gb-recs"></div>'
            '<h2 id="builder">Group builder</h2><div id="gb-slots" class="gb-slots"></div><p><button type="button" id="gb-clear">Clear</button></p>'
            '<div id="gb-out" aria-live="polite"></div><script>window.MNM_GB=%s;</script><script src="/assets/mod-groups.js"></script>') % json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
_trio_prev_bc = build_content
def build_content():
    _trio_prev_bc()
    meta, txt = read_md(os.path.join(CONTENT, 'trio.md'))
    add_page('trio.html', 'Trio leveling & money plan', body_md='<link rel="stylesheet" href="/assets/mod-trio.css">\n' + txt, section='trio', desc='Fresh-alt trio plan: classes, races, camps, money camps',
             sources=['Official New Player Guide|https://monstersandmemories.com/new-player-guide', 'Per-Level Hunting Guide (wiki)|%sPer-Level_Hunting_Guide' % WIKI,
                      'Loot Worth Keeping (fan DB)|https://monstersandmemories.wiki/loot-value', 'Patch notes|https://account.monstersandmemories.com/community/patch_notes'])
    add_page('groups.html', 'Group builder & recommended trios', body_html=_groups_page(), section='groups', desc='Interactive trio + 4th group builder',
             sources=['Wiki class spell lists|%sCategory:Classes' % WIKI, 'Official class pages|https://monstersandmemories.com/class-shaman',
                      'Races and start cities (CoGM, from official FAQ and wiki)|https://cogm.app/monsters-and-memories/guides/races'])
NAV.insert(len(NAV) - 1, ('Trio plan', '/trio.html', 'trio'))
NAV.insert(len(NAV) - 1, ('Group builder', '/groups.html', 'groups'))

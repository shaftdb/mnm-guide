# Hotbar planner module: /hotbar.html + docs/assets/hotbar-data.js (class spells, skills, trait actives, clickies, chargen builds)
# + docs/assets/hotbar-items.js (equippable items with numeric stats, loaded only when the character sheet opens)
# + static/mod-hotbar.js/.css. Reads the shared top-bar pickers (mnm-class / mnm-race / mnm-range); never edits their code.
# Facts: wiki class spell lists, Template:Traits, item pages; bar layout from the official New Player Guide (see HB_FACTS).
# Suggested layouts are rule-of-thumb picks from the class's own spell list (STRATEGY); nothing is invented.
HB_RACE_CODES = {'Human': 'HUM', 'Ogre': 'OGR', 'Troll': 'TRL', 'Wood Elf': 'ELF', 'High Elf': 'HIE', 'Dwarf': 'DWF', 'Gnome': 'GNM',
                 'Goblin': 'GOB', 'Halfling': 'HFL', 'Deep Dwarf': 'DDF', 'Deep Elf': 'DEF', 'Deep Gnome': 'DGN'}
# Gear slots: names from wiki Equipment By Slot + GameLibraryData; counts of 2 for Ear/Finger/Wrist are UNVERIFIED (no source found).
HB_GEAR = [['Head', 1, 'FACT'], ['Face', 1, 'FACT'], ['Ear', 2, 'UNVERIFIED'], ['Neck', 1, 'FACT'], ['Shoulders', 1, 'FACT'], ['Back', 1, 'FACT'],
           ['Chest', 1, 'FACT'], ['Shirt', 1, 'FACT'], ['Wrist', 2, 'UNVERIFIED'], ['Hands', 1, 'FACT'], ['Finger', 2, 'UNVERIFIED'], ['Waist', 1, 'FACT'],
           ['Legs', 1, 'FACT'], ['Feet', 1, 'FACT'], ['Primary', 1, 'FACT'], ['Secondary', 1, 'FACT'], ['Range', 1, 'FACT'], ['Ammo', 1, 'FACT'], ['Belt', 3, 'FACT']]
HB_SRC = {
    'npg': ['Official New Player Guide (keys, ability bar, hotbar, belt slots)', 'https://monstersandmemories.com/new-player-guide'],
    'wiz': ['Official Wizard deep dive ("every casting class has ten spell slots")', 'https://monstersandmemories.com/class-wizard-deep-dive'],
    'pn2': ['Patch 0.20.25.0 (trait abilities on the HotBar; Hide and Sneak on the Aura bar; cantrip slots)', 'https://account.monstersandmemories.com/community/patch_notes/2'],
    'fui': ['Forum: "My UI Wishlist" (12 hotbar slots at a time, switchable hotbars, 324 macro slots), Sep 2026', 'https://forum.monstersandmemories.com/d/1026-my-ui-wishlist'],
    'fab': ['Forum: "Ability Bar Re-shape?" (one hotbar; ability bar shape can be cycled), Sep 2026', 'https://forum.monstersandmemories.com/d/698-ability-bar-re-shape'],
    'slot': ['Wiki: Equipment By Slot', WIKI + 'Equipment_By_Slot'],
    'gld': ['Wiki: GameLibraryData (item slot codes)', WIKI + 'Monsters_and_Memories_Wiki:GameLibraryData'],
    'mem': ['Wiki: Meming your Spell/Abilities', WIKI + 'Meming_your_Spell/Abilities'],
}
HB_FACTS = [
    ['FACT', 'Ability bar: 10 slots for memorized spells and abilities, used with keys 1 to 0. Melee abilities (Innates tab) and spells both have to be memorized here.', ['npg', 'wiz', 'mem']],
    ['FACT', 'Hotbar: keys Shift+1 to 0, minus and equals (12 buttons). It holds skills from the Skills tab, macros and clicky items, not memorized spells.', ['npg']],
    ['FACT', 'Aura bar: keys Ctrl+1 to 0. Hide and Sneak sit on the Aura bar and need no memorization; other trait abilities are skills that go on the HotBar.', ['npg', 'pn2']],
    ['FACT', 'Your spellbook has to be in a belt slot (3 belt slots) to scribe or memorize, but not to cast.', ['npg']],
    ['UNVERIFIED', 'Hotbar pages: players report 12 slots shown at a time with switchable hotbar pages, and only one hotbar on screen. The number of pages and the page-switch keys are not documented, so the page count here is a setting.', ['fui', 'fab']],
    ['UNVERIFIED', 'Aura bar size: 10 keys are bound (Ctrl+1 to 0); how many aura slots the bar shows is not documented.', ['npg']],
    ['UNVERIFIED', 'Cantrips: you gain cantrip slots that keep a memorized spell on death; how many, and at which levels, is not documented, so this planner does not model them.', ['pn2']],
]
_HB_UNIT = r'(hit points|health|hp)'
_HB_CATS = [  # (key, label, regex on name, regex on description)
    ('threat', 'Threat / taunt', r'taunt|provoke|challenge', r'threat|hate|draw\w* (their )?attention|taunt'),
    ('heal', 'Heal', r'\bheal|mend|renew|restor', r'\b(heals?|healing|restores?) (you|your|the|a|an|\d|target|group)[^.]{0,40}' + _HB_UNIT + r'|\bheals (the )?target'),
    ('dot', 'Damage over time', r'$^', r'damage[^.]{0,40}(every|over) \d+ (seconds|ticks?)|(every|over) \d+ seconds[^.]{0,40}damage'),
    ('nuke', 'Direct damage', r'$^', r'deal\w*[^.]{0,40}damage|damage (to|on) (the|your) target'),
    ('stun', 'Stun / interrupt', r'\bstun|bash|interrupt', r'\bstun|interrupt|incapacitat'),
    ('mez', 'Mesmerize', r'mesmer|\blull', r'mesmeriz'),
    ('slow', 'Slow', r'\bslow|lethargy', r'(decreas|reduc|slow)\w*[^.]{0,30}(attack|casting) speed'),
    ('snare', 'Root / snare', r'\broot\b|snare|ensnar', r'roots? (the )?target|ensnar|(decreas|reduc)\w* (the |their )?(target\W?s? )?(movement|run) speed'),
    ('debuff', 'Debuff', r'$^', r'(decreas|reduc|lower)\w*[^.]{0,30}(resist|armou?r|\bac\b|attack|strength)'),
    ('pet', 'Pet', r'summon|animate', r'summons? (a |an |your )?[^.]{0,30}\b(pet|companion|warder|minion|servant)'),
    ('cure', 'Cure', r'\bcure|purif|cleanse', r'\bcures?\b|removes? (a |one |all )?(detrimental|poison|disease|curse)'),
    ('rez', 'Resurrect', r'resurrect|revive', r'resurrect'),
    ('buff', 'Buff', r'$^', r'increas\w*[^.]{0,40}(armou?r|\bac\b|hit points|max(imum)? (health|mana)|strength|stamina|agility|dexterity|resist|attack speed|regen)'),
]
def _hb_cats(sp):
    nm = sp.get('spell name') or ''; ds = sp.get('spell description') or ''
    return [k for k, _, rn, rd in _HB_CATS if re.search(rn, nm, re.I) or re.search(rd, ds, re.I)]
def _hb_role(c):
    r = CLASS_NOTES.get(c, {}).get('role', '').lower()
    if 'tank' in r: return 'tank'
    if 'heal' in r: return 'healer'
    if 'crowd' in r or 'support' in r: return 'cc'
    if 'pet' in r: return 'pet'
    return 'dps'
def _hb_aura(sp):
    nm = sp.get('spell name') or ''
    return 1 if (nm.startswith('Aura of') or (sp.get('mana') or '') == 'Aura' or nm in ('Hide', 'Sneak')) else 0
def _hb_data():
    cls = {}
    for c in CLASS_LIST:
        sps = []
        for sp in CLASSES[c]['spells']:
            nm = sp.get('spell name')
            if not nm: continue
            mana = sp.get('mana') or ''
            sps.append([nm, sp.get('level') or 0, mana, sp.get('location') or '', sp.get('class') or sp.get('school') or '', sp.get('spell description') or '',
                        'i' if mana == 'Innate' else ('a' if _hb_aura(sp) else 's'), _hb_cats(sp), _hb_aura(sp)])
        sk = [[s['skill'], int(s['level']) if str(s.get('level', '')).isdigit() else 0] for s in CLASSES[c].get('skills', []) if s.get('group') == 'Non-Combat Skills']
        D = CGC.get(c, {})
        cls[c] = {'code': CABBR.get(c, ''), 'role': CLASS_NOTES.get(c, {}).get('role', ''), 'rk': _hb_role(c), 'url': class_url(c).lstrip('/'), 'wiki': CLASSES[c].get('url', ''),
                  'rev': CLASSES[c].get('revid'), 'spells': sps, 'nsolo': CLASS_NOTES.get(c, {}).get('solo', ''), 'ngroup': CLASS_NOTES.get(c, {}).get('group', ''), 'skills': sk,
                  'builds': [{'n': b['name'], 'a': b['alloc'], 'w': b.get('why', '')} for b in D.get('builds', [])],
                  'tpick': [[t.get('pick'), t.get('race_pick') or {}] for t in D.get('traits', []) if t.get('pick')]}
    races = {r: {'code': HB_RACE_CODES.get(r, ''), 'start': {k: v.get('stats') for k, v in (d.get('start') or {}).items()}, 'url': d.get('url', ''), 'rev': d.get('revid')}
             for r, d in CG['races'].items()}
    traits = []
    for cat, lst in CG['traits'].items():
        for t in lst:
            ds = t.get('desc') or ''
            if 'Active:' in ds or t['name'] == 'Forage':
                traits.append([t['name'], t.get('race') or 'Any', t.get('cls') or 'Any', ds, cat])
    clicky = []
    for nm, it in sorted(ITEMS.items()):
        ef = it.get('effect') or ''
        if re.search(r'on click|click', ef, re.I):
            clicky.append([nm, ' '.join(class_codes(it)), it.get('slot') or '', ef, item_level(it) or 0])
    return {'classes': cls, 'races': races, 'traits': traits, 'clicky': clicky, 'gear': HB_GEAR, 'cats': [[k, l] for k, l, _, _ in _HB_CATS],
            'src': HB_SRC, 'facts': HB_FACTS, 'tsrc': [CG['_source']['traits']['url'], CG['_source']['traits']['revid']]}
_HB_STATS = ['ac', 'hp', 'mana', 'str', 'sta', 'agi', 'dex', 'int', 'wis', 'cha', 'hp_regen', 'mana_regen', 'haste', 'spell_haste', 'cr', 'cor', 'dr', 'er', 'fr', 'mr', 'pr', 'hr']
def _hb_items():
    gear = {g for g, _, _ in HB_GEAR}
    rows = []
    for nm, it in sorted(ITEMS.items()):
        sl = [s for s in slots_of(it) if s in gear]
        if not sl: continue
        st = {}
        for k in _HB_STATS:
            v = it.get(k)
            if v not in (None, '', '0'):
                n = num(v)
                if n: st[k] = int(n) if n == int(n) else n
        dr = []
        for d in it.get('drops', [])[:3]:
            z = d.get('zone') or ''
            dr.append([d.get('mob') or '', z, (dungeon_url(z) if z in DUNGEON_ORDER else zone_url(z) if z in ZONES else '').lstrip('/'), d.get('level') or ''])
        o = [nm, ' '.join(sl), ' '.join(class_codes(it)), item_level(it) or 0, st, it.get('url', ''), dr,
             (it.get('quests') or [''])[0], 1 if it.get('soldby') else 0, 1 if it.get('crafted') else 0]
        if it.get('dmg') and it.get('delay'): o.append('%s/%s' % (it['dmg'], it['delay']))
        else: o.append('')
        o.append(it.get('effect') or '')
        rows.append(o)
    return rows
def _hb_page():
    src = ''.join('<li><span class="badge %s">%s</span> %s <span class="dim">(%s)</span></li>' % (
        'fact' if l == 'FACT' else 'unc', l.lower(), esc(t), ', '.join('<a class="ext" target="_blank" rel="noopener" href="%s">%s</a>' % (esc(HB_SRC[k][1]), esc(HB_SRC[k][0].split(' (')[0])) for k in ks))
        for l, t, ks in HB_FACTS)
    return ('<link rel="stylesheet" href="/assets/mod-hotbar.css">'
            '<div id="hb-app" class="hb-app">'
            '<p class="hb-intro">Plan your bars for the Class, Race and Levels picked in the top bar. Drag a spell or ability onto a slot, or click/tap it and then a slot. Keyboard: Enter picks up, arrow keys move between slots, Enter places, Delete clears, Esc cancels. '
            '<span class="badge fact">fact</span> Spells and abilities come from your class\'s wiki spell list, gated by level. <span class="badge strat">strategy</span> Suggested layouts are rules of thumb, not tested rotations.</p>'
            '<details class="box hb-facts"><summary><b>How M&amp;M bars work</b> (sourced vs unverified)</summary><ul class="tight">%s</ul>'
            '<p class="dim">Gear slots: names from the wiki <a class="ext" target="_blank" rel="noopener" href="%s">Equipment By Slot</a> list and its item slot codes <span class="badge fact">fact</span>; 3 belt slots from the official guide <span class="badge fact">fact</span>; two each of Ear, Wrist and Finger is an assumption <span class="badge unc">unverified</span>.</p></details>'
            '<div class="hb-toolbar" role="toolbar" aria-label="Hotbar planner tools">'
            '<label>Level <input type="number" id="hb-level" min="1" max="60" inputmode="numeric" aria-describedby="hb-lvlnote"></label>'
            '<label>Layout <select id="hb-layout" aria-label="Saved layout"></select></label>'
            '<label>Name <input id="hb-lname" maxlength="24" aria-label="Layout name"></label>'
            '<button type="button" id="hb-new" title="New custom layout">+ New</button><button type="button" id="hb-del" title="Delete this custom layout">Delete</button>'
            '<label title="How many hotbar pages exist is not documented">Hotbar pages <input type="number" id="hb-pages" min="1" max="10" inputmode="numeric"> <span class="badge unc">unverified</span></label>'
            '<button type="button" id="hb-suggest" title="Fill this layout with the suggested starter layout">Suggest</button>'
            '<button type="button" id="hb-undo" title="Undo (Ctrl+Z)" disabled>Undo</button><button type="button" id="hb-clear">Clear layout</button>'
            '<button type="button" id="hb-keys" aria-pressed="false">Edit keybinds</button>'
            '<button type="button" id="hb-sheet-t" aria-pressed="false" aria-controls="hb-sheet">Character sheet</button>'
            '<button type="button" id="hb-focus-t" class="hb-primary" aria-pressed="false">Focus mode</button></div>'
            '<p id="hb-lvlnote" class="dim hb-lvlnote"></p>'
            '<p id="hb-msg" class="hb-msg" role="status" aria-live="polite"></p>'
            '<div class="hb-main"><section class="hb-bars-wrap" aria-label="Bars">'
            '<div class="hb-focusbar"><b id="hb-ftitle"></b><label>Size <input type="range" id="hb-size" min="28" max="96" step="2" aria-label="Focus mode size"></label>'
            '<button type="button" id="hb-pop">Pop out</button><button type="button" id="hb-print">Print</button><button type="button" id="hb-focus-x">Exit (Esc)</button></div>'
            '<div id="hb-bars" class="hb-bars"></div>'
            '<div class="hb-side"><div class="hb-rot"><h3>Rotation / priority</h3><ol id="hb-rotlist" class="hb-rotlist"></ol>'
            '<label class="hb-edit">Edit (one step per line; blank = from your bars)<textarea id="hb-rot" rows="4"></textarea></label></div>'
            '<div class="hb-notes"><h3>Notes</h3><div id="hb-notesview" class="hb-notesview"></div><label class="hb-edit">Notes for this layout<textarea id="hb-notes" rows="3"></textarea></label></div></div>'
            '<div id="hb-why" class="hb-why"></div>'
            '</section>'
            '<section class="hb-pal" aria-label="Spells and abilities"><h2 id="palette">Your spells and abilities</h2>'
            '<div class="hb-paltools"><input type="search" id="hb-q" placeholder="Filter by name or effect…" aria-label="Filter spells"><select id="hb-kind" aria-label="Type"><option value="">All types</option><option value="s">Spells</option><option value="i">Innate abilities</option><option value="a">Auras / Hide / Sneak</option><option value="h">Hotbar: skills, traits, clickies, macros</option></select>'
            '<label><input type="checkbox" id="hb-future"> Show higher-level too</label></div>'
            '<p id="hb-palcount" class="dim"></p><div id="hb-palette" class="hb-palette" role="listbox" aria-label="Spells and abilities to place"></div>'
            '<form id="hb-macro" class="hb-macro"><b>Macro button</b> <input id="hb-mname" placeholder="Label" maxlength="24" aria-label="Macro label"> <input id="hb-mcmd" placeholder="/command" maxlength="200" aria-label="Macro command"> <button type="submit">Add to palette</button>'
            '<span class="dim">Macros run slash commands (see <code>/help</code> in game); they go on the hotbar.</span></form>'
            '</section></div>'
            '<section id="hb-sheet" class="hb-sheet" hidden aria-label="Character sheet"><h2 id="charsheet">Character sheet</h2>'
            '<p class="dim">Pick gear from the <a href="/items.html">Item database</a> for each slot (filtered to your class and slot). Totals use only the item stats on the wiki item pages <span class="badge fact">fact</span> plus the base stats of the build you pick: your race\'s starting stats for this class plus that build\'s bonus points (wiki race pages; builds are this Codex\'s <span class="badge strat">strategy</span>). Base resists, level-up stat gains and caps are not sourced, so they are not added <span class="badge unc">unverified</span>.</p>'
            '<p><label>Base build <select id="hb-build" aria-label="Base stat build"></select></label> <button type="button" id="hb-gclear">Clear all gear</button></p>'
            '<div class="hb-sheetgrid"><div id="hb-doll" class="hb-doll"></div><div><div id="hb-totals" class="hb-totals"></div><div id="hb-picker" class="hb-picker" hidden></div></div></div></section>'
            '<section class="hb-share" aria-label="Save and share"><h2 id="share">Save, share, import</h2>'
            '<p class="dim">Saved automatically in this browser (per class). The share link stores your current class\'s layouts and gear compressed in the link after <code>#hb=</code>.</p>'
            '<div class="hb-toolbar"><button type="button" id="hb-copy">Copy share link</button><button type="button" id="hb-code">Show share code</button>'
            '<button type="button" id="hb-export">Export JSON</button><label class="hb-file">Import JSON <input type="file" id="hb-import" accept="application/json,.json"></label>'
            '<label><input type="checkbox" id="hb-strict" checked> M&amp;M bar rules (spells on the ability bar, skills/macros/items on the hotbar)</label></div>'
            '<textarea id="hb-codebox" rows="2" hidden aria-label="Share code" readonly></textarea>'
            '<form id="hb-codeform" class="hb-codeform"><input id="hb-codein" placeholder="Paste a share code or link" aria-label="Paste share code"> <button type="submit">Load code</button></form></section>'
            '</div><div id="hb-tip" class="hb-tip" role="tooltip" hidden></div>'
            '<script src="/assets/hotbar-data.js"></script><script src="/assets/mod-hotbar.js"></script>') % (src, esc(HB_SRC['slot'][1]))
_hb_prev_bc = build_content
def build_content():
    _hb_prev_bc()
    add_page('hotbar.html', 'Hotbar planner', body_html=_hb_page(), section='hotbar', desc='Plan ability bar, hotbar and aura bar layouts per class, with focus mode and a character sheet',
             sources=['%s|%s' % (v[0], v[1]) for v in HB_SRC.values()] + ['Wiki class pages (spell lists)|%sCategory:Classes' % WIKI, 'Wiki Template:Traits (rev %s)|%s' % (CG['_source']['traits']['revid'], CG['_source']['traits']['url']), 'Wiki item pages|%sCategory:Items' % WIKI])
_hb_prev_ra = render_all
def render_all():
    _hb_prev_ra()
    open(os.path.join(OUT, 'assets', 'hotbar-data.js'), 'w', encoding='utf8').write('window.MNM_HB=' + json.dumps(_hb_data(), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + ';')
    open(os.path.join(OUT, 'assets', 'hotbar-items.js'), 'w', encoding='utf8').write('window.MNM_HBI=' + json.dumps(_hb_items(), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + ';')
NAV.insert(len(NAV) - 1, ('Hotbar planner', '/hotbar.html', 'hotbar'))

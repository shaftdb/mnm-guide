# Quest helper module: /quest-helper.html from data/quest_steps.json (tools/wikifetch.py + tools/quest_steps.py)
QSTEPS = json.load(open(os.path.join(DATA, 'quest_steps.json'), encoding='utf8')) if os.path.exists(os.path.join(DATA, 'quest_steps.json')) else {}
_QK = {'do': '', 'info': 'ℹ ', 'get': 'Receive: ', 'fac': 'Faction: ', 'xp': ''}
def _qrow(q):
    st = []
    for k, v in q['steps']:
        if k == 'h': st.append('</ol><h4>%s</h4><ol class="tight">' % esc(v))
        elif k == 'xp': st.append('<li class="dim">Experience reward</li>')
        else: st.append('<li%s>%s%s</li>' % (' class="dim"' if k in ('info', 'fac', 'get') else '', _QK[k], esc(v)))
    steps = ('<ol class="tight">%s</ol>' % ''.join(st)).replace('<ol class="tight"></ol>', '') if st else '<p><span class="badge unc">unverified</span> No walkthrough on the wiki yet.</p>'
    z = q['zone']; zl = (zlink(z) if z in ZONES else esc(z)) if z else '<span class="dim">zone not listed</span>'
    kinds = ''.join('<span class="tag">%s</span>' % k for k in q['kinds'])
    return ('<details class="call qh" data-k="%s" data-cls="%s"><summary><b>%s</b> <span class="dim">min lvl %s</span> %s</summary>'
            '<p class="dim">%s · Giver: %s%s%s</p>%s%s<p class="dim"><a class="ext" target="_blank" rel="noopener" href="%s">Wiki page</a> (updated %s)</p></details>') % (
        ' '.join(q['kinds']) or 'other', esc('|'.join(q['classes'])), esc(q['title']), esc(q['min'] or '?'), kinds, zl, esc(q['giver'] or '?'),
        (' · Classes: ' + esc(', '.join(q['classes']))) if q['classes'] else '', (' · Rewards: ' + esc(q['rewards'])) if q['rewards'] else '',
        '<p><span class="badge unc">unverified</span> The wiki marks this page as needing more info.</p>' if q['needsinfo'] else '', steps, esc(wiki(q['title'])), esc(q['ts']))
def _quest_page():
    order = sorted(QSTEPS.values(), key=lambda q: (0 if q['kinds'] else 1, lvl_num(q['min']) or 0, q['title']))
    n = {k: sum(1 for q in QSTEPS.values() if k in q['kinds']) for k in ('class', 'armor', 'spell', 'access')}
    return ('<link rel="stylesheet" href="/assets/mod-quests.css"><p>Step lists for %d quests from the community wiki walkthroughs <span class="badge fact">fact</span>, shortened to the actions, items received and faction changes; NPC dialogue is left out. '
            'Class, armor, spell and access quests come first. The quest types are sorted by keyword and may be wrong <span class="badge unc">unverified</span>. Use "Filter this page" for an NPC, item or zone.</p>'
            '<p class="qh-tools"><label><input type="checkbox" id="qh-mine"> Only my class (plus all-class)</label> <select id="qh-kind" aria-label="Quest type"><option value="">All types</option>'
            '<option value="class">Class (%d)</option><option value="armor">Armor (%d)</option><option value="spell">Spell (%d)</option><option value="access">Access / key (%d)</option><option value="other">Other</option></select></p>%s'
            '<script src="/assets/mod-quests.js"></script>') % (len(QSTEPS), n['class'], n['armor'], n['spell'], n['access'], ''.join(_qrow(q) for q in order))
_q_prev_bc = build_content
def build_content():
    _q_prev_bc()
    add_page('quest-helper.html', 'Quest helper', body_html=_quest_page(), section='quests',
             sources=['Wiki: Category:Quests (walkthroughs, fetched with tools/wikifetch.py)|%sCategory:Quests' % WIKI], desc='Quest step lists')
NAV[:] = [(t, '/quest-helper.html', k) if k == 'quests' else (t, u, k) for t, u, k in NAV]

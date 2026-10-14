# Faction guide module: page /faction-guide.html from data/faction_guide.json (tools/factions_fetch.py)
FGUIDE = json.load(open(os.path.join(DATA, 'faction_guide.json'), encoding='utf8')) if os.path.exists(os.path.join(DATA, 'faction_guide.json')) else {}
_FK = [('zones_raise', 'Raise in zones'), ('quests_raise', 'Raise with quests'), ('mobs_raise', 'Raise by killing'),
       ('zones_lower', 'Lower in zones'), ('quests_lower', 'Lower with quests'), ('mobs_lower', 'Lower by killing')]
def _fz(x):
    b = re.sub(r'\s*\(.*$', '', x).strip()
    if b in DUNGEON_ORDER: return '<a href="%s">%s</a>%s' % (dungeon_url(b), esc(b), esc(x[len(b):]))
    if b in ZONES: return zlink(b) + esc(x[len(b):])
    return esc(x)
def _fq(x): return '<a class="ext" target="_blank" rel="noopener" href="%s">%s</a>' % (esc(wiki(x)), esc(x))
def _faction_page():
    cities = [z for z in sorted(ZONES) if re.search(r'city|hub|capital', ZEXTRA.get(z, {}).get('type', ''), re.I)]
    o = ['<p>What raises or lowers each faction, from the community wiki faction pages <span class="badge fact">fact</span>. '
         'The wiki lists sources, not amounts. How much each kill or quest moves a faction, and the standing a city needs before its guards attack or its merchants refuse you, is not on the wiki <span class="badge unc">unverified</span>. '
         'Use "Filter this page" for a zone, mob or quest.</p>', '<h2 id="cities">Cities and their factions</h2>',
         '<p><span class="badge fact">fact</span> Factions the wiki says you can raise or lower inside each city or hub. <span class="badge strat">strategy</span> Before you travel to a city, check these. A faction you have lowered is the likeliest reason its guards turn hostile.</p><ul class="tight">']
    for z in cities:
        up = sorted(n for n, F in FGUIDE.items() if any(re.sub(r'\s*\(.*$', '', x).strip() == z for x in F.get('zones_raise', [])))
        dn = sorted(n for n, F in FGUIDE.items() if any(re.sub(r'\s*\(.*$', '', x).strip() == z for x in F.get('zones_lower', [])))
        o.append('<li><b>%s</b> <span class="dim">(%s)</span>: raise %s%s</li>' % (zlink(z), esc(ZEXTRA[z].get('type', '')), ', '.join('<a href="#f-%s">%s</a>' % (slug(n), esc(n)) for n in up) or '<span class="dim">none listed</span>',
                 ('; lower ' + ', '.join('<a href="#f-%s">%s</a>' % (slug(n), esc(n)) for n in dn)) if dn else ''))
    o.append('</ul><h2 id="all">All factions</h2>')
    for n, F in sorted(FGUIDE.items()):
        rows = []
        for k, lab in _FK:
            v = F.get(k) or []
            if v: rows.append('<tr><th>%s</th><td>%s</td></tr>' % (lab, ', '.join((_fq if k.startswith('quests') else _fz)(x) for x in v)))
        if not rows: rows.append('<tr><td colspan="2"><span class="badge unc">unverified</span> The wiki lists no way to raise or lower this faction.</td></tr>')
        o.append('<details class="call" id="f-%s"><summary><b>%s</b></summary><p>%s</p><div class="tw"><table class="grid">%s</table></div><p class="dim"><a class="ext" target="_blank" rel="noopener" href="%s">Wiki page</a> (rev %s)</p></details>' % (
            slug(n), esc(n), esc(F.get('desc') or '') or '<span class="dim">No description on the wiki.</span>', ''.join(rows), esc(F['url']), F.get('revid')))
    return ''.join(o)
_fac_prev_bc = build_content
def build_content():
    _fac_prev_bc()
    add_page('faction-guide.html', 'Faction guide', body_html=_faction_page(), section='factions',
             sources=['Wiki: Factions|%sFactions' % WIKI, 'Wiki faction pages (raise/lower tables), fetched with tools/factions_fetch.py|%sCategory:Factions' % WIKI], desc='Faction guide: raise, lower, city access')
NAV[:] = [(t, '/faction-guide.html', k) if k == 'factions' else (t, u, k) for t, u, k in NAV]

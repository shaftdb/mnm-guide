# Tradeskills & gathering module: /trades-guide.html from data/trades.json (tools/wikifetch.py + tools/trades_extract.py)
TRADEX = json.load(open(os.path.join(DATA, 'trades.json'), encoding='utf8')) if os.path.exists(os.path.join(DATA, 'trades.json')) else {}
def _col(head, *names):
    for i, h in enumerate(head):
        if any(n in h.lower() for n in names): return i
    return None
def _num(s):
    m = re.search(r'\d+', s or ''); return int(m.group()) if m else None
def _trades_page():
    nodes = {}; paths = []; recipes = []
    for n, S in sorted(TRADEX.items()):
        for tb in S['tables']:
            h = tb['head']; il = _col(h, 'location'); imn = _col(h, 'min', 'req'); itr = _col(h, 'trivial')
            if il is not None and imn is not None:   # gathering chart
                rows = []
                for r in tb['rows']:
                    c = r['c'] + [''] * 6
                    zs = [x for x in (r['l'][il] if il < len(r['l']) else []) if x in ZONES]
                    for z in zs: nodes.setdefault(z, []).append((n, c[0], c[imn], c[itr] if itr is not None else ''))
                    rows.append((_num(c[imn]) or 0, c[0], c[imn], c[itr] if itr is not None else '', c[il]))
                if rows: paths.append((n, tb['sec'], sorted(rows)))
            else:
                recipes.append((n, tb))
    o = ['<link rel="stylesheet" href="/assets/mod-trades.css">',
         '<p>Gathering nodes, skill-up charts and recipes from the community wiki tradeskill pages <span class="badge fact">fact</span>. Use "Filter this page" for an ore, recipe or zone.</p>',
         '<div class="call note"><p><span class="badge strat">strategy</span> <b>Self-sufficient play:</b> pair a gathering skill with the skill that refines it and the one that uses it, and you can make much of your own gear and consumables without the market. The wiki states these chains: Mining → Smelting → Blacksmithing or Jewelcrafting; Lumberjacking → Carpentry, Woodworking or Fletching; Herbalism → Alchemy; Skinning → Tanning → Leatherworking; Fishing and Farming → Cooking. Level a gathering skill while you hunt in a zone that has its nodes (table below).</p></div>']
    o.append('<h2 id="nodes">Nodes by zone</h2><p class="dim"><span class="badge fact">fact</span> Zones named in each wiki gathering chart. Min = skill needed to attempt, Trivial = where skill-ups stop.</p><div class="tw"><table class="grid sortable"><thead><tr><th>Zone</th><th>Skill</th><th>Node</th><th>Min</th><th>Trivial</th></tr></thead><tbody>%s</tbody></table></div>' % ''.join(
        '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (zlink(z), esc(s), esc(nd), esc(mn), esc(tr)) for z in sorted(nodes) for s, nd, mn, tr in sorted(nodes[z], key=lambda x: (x[0], _num(x[2]) or 0))))
    o.append('<h2 id="paths">Skill-up paths (gathering)</h2><p class="dim"><span class="badge strat">strategy</span> Work down each list, moving to the next node once the current one turns trivial. The order comes from the wiki min/trivial values.</p>')
    for n, sec, rows in paths:
        o.append('<details class="call"><summary><b>%s</b> <span class="dim">%s</span></summary><ol class="tight">%s</ol></details>' % (esc(n), esc(sec), ''.join('<li><b>%s</b> (skill %s–%s): %s</li>' % (esc(nd), esc(mn), esc(tr) or '?', esc(loc)) for _, nd, mn, tr, loc in rows)))
    o.append('<h2 id="skills">Skills, trainers and recipes</h2>')
    for n, S in sorted(TRADEX.items()):
        inf = ''.join('<tr><th>%s</th><td>%s</td></tr>' % (esc(k), esc(v)) for k, v in S['info'].items() if v and v != '-' and k != n)
        tips = ''.join('<li>%s</li>' % esc(t) for t in S['tips'] if 'Formatting' not in t)
        tbs = ''.join('<h4>%s</h4><div class="tw"><table class="grid sortable"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
            esc(tb['sec']), ''.join('<th>%s</th>' % esc(x) for x in tb['head']), ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % esc(x) for x in r['c']) for r in tb['rows'][:250])) for m, tb in recipes if m == n)
        o.append('<details class="call" id="t-%s"><summary><b>%s</b>%s</summary>%s%s%s%s<p class="dim"><a class="ext" target="_blank" rel="noopener" href="%s">Wiki page</a> (updated %s)</p></details>' % (
            slug(n), esc(n), '' if (S['tables'] or S['intro']) else ' <span class="badge unc">stub on wiki</span>', ''.join('<p>%s</p>' % esc(p) for p in S['intro']),
            ('<table class="grid">%s</table>' % inf) if inf else '', ('<ul class="tight">%s</ul>' % tips) if tips else '', tbs, esc(wiki(S['title'])), esc(S['ts'])))
    return ''.join(o)
_t_prev_bc = build_content
def build_content():
    _t_prev_bc()
    add_page('trades-guide.html', 'Tradeskills & gathering', body_html=_trades_page(), section='tradeskills',
             sources=['Wiki: Category:Tradeskills (skill pages, fetched with tools/wikifetch.py)|%sCategory:Tradeskills' % WIKI], desc='Tradeskills, gathering nodes and recipes')
NAV[:] = [(t, '/trades-guide.html', k) if k == 'tradeskills' else (t, u, k) for t, u, k in NAV]

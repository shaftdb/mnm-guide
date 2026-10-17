# Tradeskill selector module: multi-select tradeskill picker in the top bar (localStorage mnm-trades),
# per-level-range tradeskill guidance (zones picked by character level, skill numbers from the wiki),
# per-skill skill-up guides (/trades/<skill>.html), selection filtering on tradeskill content,
# and tradeskill badges on gear items linked to wiki recipes.
TS_KEY = 'mnm-trades'
TS_GATHER_DEFAULT = ['Mining', 'Lumberjacking', 'Smelting']     # user default: gathering skills + smelting (separate skill on the wiki)
TS_SMITH = ['Blacksmithing']                                    # smithing: off by default, still selectable
TS_KINDS = [('gather', 'Gathering'), ('refine', 'Refining'), ('craft', 'Crafting'), ('other', 'Other')]
TS_REFINE = ['Smelting', 'Tanning', 'Woodworking', 'Stone Cutting']
TS_ALIAS = {'Smithing': 'Blacksmithing'}                        # item pages say "Smithing"; the skill page is Blacksmithing

def _tnum(s):
    m = re.search(r'\d+', s or ''); return int(m.group()) if m else None
def _hcol(head, *pats):
    for i, h in enumerate(head):
        if any(re.search(p, h, re.I) for p in pats): return i
    return None
def _zone_lo(z):
    """(low level, high level, how) for a zone; wiki zone level, else lowest wiki mob level (estimate)."""
    Z = ZONES.get(z)
    if not Z: return None, None, 'none'
    lv = Z.get('level') or ''
    ns = [int(x) for x in re.findall(r'\d+', lv)]
    if ns: return ns[0], (ns[1] if len(ns) > 1 else None), 'wiki'
    ls = [lvl_num(e.get('level')) for e in Z['npcs'] + Z['named']]
    ls = [x for x in ls if x]
    if ls: return min(ls), max(ls), 'est'
    return None, None, 'none'
def _zsafe(z, hi):
    lo, _, how = _zone_lo(z)
    return None if (lo is None or how != 'wiki') else lo <= hi   # mob-level estimates are not trusted for safety
def _zlabel(z):
    lo, h2, how = _zone_lo(z)
    if lo is None: lab = 'zone level not on wiki'
    elif how == 'est': lab = 'no zone level on wiki; listed mobs lvl %s–%s' % (lo, h2)
    else: lab = 'zone lvl %s%s' % (lo, '–%s' % h2 if h2 else '+')
    return '%s <span class="dim">(%s)</span>' % (zlink(z) if z in ZONES else esc(z), lab)
def _split_ing(s):
    out = []
    for part in re.split(r',\s*', s or ''):
        part = part.strip()
        if not part or part in ('-', '?'): continue
        m = re.match(r'(\d+)\s*x\s+(.+)$', part, re.I) or re.match(r'(.+?)\s+x\s*(\d+)$', part, re.I)
        if m:
            a, b = m.groups(); q, n = (a, b) if a.isdigit() else (b, a)
        else: q, n = '', part
        out.append((q, n.strip()))
    return out

def _ts_model():
    """normalise data/trades.json into gathering steps and recipes per skill (only rows the wiki gives)."""
    M = {}
    for n, S in TRADEX.items():
        gather, recipes, other = [], [], []
        for tb in S['tables']:
            h = tb['head']
            il = _hcol(h, r'location'); imn = _hcol(h, r'^min', r'req'); itr = _hcol(h, r'trivial')
            if il is not None and imn is not None and n != 'Bind Wound':
                iy = _hcol(h, r'yield')
                for r in tb['rows']:
                    c = r['c'] + [''] * 8; L = r['l'] + [[]] * 8
                    zs = [x for x in L[il] if x in ZONES] or [x.strip() for x in re.sub(r'\([^)]*\)', '', c[il]).split(',') if x.strip()]
                    zs = list(dict.fromkeys(zs))
                    extra = [c[i] for i in range(len(h)) if i not in (0, il, imn, itr, iy) and c[i] and c[i] not in ('-', '}')]
                    gather.append(dict(node=c[0], mn=c[imn], tr=c[itr] if itr is not None else '', mnv=_tnum(c[imn]), trv=_tnum(c[itr]) if itr is not None else None,
                                       zones=zs, loc=c[il], yields=c[iy] if iy is not None else '', notes='; '.join(extra), sec=tb['sec']))
                continue
            if itr is None: other.append(tb); continue
            ires = _hcol(h, r'result', r'^item', r'scroll', r'product', r'processed', r'enchanted material', r'^component$')
            if ires == itr: ires = None
            ing = _hcol(h, r'ingredient', r'component', r'materials', r'^unprocessed', r'^unenchanted', r'target')
            if _hcol(h, r'disenchants into') is not None: ires, ing = _hcol(h, r'disenchants into'), _hcol(h, r'target')
            if ires is None or ing is None or ing == ires:
                if _hcol(h, r'^metal$') is not None: ing = None
                else: other.append(tb); continue
            ist = _hcol(h, r'station', r'bench', r'mold', r'kit')
            for r in tb['rows']:
                c = r['c'] + [''] * 30; L = r['l'] + [[]] * 30
                if ing is None:   # jewelry tables: Metal / Gem / Mold Type columns
                    parts = [c[i] for i in (_hcol(h, r'^metal$'), _hcol(h, r'^gem$')) if i is not None and c[i] not in ('', '-')]
                    ings = [('1', p) for p in parts]; lk = [x for i in (_hcol(h, r'^metal$'), _hcol(h, r'^gem$')) if i is not None for x in L[i]]
                    st = c[_hcol(h, r'mold')] if _hcol(h, r'mold') is not None else ''
                else:
                    ings = _split_ing(c[ing]); lk = L[ing]; st = c[ist] if ist is not None else ''
                res = c[ires]
                if not res or res in ('}', '-'): continue
                rq = re.match(r'(\d+)\s*x\s+(.+)$', res); rname = rq.group(2) if rq else res
                rname = re.sub(r'\s*\(item\)$', '', rname).strip()
                recipes.append(dict(tr=c[itr], trv=_tnum(c[itr]), res=res, rname=rname, rlinks=[re.sub(r'\s*\(item\)$', '', x) for x in L[ires]],
                                    ings=ings, ilinks=lk, station=st if st not in ('-', '}') else '', sec=tb['sec']))
        kind = 'gather' if gather else ('refine' if n in TS_REFINE else ('craft' if recipes else 'other'))
        if n == 'Bind Wound': kind = 'other'
        M[n] = dict(name=n, kind=kind, gather=gather, recipes=recipes, other=other, S=S,
                    stub=not (gather or recipes or other))
    return M
TSM = _ts_model()
TS_ORDER = [n for k, _ in TS_KINDS for n in sorted(TSM) if TSM[n]['kind'] == k and not TSM[n]['stub']]
TS_STUBS = sorted(n for n in TSM if TSM[n]['stub'])
def ts_url(n): return '/trades/%s.html' % slug(n)

# ---- material sources (only what the wiki states)
def _mat_index():
    idx = {}
    def add(name, src): idx.setdefault(name.lower(), []).append(src)
    for n, T in TSM.items():
        for g in T['gather']:
            for y in re.split(r',\s*', g['yields']) if g['yields'] else []:
                if y: add(y, ('gather', n, g))
            add(g['node'], ('gather', n, g))          # herbs and fish: the node is the material
        for r in T['recipes']:
            add(r['rname'], ('craft', n, r))
        for tb in T['other']:
            h = tb['head']; idf = _hcol(h, r'drops from')
            if idf is not None:
                for row in tb['rows']:
                    add(row['c'][0], ('drop', n, row['c'][idf]))
            iyd = _hcol(h, r'yield', r'resulting')
            if iyd is not None:
                for row in tb['rows']:
                    c = row['c'] + [''] * 4
                    for q, m in _split_ing(re.sub(r'^Yields\s*', '', c[iyd])):
                        add(m, ('scrap', n, c[0]))
    for m, Mm in MERCH.items():
        for s in Mm['sells']: add(s, ('vendor', m, Mm))
    for nm, it in ITEMS.items():
        for d in it.get('drops') or []:
            add(nm, ('itemdrop', nm, d))
    return idx
TS_MATS = _mat_index()
def _mob_info(mob):
    out = []
    for z, Z in ZONES.items():
        for e in Z['npcs'] + Z['named']:
            if e['name'].lower() == mob.lower(): out.append((z, e.get('level') or '?'))
    return out
def _zstate(zs, hi):
    v = [_zsafe(z, hi) for z in zs]
    return True if any(v) else (None if (None in v or not v) else False)
def mat_sources(name, hi=None, skip_skill=None):
    """list of (html, safe) source lines for a material; safe = reachable at band top hi (None = unknown)."""
    out = []
    for kind, who, d in TS_MATS.get(name.lower(), []):
        if kind == 'gather':
            if who == skip_skill and d['node'].lower() == name.lower(): continue
            zs = d['zones']
            out.append(('<b>%s</b> %s node %s (skill %s–%s): %s' % (esc(who), 'gather' if d['node'].lower() == name.lower() else 'from', esc(d['node']), esc(d['mn'] or '?'), esc(d['tr'] or '?'),
                        ', '.join(_zlabel(z) for z in zs) or 'location not on wiki'), _zstate(zs, hi) if hi is not None else None))
        elif kind == 'craft':
            if who == skip_skill and d['rname'].lower() == name.lower(): out.append(('crafted earlier in this skill (trivial %s)' % esc(d['tr'] or '?'), True)); continue
            out.append(('crafted with <a href="%s">%s</a> (trivial %s from %s)' % (ts_url(who), esc(who), esc(d['tr'] or '?'), esc(', '.join('%s%s' % (q + 'x ' if q else '', i) for q, i in d['ings'])) or '?'), None))
        elif kind == 'scrap':
            out.append(('scrapped from %s (<a href="%s">%s</a> table)' % (esc(d), ts_url(who), esc(who)), None))
        elif kind == 'vendor':
            zs = [z for z in d['zone'] if z]
            out.append(('vendor <a class="ext" target="_blank" rel="noopener" href="%s">%s</a>: %s%s' % (esc(d['url']), esc(who), ', '.join(_zlabel(z) for z in zs) or 'zone not on wiki',
                        (' · ' + esc(d['location'])[:90]) if d.get('location') else ''), _zstate(zs, hi) if hi is not None else None))
        elif kind in ('drop', 'itemdrop'):
            mobs = [x.strip() for x in re.split(r',\s*', d if isinstance(d, str) else (d.get('mob') or d.get('name') or str(d)))]
            seg = []; safe = None
            for mb in mobs[:4]:
                inf = _mob_info(mb)
                if inf:
                    seg.append('%s (%s)' % (esc(mb), ', '.join('%s lvl %s' % (zlink(z), esc(l)) for z, l in inf[:3])))
                    if hi is not None:
                        lv = [lvl_num(l) for _, l in inf if lvl_num(l)]
                        if lv:
                            ok = min(lv) <= hi; safe = ok if safe is None else (safe or ok)
                else: seg.append(esc(mb))
            out.append(('drops from %s' % ', '.join(seg), safe))
    return out

def _name_match(name):
    """'Copper Ore' / 'Limestone' / 'Coal' -> gathering nodes whose name starts with the same material word (name match only: unverified)"""
    base = re.sub(r'\s+Ore$', '', name).strip().lower()
    hits = []
    for n, T in TSM.items():
        for g in T['gather']:
            nn = g['node'].lower()
            if re.match(r'(rich )?%s (vein|deposit)$' % re.escape(base), nn): hits.append((n, g))
    return hits
def _srcs_html(name, hi=None, skip=None):
    s = list(dict.fromkeys(mat_sources(name, hi, skip)))
    if not s:
        nm = _name_match(name)
        if nm:
            def ok(g):
                if hi is None: return ''
                v = [_zsafe(z, hi) for z in g['zones']]
                return ' <span class="ts-ok">✓ fits your level</span>' if any(v) else (' <span class="badge unc">zone level unverified</span>' if None in v else ' <span class="ts-no">above your level</span>')
            return '<span class="badge unc">unverified</span> name match only: %s' % '; '.join('<a href="%s">%s</a> %s (skill %s–%s)%s' % (ts_url(n), esc(n), esc(g['node']), esc(g['mn'] or '?'), esc(g['tr'] or '?'), ok(g)) for n, g in nm[:2])
    if not s: return '<span class="badge unc">no wiki source</span>'
    def mark(ok):
        return '' if ok is None or hi is None else (' <span class="ts-ok">✓ fits your level</span>' if ok else ' <span class="ts-no">above your level</span>')
    return '<br>'.join(h + mark(ok) for h, ok in s[:4]) + (' <span class="dim">(+%d more)</span>' % (len(s) - 4) if len(s) > 4 else '')

TS_MAP_NOTE = ('<p class="dim ts-map"><span class="badge strat">strategy</span> <b>How this is mapped:</b> your <b>character level range</b> (top bar) picks the zones: a zone counts as safe when its low level on the wiki zone page '
               'is at or below the top of your range. Zones with no level on the wiki are marked <span class="badge unc">zone level unverified</span> and never counted as safe. <span class="badge fact">fact</span> Node and recipe skill numbers (min skill to attempt, trivial = skill-ups stop) are copied from the wiki tradeskill pages. '
               'Character level and tradeskill level are separate; wide zones like "1–50" still have dangerous corners, so /consider first. Costs: the wiki and merchant data list no prices, so costs are not sourced.</p>')

def ts_band(n, lo, hi):
    T = TSM[n]; S = T['S']
    head = '<div class="qi-sec ts-band" data-ts="%s"><h3>%s · levels %d–%d <span class="badge fact">skill numbers: fact</span> <span class="badge strat">zone fit: strategy</span></h3>' % (slug(n), esc(n), lo, hi)
    tail = '<p><a href="%s">Full %s skill-up guide →</a></p></div>' % (ts_url(n), esc(n))
    trainer = S['info'].get('Trainer') or S['info'].get('Trainers')
    tl = []
    if trainer: tl.append('Trainer: %s%s' % (esc(trainer), (' — ' + esc(S['info'].get('Location'))) if S['info'].get('Location') else ''))
    tool = S['info'].get('Primary Tool') or S['info'].get('Primary Tools')
    if tool: tl.append('Tool: %s' % esc(tool))
    info = ('<p class="dim">%s <span class="badge fact">fact</span></p>' % ' · '.join(tl)) if tl else ''
    if T['gather']:
        ok, later = [], []
        for g in sorted(T['gather'], key=lambda g: (g['mnv'] if g['mnv'] is not None else 999)):
            safe = [z for z in g['zones'] if _zsafe(z, hi)]; unk = [z for z in g['zones'] if _zsafe(z, hi) is None]
            row = '<tr><td>%s%s</td><td>%s–%s</td><td>%s</td></tr>'
            if safe or unk:
                ok.append(row % (esc(g['node']), (' <span class="dim">→ %s</span>' % esc(g['yields'])) if g['yields'] else '', esc(g['mn'] or '?'), esc(g['tr'] or '?'),
                                 ', '.join(_zlabel(z) for z in safe) + ((' · <span class="badge unc">zone level unverified</span> ' + ', '.join(_zlabel(z) for z in unk)) if unk else '')
                                 + ((' <span class="dim">· wiki: %s</span>' % esc(g['loc'])) if '(' in g['loc'] else '')))
            else:
                later.append('<li>%s (skill %s–%s): %s</li>' % (esc(g['node']), esc(g['mn'] or '?'), esc(g['tr'] or '?'), ', '.join(_zlabel(z) for z in g['zones']) or 'location not on wiki'))
        body = ('<p><span class="badge strat">strategy</span> Gather the lowest node that still gives skill-ups for you (your skill below its trivial), in a zone that fits your level:</p>'
                '<div class="tw"><table class="grid ts-t"><thead><tr><th>Node</th><th>Skill min–trivial</th><th>Zones that fit %d–%d</th></tr></thead><tbody>%s</tbody></table></div>' % (lo, hi, ''.join(ok) or '<tr><td colspan="3">No wiki node is in a zone that fits this level range.</td></tr>'))
        if later: body += '<details><summary>Nodes only in zones above your level (%d)</summary><ul class="tight">%s</ul></details>' % (len(later), ''.join(later))
        return head + info + body + tail
    if T['recipes']:
        rs = sorted([r for r in T['recipes'] if r['trv'] is not None], key=lambda r: r['trv'])
        first = rs[:6]
        rows = ''.join('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (esc(r['tr']), esc(r['res']), '<br>'.join('%s%s: %s' % (esc(q + 'x ' if q else ''), esc(i), _srcs_html(i, hi, n)) for q, i in r['ings']) or '<span class="badge unc">ingredients not on wiki</span>') for r in first)
        mats = {}
        for r in rs[:25]:
            for q, i in r['ings']: mats.setdefault(i, 0)
        okm = [i for i in mats if any(ok for _, ok in mat_sources(i, hi, n))]
        nos = [i for i in mats if not mat_sources(i, hi, n) and not _name_match(i)]
        body = ('<p><span class="badge strat">strategy</span> Recipes are not tied to character level; your level decides where you can get the materials. First recipes by wiki trivial (combine until trivial, then move up):</p>'
                '<div class="tw"><table class="grid ts-t"><thead><tr><th>Trivial</th><th>Make</th><th>Materials and where (✓ = source fits %d–%d)</th></tr></thead><tbody>%s</tbody></table></div>' % (lo, hi, rows))
        if okm: body += '<p class="dim"><span class="badge strat">strategy</span> Materials for the first 25 recipes you can source at this level: %s.</p>' % esc(', '.join(okm[:20]))
        if nos: body += '<p class="dim"><span class="badge unc">unverified</span> No wiki source found for: %s.</p>' % esc(', '.join(nos[:15]))
        return head + info + body + tail
    return head + info + '<p class="dim"><span class="badge unc">no wiki data</span> The wiki page has tables but no skill-up chart this guide can map to levels. See the full guide.</p>' + tail

# ---- skill-up guide pages
def _brackets(mx):
    b = [(1, 25), (26, 50), (51, 75), (76, 100)]
    a = 101
    while a <= max(mx, 100):
        b.append((a, a + 49)); a += 50
    return b
def ts_page(n):
    T = TSM[n]; S = T['S']
    o = ['<div class="ts-page" data-ts="%s"></div>' % slug(n)]
    o.append('<p class="ts-notsel call note" hidden>%s is not in your selected tradeskills. Add it with the <b>Trades</b> picker in the top bar.</p>' % esc(n))
    inf = ''.join('<tr><th>%s</th><td>%s</td></tr>' % (esc(k), esc(v)) for k, v in S['info'].items() if v and v != '-' and k != n)
    o.append('<p><span class="badge fact">fact</span> From the wiki page <a class="ext" target="_blank" rel="noopener" href="%s">%s</a> (edited %s).</p>' % (esc(wiki(S['title'])), esc(S['title']), esc(S['ts'])))
    if inf: o.append('<table class="kv">%s</table>' % inf)
    o += ['<p>%s</p>' % esc(p) for p in S['intro']]
    tips = [t for t in S['tips'] if 'Formatting' not in t]
    if tips: o.append('<ul class="tight">%s</ul>' % ''.join('<li>%s</li>' % esc(t) for t in tips))
    if T['stub']:
        o.append('<div class="call note"><p><span class="badge unc">no wiki data</span> The wiki page for %s has no skill chart, recipes or nodes yet, so there is no skill-up guide. Nothing here is guessed.</p></div>' % esc(n))
        return ''.join(o)
    o.append(TS_MAP_NOTE.replace('your <b>character level range</b> (top bar) picks the zones', 'on this page every zone shows its wiki level so you can judge safety; the per-level guidance on the <a href="/tradeskills.html">Tradeskills</a> and <a href="/leveling.html">Leveling</a> pages uses your <b>character level range</b> to pick zones'))
    vals = [x for g in T['gather'] for x in (g['mnv'], g['trv']) if x] + [r['trv'] for r in T['recipes'] if r['trv']]
    br = _brackets(max(vals) if vals else 100)
    o.append('<h2 id="steps">Skill-up steps by bracket</h2><p class="dim"><span class="badge strat">strategy</span> Each bracket lists what still gives skill-ups there: '
             + ('nodes whose min skill is at or below the bracket top and whose trivial is above the bracket start.' if T['gather'] else 'recipes whose wiki trivial falls in the bracket (work them from your current skill until they turn trivial).') + ' Cost: not sourced (no prices on the wiki or merchant pages).</p>')
    unknown = []
    for a, z in br:
        rows = []
        if T['gather']:
            for g in sorted(T['gather'], key=lambda g: (g['mnv'] if g['mnv'] is not None else 999)):
                if g['mnv'] is None: continue
                if g['mnv'] <= z and (g['trv'] is None or g['trv'] > a):
                    rows.append('<tr><td>%s%s</td><td>%s–%s</td><td>%s%s</td></tr>' % (esc(g['node']), (' <span class="dim">→ %s</span>' % esc(g['yields'])) if g['yields'] else '', esc(g['mn']), esc(g['tr'] or '?'),
                                ', '.join(_zlabel(z2) for z2 in g['zones']) or '<span class="badge unc">location not on wiki</span>', (' <span class="dim">· %s</span>' % esc(g['loc'])) if '(' in g['loc'] else ''))
        else:
            for r in sorted(T['recipes'], key=lambda r: r['trv'] or 0):
                if r['trv'] is not None and a <= r['trv'] <= z or (a == 1 and r['trv'] is not None and r['trv'] < 1):
                    rows.append('<tr><td>%s</td><td>%s%s</td><td>%s</td></tr>' % (esc(r['tr']), esc(r['res']), (' <span class="dim">· %s</span>' % esc(r['station'])) if r['station'] else '',
                                '<br>'.join('%s%s: %s' % (esc(q + 'x ' if q else ''), esc(i), _srcs_html(i, None, n)) for q, i in r['ings']) or '<span class="badge unc">ingredients not on wiki</span>'))
        if rows:
            o.append('<h3 id="b%d">Skill %d–%d</h3><div class="tw"><table class="grid ts-t"><thead><tr><th>%s</th><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody></table></div>' % (
                a, a, z, *(('Node', 'Min–trivial', 'Where (zone level)') if T['gather'] else ('Trivial', 'Make', 'Materials and where to get them')), ''.join(rows)))
    if T['gather']:
        unknown = [g for g in T['gather'] if g['mnv'] is None]
        if unknown: o.append('<h3>Nodes with no skill numbers on the wiki</h3><p><span class="badge unc">unverified</span> %s</p>' % esc(', '.join('%s (%s)' % (g['node'], ', '.join(g['zones']) or 'location not listed') for g in unknown)))
        extra = [tb for tb in T['other'] if tb['rows']]
    else:
        unknown = [r for r in T['recipes'] if r['trv'] is None]
        if unknown: o.append('<h3>Recipes with no trivial on the wiki</h3><p><span class="badge unc">unverified</span> %s</p>' % esc(', '.join('%s (%s)' % (r['res'], r['tr'] or 'blank') for r in unknown)))
    if T['other']:
        o.append('<h2 id="more">Other wiki tables</h2><p class="dim"><span class="badge fact">fact</span> Copied as-is; not used for the steps above.</p>')
        for tb in T['other']:
            o.append('<details class="call"><summary>%s</summary><div class="tw"><table class="grid"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div></details>' % (
                esc(tb['sec']), ''.join('<th>%s</th>' % esc(x) for x in tb['head']), ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % esc(x) for x in r['c'] if x != '}') for r in tb['rows'][:200])))
    return ''.join(o)

def ts_index():
    o = ['<p><span class="badge fact">fact</span> One skill-up guide per tradeskill, built from the wiki tradeskill pages. Only the tradeskills picked in the <b>Trades</b> menu in the top bar are shown. <label class="ts-all"><input type="checkbox" class="ts-showall"> Show all</label></p>']
    for k, lab in TS_KINDS:
        ns = [n for n in TS_ORDER if TSM[n]['kind'] == k]
        if not ns: continue
        o.append('<h2>%s</h2><ul class="tight">%s</ul>' % (lab, ''.join('<li data-ts="%s"><a href="%s">%s</a> <span class="dim">%s</span></li>' % (
            slug(n), ts_url(n), esc(n), esc('%d nodes' % len(TSM[n]['gather']) if TSM[n]['gather'] else ('%d recipes' % len(TSM[n]['recipes']) if TSM[n]['recipes'] else 'tables only'))) for n in ns)))
    o.append('<h2>No wiki data yet</h2><p class="dim"><span class="badge unc">no wiki data</span> %s</p>' % ', '.join('<a href="%s">%s</a>' % (ts_url(n), esc(n)) for n in TS_STUBS))
    return ''.join(o)

# ---- gear badges: items made by (or used in) a tradeskill recipe
def _ts_items():
    m = {}
    for n, T in TSM.items():
        for r in T['recipes']:
            linked = {x.lower() for x in r['rlinks']}
            for nm in {r['rname']} | set(r['rlinks']):
                it = ITEMS.get(nm)
                if not it or not it.get('slot'): continue
                ver = nm.lower() in linked
                m.setdefault(nm, []).append([n, r['tr'] or '?', 'made', 1 if ver else 0])
            for x in r['ilinks']:
                it = ITEMS.get(x)
                if it and it.get('slot'): m.setdefault(x, []).append([n, r['tr'] or '?', 'used', 1])
    for nm, it in ITEMS.items():
        c = it.get('crafted') or {}
        if not c.get('skill') or not it.get('slot'): continue
        sk = TS_ALIAS.get(c['skill'], c['skill'])
        if any(e[0] == sk and e[2] == 'made' for e in m.get(nm, [])): continue
        m.setdefault(nm, []).append([sk, c.get('trivial') or '?', 'made', 0])   # item page only: not linked from a recipe table -> unverified
    out = {}
    for nm, es in m.items():
        it = ITEMS[nm]; seen = set(); ee = []
        for e in es:
            k = (e[0], e[2])
            if k in seen: continue
            seen.add(k); ee.append(e)
        out[nm] = {'e': ee, 'c': class_codes(it), 'l': item_level(it)}
    return out

_ts_prev_bc = build_content
def build_content():
    _ts_prev_bc()
    add_page('trades/index.html', 'Tradeskill skill-up guides', body_html=ts_index(), section='tradeskills', sources=['Wiki: Category:Tradeskills|%sCategory:Tradeskills' % WIKI], desc='Tradeskill skill-up guides')
    for n in sorted(TSM):
        S = TSM[n]['S']
        add_page(ts_url(n).lstrip('/'), '%s skill-up guide' % n, body_html=ts_page(n), section='tradeskills',
                 sources=['Wiki: %s|%s' % (S['title'], wiki(S['title'])), 'Wiki zone pages (zone levels)|%sZones' % WIKI, 'Wiki merchant pages|%sCategory:Merchant' % WIKI], desc='%s skill-up guide' % n)
    mount = ('<div class="ts-guide" data-ts-mount><h2 id="trades-band">Tradeskills for your level range</h2><p class="dim">Shows the tradeskills picked in the <b>Trades</b> menu (top bar) for your level range. '
             '<a href="/trades/index.html">All skill-up guides</a>.</p><noscript>Needs JavaScript.</noscript></div>')
    for p in PAGES:
        pa = p['path']
        if pa in ('leveling.html', 'shaman/leveling.html', 'shaman/tradeskills.html') or (pa.startswith('classref/') and pa.endswith('/leveling.html')):
            p['body'] = mount + p['body']
            if p['ctx'].get('toc'): p['ctx']['toc'].insert(0, ('trades-band', 'Tradeskills for your level range'))
        elif pa == 'index.html':
            hm = mount.replace('Tradeskills for your level range</h2>', 'Quick info · tradeskills for your level range</h2>', 1)
            p['body'] = p['body'].replace('<div id="mnm-quickinfo" class="quickinfo" data-mnm-quick="full"></div>', '<div id="mnm-quickinfo" class="quickinfo" data-mnm-quick="full"></div>' + hm, 1)
        elif pa in ('tradeskills.html', 'trades-guide.html'):
            p['body'] = '<p class="ts-tog"><label class="ts-all"><input type="checkbox" class="ts-showall"> Show all tradeskills</label> <span class="dim">(otherwise only the ones picked in the top-bar <b>Trades</b> menu; <a href="/trades/index.html">skill-up guides</a>)</span></p>' + mount + p['body']

def _ts_tag_body(h):
    # trades-guide: tag per-skill blocks, node rows and path blocks with data-ts so the picker can filter them
    h = re.sub(r'<details class="call" id="t-([a-z0-9-]+)">', lambda m: '<details class="call" id="t-%s" data-ts="%s">' % (m.group(1), m.group(1)), h)
    h = re.sub(r'<details class="call"><summary><b>([^<]+)</b>', lambda m: '<details class="call" data-ts="%s"><summary><b>%s</b>' % (slug(html.unescape(m.group(1))), m.group(1)), h)
    def row(m):
        cells = re.findall(r'<td>(.*?)</td>', m.group(0))
        return m.group(0).replace('<tr>', '<tr data-ts="%s">' % slug(re.sub('<[^>]+>', '', html.unescape(cells[1]))), 1) if len(cells) == 5 else m.group(0)
    h = re.sub(r'<tr><td>(?:(?!</tr>).)*</tr>', row, h)
    return h
_ts_prev_tp = _trades_page
def _trades_page():
    return _ts_tag_body(_ts_prev_tp())
_ts_prev_gt = g_tradeskills
def g_tradeskills(arg, ctx):
    h = _ts_prev_gt(arg, ctx)
    h = re.sub(r'<tr><td><a class="ext" target="_blank" rel="noopener" href="[^"]*">([^<]+)</a>', lambda m: m.group(0).replace('<tr>', '<tr data-ts="%s">' % slug(html.unescape(m.group(1))), 1), h)
    return h.replace('<th>Skill</th>', '<th>Skill</th>', 1).replace('</td></tr>', '</td></tr>')
GENS['tradeskills'] = g_tradeskills

_ts_prev_lr = load_ranges
def load_ranges():
    out = _ts_prev_lr()
    for k, v in out.items():   # Shaman band notes: their "Gathering" section covers Mining/Smelting/Lumberjacking
        v['html'] = re.sub(r'(<h2[^>]*>Gathering[^<]*</h2>)(.*?)(?=<h2|$)', r'<div data-ts="mining smelting lumberjacking">\1\2</div>', v['html'], flags=re.S)
    return out

_ts_prev_ra = render_all
def render_all():
    _ts_prev_ra()
    skills = [{'n': n, 's': slug(n), 'k': TSM[n]['kind'], 'd': 1 if n in TS_GATHER_DEFAULT else 0, 'x': 1 if n in TS_SMITH else 0} for n in TS_ORDER]
    bands = {}
    for key in RANGE_ORDER:
        lo, hi = [int(x) for x in key.split('-')]
        for n in TS_ORDER: bands[slug(n) + '|' + key] = ts_band(n, lo, hi)
    payload = {'key': TS_KEY, 'skills': skills, 'kinds': TS_KINDS, 'bands': bands, 'note': TS_MAP_NOTE, 'urls': {slug(n): ts_url(n) for n in TS_ORDER},
               'items': _ts_items()}
    open(os.path.join(OUT, 'assets', 'trade-data.js'), 'w', encoding='utf8').write('window.MNM_TS=' + json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + ';')

RANGEBAR_HTML = RANGEBAR_HTML.replace('<a class="range-qi"',
    '<div class="rb-f ts-f"><span class="range-lab">Trades</span><details class="ts-dd" id="mnm-ts"><summary id="mnm-ts-sum" aria-label="Tradeskills">Gathering</summary><div class="ts-menu" id="mnm-ts-menu"></div></details></div><a class="range-qi"', 1)
TEMPLATE = TEMPLATE.replace('</head>', '<link rel="stylesheet" href="{root}assets/mod-tradesel.css">\n</head>', 1).replace(
    '<script src="{root}assets/site.js"></script>', '<script src="{root}assets/site.js"></script>\n<script src="{root}assets/trade-data.js" defer></script>\n<script src="{root}assets/mod-tradesel.js" defer></script>', 1)

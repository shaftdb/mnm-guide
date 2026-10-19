# UX pass 1 (runs after zz_nav so its stylesheet loads last): design tokens, wider ultrawide layout with a prose measure,
# 44px touch targets + compact sticky mini bar on phones, skip link + :focus-visible rings, control-border contrast,
# prefers-reduced-motion. CSS/JS only: static/mod-ux.css + static/mod-ux.js. Remove by deleting this module.
# NOTE: TEMPLATE goes through str.format, so literal braces are doubled.
TEMPLATE = TEMPLATE.replace('</head>', '<link rel="stylesheet" href="{root}assets/mod-ux.css">\n</head>', 1
    ).replace('<body class="sec-{section}">', '<body class="sec-{section}">\n<a class="skip" href="#content">Skip to content</a>', 1
    ).replace('<main class="main">', '<main class="main" id="content" tabindex="-1">', 1
    ).replace('</body>', '<script src="{root}assets/mod-ux.js"></script>\n</body>', 1)

# ---------------------------------------------------------------- UX pass 2: lazy-loading of the big data files
# One tiny loader (window.MNM_LOAD(file) -> Promise, script-tag based so it also works on file:// and offline from cache)
# is inlined in <head>. search-index.js and item-tips.js are no longer linked on every page (site.js loads them on first
# search focus / first item hover). After the whole build, quick-data.js and trade-data.js are split into a small base
# file plus per-class / per-band / per-skill chunks; the base file carries a "lazy" map that site.js / mod-tradesel.js use.
# If a split is skipped (unexpected file format), the base file stays complete and the JS uses it as before.
_UX_LOADER = ('<script>window.MNM_LOAD=window.MNM_LOAD||(function(){var c={};return function(f){if(c[f])return c[f];'
    'var r=document.documentElement.getAttribute("data-root")||"";return c[f]=new Promise(function(ok,no){var s=document.createElement("script");'
    's.src=r+"assets/"+f;s.async=true;s.onload=function(){ok()};s.onerror=function(){delete c[f];s.remove();no(new Error("Could not load "+f))};'
    'document.head.appendChild(s)})}})();</script>')
TEMPLATE = TEMPLATE.replace('</head>', _UX_LOADER.replace('{', '{{').replace('}', '}}') + '\n</head>', 1)
for _t in ('<script src="{root}assets/search-index.js"></script>\n', '<script src="{root}assets/item-tips.js"></script>\n'):
    if _t in TEMPLATE: TEMPLATE = TEMPLATE.replace(_t, '', 1)
    else: print('zzz_ux: eager tag not found (left as is):', _t.strip())

def _ux_read_assign(path, var):
    """Parse 'window.VAR={...};window.VAR.k={...};...' -> (base dict, {k: value}) or None."""
    s = open(path, encoding='utf8').read(); dec = json.JSONDecoder(); pre = 'window.%s=' % var
    if not s.startswith(pre): return None
    base, i = dec.raw_decode(s, len(pre)); extra = {}
    while True:
        while i < len(s) and s[i] in ';\n ': i += 1
        if i >= len(s): break
        m = re.compile(r'window\.%s\.(\w+)=' % var).match(s, i)
        if not m: return None
        v, i = dec.raw_decode(s, m.end()); extra[m.group(1)] = v
    return base, extra

def _ux_js(path, text):
    open(os.path.join(OUT, 'assets', path), 'w', encoding='utf8').write(text)

def _ux_dump(v): return json.dumps(v, ensure_ascii=False, separators=(',', ':'))

def _ux_split_quick():
    fp = os.path.join(OUT, 'assets', 'quick-data.js')
    if not os.path.exists(fp): return
    r = _ux_read_assign(fp, 'MNM_QUICK')
    if not r or 'panels' not in r[0]: print('zzz_ux: quick-data.js not split (unexpected format)'); return
    base, extra = r; panels = base['panels']; route = extra.pop('route', {}); routenh = extra.pop('routenh', {})
    lazy = {'cls': {}, 'band': {}}
    for c in base['classes']:
        f = 'quick-c-%s.js' % slug(c); lazy['cls'][c] = f
        _ux_js(f, 'Object.assign(window.MNM_QUICK.panels,%s);' % _ux_dump({k: v for k, v in panels.items() if k.split('|')[0] == c}))
    for k in base['order']:
        if k in route or k in routenh:
            f = 'quick-r-%s.js' % k; lazy['band'][k] = f
            _ux_js(f, _ux_route_js(k, route.get(k, ''), routenh.get(k, '')))  # UX pass 3: route stored once (see below)
    base.update(panels={}, route={}, routenh={}, lazy=lazy)
    _ux_js('quick-data.js', 'window.MNM_QUICK=%s;%s' % (_ux_dump(base), ''.join('window.MNM_QUICK.%s=%s;' % (k, _ux_dump(v)) for k, v in extra.items())))

def _ux_split_trades():
    fp = os.path.join(OUT, 'assets', 'trade-data.js')
    if not os.path.exists(fp): return
    r = _ux_read_assign(fp, 'MNM_TS')
    if not r or r[1] or 'bands' not in r[0] or 'items' not in r[0]: print('zzz_ux: trade-data.js not split (unexpected format)'); return
    base = r[0]; lazy = {'items': 'trade-items.js', 'bands': {}}
    _ux_js('trade-items.js', 'window.MNM_TS.items=%s;' % _ux_dump(base['items']))
    for sk in base['skills']:
        s = sk['s']; f = 'trade-b-%s.js' % s; lazy['bands'][s] = f
        _ux_js(f, 'Object.assign(window.MNM_TS.bands,%s);' % _ux_dump({k: v for k, v in base['bands'].items() if k.split('|')[0] == s}))
    base.update(bands={}, items=None, lazy=lazy)
    _ux_js('trade-data.js', 'window.MNM_TS=%s;' % _ux_dump(base))

_ux_prev_ra = render_all
def render_all():
    _ux_prev_ra()
    _ux_split_quick(); _ux_split_trades()

# ---------------------------------------------------------------- UX pass 3: smaller downloads
# 1) walk-data.js: the start-city route HTML (one string per level band holding all four cities, ~715 KB) and the city
#    overview (schead, ~80 KB) move into per-band x per-city chunks (walk-r-<band>-<city>.js, walk-h-<city>.js). The base
#    file carries lazy.route[band][city] / lazy.schead[city]; mod-chargen.js loads only the bands it renders.
#    Each city chunk = the wrapper + that city's block, so the client-side scFor() result is byte-identical.
# 2) quick-r-<band>.js: routenh is route plus one "notes written for Night Harbor" paragraph per non-NH city, so the
#    chunk stores route once plus those inserts (UTF-16 offsets) and rebuilds routenh on load. Verified exact at build.
# 3) search: search-titles.js (titles/urls/sections, compact) loads first; search-text.js (the full text, same order)
#    loads in the background after the first query. search-index.js is still written (unused fallback).
# Any check that fails leaves that file complete, and the JS uses it as before.
_UX_WALK = {}  # band -> full route HTML (all cities), filled by _ux_split_walk (pass 4 reuses it)
_SC_BLOCK = re.compile(r'<div class="sc-route" data-sc="([a-z0-9-]+)">')

def _ux_city_split(h):
    """'<div class="sc-wrap">PICK<div class="sc-route" data-sc=a>..</div>..</div>' -> (prefix, {slug: block}, suffix) or None"""
    ms = list(_SC_BLOCK.finditer(h))
    if not ms or not h.endswith('</div>'): return None
    pre, suf, blocks = h[:ms[0].start()], '</div>', {}
    for i, m in enumerate(ms):
        b = h[m.start():ms[i + 1].start() if i + 1 < len(ms) else len(h) - len(suf)]
        if b.count('<div') != b.count('</div>') or m.group(1) in blocks: return None
        blocks[m.group(1)] = b
    if pre + ''.join(blocks.values()) + suf != h or pre.count('<div') != pre.count('</div>') + 1: return None
    return pre, blocks, suf

def _ux_split_walk():
    fp = os.path.join(OUT, 'assets', 'walk-data.js')
    if not os.path.exists(fp): return
    r = _ux_read_assign(fp, 'MNM_WT')
    if not r or r[1] or not isinstance(r[0].get('route'), dict): print('zzz_ux: walk-data.js not split (unexpected format)'); return
    d = r[0]; lazy = {'route': {}, 'schead': {}}; files = {}
    for k, h in d['route'].items():
        sp = _ux_city_split(h)
        if not sp or not re.match(r'^\d+-\d+$', k): print('zzz_ux: walk route band %s not split' % k); return
        pre, blocks, suf = sp; lazy['route'][k] = {}
        for sl, b in blocks.items():
            f = 'walk-r-%s-%s.js' % (k, sl); lazy['route'][k][sl] = f
            files[f] = 'window.MNM_WT.route[%s]=%s;' % (_ux_dump(k + '|' + sl), _ux_dump(pre + b + suf))
    if d.get('schead'):
        sp = _ux_city_split(d['schead'])
        if not sp: print('zzz_ux: walk schead not split'); return
        pre, blocks, suf = sp
        for sl, b in blocks.items():
            f = 'walk-h-%s.js' % sl; lazy['schead'][sl] = f
            files[f] = 'window.MNM_WT.schead_c[%s]=%s;' % (_ux_dump(sl), _ux_dump(pre + b + suf))
        d['schead'] = ''
    # UX pass 4: route chunks write into window.MNM_WTR, which walk-data.js aliases as MNM_WT.route, so a chunk loaded before
    # walk-data.js (class pages load their own start-city route chunks) is kept, and loading order never matters.
    for f, t in files.items(): _ux_js(f, t.replace('window.MNM_WT.route[', '(window.MNM_WTR=window.MNM_WTR||{})[', 1))
    _UX_WALK.update({k: h for k, h in d['route'].items()})
    d.update(route={}, schead_c={}, lazy=lazy)
    _ux_js('walk-data.js', 'window.MNM_WT=%s;window.MNM_WT.route=window.MNM_WTR=window.MNM_WTR||{};' % _ux_dump(d))

def _u16(s): return len(s.encode('utf-16-le')) // 2
_NH_NOTE = re.compile(r'<p class="sc-nhnote">.*?</p>', re.S)
def _ux_route_js(k, route, routenh):
    """quick-r chunk: route once + the Night Harbor notes as inserts (falls back to both strings if not exact)"""
    ins, plain, last = [], [], 0
    for m in _NH_NOTE.finditer(routenh):
        plain.append(routenh[last:m.start()]); ins.append([_u16(''.join(plain)), m.group(0)]); last = m.end()
    plain.append(routenh[last:])
    if ''.join(plain) != route or not ins:
        return 'window.MNM_QUICK.route[%s]=%s;window.MNM_QUICK.routenh[%s]=%s;' % (_ux_dump(k), _ux_dump(route), _ux_dump(k), _ux_dump(routenh))
    # self-check of the rebuild in Python using the same UTF-16 offsets
    u = route.encode('utf-16-le'); o, p = b'', 0
    for at, t in ins: o += u[2 * p:2 * at] + t.encode('utf-16-le'); p = at
    assert (o + u[2 * p:]).decode('utf-16-le') == routenh, 'zzz_ux: routenh rebuild mismatch ' + k
    return ('(function(Q,k,r,n){Q.route[k]=r;var o="",p=0;n.forEach(function(x){o+=r.slice(p,x[0])+x[1];p=x[0]});Q.routenh[k]=o+r.slice(p)})'
            '(window.MNM_QUICK,%s,%s,%s);' % (_ux_dump(k), _ux_dump(route), _ux_dump(ins)))

def _ux_split_search():
    fp = os.path.join(OUT, 'assets', 'search-index.js')
    if not os.path.exists(fp): return
    s = open(fp, encoding='utf8').read()
    if not s.startswith('window.MNM_INDEX='): print('zzz_ux: search index not split'); return
    idx = json.loads(s[len('window.MNM_INDEX='):].rstrip(';\n '))
    secs = sorted({x.get('s', '') for x in idx}); si = {v: i for i, v in enumerate(secs)}
    pc = {}
    for x in idx:
        if x.get('e'): pc[x['u'].rsplit('/', 1)[0] + '/'] = pc.get(x['u'].rsplit('/', 1)[0] + '/', 0) + 1
    pre = sorted(p for p, n in pc.items() if n >= 20); rows = []
    for x in idx:
        row = [x['t'], x['u'], si[x.get('s', '')]]
        if x.get('e'):
            p = x['u'].rsplit('/', 1)[0] + '/'
            if p in pre: row[1] = x['u'][len(p):]; row.append(pre.index(p))
            else: row.append(-1)
        rows.append(row)
    _ux_js('search-titles.js', 'window.MNM_TITLES=%s;' % _ux_dump({'s': secs, 'p': pre, 'r': rows}))
    _ux_js('search-text.js', 'window.MNM_STEXT=%s;' % _ux_dump([x.get('x', '') for x in idx]))

_ux_prev_ra3 = render_all
def render_all():
    _ux_prev_ra3()
    _ux_split_walk(); _ux_split_search()

# ---------------------------------------------------------------- UX pass 4: class pages render on demand
# 1) Start-city routes on class guides / Leveling: every page carried all four cities' routes for all eight bands (~700 KB
#    of the 870 KB Inquisitor page), with CSS showing one city. Each band's block list is replaced by a small placeholder;
#    mod-ux.js loads only the picked city's walk-r-<band>-<city>.js chunk (the same files the walkthrough uses) when the
#    band nears the screen. Done only where the page HTML is byte-identical to the relinked walk route, else left as is.
#    Without JavaScript nothing changes for the reader: the routes were already hidden until a start city was picked.
# 2) Class guides: inactive tabs (not the open Quick reference tab and not Character creation, which mod-chargen wires up)
#    move into assets/ct-<class>.js and render when the tab is opened (or a #link points into them). Every id in a moved
#    tab stays as an empty placeholder, so deep links, the On this page sheet and Ctrl+K anchors still find their tab.
# 3) data-cl on <html>: changelog rows per day ("2026-10-19:2 ..."), for the in-page "What's new since your last visit" badge.
# 4) The palette + shortcuts overlay (between the @@ux-pal markers in mod-ux.js) move into assets/mod-ux-pal.js, loaded on
#    first use; mod-ux.js keeps tiny stubs.
import datetime as _ux_dt
def _ux_cl_dates():
    try: t = open(os.path.join(ROOT, 'content', 'changelog.md'), encoding='utf8').read()
    except OSError: return ''
    out = []
    for m in re.finditer(r'^\| *([A-Z][a-z]{2} \d{1,2}, \d{4}) *\|', t, re.M):
        try: out.append(_ux_dt.datetime.strptime(m.group(1), '%b %d, %Y').strftime('%Y-%m-%d'))
        except ValueError: pass
    cnt = {}
    for d in out: cnt[d] = cnt.get(d, 0) + 1
    return ' '.join('%s:%d' % (d, cnt[d]) for d in sorted(cnt, reverse=True)[:60])  # "day:rows", newest first
_UX_CL = _ux_cl_dates()
if _UX_CL and '<html lang="en" data-root="{root}">' in TEMPLATE:
    TEMPLATE = TEMPLATE.replace('<html lang="en" data-root="{root}">', '<html lang="en" data-root="{root}" data-cl="%s">' % _UX_CL, 1)

_UX_SCWRAP = re.compile(r'<div class="sc-wrap">')
def _ux_div_end(h, i):
    d = 0
    for t in re.finditer(r'<div\b|</div>', h[i:]):
        d += 1 if t.group(0) == '<div' else -1
        if d == 0: return i + t.end()
    return -1

def _ux_lazy_routes(h, depth):
    """Swap each start-city wrap that equals a relinked walk route for its sc-pick line + a placeholder. Returns (html, n)."""
    if '<div class="sc-wrap">' not in h or not _UX_WALK: return h, 0
    want, bypre = {}, {}
    for k, full in _UX_WALK.items():
        sp = _ux_city_split(full)
        if sp: want[relink(full, depth)] = (k, sp); bypre[relink(sp[0], depth)] = (k, sp)
    out, last, n = [], 0, 0
    for m in _UX_SCWRAP.finditer(h):
        if m.start() < last: continue
        e = _ux_div_end(h, m.start())
        if e < 0: continue
        w = h[m.start():e]; hit = want.get(w); notes = {}
        if not hit:  # UX pass 5: the Shaman guide's variant (routes with a "notes written for Night Harbor" paragraph per city)
            hit, notes = _ux_nh_match(w, bypre, depth)
            if not hit: continue
        k, (pre, blocks, suf) = hit; lo, hi = k.split('-')
        ph = ('<div class="sc-lz" data-band="%s" data-cities="%s"><noscript><p class="dim">Start-city routes for levels %s–%s need JavaScript: '
              'see the <a href="%swalkthrough.html">walkthrough</a>.</p></noscript></div>') % (k, ' '.join(blocks), lo, hi, '../' * depth)
        ph += ''.join('<template class="sc-nht" data-sc="%s">%s</template>' % (sl, t) for sl, t in notes.items())
        out.append(h[last:m.start()]); out.append(relink(pre, depth) + ph + suf); last = e; n += 1
    out.append(h[last:])
    return ''.join(out), n

_NH_ONE = re.compile(r'<p class="sc-nhnote">(?:(?!</p>).)*</p>', re.S)
def _ux_nh_match(w, bypre, depth):
    """Shaman variant: w == relinked walk route band, except each city block may end with one sc-nhnote paragraph.
    Returns ((band, split), {city: note html}) only if pre + blocks + notes + suf rebuilds w byte for byte, else (None, {})."""
    sp = _ux_city_split(w)
    if not sp: return None, {}
    pre2, blocks2, suf2 = sp; hit = bypre.get(pre2)
    if not hit: return None, {}
    k, (pre, blocks, suf) = hit
    if suf2 != suf or list(blocks2) != list(blocks): return None, {}
    notes, rebuilt = {}, relink(pre, depth)
    for sl, b in blocks.items():
        rb, b2 = relink(b, depth), blocks2[sl]
        if b2 != rb:
            mid = b2[len(rb) - 6:-6] if b2.startswith(rb[:-6]) and b2.endswith('</div>') else ''
            if not _NH_ONE.fullmatch(mid or '-') or '<template' in mid: return None, {}
            notes[sl] = mid
        rebuilt += rb[:-6] + notes.get(sl, '') + '</div>'
    if rebuilt + suf != w or not notes: return None, {}
    return hit, notes

_UX_PANE = re.compile(r'<div class="tabpane( on)?" id="(t\d+-[\w-]+)">')
_UX_PANE_SKIP = re.compile(r'<script|<form|<input|<select|<button|<textarea|sortable|data-ts|cg-|class="rr|sc-wrap|mnm-|<dialog|onclick')
def _ux_lazy_tabs(h, page_slug):
    """Move inactive, static tab panes into assets/ct-<slug>.js. Returns (html, {pane id: html}) ."""
    panes, out, last = {}, [], 0
    for m in list(_UX_PANE.finditer(h)):
        if m.group(1) or m.group(2).endswith('-cg'): continue
        e = _ux_div_end(h, m.start())
        if e < 0: continue
        inner = h[m.end():e - 6]
        if _UX_PANE_SKIP.search(inner) or len(inner) < 400: continue
        ids = re.findall(r'\sid="([^"]+)"', inner)
        if len(ids) != len(set(ids)): continue
        f = 'ct-%s.js' % page_slug
        ph = ('<div class="tabpane" id="%s" data-lz="%s"><p class="lz-status ux-lzp" role="status">This tab loads when you open it.</p>%s</div>'
              % (m.group(2), f, ''.join('<span class="ux-lzid" id="%s"></span>' % i for i in ids)))
        out.append(h[last:m.start()]); out.append(ph); last = e; panes[m.group(2)] = inner
    out.append(h[last:])
    return ''.join(out), panes

def _ux_split_pal():
    fp = os.path.join(OUT, 'assets', 'mod-ux.js')
    s = open(fp, encoding='utf8').read(); a, b = '// @@ux-pal-start', '// @@ux-pal-end'
    if s.count(a) != 1 or s.count(b) != 1 or s.index(a) > s.index(b): print('zzz_ux: palette not split (markers)'); return
    i, j = s.index(a), s.index(b) + len(b)
    _ux_js('mod-ux-pal.js', _ux_compact_js(s[i:j]))
    _ux_js('mod-ux.js', _ux_compact_js(s[:i] + s[j:]))
    fc = os.path.join(OUT, 'assets', 'mod-ux.css'); c = open(fc, encoding='utf8').read()
    if '"/*' not in c and "'/*" not in c:
        c = re.sub(r'/\*.*?\*/', '', c, flags=re.S); _ux_js('mod-ux.css', '\n'.join(l.strip() for l in c.split('\n') if l.strip()) + '\n')

def _ux_compact_js(s):
    """Drop whole-line // comments and indentation (line breaks kept, so the code itself is untouched). Source stays readable."""
    return '\n'.join(l.strip() for l in s.split('\n') if l.strip() and not l.strip().startswith('//')) + '\n'

def _ux_pass4():
    nr = nt = 0; saved = 0
    for d, _, fs in os.walk(OUT):
        for f in fs:
            if not f.endswith('.html'): continue
            fp = os.path.join(d, f); rel = os.path.relpath(fp, OUT).replace(os.sep, '/'); depth = rel.count('/')
            h0 = h = open(fp, encoding='utf8').read()
            h, n = _ux_lazy_routes(h, depth); nr += n
            if rel.startswith('classes/') and rel != 'classes/index.html':
                h, panes = _ux_lazy_tabs(h, f[:-5])
                if panes:
                    _ux_js('ct-%s.js' % f[:-5], '(window.MNM_CT=window.MNM_CT||{})[%s]=%s;' % (_ux_dump(f[:-5]), _ux_dump(panes))); nt += len(panes)
            if h != h0:
                saved += len(h0.encode('utf8')) - len(h.encode('utf8'))
                open(fp, 'w', encoding='utf8').write(h)
    _ux_split_pal()
    print('zzz_ux pass 4: %d route bands and %d class tabs load on demand, %d KB less HTML' % (nr, nt, saved // 1024))

_ux_prev_ra4 = render_all
def render_all():
    _ux_prev_ra4()
    _ux_pass4()

# ---------------------------------------------------------------- UX pass 5
# 1) Shaman guide routes on demand: its start-city routes carry one "notes written for Night Harbor" paragraph per city, so
#    they never matched the walk route in pass 4. _ux_nh_match (above) accepts them only when the walk route + those notes
#    rebuild the page HTML byte for byte; the notes stay in the page as <template class="sc-nht"> and mod-ux.js appends the
#    picked city's note to its loaded route block, so the DOM ends up the same as before.
# 3) Theme (#15): this <head> script applies localStorage mnm-theme (dark | light | contrast) before the first paint. With no saved
#    choice, prefers-contrast: more starts High contrast (nothing is saved until the toggle is used). prefers-color-scheme: light
#    does not switch anything: the default stays the dark (Irem) theme and the toggle shows a small "Light available" hint.
_UX_THEME = ('<script>try{var t=localStorage.getItem("mnm-theme");if(!t&&window.matchMedia){if(matchMedia("(prefers-contrast: more)").matches)t="contrast"}'
    'if(t==="light"||t==="contrast"){var d=document.documentElement;d.setAttribute("data-theme",t);'
    'document.write(\'<link rel="stylesheet" id="ux-theme-css" href="\'+(d.getAttribute("data-root")||"")+"assets/mod-ux-"+t+\'.css">\')}}catch(e){}</script>')
TEMPLATE = TEMPLATE.replace('</head>', _UX_THEME.replace('{', '{{').replace('}', '}}') + '\n</head>', 1)
# 2) Spell and mob tooltips (#7): spell-tips.js (the same fields as the Spells page table) and mob-tips.js (the same fields
#    as the Mobs database: level, zone, named, type, where, wiki-listed loot). Both load on the first tooltip of their kind.
def _ux_cut(t, n): return t if len(t) <= n else t[:t.rfind(' ', 0, n - 1) if ' ' in t[:n - 1] else n - 1].rstrip(' ,;') + '…'

def _ux_tips():
    st = {}
    try:
        for c in CLASS_LIST:
            for sp in CLASSES[c]['spells']:
                nm = sp.get('spell name')
                if not nm: continue
                st.setdefault(nm.strip().lower(), []).append([nm, sp.get('level') or 0, c, sp.get('spell description') or '', sp.get('mana') or '', sp.get('location') or ''])
    except (NameError, KeyError, TypeError) as ex:
        print('zzz_ux: spell tips skipped', ex); st = {}
    if st: _ux_js('spell-tips.js', 'window.MNM_STIPS=%s;' % _ux_dump(st))
    fp = os.path.join(OUT, 'assets', 'mobs-db.js'); mt = {}
    if os.path.exists(fp):
        s = open(fp, encoding='utf8').read().strip()
        try:
            rows = json.JSONDecoder().raw_decode(s, len('window.MNM_MOBS='))[0] if s.startswith('window.MNM_MOBS=') else []
        except ValueError: rows = []
        for d in rows:
            if not isinstance(d, list) or len(d) < 10 or not d[0]: continue
            loot = list(d[8] or []) + list(d[9] or [])
            mt.setdefault(str(d[0]).strip().lower(), []).append([d[0], d[2] or '', d[3] or '', d[4] or '', 1 if d[5] else 0, d[6] or '', _ux_cut(d[7] or '', 160), loot[:4], len(loot)])
    if mt: _ux_js('mob-tips.js', 'window.MNM_MTIPS=%s;' % _ux_dump(mt))
    print('zzz_ux pass 5: tooltips for %d spell names, %d mob names' % (len(st), len(mt)))

_ux_prev_ra5 = render_all
def render_all():
    _ux_prev_ra5()
    _ux_tips()

# 4) Theme stylesheets: assets/mod-ux-light.css and assets/mod-ux-contrast.css are generated from every built stylesheet. Each rule
#    that sets a literal colour gets a themed copy (scoped by html[data-theme=...], so it out-ranks the original), with colours
#    moved in lightness only (hue kept, so the amber/gold/brown/olive family stays). Hand-written rules from
#    static/mod-ux-themes.css (variables, controls, badges, decorations) follow and win. Only the chosen theme's file loads.
import colorsys as _ux_cs
_UX_NAMED = {'white': (255, 255, 255, 1.0), 'black': (0, 0, 0, 1.0)}
_UX_COL = re.compile(r'#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|\b(?:white|black)\b')
def _ux_pcol(t):
    t = t.strip().lower()
    if t in _UX_NAMED: return _UX_NAMED[t]
    if t.startswith('#'):
        h = t[1:]
        if len(h) in (3, 4): h = ''.join(c * 2 for c in h)
        if len(h) not in (6, 8): return None
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), (int(h[6:8], 16) / 255 if len(h) == 8 else 1.0)
    m = re.match(r'rgba?\(([^)]*)\)', t)
    if not m: return None
    p = [x.strip() for x in re.split(r'[,\s/]+', m.group(1)) if x.strip()]
    try:
        v = [float(x[:-1]) * 2.55 if x.endswith('%') else float(x) for x in p[:3]]
        a = (float(p[3][:-1]) / 100 if p[3].endswith('%') else float(p[3])) if len(p) > 3 else 1.0
    except (ValueError, IndexError): return None
    return v[0], v[1], v[2], a
def _ux_fcol(r, g, b, a):
    r, g, b = [max(0, min(255, int(round(x)))) for x in (r, g, b)]
    return '#%02x%02x%02x' % (r, g, b) if a >= 0.999 else 'rgba(%d,%d,%d,%s)' % (r, g, b, ('%.3f' % a).rstrip('0').rstrip('.'))
_UX_ACC_VARS = ('--gold', '--gold2', '--red', '--teal', '--magic', '--lore', '--unc', '--strat', '--glow', '--crystal')
def _ux_map(col, kind, theme):
    c = _ux_pcol(col)
    if not c: return col
    r, g, b, a = c; h, l, s = _ux_cs.rgb_to_hls(r / 255, g / 255, b / 255)
    if theme == 'light':
        if kind == 'bg':
            if l >= 0.35 and a > 0.5: return col                    # accent fill (badge, button): keep with its own text colour
            l, s = 0.97 - l * 0.5, min(s, 0.45)
            if a < 0.5: l = 0.35 + l * 0.2; a = min(a * 1.4, 0.35)  # translucent tints (row stripes, hovers): faint amber
        elif kind == 'fg':
            if l <= 0.55: return col
            l = min(0.30, max(0.12, 1.02 - l))
        elif kind == 'bd':
            l = 0.62 if l < 0.4 else max(0.30, l - 0.22)
        elif kind == 'sh':
            if l > 0.5: return 'transparent'
            r, g, b, a = 80, 55, 20, a * 0.35; return _ux_fcol(r, g, b, a)
    else:
        if kind == 'bg':
            if l >= 0.35 and a > 0.5: return col
            l = l * 0.35
            if a < 0.5: a = min(a, 0.2)
        elif kind == 'fg':
            if l <= 0.5: return col
            l, s = max(l, 0.88), min(s, 0.9)
        elif kind == 'bd':
            l, s = (0.72, min(s, 0.5)) if l < 0.5 else (max(l, 0.72), s)
        elif kind == 'sh':
            return col
    r, g, b = _ux_cs.hls_to_rgb(h, max(0, min(1, l)), max(0, min(1, s)))
    return _ux_fcol(r * 255, g * 255, b * 255, a)
def _ux_kind(prop):
    if prop.startswith('background'): return 'bg'
    if prop in ('color', 'fill', 'stroke', 'caret-color', 'text-decoration-color', 'accent-color', '-webkit-text-fill-color'): return 'fg'
    if prop.startswith('border') or prop.startswith('outline') or prop == 'column-rule-color': return 'bd'
    if prop in ('box-shadow', 'text-shadow'): return 'sh'
    return None
def _ux_scope(sel, theme):
    out = []
    for x in sel.split(','):
        x = x.strip()
        if not x: continue
        if x.startswith(':root'): return None
        m = re.match(r'html(?![\w-])', x)
        out.append(('html[data-theme="%s"]' % theme + x[4:]) if m else 'html[data-theme="%s"] %s' % (theme, x))
    return ','.join(out)
def _ux_rules(css):
    """yield (wrapper or '', selector, body) for plain rules, one @media/@supports level deep; other at-rules skipped"""
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S); i, n = 0, len(css)
    def block(j):
        d = 0
        for k in range(j, n):
            if css[k] == '{': d += 1
            elif css[k] == '}':
                d -= 1
                if d == 0: return k
        return n
    while i < n:
        j = css.find('{', i)
        if j < 0: break
        head = css[i:j].strip(); e = block(j)
        if head.startswith('@media') or head.startswith('@supports'):
            for _, s2, b2 in _ux_rules(css[j + 1:e]): yield head, s2, b2
        elif not head.startswith('@'):
            yield '', head, css[j + 1:e]
        i = e + 1
def _ux_theme_css(theme, sources):
    out = []
    for css in sources:
        for wrap, sel, body in _ux_rules(css):
            decl = []
            bgvars = re.search(r'background(?:-color)?\s*:[^;]*var\((--[\w-]+)', body)
            accent_bg = bgvars and bgvars.group(1) in _UX_ACC_VARS
            for d in body.split(';'):
                if ':' not in d: continue
                p, v = d.split(':', 1); p = p.strip().lower(); v = v.strip(); k = _ux_kind(p)
                if not k or p.startswith('--') or 'url(' in v: continue
                if not _UX_COL.search(v):  # var()-based colour: re-assert it so the themed copies keep the original cascade order
                    if 'var(' in v: decl.append('%s:%s' % (p, v))
                    continue
                if k == 'fg' and accent_bg: decl.append('%s:%s' % (p, v)); continue
                if k == 'fg':  # text on a literal accent fill in the same rule keeps its colour
                    bgm = re.search(r'background(?:-color)?\s*:\s*([^;]+)', body)
                    if bgm:
                        bc = _UX_COL.search(bgm.group(1)); pc = _ux_pcol(bc.group(0)) if bc else None
                        if pc and pc[3] > 0.5 and _ux_cs.rgb_to_hls(pc[0] / 255, pc[1] / 255, pc[2] / 255)[1] >= 0.35: decl.append('%s:%s' % (p, v)); continue
                decl.append('%s:%s' % (p, _UX_COL.sub(lambda m: _ux_map(m.group(0), k, theme), v)))
            if not decl or not any(_UX_COL.search(x) for x in decl) and not re.search(r'background|color|border', sel + body): continue
            sc = _ux_scope(sel, theme)
            if not sc: continue
            r = '%s{%s}' % (sc, ';'.join(decl))
            out.append('%s{%s}' % (wrap, r) if wrap else r)
    return '\n'.join(out)
def _ux_themes():
    ad = os.path.join(OUT, 'assets'); hand = ''
    hp = os.path.join(ad, 'mod-ux-themes.css')
    if os.path.exists(hp): hand = open(hp, encoding='utf8').read(); os.remove(hp)
    order = lambda f: (0 if f == 'site.css' else 3 if f == 'mod-ux.css' else 2 if f == 'mod-nav.css' else 1, f)  # same order as the <link> tags
    srcs = [open(os.path.join(ad, f), encoding='utf8').read() for f in sorted(os.listdir(ad), key=order)
            if f.endswith('.css') and not f.startswith('mod-ux-light') and not f.startswith('mod-ux-contrast')]
    for th in ('light', 'contrast'):
        hw = '\n'.join(_ux_hand_part(hand, th))
        _ux_js('mod-ux-%s.css' % th, '/* generated by modules/zzz_ux.py (UX pass 5) */\n' + _ux_theme_css(th, srcs) + '\n' + hw + '\n')
def _ux_hand_part(hand, th):
    """keep rules of static/mod-ux-themes.css that mention this theme (or no theme)"""
    hand = re.sub(r'/\*.*?\*/', '', hand, flags=re.S); other = 'contrast' if th == 'light' else 'light'
    for wrap, sel, body in _ux_rules(hand):
        sels = [x for x in sel.split(',') if 'data-theme="%s"' % other not in x]
        if not sels: continue
        r = '%s{%s}' % (','.join(s.strip() for s in sels), body.strip())
        yield '%s{%s}' % (wrap, r) if wrap else r

_ux_prev_ra5b = render_all
def render_all():
    _ux_prev_ra5b()
    _ux_themes()

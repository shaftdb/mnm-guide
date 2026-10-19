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
    for f, t in files.items(): _ux_js(f, t)
    d.update(route={}, schead_c={}, lazy=lazy)
    _ux_js('walk-data.js', 'window.MNM_WT=%s;' % _ux_dump(d))

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

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
            _ux_js(f, 'window.MNM_QUICK.route[%s]=%s;window.MNM_QUICK.routenh[%s]=%s;' % (_ux_dump(k), _ux_dump(route.get(k, '')), _ux_dump(k), _ux_dump(routenh.get(k, ''))))
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

# Class-following gear & quick reference module: per-class gear/leveling/spells/overview pages for all 18 classes;
# nav links and class-specific pages follow the top-bar class picker (localStorage key mnm-class).
def _cref(c):
    s = slug(c)
    if c == 'Shaman':
        return {'overview': '/shaman/index.html', 'spells': '/shaman/spells.html', 'leveling': '/shaman/leveling.html', 'gear': '/gear/shaman.html', 'quickinfo': '/shaman/quickinfo.html'}
    return {'overview': '/classref/%s/index.html' % s, 'spells': '/classref/%s/spells.html' % s, 'leveling': '/classref/%s/leveling.html' % s, 'gear': '/gear/%s.html' % s, 'quickinfo': '/index.html#mnm-quickinfo'}
_CG_BANDS = [(1, 10), (11, 15), (16, 20), (21, 25), (26, 30), (31, 35), (36, 40), (41, 50), (51, 60)]
def _marker(kind, c): return '<div class="cpage" data-cpage="%s" data-ccls="%s"></div>' % (kind, esc(c))
def g_cgear(arg, ctx):
    c, lo, hi = [a.strip() for a in arg.split(',')]; return class_gear_band(c, int(lo), int(hi))
def g_cgearlist(arg, ctx):
    c, lo, hi = [a.strip() for a in arg.split(',')]; lo, hi = int(lo), int(hi); code = CABBR[c]
    its = sorted([(lv, it) for it, lv, k in easy_items(code) if lv is not None and lo <= lv <= hi and len(class_codes(it)) < 18], key=lambda x: (x[0], ', '.join(slots_of(x[1]))))
    if not its: return '<p class="dim"><span class="badge unc">unverified</span> No wiki items usable by %s with a known level in %d–%d.</p>' % (esc(c), lo, hi)
    more = ' <span class="dim">Showing 60 of %d; use "Filter this page" or the <a href="/items.html">item database</a>.</span>' % len(its) if len(its) > 60 else ''
    return '<details><summary>All %s-usable gear at levels %d–%d (%d items) <span class="badge fact">fact</span></summary>%s<div class="tw"><table class="grid gear sortable">%s<tbody>%s</tbody></table></div></details>' % (
        esc(c), lo, hi, len(its), more, GEAR_HEAD % '<th>Classes</th>', ''.join(gear_row(it, lv) for lv, it in its[:60]))
def g_ccamps_note(arg, ctx):
    c = arg.strip(); n = CLASS_NOTES.get(c, {})
    out = []
    for k, lab in (('solo', 'Solo'), ('group', 'Group')):
        v = n.get(k)
        out.append('<li><b>%s:</b> %s</li>' % (lab, esc(v) if v and 'UNCONFIRMED' not in v else '<span class="badge unc">unverified</span> no sourced note'))
    return '<ul class="tight">%s</ul>' % ''.join(out)
GENS.update(cgear=g_cgear, cgearlist=g_cgearlist, ccampsnote=g_ccamps_note)
def _tabs(fn):
    return ':::tabs\n' + ''.join('=== %d–%d\n%s\n' % (lo, hi, fn(lo, hi)) for lo, hi in _CG_BANDS) + ':::\n'
_cg_prev_bc = build_content
def build_content():
    _cg_prev_bc()
    for c in CLASS_LIST:
        if c == 'Shaman': continue
        s = slug(c); U = _cref(c); code = CABBR[c]
        sub = '<p class="cnav">%s</p>' % ' · '.join('<a href="%s">%s</a>' % (U[k], t) for k, t in (('overview', 'Overview'), ('gear', 'Gear (easy BiS)'), ('leveling', 'Leveling'), ('spells', 'Spells by level')))
        src = ['Wiki: %s|%s' % (c, CLASSES[c]['url']), 'Wiki item pages|%sCategory:Items' % WIKI, 'Wiki zone pages (mob levels)|%sZones' % WIKI]
        gear_md = (_marker('gear', c) + sub + '\n\n:::strategy How to read this\nFor each level range: what to wear per slot when you start it, and the upgrade to pick up by its top level. Items, stats and where to get them come from the wiki item pages (quest, vendor, craft or drop). '
                   'The pick per slot is this guide\'s suggestion based on the wiki stat advice for %s (%s). It is not a game formula. Slots with no wiki item are left out. "Lvl" is the lowest drop or quest level on the wiki, not a required level.\n:::\n\n' % (c, CLASS_NOTES.get(c, {}).get('stat', 'stat advice unverified'))
                   + _tabs(lambda lo, hi: '{{gen:cgear %s,%d,%d}}\n{{gen:cgearlist %s,%d,%d}}' % (c, lo, hi, c, lo, hi)))
        add_page('gear/%s.html' % s, '%s gear — easy BiS by level' % c, gear_md, 'gear', {'sources': '; '.join(src)}, desc='%s gear by level' % c)
        lev_md = (_marker('leveling', c) + sub + '\n\n## Solo and group notes\n{{gen:ccampsnote %s}}\n\n:::strategy Using the camp lists\nThe camps are every wiki mob whose listed level overlaps the range (★ = named). Many wiki mobs have no level and are left out. /consider before pulling. For farming, named camps list their wiki loot; look for items your class can use in the [gear page](%s).\n:::\n\n' % (c, U['gear'])
                  + _tabs(lambda lo, hi: '{{gen:zones_band_md %d,%d}}\n{{gen:camps %d,%d}}' % (lo, hi, lo, hi)))
        add_page('classref/%s/leveling.html' % s, '%s leveling by level range' % c, lev_md, 'cref-' + s, {'sources': '; '.join(src[2:])}, desc='%s leveling' % c)
        add_page('classref/%s/spells.html' % s, '%s spells by level' % c, _marker('spells', c) + sub + '\n\n{{gen:spells %s}}' % c, 'cref-' + s, {'sources': src[0]}, desc='%s spells' % c)
        ov_md = (_marker('overview', c) + sub + '\n\n{{gen:classglance %s}}\n\n{{gen:classtips %s}}\n\n:::note Quick info by level\nThe [home page quick info](/index.html#mnm-quickinfo) shows %s spells, gear and zones for the level range picked in the top bar.\n:::\n' % (c, c, c))
        add_page('classref/%s/index.html' % s, '%s quick reference' % c, ov_md, 'cref-' + s, {'sources': '; '.join(src)}, desc='%s quick reference' % c)
def g_zones_band_md(arg, ctx):
    lo, hi = [int(x) for x in arg.split(',')]; return zones_band(lo, hi)
GENS.update(zones_band_md=g_zones_band_md, classglance=lambda a, ctx: class_glance(a.strip()), classtips=lambda a, ctx: class_tips(a.strip()))
_cg_prev_ln = left_nav
def left_nav(section):
    if section.startswith('cref-'):
        c = next(x for x in CLASS_LIST if slug(x) == section[5:]); U = _cref(c)
        return ('<div class="box nav"><h3>%s</h3><ul>%s</ul></div>' % (esc(c), ''.join('<li><a href="%s">%s</a></li>' % (U[k], t) for k, t in (('overview', 'Overview'), ('gear', 'Gear (easy BiS)'), ('leveling', 'Leveling'), ('spells', 'Spells by level'))))
                + '<div class="box nav"><h3>Other classes</h3><ul>%s</ul></div>' % ''.join('<li><a href="%s">%s</a></li>' % (_cref(x)['overview'], esc(x)) for x in CLASS_LIST if x != c))
    return _cg_prev_ln(section)
NAV[:] = [('My class', u, k) if k == 'shaman' else (t, u, k) for t, u, k in NAV]
GEAR_NAV[:] = [('Easy BiS (my class)', u) if u == '/gear/shaman.html' else (t, u) for t, u in GEAR_NAV]
TEMPLATE = TEMPLATE.replace('<script src="{root}assets/site.js"></script>', '<script>window.MNM_CREF=%s;</script>\n<script src="{root}assets/site.js"></script>\n<script src="{root}assets/mod-classgear.js"></script>' % json.dumps({c: _cref(c) for c in CLASS_LIST}).replace('{', '{{').replace('}', '}}'))

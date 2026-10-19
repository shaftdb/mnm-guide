# Grouped top nav (runs last): Home + category dropdowns; hamburger with collapsible groups on narrow screens.
NAV_GROUPS = [('Class', ['shaman', 'classes', 'gear', 'leveling', 'farming']), ('World', ['dungeons', 'zones', 'mobs', 'quests', 'factions']),
              ('Database', ['items', 'spells']), ('Crafting & Economy', ['tradeskills', 'economy', 'market']), ('News', ['news', 'patches', 'events', 'changelog']), ('Tools', ['planner', 'hotbar', 'groups', 'trio', 'tools'])]
def nav_html(section):
    by = {k: (t, u) for t, u, k in NAV}
    used = {'home'}; out = ['<a href="%s"%s>%s</a>' % (by['home'][1], ' class="on"' if section == 'home' else '', 'Home')]
    for i, (g, keys) in enumerate(NAV_GROUPS):
        ks = [k for k in keys if k in by]; used.update(ks)
        on = section in ks or (g == 'Class' and section.startswith('cref-'))
        out.append('<div class="ng%s"><button type="button" class="ngb" aria-expanded="false" aria-controls="ngm%d">%s <span aria-hidden="true">▾</span></button><div class="ngm" id="ngm%d" role="group" aria-label="%s">%s</div></div>' % (
            ' on' if on else '', i, esc(g), i, esc(g), ''.join('<a href="%s"%s>%s</a>' % (by[k][1], ' class="on"' if k == section else '', esc(by[k][0])) for k in ks)))
    rest = [(t, u, k) for t, u, k in NAV if k not in used]
    if rest: print('nav: ungrouped', rest)
    return ''.join(out)
_nav_prev_ra = render_all
def render_all():
    _nav_prev_ra()
    by_path = {p['path']: p['section'] for p in PAGES}
    for path, sec in by_path.items():
        fp = os.path.join(OUT, path); h = open(fp, encoding='utf8').read()
        h = re.sub(r'<nav class="mainnav">.*?</nav>', lambda m: '<nav class="mainnav" aria-label="Main">%s</nav>' % relink(nav_html(sec), path.count('/')), h, count=1, flags=re.S)
        open(fp, 'w', encoding='utf8').write(h)
TEMPLATE = TEMPLATE.replace('</head>', '<link rel="stylesheet" href="{root}assets/mod-nav.css">\n</head>', 1).replace('<script src="{root}assets/site.js"></script>', '<script src="{root}assets/site.js"></script>\n<script src="{root}assets/mod-nav.js"></script>', 1)

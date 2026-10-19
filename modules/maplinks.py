# Map deep links (mnmatlas.com) from data/map_links.json: only sourced entries, never guessed coordinates.
# Self-contained: wraps zone_page/dungeon_page output and exposes map_link(name) for other renderers.
MAPLINKS = json.load(open(os.path.join(DATA, 'map_links.json'), encoding='utf8')) if os.path.exists(os.path.join(DATA, 'map_links.json')) else {}
def map_link(name, kinds=('zones', 'camps', 'mobs', 'npcs', 'quest_givers', 'trainers')):
    for k in kinds:
        e = (MAPLINKS.get(k) or {}).get(name)
        if e and e.get('url'):
            return ' <a class="maplink ext" target="_blank" rel="noopener" href="%s" title="Map: %s (source: %s)">🗺 Map</a>' % (esc(e['url']), esc(name), esc(e.get('source', '')))
    return ''
def _ml_wrap(fn):
    def w(z, *a):
        r = fn(z, *a); m = map_link(z, ('zones',))
        if not m: return r
        e = MAPLINKS['zones'][z]
        return ('<p class="maplink-row">Interactive map:%s <span class="dim">(mnmatlas.com, community atlas)</span></p>' % m + r[0], r[1] + ['Map link: %s|%s' % (e['source'], e['source_url'])]) + tuple(r[2:])
    return w
zone_page = _ml_wrap(zone_page)
dungeon_page = _ml_wrap(dungeon_page)

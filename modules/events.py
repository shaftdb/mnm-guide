# Events timeline module: /events.html from data/events.json (tools/events_fetch.py) + milestones stated in official posts
EVENTS = json.load(open(os.path.join(DATA, 'events.json'), encoding='utf8')) if os.path.exists(os.path.join(DATA, 'events.json')) else {'events': [], 'fetched': ''}
_MILESTONES = [('2026-10-01', 'Early Access launch with Module 1: Descent into the Deep (four starting cities; Deep Elves and Deep Gnomes playable)',
                'https://monstersandmemories.com/updates/early-access-launch-october-1-2026')]
def _events_page():
    ev = [dict(e) for e in EVENTS['events']] + [{'date': d, 'kind': 'milestone', 'title': t, 'url': u} for d, t, u in _MILESTONES]
    ev.sort(key=lambda e: e['date'], reverse=True)
    today = BUILD_DATE
    up = [e for e in ev if e['date'] > today]
    o = ['<p>A dated timeline of officially announced events: patches, news posts and launch milestones <span class="badge fact">fact</span>. ',
         'The developers don\'t publish an events calendar or a server status page, so nothing here is a guess about future dates.</p>',
         '<h2 id="upcoming">Upcoming</h2>', ('<ul class="tight">%s</ul>' % ''.join('<li><b>%s</b> %s</li>' % (e['date'], esc(e['title'])) for e in up)) if up else
         '<p class="dim">No future dates announced in official sources as of %s. For plans without dates, see the <a class="ext" target="_blank" rel="noopener" href="https://monstersandmemories.com/roadmaps">official roadmaps</a>.</p>' % esc(EVENTS.get('fetched') or today),
         '<h2 id="timeline">Timeline</h2><p><label><select id="ev-kind" aria-label="Event type"><option value="">All</option><option value="patch">Patches</option><option value="news">News posts</option><option value="milestone">Milestones</option></select></label></p><ul class="tight evl">']
    for e in ev:
        o.append('<li class="ev-%s"><b>%s</b> <span class="tag">%s</span> <a class="ext" target="_blank" rel="noopener" href="%s">%s</a></li>' % (e['kind'], e['date'], e['kind'], esc(e['url']), esc(e['title'])))
    o.append('</ul><h2 id="update">Keeping it updated</h2><ol class="tight"><li>Run <code>python3 tools/events_fetch.py</code>. It reads the official news feed (monstersandmemories.com/updates?format=rss) and the official patch notes pages, and stops after 8 missing numbers in a row.</li>'
             '<li>Run <code>python3 build.py</code> and commit <code>data/events.json</code> and <code>docs/</code>.</li><li>Add a milestone only when an official post states the date, with that post\'s URL (the <code>_MILESTONES</code> list in <code>modules/events.py</code>).</li></ol>'
             '<p class="dim">Last fetched: %s.</p><script>(function(){var s=document.getElementById("ev-kind");s.onchange=function(){document.querySelectorAll(".evl li").forEach(function(l){l.style.display=!s.value||l.className==="ev-"+s.value?"":"none"})}})();</script>' % esc(EVENTS.get('fetched') or '?'))
    return ''.join(o)
_e_prev_bc = build_content
def build_content():
    _e_prev_bc()
    add_page('events.html', 'Events & patch timeline', body_html=_events_page(), section='events',
             sources=['Official news (RSS)|https://monstersandmemories.com/updates?format=rss', 'Official patch notes|https://account.monstersandmemories.com/community/patch_notes', 'Official roadmaps|https://monstersandmemories.com/roadmaps'], desc='Events and patch timeline')
NAV.insert(len(NAV) - 1, ('Events', '/events.html', 'events'))

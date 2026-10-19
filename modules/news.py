# Latest News module: data in content/news.json (no layout), newest 5 on home via {{gen:news 5}}, full archive at /news.html.
# Append items safely with tools/news_add.py (dedupe by source_url, validation, optional rebuild).
def _news_items():
    p = os.path.join(CONTENT, 'news.json')
    items = json.load(open(p, encoding='utf8')) if os.path.exists(p) else []
    return sorted(items, key=lambda i: (i.get('date', ''), i.get('id', '')), reverse=True)
def _news_date(d):
    try:
        import datetime as _dt; x = _dt.date.fromisoformat(d); return x.strftime('%b %d, %Y').replace(' 0', ' ')
    except Exception: return esc(d)
def _news_list(items):
    return '<ul class="news-list">%s</ul>' % ''.join(
        '<li id="news-%s"><time datetime="%s">%s</time> <a class="ext" href="%s" target="_blank" rel="noopener">%s</a><br><span class="news-sum">%s</span> <span class="dim">— %s%s</span></li>' % (
            esc(i['id']), esc(i['date']), _news_date(i['date']), esc(i['source_url']), esc(i['headline']), esc(i['summary']), esc(i['source_name']),
            ''.join(' <span class="news-tag">%s</span>' % esc(t) for t in i.get('tags', []))) for i in items)
def _gen_news(arg, ctx):
    n = int(arg or 5); items = _news_items()
    return '<link rel="stylesheet" href="/assets/mod-news.css">%s<p><a href="/news.html">All news (%d)</a></p>' % (_news_list(items[:n]), len(items))
GENS['news'] = _gen_news
_news_prev_bc = build_content
def build_content():
    _news_prev_bc()
    items = _news_items()
    body = ('<link rel="stylesheet" href="/assets/mod-news.css"><p>Notable Monsters &amp; Memories news from official sources. Each summary is taken only from the linked source. '
            'Newest first.</p>%s<p class="dim">Sources: <a class="ext" href="https://monstersandmemories.com/updates" target="_blank" rel="noopener">Official updates</a> · '
            '<a class="ext" href="https://account.monstersandmemories.com/community/patch_notes" target="_blank" rel="noopener">Official patch notes</a></p>') % _news_list(items)
    add_page('news.html', 'Latest news', body_html=body, section='news', desc='Monsters & Memories news archive',
             sources=['Official updates (RSS)|https://monstersandmemories.com/updates?format=rss', 'Official patch notes|https://account.monstersandmemories.com/community/patch_notes'])
NAV.insert(len(NAV) - 1, ('News', '/news.html', 'news'))

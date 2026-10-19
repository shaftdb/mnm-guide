# Market / pricing module: /market.html + docs/assets/market-db.js (data from content/prices.json, kept up to date by
# tools/prices_update.py) + static/mod-market.js/.css. Also links the Items page to the Market.
# No in-game auction house exists; every price row is one dated observation from a named source. Never invent prices.
_MKT_PATH = os.path.join(CONTENT, 'prices.json')
MKT = json.load(open(_MKT_PATH, encoding='utf8'))
_MKT_KINDS = {'vendor_buys': 'Vendor pays', 'vendor_sells': 'NPC sells for', 'player_ask': 'Player asking (WTS)',
              'player_bid': 'Player wants (WTB)', 'player_sale': 'Reported sale', 'report': 'Player report'}
def _mkt_place(z):
    if z in DUNGEON_ORDER: return dungeon_url(z).lstrip('/')
    if z in ZONES: return zone_url(z).lstrip('/')
    return ''
def _mkt_item(nm):
    it = ITEMS.get(nm)
    if not it: return None
    drops = []
    for d in it.get('drops', []):
        z = d.get('zone') or ''
        drops.append([d.get('mob') or '', z, _mkt_place(z), d.get('level') or ''])
    return {'url': it.get('url', ''), 'wt': it.get('weight'), 'drops': drops[:8]}
def _mkt_db():
    S = MKT['sources']; rows = []
    for e in MKT['entries']:
        ln = None if e.get('nolink') else (e.get('link') or e['item'])
        I = _mkt_item(ln) if ln else None
        wt = e.get('weight') if e.get('weight') is not None else (I or {}).get('wt')
        rows.append({'i': e['item'], 'k': e['kind'], 'p': e['price'], 'cp': e['cp'], 'cx': e.get('cp_max'), 'sv': e.get('server') or '',
                     'wh': e.get('where') or '', 's': e['source'], 'u': e.get('url') or S[e['source']]['url'], 'd': e['seen'], 'ck': e.get('checked') or '',
                     'c': e['confidence'], 'l': e['label'], 'n': e.get('note') or '', 'w': wt, 'db': ln if I else '', 'wu': (I or {}).get('url', ''),
                     'dr': (I or {}).get('drops', [])})
    camps = []
    for c in MKT.get('camps', []):
        its = []
        for nm in c['items']:
            vals = [e for e in MKT['entries'] if e['item'] == nm and e['kind'] == 'vendor_buys']
            I = _mkt_item(next((e.get('link') for e in vals if e.get('link')), nm)) or {}
            here = [d for d in I.get('drops', []) if d[1] in (c['zone'], c.get('zone2'))]
            its.append({'i': nm, 'p': ' / '.join(sorted({e['price'] for e in vals})) or 'no value sourced', 'db': nm if nm in ITEMS else (vals[0].get('link') if vals and vals[0].get('link') in ITEMS else ''),
                        'here': [d[0] for d in here][:4]})
        mobs = [[m, m] for m in c.get('mobs', [])]
        camps.append({'b': c['band'], 'c': c['camp'], 'z': c['zone'], 'zu': _mkt_place(c['zone']), 'z2': c.get('zone2') or '', 'z2u': _mkt_place(c.get('zone2') or ''),
                      'm': mobs, 'it': its, 'n': c.get('note') or '', 'l': c.get('label') or 'FACT'})
    cities = []
    for city, D in sorted(SC.items(), key=lambda x: (x[0] != "Ail'Vorith", x[0])):
        src = D.get('sources', {})
        cities.append({'city': city, 'status': D.get('status'), 'race': 'Deep Elf' if city == "Ail'Vorith" else '',
                       'money': [{'l': m.get('label', ''), 't': m.get('text', ''), 's': [[src[k][0], src[k][1]] for k in m.get('src', []) if k in src]} for m in D.get('money', [])]})
    return {'rows': rows, 'camps': camps, 'cities': cities, 'kinds': _MKT_KINDS, 'meta': MKT['meta'],
            'sources': [[k, v.get('short') or v['name'], v['url'], v.get('label', ''), v['name']] for k, v in MKT['sources'].items()]}
def _mkt_src_table():
    h = ['<div class="mkt-wrap"><table class="mkt-src"><thead><tr><th>Source</th><th>What it gives</th><th>Freshness</th><th>Automatic refresh?</th><th>Reliability</th></tr></thead><tbody>']
    lab = {'FACT': '<span class="badge fact">fact</span>', 'UNVERIFIED': '<span class="badge unc">unverified</span>', 'STRATEGY': '<span class="badge strat">strategy</span>'}
    for k, s in MKT['sources'].items():
        h.append('<tr><td data-l="Source"><a class="ext" target="_blank" rel="noopener" href="%s">%s</a> %s</td><td data-l="Gives">%s</td><td data-l="Freshness">%s</td><td data-l="Auto">%s</td><td data-l="Reliability">%s</td></tr>' % (
            esc(s['url']), esc(s['name']), lab.get(s.get('label'), ''), esc(s.get('kind', '')), esc(s.get('freshness', '')), esc(s.get('auto', '')), esc(s.get('reliability', ''))))
    h.append('</tbody></table></div>')
    return ''.join(h)
def _mkt_page():
    n = len(MKT['entries']); upd = MKT['meta'].get('updated', '')
    return ('<link rel="stylesheet" href="/assets/mod-market.css">'
            '<div class="box facts mkt-facts"><b>How trading works in M&amp;M</b><ul class="tight">'
            '<li><span class="badge fact">fact</span> There is <b>no in-game auction house or bazaar</b>. Players trade in zone-wide <code>/auction</code> chat, by <code>/tell</code>, and on fan sites. The devs have discussed consignment selling, with no date (forum, Aug 20).</li>'
            '<li><span class="badge fact">fact</span> Merchants mostly buy only what they sell, and pay a premium for it. Shady merchants buy anything for less. What players sell joins the merchant\'s stock.</li>'
            '<li><span class="badge fact">fact</span> Patch 0.30.2.9 (Oct 15) rebalanced coin drops across many NPC types, and humanoids now also drop sellable medallions. Values seen before then may be out of date.</li>'
            '<li><span class="badge unc">unverified</span> Player prices below are single asking prices or anonymous sale reports from The Tunnel, not market averages. Use them as a rough guide only.</li></ul>'
            '<p class="dim">%d observations, data file updated %s. Nothing here is estimated: a blank means no source. Item names link to the <a href="/items.html">Item database</a>, which links back here.</p></div>'
            '<nav class="mkt-jump"><a href="#prices">Price table</a> · <a href="#vendor">Vendor values</a> · <a href="#money">Good money items</a> · <a href="#sources">Sources</a></nav>'
            '<h2 id="prices">Price table</h2>'
            '<div class="idb-tools"><input id="mkt-q" type="search" placeholder="Item, server, zone or mob…" aria-label="Search prices">'
            '<select id="mkt-k" aria-label="Type"><option value="">Any type</option></select>'
            '<select id="mkt-c" aria-label="Confidence"><option value="">Any confidence</option><option value="high">High</option><option value="medium">Medium+</option><option value="low">Low only</option></select>'
            '<select id="mkt-s" aria-label="Server"><option value="">Any server</option></select><select id="mkt-sort" aria-label="Sort"><option value="i:1">Sort: item A-Z</option><option value="cp:-1">Price, high to low</option><option value="cp:1">Price, low to high</option><option value="d:-1">Newest first</option><option value="c:-1">Most confident first</option></select></div>'
            '<p id="mkt-count" class="dim" aria-live="polite"></p><div class="mkt-wrap"><table class="mkt-t" id="mkt-t"><thead><tr>'
            '<th data-s="i" aria-sort="ascending"><button type="button">Item</button></th><th data-s="cp"><button type="button">Price</button></th><th data-s="k"><button type="button">Type</button></th>'
            '<th data-s="s"><button type="button">Source</button></th><th data-s="d"><button type="button">Seen</button></th><th data-s="c"><button type="button">Confidence</button></th></tr></thead><tbody id="mkt-b"></tbody></table></div>'
            '<p class="dim">Confidence: <b>high</b> = official or confirmed in game; <b>medium</b> = vendor ledger database or a recent wiki page; <b>low</b> = a single player post or listing, or data from before Early Access. Tap a column to sort.</p>'
            '<h2 id="vendor">NPC vendor values</h2><p>What merchants pay you, with value per 1.0 weight so you know what to carry home. <span class="badge strat">strategy</span> Keep anything worth about 1 sp per 1.0 weight or more, and sell to the merchant who stocks that kind of item.</p>'
            '<div class="mkt-wrap"><table class="mkt-t" id="mkt-v"><thead><tr><th data-s="i"><button type="button">Item</button></th><th data-s="cp"><button type="button">Vendor pays</button></th>'
            '<th data-s="w"><button type="button">Weight</button></th><th data-s="pw" aria-sort="descending"><button type="button">Per 1.0 wt</button></th><th>Drops from</th><th data-s="d"><button type="button">Seen</button></th></tr></thead><tbody id="mkt-vb"></tbody></table></div>'
            '<h2 id="money">Good money items by camp</h2><p>Camps from the <a href="/trio.html#6-best-money-camps-per-band">Trio plan money camps</a> and the <a href="/farming.html">Farming</a> notes, with the vendor values above. Mob names open the <a href="/mobs.html">Mob lookup</a>. <b>Drops here</b> lists the wiki\'s drop sources inside that zone; if it is empty, the wiki does not tie the item to that zone.</p>'
            '<div id="mkt-camps" class="mkt-camps"></div>'
            '<h3 id="money-cities">Start-city money notes</h3><p>From the start-city route files that drive the <a href="/walkthrough.html">New-character walkthrough</a>.</p><div id="mkt-cities"></div>'
            '<h2 id="sources">Sources and how fresh they are</h2>%s'
            '<h3>Adding a price</h3><p>Prices are kept in <code>content/prices.json</code>. Add new observations with <code>tools/prices_update.py --add new.json --build</code>: it checks every field, turns prices into copper, removes duplicates, stamps dates and rebuilds. Only add a price you saw in a source, with its link and date.</p>'
            '<script src="/assets/market-db.js"></script><script src="/assets/mod-market.js"></script>') % (n, esc(upd), _mkt_src_table())
_mkt_prev_items = _items_page
def _items_page():
    return _mkt_prev_items().replace('<div class="idb-tools">', '<p class="dim">💰 Prices and vendor values: see the <a href="/market.html">Market</a>. Items with a known price show a <b>Market</b> link.</p><div class="idb-tools">', 1).replace(
        '<script src="/assets/mod-items.js">', '<script src="/assets/market-items.js"></script><script src="/assets/mod-items.js">', 1)
_mkt_prev_bc = build_content
def build_content():
    _mkt_prev_bc()
    add_page('market.html', 'Market & prices', body_html=_mkt_page(), section='market', desc='Item prices, NPC vendor values and money items (sourced, dated)',
             sources=['%s|%s' % (s['name'], s['url']) for s in MKT['sources'].values()])
_mkt_prev_ra = render_all
def render_all():
    _mkt_prev_ra()
    D = _mkt_db()
    open(os.path.join(OUT, 'assets', 'market-db.js'), 'w', encoding='utf8').write('window.MNM_MKT=' + json.dumps(D, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + ';')
    best = {}
    for r in D['rows']:
        if r['db']:
            cur = best.get(r['db'])
            if cur is None or (r['k'] == 'vendor_buys' and cur[1] != 'vendor_buys') or r['d'] > cur[2]: best[r['db']] = [r['p'], r['k'], r['d']]
    open(os.path.join(OUT, 'assets', 'market-items.js'), 'w', encoding='utf8').write('window.MNM_MKTI=' + json.dumps({k: [v[0], _MKT_KINDS[v[1]], v[2]] for k, v in best.items()}, ensure_ascii=False, separators=(',', ':')) + ';')
NAV.insert(len(NAV) - 1, ('Market', '/market.html', 'market'))

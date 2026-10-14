#!/usr/bin/env python3
"""Build the M&M Codex static site.

  content/**/*.md   hand-written pages (front matter + Markdown subset + shortcodes)
  data/*.json       facts extracted from the M&M wiki / official site (tools/extract.py etc.)
  static/           css/js copied verbatim
  -> docs/          finished site (commit it; GitHub Pages serves /docs)

Standard library only. Run:  python3 build.py
"""
import json, os, re, html, shutil, datetime, glob
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'docs')
CONTENT = os.path.join(ROOT, 'content')
DATA = os.path.join(ROOT, 'data')
SITE_NAME = "M&M Quick Codex"
BUILD_DATE = datetime.date.today().isoformat()

def J(name):
    return json.load(open(os.path.join(DATA, name + '.json'), encoding='utf8'))

ZONES = J('zones'); ITEMS = J('items'); QUESTS = J('quests'); MERCH = J('merchants')
CLASSES = J('classes'); DD = J('deepdives'); IMAGES = J('images'); SETS = J('armor_sets')
FACTIONS = J('factions'); TRADES = J('tradeskills')

ZEXTRA = json.load(open(os.path.join(CONTENT, 'zones_extra.json'), encoding='utf8'))
CLASS_NOTES = json.load(open(os.path.join(CONTENT, 'class_notes.json'), encoding='utf8'))

def esc(s): return html.escape(str(s if s is not None else ''), quote=True)
def slug(s): return re.sub(r'[^a-z0-9]+', '-', str(s).lower().replace("'", '')).strip('-')
WIKI = 'https://monstersandmemories.miraheze.org/wiki/'
def wiki(t): return WIKI + t.replace(' ', '_').replace("'", '%27').replace('?', '%3F')

CLASS_LIST = ['Archer','Bard','Beastmaster','Cleric','Druid','Elementalist','Enchanter','Fighter','Inquisitor','Monk','Necromancer','Paladin','Ranger','Rogue','Shadow Knight','Shaman','Spellblade','Wizard']
ABBR = {'ARC':'Archer','BRD':'Bard','BST':'Beastmaster','CLR':'Cleric','DRU':'Druid','ELE':'Elementalist','ENC':'Enchanter','FTR':'Fighter','INQ':'Inquisitor','MNK':'Monk','NEC':'Necromancer','PAL':'Paladin','RNG':'Ranger','ROG':'Rogue','SHD':'Shadow Knight','SHM':'Shaman','SPB':'Spellblade','WIZ':'Wizard'}
CABBR = {v: k for k, v in ABBR.items()}
# Armor families: taken from the wiki's Wyrmsbane armor-set class lines (Plate / Chain / Leather / Cloth).
FAMILIES = [
    ('cloth', 'Cloth casters', ['ELE','ENC','NEC','WIZ'], 'Wyrmsbane Cloth'),
    ('leather', 'Leather wearers', ['ARC','BST','DRU','MNK','SPB'], 'Wyrmsbane Leather'),
    ('chain', 'Chain hybrids', ['BRD','RNG','ROG','SHM'], 'Wyrmsbane Chain'),
    ('plate', 'Plate tanks & healers', ['CLR','FTR','INQ','PAL','SHD'], 'Wyrmsbane Plate'),
]
def class_url(c):
    return '/shaman/index.html' if c == 'Shaman' else '/classes/%s.html' % slug(c)
def zone_url(z): return '/zones/%s.html' % slug(z)

# ------------------------------------------------------------------ pages registry
PAGES = []   # dicts: path, title, section, html(body), left, right, crumbs, sources, verified, desc
USED_ITEMS = set()

def item_link(name, label=None):
    it = ITEMS.get(name)
    if not it:
        return '<span class="itm unk" title="Not found in wiki item data">%s</span>' % esc(label or name)
    USED_ITEMS.add(name)
    q = 'q-magic' if it.get('magic') else ('q-lore' if it.get('lore') else 'q-common')
    return '<a class="itm %s" data-i="%s" href="%s" target="_blank" rel="noopener">%s</a>' % (q, esc(name), esc(it['url']), esc(label or name))

def zlink(z, label=None):
    if z in ZONES: return '<a href="%s">%s</a>' % (zone_url(z), esc(label or z))
    return '<a href="%s" target="_blank" rel="noopener" class="ext">%s</a>' % (wiki(z), esc(label or z))

def clink(c, label=None):
    return '<a href="%s">%s</a>' % (class_url(c), esc(label or c))

# ------------------------------------------------------------------ markdown subset
def inline(s):
    s = esc(s).replace('&#x27;', "'")
    # shortcode links  [[kind:Target|label]]
    def sc(m):
        kind, rest = m.group(1), m.group(2)
        tgt, _, label = rest.partition('|')
        tgt = html.unescape(tgt); label = html.unescape(label) if label else None
        if kind == 'item': return item_link(tgt, label)
        if kind == 'zone': return zlink(tgt, label)
        if kind == 'class': return clink(tgt, label)
        if kind == 'wiki': return '<a class="ext" href="%s" target="_blank" rel="noopener">%s</a>' % (esc(wiki(tgt)), esc(label or tgt))
        if kind == 'quest': return '<a class="ext" href="%s" target="_blank" rel="noopener">%s</a>' % (esc(wiki(tgt)), esc(label or tgt))
        return m.group(0)
    s = re.sub(r'\[\[(item|zone|class|wiki|quest):([^\]]+)\]\]', sc, s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', s)
    def lk(m):
        t, u = m.group(1), html.unescape(m.group(2))
        ext = u.startswith('http')
        return '<a href="%s"%s>%s</a>' % (esc(u), ' class="ext" target="_blank" rel="noopener"' if ext else '', t)
    s = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', lambda m: '<img src="%s" alt="%s" loading="lazy">' % (esc(html.unescape(m.group(2))), m.group(1)), s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lk, s)
    s = s.replace('UNVERIFIED', '<span class="badge unc">unverified</span>')
    s = s.replace('UNCONFIRMED', '<span class="badge unc">unconfirmed</span>')
    s = s.replace('STRATEGY', '<span class="badge strat">strategy</span>')
    s = s.replace('VERIFIED', '<span class="badge ok">verified</span>')
    return s

def md(text, ctx):
    lines = text.split('\n'); out = []; i = 0
    def para_flush(buf):
        if buf: out.append('<p>%s</p>' % inline(' '.join(buf)))
    buf = []
    while i < len(lines):
        ln = lines[i]; st = ln.strip()
        if not st:
            para_flush(buf); buf = []; i += 1; continue
        m = re.match(r'^\{\{gen:(\w+)\s*(.*?)\}\}$', st)
        if m:
            para_flush(buf); buf = []
            out.append(GENS[m.group(1)](m.group(2).strip(), ctx)); i += 1; continue
        if st.startswith(':::'):
            para_flush(buf); buf = []
            kind, _, title = st[3:].strip().partition(' ')
            j = i + 1; depth = 1; inner = []
            while j < len(lines):
                s2 = lines[j].strip()
                if s2.startswith(':::') and s2 != ':::': depth += 1
                elif s2 == ':::':
                    depth -= 1
                    if depth == 0: break
                inner.append(lines[j]); j += 1
            i = j + 1
            if kind == 'facts':
                rows = []
                for l in inner:
                    if ':' in l:
                        k, v = l.split(':', 1); rows.append('<tr><th>%s</th><td>%s</td></tr>' % (inline(k.strip()), inline(v.strip())))
                ctx['facts'] = '<div class="box facts"><h3>%s</h3><table>%s</table></div>' % (esc(title or 'Quick Facts'), ''.join(rows))
            elif kind == 'tabs':
                tabs = []; cur = None
                for l in inner:
                    mm = re.match(r'^===\s*(.+)$', l.strip())
                    if mm: cur = [mm.group(1), []]; tabs.append(cur)
                    elif cur: cur[1].append(l)
                tid = 't%d' % ctx.setdefault('tabn', [0])[0]; ctx['tabn'][0] += 1
                head = ''.join('<button class="tab%s" data-tab="%s-%d">%s</button>' % (' on' if k == 0 else '', tid, k, inline(t[0])) for k, t in enumerate(tabs))
                body = ''.join('<div class="tabpane%s" id="%s-%d">%s</div>' % (' on' if k == 0 else '', tid, k, md('\n'.join(t[1]), ctx)) for k, t in enumerate(tabs))
                out.append('<div class="tabs"><div class="tabbar">%s</div>%s</div>' % (head, body))
            else:
                out.append('<div class="call %s">%s%s</div>' % (esc('hint' if kind == 'tip' else kind), ('<div class="call-t">%s</div>' % inline(title)) if title else '', md('\n'.join(inner), ctx)))
            continue
        m = re.match(r'^(#{1,4})\s+(.*)$', st)
        if m:
            para_flush(buf); buf = []
            n = len(m.group(1)) + 0
            t = m.group(2); hid = slug(re.sub(r'\[\[\w+:([^|\]]+)(\|[^\]]*)?\]\]', r'\1', t))
            if n == 1: n = 2
            out.append('<h%d id="%s">%s</h%d>' % (n, hid, inline(t), n))
            if n == 2: ctx.setdefault('toc', []).append((hid, re.sub('<[^>]+>', '', inline(t))))
            i += 1; continue
        if st.startswith('|'):
            para_flush(buf); buf = []
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')]); i += 1
            hdr = rows[0]; body = [r for r in rows[1:] if not all(re.match(r'^:?-+:?$', c) for c in r)]
            out.append('<div class="tw"><table class="grid"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
                ''.join('<th>%s</th>' % inline(c) for c in hdr),
                ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c) for c in r) for r in body)))
            continue
        if re.match(r'^(\s*)([-*]|\d+\.)\s+', ln):
            para_flush(buf); buf = []
            items = []
            while i < len(lines) and (re.match(r'^(\s*)([-*]|\d+\.)\s+', lines[i]) or (lines[i].startswith('    ') and lines[i].strip())):
                mm = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)$', lines[i])
                if mm: items.append((len(mm.group(1)), mm.group(2)[0].isdigit(), mm.group(3)))
                else: items[-1] = (items[-1][0], items[-1][1], items[-1][2] + ' ' + lines[i].strip())
                i += 1
            def render(lst, lvl):
                o = []; k = 0
                tag = 'ol' if lst and lst[0][1] else 'ul'
                o.append('<%s>' % tag)
                while k < len(lst):
                    ind, num, txt = lst[k]; sub = []; k += 1
                    while k < len(lst) and lst[k][0] > ind: sub.append(lst[k]); k += 1
                    o.append('<li>%s%s</li>' % (inline(txt), render(sub, lvl + 1) if sub else ''))
                o.append('</%s>' % tag); return ''.join(o)
            out.append(render(items, 0)); continue
        if st.startswith('>'):
            para_flush(buf); buf = []; q = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                q.append(lines[i].strip()[1:].strip()); i += 1
            out.append('<blockquote>%s</blockquote>' % md('\n'.join(q), ctx)); continue
        if st == '---':
            para_flush(buf); buf = []; out.append('<hr>'); i += 1; continue
        if st.startswith('<'):
            para_flush(buf); buf = []; out.append(ln); i += 1; continue
        buf.append(st); i += 1
    para_flush(buf)
    return '\n'.join(out)

def read_md(path):
    t = open(path, encoding='utf8').read()
    meta = {}
    if t.startswith('---'):
        _, fm, t = t.split('---', 2)
        for l in fm.strip().split('\n'):
            if ':' in l:
                k, v = l.split(':', 1); meta[k.strip()] = v.strip()
    return meta, t

# ------------------------------------------------------------------ data helpers
def lvl_num(s):
    m = re.search(r'(\d+)', s or ''); return int(m.group(1)) if m else None

ARMOR_SLOTS = ['Head','Face','Ear','Neck','Shoulders','Back','Chest','Arms','Wrist','Hands','Finger','Waist','Legs','Feet','Shirt']
WEAPON_SLOTS = ['Primary','Secondary','Range','Ammo']
STAT_LABEL = [('ac','AC'),('str','STR'),('sta','STA'),('agi','AGI'),('dex','DEX'),('int','INT'),('wis','WIS'),('cha','CHA'),('hp','HP'),('mana','Mana'),('hp_regen','HP Regen'),('mana_regen','Mana Regen'),('haste','Haste'),('spell_haste','Spell Haste'),('cr','SV Cold'),('cor','SV Corruption'),('dr','SV Disease'),('er','SV Elec'),('fr','SV Fire'),('mr','SV Magic'),('pr','SV Poison'),('hr','SV Holy')]
def slots_of(it):
    s = (it.get('slot') or '').replace(',', ' ').split()
    return [x.title() for x in s]
def stat_str(it):
    parts = []
    if it.get('dmg') and it.get('delay'): parts.append('DMG %s / DLY %s' % (it['dmg'], it['delay']))
    for k, lab in STAT_LABEL:
        v = it.get(k)
        if v and v not in ('0',):
            parts.append('%s %s%s' % (lab, '' if str(v).startswith(('+', '-')) or k == 'ac' else '+', v))
    for e in ('effect', 'effect1', 'effect2'):
        if it.get(e): parts.append('Effect: ' + it[e])
    return ', '.join(parts)
def num(v):
    try: return float(str(v).strip('+%'))
    except: return 0.0
def class_codes(it):
    return it.get('classes') or []
def classes_short(it):
    c = class_codes(it)
    if not c: return '<span class="badge unc">class unconfirmed</span>'
    if len(c) == 18: return 'All classes'
    return ' '.join(c)

def acquisitions(it):
    """list of (kind, level or None, html description)"""
    acq = []
    for q in it.get('quests', []):
        Q = QUESTS.get(q, {})
        lv = lvl_num(Q.get('min_level'))
        d = 'Quest: <a class="ext" target="_blank" rel="noopener" href="%s">%s</a>' % (esc(wiki(q)), esc(q))
        bits = []
        if Q.get('giver'): bits.append(esc(Q['giver']))
        if Q.get('zone'): bits.append(zlink(Q['zone']))
        if Q.get('min_level'): bits.append('min lvl ' + esc(Q['min_level']))
        if bits: d += ' (' + ', '.join(bits) + ')'
        acq.append(('quest', lv, d))
    if it.get('soldby'):
        ms = []
        for m in it['soldby'][:3]:
            M = MERCH.get(m, {}); z = ', '.join(zlink(x) for x in (M.get('zone') or []) if x)
            ms.append('%s%s' % (esc(m), (' — ' + z) if z else ''))
        acq.append(('vendor', None, 'Vendor: ' + '; '.join(ms)))
    if it.get('crafted'):
        c = it['crafted']
        acq.append(('crafted', None, 'Crafted: %s%s' % (esc(c.get('skill') or 'tradeskill'), (' (trivial %s)' % esc(c['trivial'])) if c.get('trivial') else '')))
    for d in it.get('drops', []):
        lv = lvl_num(d.get('level'))
        kind = 'named' if d.get('named') else 'drop'
        txt = '%s: %s%s%s' % ('Named drop' if kind == 'named' else 'Drop', esc(d.get('mob') or '?'),
                              (' (lvl %s)' % esc(d['level'])) if d.get('level') else ' (lvl unconfirmed)',
                              (' — ' + zlink(d['zone'])) if d.get('zone') else '')
        if d.get('location'): txt += ', ' + esc(d['location'])
        acq.append((kind, lv, txt))
    return acq

def item_level(it):
    lv = [l for k, l, _ in acquisitions(it) if l]
    return min(lv) if lv else None

def item_score(it, weights):
    return sum(num(it.get(k)) * w for k, w in weights.items())

SHAMAN_W = {'ac': 1, 'wis': 3, 'sta': 2, 'hp': 0.25, 'mana': 0.3, 'str': 0.5, 'dex': 0.75, 'agi': 0.5, 'mana_regen': 4, 'hp_regen': 2, 'int': 0, 'cha': 0}
GENERIC_W = {'ac': 1, 'str': 1, 'sta': 1.5, 'agi': 1, 'dex': 1, 'int': 1, 'wis': 1, 'cha': 0.5, 'hp': 0.25, 'mana': 0.25, 'mana_regen': 3, 'hp_regen': 2}
BANDS = [(1,5),(6,10),(11,15),(16,20),(21,25),(26,30),(31,35),(36,40),(41,50),(51,60)]
EASY_KINDS = ('quest','vendor','crafted','drop','named')

def easy_items(code=None):
    """items with a usable acquisition and stats/slot; returns list of (it, level, kinds)."""
    res = []
    for it in ITEMS.values():
        if not it.get('slot'): continue
        if code and code not in class_codes(it): continue
        acq = acquisitions(it)
        if not acq: continue
        kinds = {k for k, _, _ in acq}
        res.append((it, item_level(it), kinds))
    return res

def gear_row(it, lv, show_classes=True, extra=None):
    acq = acquisitions(it)
    how = '<br>'.join(d for _, _, d in acq[:4])
    kinds = sorted({k for k, _, _ in acq})
    st = stat_str(it) or '<span class="dim">no stats listed on wiki</span>'
    cls = class_codes(it)
    return '<tr data-c="%s" data-k="%s"><td>%s</td><td>%s</td><td>%s</td><td class="how">%s</td><td>%s</td>%s%s</tr>' % (
        ' '.join(cls), ' '.join(kinds), esc(', '.join(slots_of(it))), item_link(it['name']), st, how,
        esc(lv) if lv else '<span class="dim">any / ?</span>',
        ('<td class="cls">%s</td>' % classes_short(it)) if show_classes else '', extra or '')

GEAR_HEAD = '<thead><tr><th>Slot</th><th>Item</th><th>Key stats (wiki)</th><th>How to get</th><th>Lvl</th>%s</tr></thead>'

# ------------------------------------------------------------------ generators (shortcodes)
def g_spells(arg, ctx):
    cls = arg or 'Shaman'
    C = CLASSES[cls]; lo, hi = 1, 60
    rows = []
    by = {}
    for s in C['spells']:
        by.setdefault(s.get('level') or 0, []).append(s)
    tabs = []
    for lv in sorted(by):
        trs = ''.join('<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            esc(s.get('spell name') or s.get('ability name') or s.get('name') or list(s.values())[0]), esc(s.get('spell description') or s.get('description') or ''),
            esc(s.get('class') or s.get('school') or ''), esc(s.get('location') or ''), esc(s.get('mana') or '')) for s in by[lv])
        tabs.append('<h3 id="lvl-%s">Level %s</h3><div class="tw"><table class="grid spells"><thead><tr><th>Spell / ability</th><th>Description (wiki)</th><th>School</th><th>Source</th><th>Mana</th></tr></thead><tbody>%s</tbody></table></div>' % (lv, lv, trs))
    return '<div class="spelllist">%s</div><p class="src">Source: <a class="ext" target="_blank" rel="noopener" href="%s">wiki: %s</a> (rev %s, pulled %s). The wiki is community-maintained; ranks/levels can lag patches.</p>' % (''.join(tabs), C['url'], esc(cls), esc(C.get('revid')), BUILD_DATE)

def g_spells_range(arg, ctx):
    cls, lo, hi = arg.split(',')
    C = CLASSES[cls.strip()]; lo = int(lo); hi = int(hi)
    trs = []
    for s in C['spells']:
        lv = s.get('level') or 0
        if lo <= lv <= hi:
            trs.append('<tr><td>%s</td><td><strong>%s</strong></td><td>%s</td><td>%s</td></tr>' % (lv, esc(s.get('spell name') or list(s.values())[0]), esc((s.get('spell description') or '')[:220]), esc(s.get('location') or '')))
    if not trs: return '<p class="dim">No spell rows for levels %d–%d on the wiki page yet.</p>' % (lo, hi)
    return '<div class="tw"><table class="grid spells"><thead><tr><th>Lvl</th><th>Spell / ability</th><th>Description (wiki)</th><th>Source</th></tr></thead><tbody>%s</tbody></table></div>' % ''.join(trs)

def g_racestats(arg, ctx):
    C = CLASSES[arg]
    if not C['races']: return ''
    hdr = list(C['races'][0].keys())
    return '<div class="tw"><table class="grid"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div><p class="src">Starting stats after class modifier (%s), from <a class="ext" target="_blank" rel="noopener" href="%s">wiki</a>. Bonus = free points to assign.</p>' % (
        ''.join('<th>%s</th>' % esc(h.upper()) for h in hdr),
        ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % esc(r.get(h, '')) for h in hdr) for r in C['races']), esc(C.get('modifier') or 'n/a'), C['url'])

def zones_for_band(lo, hi):
    """zones that have wiki-listed mobs within the band, with example camps"""
    res = []
    for z, Z in ZONES.items():
        camps = []
        for e in Z['npcs'] + Z['named']:
            l = lvl_num(e.get('level'))
            if l is None: continue
            l2 = l
            m = re.search(r'(\d+)\s*-\s*(\d+)', e.get('level') or '')
            if m: l2 = int(m.group(2))
            if l2 >= lo and l <= hi:
                camps.append(e)
        if camps: res.append((z, camps))
    return res

def g_camps(arg, ctx):
    lo, hi = [int(x) for x in arg.split(',')[:2]]
    only = arg.split(',')[2:] if len(arg.split(',')) > 2 else None
    out = []
    for z, camps in sorted(zones_for_band(lo, hi), key=lambda x: -len(x[1])):
        if only and z not in only: continue
        named = [e for e in camps if e in ZONES[z]['named']]
        common = [e for e in camps if e not in named]
        def fmt(e, nm):
            loc = (' @ ' + esc(e['location'])) if e.get('location') and e['location'] not in ('-',) else ''
            loot = ''
            if nm and e.get('loot') and e['loot'] not in ('-',):
                loot = ' — <span class="loot">%s</span>' % ', '.join(item_link(x.strip()) if x.strip() in ITEMS else esc(x.strip()) for x in e['loot'].split(','))
            return '<li>%s<strong>%s</strong> (lvl %s)%s%s</li>' % ('★ ' if nm else '', esc(e['name']), esc(e['level']), loc, loot)
        out.append('<div class="camp"><h4>%s <span class="dim">— wiki zone level: %s</span></h4><ul>%s%s</ul></div>' % (
            zlink(z), esc(ZONES[z]['level'] or 'not stated'), ''.join(fmt(e, True) for e in named[:12]), ''.join(fmt(e, False) for e in common[:14])))
    if not out: return '<p class="dim">No wiki mob rows with levels in %d–%d.</p>' % (lo, hi)
    return '<div class="camps">%s</div><p class="src">Mobs whose wiki-listed level overlaps %d–%d (★ = named). Levels come from zone NPC tables on the wiki; many mobs have no level listed and are omitted. Pulled %s.</p>' % (''.join(out), lo, hi, BUILD_DATE)

def g_gear_band(arg, ctx):
    """gear table for class code within band; arg 'SHM,11,15,shaman' """
    parts = [p.strip() for p in arg.split(',')]
    code, lo, hi = parts[0], int(parts[1]), int(parts[2])
    weights = SHAMAN_W if code == 'SHM' else GENERIC_W
    cands = [(it, lv, k) for it, lv, k in easy_items(code if code != 'ALL' else None) if lv is not None and lv <= hi]
    best = {}
    for it, lv, k in cands:
        sc = item_score(it, weights)
        if sc <= 0: continue
        for s in slots_of(it):
            best.setdefault(s, []).append((sc, lv, it))
    rows = []
    for s in ARMOR_SLOTS + WEAPON_SLOTS:
        if s not in best: continue
        lst = sorted(best[s], key=lambda x: (-x[0], x[1]))
        seen = set(); n = 0
        for sc, lv, it in lst:
            if it['name'] in seen: continue
            seen.add(it['name']); n += 1
            rows.append(gear_row(it, lv, True, '<td class="num">%g</td>' % round(sc, 1)).replace('<td>%s</td>' % esc(', '.join(slots_of(it))), '<td>%s</td>' % esc(s), 1))
            if n >= (2 if code == 'SHM' else 1): break
    if not rows: return '<p class="dim">No sourced items for this band.</p>'
    return '<div class="tw"><table class="grid gear sortable">%s<tbody>%s</tbody></table></div>' % (
        GEAR_HEAD % '<th>Classes</th><th title="Simple stat score used to rank; see method">Score</th>', ''.join(rows))

def g_gear_family(arg, ctx):
    key = arg.strip()
    fam = [f for f in FAMILIES if f[0] == key][0]
    codes = fam[2]
    out = []
    for lo, hi in BANDS:
        cands = []
        for it, lv, k in easy_items():
            if lv is None or not (lo <= lv <= hi): continue
            cc = class_codes(it)
            if len(cc) == 18 or not any(c in cc for c in codes): continue
            if not any(s in ARMOR_SLOTS for s in slots_of(it)): continue
            if item_score(it, GENERIC_W) <= 0: continue
            cands.append((lv, it))
        cands.sort(key=lambda x: (ARMOR_SLOTS.index(slots_of(x[1])[0]) if slots_of(x[1])[0] in ARMOR_SLOTS else 99, -item_score(x[1], GENERIC_W)))
        if not cands: continue
        out.append('<h3 id="b%d">Levels %d–%d <span class="dim">(%d items)</span></h3><div class="tw"><table class="grid gear filt">%s<tbody>%s</tbody></table></div>' % (
            lo, lo, hi, len(cands), GEAR_HEAD % '<th>Classes</th>', ''.join(gear_row(it, lv) for lv, it in cands[:60])))
    return '\n'.join(out)

WEAPON_TYPES = None
def g_gear_weapons(arg, ctx):
    groups = {}
    for it, lv, k in easy_items():
        if lv is None: continue
        if not any(s in WEAPON_SLOTS for s in slots_of(it)): continue
        sk = it.get('skill') or ('Shield / off-hand' if slots_of(it) == ['Secondary'] else 'Other / unknown type')
        groups.setdefault(sk, []).append((lv, it))
    out = []
    for sk in sorted(groups):
        lst = sorted(groups[sk], key=lambda x: (x[0], -item_score(x[1], GENERIC_W)))
        out.append('<h3 id="%s">%s <span class="dim">(%d)</span></h3><div class="tw"><table class="grid gear filt">%s<tbody>%s</tbody></table></div>' % (
            slug(sk), esc(sk), len(lst), GEAR_HEAD % '<th>Classes</th>', ''.join(gear_row(it, lv) for lv, it in lst[:80])))
        ctx.setdefault('toc', []).append((slug(sk), sk))
    return '\n'.join(out)

def g_gear_allclass(arg, ctx):
    lo, hi = [int(x) for x in arg.split(',')]
    cands = [(lv, it) for it, lv, k in easy_items() if lv is not None and lo <= lv <= hi and len(class_codes(it)) == 18 and item_score(it, GENERIC_W) > 0]
    cands.sort(key=lambda x: (ARMOR_SLOTS.index(slots_of(x[1])[0]) if slots_of(x[1]) and slots_of(x[1])[0] in ARMOR_SLOTS else 99, -item_score(x[1], GENERIC_W)))
    if not cands: return '<p class="dim">None sourced.</p>'
    return '<div class="tw"><table class="grid gear">%s<tbody>%s</tbody></table></div>' % (GEAR_HEAD % '', ''.join(gear_row(it, lv, False) for lv, it in cands[:50]))

def g_gear_anylevel(arg, ctx):
    """vendor & crafted items (no level attached) usable by a class code (or ALL)."""
    code = arg.strip() or None
    rows = []
    for it, lv, kinds in easy_items(None if code in (None, 'ALL') else code):
        if lv is not None or not (kinds & {'vendor', 'crafted'}): continue
        if item_score(it, GENERIC_W) <= 0: continue
        rows.append(it)
    def ckey(it):
        c = it.get('crafted') or {}
        return (str((c.get('skill') or 'zz')), lvl_num(c.get('trivial')) or 999, it['name'])
    rows.sort(key=ckey)
    return '<div class="tw"><table class="grid gear filt">%s<tbody>%s</tbody></table></div><p class="src">%d items. Vendor- or player-crafted items have no level requirement in M&amp;M; crafted ones list the recipe trivial (skill level) from the wiki.</p>' % (
        GEAR_HEAD % '<th>Classes</th>', ''.join(gear_row(it, None) for it in rows[:400]), len(rows))

def g_crafted_sets(arg, ctx):
    out = []
    for name, S in sorted(SETS.items()):
        if not S['crafted'] or not S['rows']: continue
        rows = S['rows']
        cls = rows[0].get('class', '')
        trs = ''.join('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            esc(r.get('armor slot') or r.get('slot') or ''), item_link(r.get('name', '')) if r.get('name') in ITEMS else esc(r.get('name', '')),
            esc(r.get('ac', '')), esc(r.get('stats', '')), esc(r.get('vendor price', ''))) for r in rows)
        out.append('<details class="set"><summary><strong>%s</strong> <span class="dim">— %s</span></summary><div class="tw"><table class="grid"><thead><tr><th>Slot</th><th>Item</th><th>AC</th><th>Stats</th><th>Vendor price (wiki)</th></tr></thead><tbody>%s</tbody></table></div><p class="src"><a class="ext" target="_blank" rel="noopener" href="%s">wiki: %s</a> (edited %s)</p></details>' % (
            esc(name), esc(cls), trs, S['url'], esc(name), S['wiki_ts']))
    return '\n'.join(out)

def g_zone_table(arg, ctx):
    rows = []
    for z in sorted(ZONES, key=lambda z: (lvl_num(ZONES[z]['level'] or ZEXTRA.get(z, {}).get('level', '')) or 99, z)):
        Z = ZONES[z]; X = ZEXTRA.get(z, {})
        rows.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            zlink(z), esc(Z['level'] or 'not stated'), esc(X.get('region', '')), esc(Z.get('monster_types') or ''), ', '.join(zlink(a) for a in Z['adjacent'])))
    return '<div class="tw"><table class="grid sortable"><thead><tr><th>Zone</th><th>Wiki level</th><th>Region</th><th>Monsters</th><th>Connects to</th></tr></thead><tbody>%s</tbody></table></div>' % ''.join(rows)

def g_quests(arg, ctx):
    lo, hi = [int(x) for x in arg.split(',')[:2]] if arg else (0, 99)
    rows = []
    for q, Q in sorted(QUESTS.items(), key=lambda x: (lvl_num(x[1]['min_level']) or 0, x[0])):
        l = lvl_num(Q['min_level'])
        if l is None and arg: continue
        if l is not None and not (lo <= l <= hi): continue
        rew = ', '.join(item_link(r) if r in ITEMS else esc(r) for r in Q['rewards'][:5])
        rows.append('<tr><td><a class="ext" target="_blank" rel="noopener" href="%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            Q['url'], esc(q), esc(Q['min_level'] or '?'), zlink(Q['zone']) if Q['zone'] else '', esc(Q['giver'] or ''), esc(Q['classes'] or ''), rew))
    return '<div class="tw"><table class="grid sortable filt-text"><thead><tr><th>Quest</th><th>Min lvl</th><th>Zone</th><th>Giver</th><th>Classes</th><th>Rewards</th></tr></thead><tbody>%s</tbody></table></div><p class="src">%d quests from <a class="ext" target="_blank" rel="noopener" href="%sCategory:Quests">wiki Category:Quests</a>, pulled %s.</p>' % (''.join(rows), len(rows), WIKI, BUILD_DATE)

def g_merchants(arg, ctx):
    rows = []
    for m, M in sorted(MERCH.items()):
        rows.append('<tr><td><a class="ext" target="_blank" rel="noopener" href="%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            M['url'], esc(m), ', '.join(zlink(z) for z in M['zone'] if z), esc(M['location'] or ''), esc(', '.join(M['buys'])[:200]), esc(', '.join(M['sells'][:12]))[:300]))
    return '<div class="tw"><table class="grid sortable filt-text"><thead><tr><th>Merchant</th><th>Zone</th><th>Where</th><th>Buys</th><th>Sells (partial)</th></tr></thead><tbody>%s</tbody></table></div>' % ''.join(rows)

def g_tradeskills(arg, ctx):
    rows = []
    for t, T in sorted(TRADES.items()):
        nm = t.replace('Skill ', '')
        p = (T['paras'][0] if T['paras'] else '')[:240]
        rows.append('<tr><td><a class="ext" target="_blank" rel="noopener" href="%s">%s</a></td><td>%s</td><td>%s</td></tr>' % (T['url'], esc(nm), 'yes' if T['implemented'] else '<span class="badge unc">wiki: not fully implemented</span>', esc(p)))
    return '<div class="tw"><table class="grid sortable"><thead><tr><th>Skill</th><th>Implemented?</th><th>Wiki summary</th></tr></thead><tbody>%s</tbody></table></div>' % ''.join(rows)

def g_factions(arg, ctx):
    rows = []
    for t, F in sorted(FACTIONS.items()):
        p = ' '.join(F['paras'][:2])[:300]
        rows.append('<tr><td><a class="ext" target="_blank" rel="noopener" href="%s">%s</a></td><td>%s</td></tr>' % (F['url'], esc(t), esc(p) or '<span class="dim">stub on wiki</span>'))
    return '<div class="tw"><table class="grid sortable filt-text"><thead><tr><th>Faction</th><th>Wiki summary</th></tr></thead><tbody>%s</tbody></table></div>' % ''.join(rows)

def g_deepdive(arg, ctx):
    D = DD.get(slug(arg))
    if not D: return ''
    o = ['<div class="dd">']
    for p in D['overview']: o.append('<p>%s</p>' % esc(p))
    for s in D['sections']:
        if not s['entries'] and not s['paras']: continue
        o.append('<h4>%s</h4>' % esc(s['title']))
        for p in s['paras'][:2]: o.append('<p class="dim">%s</p>' % esc(p))
        if s['entries']:
            o.append('<ul class="ddl">%s</ul>' % ''.join('<li><strong>%s</strong>%s</li>' % (esc(e['name']), (' — ' + esc(e['desc'][:260])) if e['desc'] else '') for e in s['entries'][:14]))
    o.append('<p class="src">Official deep dive: <a class="ext" target="_blank" rel="noopener" href="%s">%s</a> (fetched %s). Deep dives describe design intent; check the wiki spell list and patch notes for what is live.</p></div>' % (D['url'], D['url'], BUILD_DATE))
    return ''.join(o)

def g_starterquests(arg, ctx):
    C = CLASSES[arg]; out = []
    for q in C.get('class_quests', []):
        Q = QUESTS.get(q)
        if Q:
            rew = ', '.join(item_link(r) if r in ITEMS else esc(r) for r in Q['rewards'][:5]) or 'see wiki'
            out.append('<li><a class="ext" target="_blank" rel="noopener" href="%s">%s</a> — %s, giver %s, min lvl %s. Rewards: %s</li>' % (Q['url'], esc(q), zlink(Q['zone']) if Q['zone'] else '?', esc(Q['giver'] or '?'), esc(Q['min_level'] or '?'), rew))
        else:
            out.append('<li><a class="ext" target="_blank" rel="noopener" href="%s">%s</a></li>' % (wiki(q), esc(q)))
    return '<ul>%s</ul>' % ''.join(out) if out else '<p class="dim">No class quests listed on the wiki.</p>'

def g_maps(arg, ctx):
    z = arg; Z = ZONES[z]
    out = []
    order = ZEXTRA.get(z, {}).get('maps') or Z['images']
    for im in order:
        key = im.replace('_', ' ')
        I = IMAGES.get(key)
        if not I: continue
        shot = key in SCREENSHOTS
        out.append('<figure class="map%s"><a href="%s" target="_blank"><img src="%s" alt="%s" loading="lazy"></a><figcaption>%s <strong>%s</strong> — by %s (uploaded %s). <a class="ext" target="_blank" rel="noopener" href="%s">source &amp; full size</a>, CC BY-SA 4.0 via M&amp;M Wiki. Click image to open the larger copy.</figcaption></figure>' % (
            ' shot' if shot else '', '/' + I['file'], '/' + I['file'], esc(key), 'Screenshot' if shot else 'Map', esc(key), esc(I['author'] or 'wiki user'), esc(I['uploaded']), I['source']))
    return '<div class="maps">%s</div>' % ''.join(out) if out else '<p class="call unconfirmed">No map image on the wiki for this zone yet.</p>'

SCREENSHOTS = {'256 Infested Crypt.png','Ailvorith.jpg','Clan Grimtide.png','Deep Dunes screenshot.png','Entrance to Ancient Crypt.png','Evershade Weald.png','Faelindral.png','Glass flats.png','Glinting hollow pinecone.png','Fallen Watch.png','Graincellarentrance.png','Keepers Bight.png','Night Harbor Sewers Entrance.png','NightHarbor1.jpg','Screenshot 2025-08-20 201810.png','Screenshot 20260327 202004.png','Shaded Dunes.png','Shallow shoals.png','Sungreetstrand.png','Telekir.png','Vale of Zintar.png','Wyrmsbane.png','UDcitadel1.jpg'}

def g_image(arg, ctx):
    I = IMAGES.get(arg)
    if not I: return ''
    return '<figure class="map"><a href="/%s" target="_blank"><img src="/%s" alt="%s" loading="lazy"></a><figcaption>%s — by %s, <a class="ext" target="_blank" rel="noopener" href="%s">source</a>, CC BY-SA 4.0 via M&amp;M Wiki.</figcaption></figure>' % (I['file'], I['file'], esc(arg), esc(arg), esc(I['author']), I['source'])

def g_classgrid(arg, ctx):
    cards = []
    for c in CLASS_LIST:
        n = CLASS_NOTES.get(c, {})
        cards.append('<a class="card cls-%s" href="%s"><span class="ct">%s</span><span class="cr">%s</span><span class="ca">%s</span></a>' % (
            slug(c), class_url(c), esc(c), esc(n.get('role', '')), esc(n.get('armor', ''))))
    return '<div class="cards">%s</div>' % ''.join(cards)

def g_zonegrid(arg, ctx):
    cards = []
    for z in sorted(ZONES, key=lambda z: (lvl_num(ZONES[z]['level'] or '') or 99, z)):
        Z = ZONES[z]; th = None
        for im in (ZEXTRA.get(z, {}).get('maps') or Z['images']):
            I = IMAGES.get(im.replace('_', ' '))
            if I and im.replace('_', ' ') not in SCREENSHOTS: th = I['thumb']; break
        cards.append('<a class="card zone" href="%s">%s<span class="ct">%s</span><span class="cr">Lvl %s</span><span class="ca">%s</span></a>' % (
            zone_url(z), ('<img src="/%s" alt="" loading="lazy">' % th) if th else '<span class="noimg">no map yet</span>', esc(z), esc(Z['level'] or '?'), esc(ZEXTRA.get(z, {}).get('region', ''))))
    return '<div class="cards zones">%s</div>' % ''.join(cards)

def g_classfilter(arg, ctx):
    opts = ''.join('<option value="%s"%s>%s</option>' % (CABBR[c], ' selected' if CABBR[c] == arg.strip() else '', c) for c in CLASS_LIST)
    return '<div class="filterbar"><label>Show items usable by <select class="clsfilter"><option value="">any class</option>%s</select></label> <label><input type="checkbox" class="kindfilter" value="named"> hide named drops</label> <input type="search" class="textfilter" placeholder="filter rows…"></div>' % opts

def g_families(arg, ctx):
    rows = ''.join('<tr><td><a href="/gear/%s.html">%s</a></td><td>%s</td><td><a class="ext" target="_blank" rel="noopener" href="%s">%s</a></td></tr>' % (k, esc(t), ', '.join(clink(ABBR[c]) for c in codes), wiki(src), esc(src)) for k, t, codes, src in FAMILIES)
    return '<div class="tw"><table class="grid"><thead><tr><th>Family</th><th>Classes</th><th>Wiki basis</th></tr></thead><tbody>%s</tbody></table></div>' % rows

GENS = {k[2:]: v for k, v in globals().items() if k.startswith('g_')}


# ------------------------------------------------------------------ level-range quick info
RANGE_ORDER = ['1-5', '6-10', '11-15', '16-20', '21-25', '26-30', '31-40', '41-60']
RANGE_DEFAULT = '11-15'
RANGES_CACHE = {}

def load_ranges():
    """Compile content/ranges/*.md into HTML panels for embedding in range-data.js (no fetch; works on file://)."""
    out = {}
    rdir = os.path.join(CONTENT, 'ranges')
    for key in RANGE_ORDER:
        fp = os.path.join(rdir, key + '.md')
        if not os.path.exists(fp):
            out[key] = {'label': key.replace('-', '\u2013'), 'html': '<p><span class="badge unc">unverified</span> No quick-info file for this band yet.</p>', 'title': key}
            continue
        raw = open(fp, encoding='utf8').read()
        meta, body = {}, raw
        if raw.startswith('---'):
            parts = raw.split('---', 2)
            if len(parts) >= 3:
                for line in parts[1].splitlines():
                    if ':' in line:
                        k, v = line.split(':', 1)
                        meta[k.strip()] = v.strip()
                body = parts[2]
        ctx = {}
        html_body = md(body, ctx)
        label = meta.get('label') or key.replace('-', '\u2013')
        out[key] = {'label': label, 'html': html_body, 'title': meta.get('title') or ('Quick info ' + label)}
    return out

def write_range_data(ranges):
    panels = {}
    for cls in CLASS_LIST:
        for key in RANGE_ORDER:
            lo, hi = [int(x) for x in key.split('-')]
            sh = ranges[key]['html'] if cls == 'Shaman' else None
            panels[cls + '|' + key] = class_quick(cls, lo, hi, sh)
    payload = {
        'order': RANGE_ORDER, 'default': RANGE_DEFAULT, 'classes': CLASS_LIST, 'defaultClass': 'Fighter',
        'labels': {k: ranges[k]['label'] for k in RANGE_ORDER},
        'urls': {c: class_url(c) for c in CLASS_LIST},
        'panels': panels,
    }
    js = 'window.MNM_QUICK=' + json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + ';'
    open(os.path.join(OUT, 'assets', 'quick-data.js'), 'w', encoding='utf8').write(js)
    meta = {'order': RANGE_ORDER, 'default': RANGE_DEFAULT, 'classes': CLASS_LIST, 'defaultClass': 'Fighter',
            'labels': {k: ranges[k]['label'] for k in RANGE_ORDER}, 'urls': {c: class_url(c) for c in CLASS_LIST}, 'codes': CABBR}
    open(os.path.join(OUT, 'assets', 'range-data.js'), 'w', encoding='utf8').write('window.MNM_RANGES=' + json.dumps(meta, separators=(',', ':')) + ';')
    return panels

# ------------------------------------------------------------------ per-class quick info (generated for every class x band)
OFFICIAL = J('official_classes')
LARGE_RACES = ('Ogre', 'Troll')
BAND_LIST = [tuple(int(x) for x in k.split('-')) for k in RANGE_ORDER]
ROLE_PARTNERS = {
    # STRATEGY: duo partner by role gap (tank needs heals, healer needs a tank/pet, dps needs a tank or healer)
    'tank': ['Cleric', 'Shaman', 'Druid'],
    'healer': ['Shadow Knight', 'Fighter', 'Paladin', 'Necromancer', 'Beastmaster'],
    'pet': ['Cleric', 'Shaman', 'Druid'],
    'dps': ['Fighter', 'Shadow Knight', 'Paladin', 'Shaman'],
    'support': ['Shadow Knight', 'Fighter', 'Necromancer', 'Beastmaster'],
}
def _strip(s): return re.sub(r'<[^>]+>', '', s or '')
def class_glance(cls):
    O = OFFICIAL.get(cls, {}); n = CLASS_NOTES.get(cls, {}); C = CLASSES[cls]
    races = [r.strip() for r in (O.get('races') or '').split(',') if r.strip()]
    rec = [r for r in races if r not in LARGE_RACES]
    rows = [('Archetype', esc(O.get('archetype') or 'UNVERIFIED')), ('Roles', esc(O.get('roles') or 'UNVERIFIED')),
            ('Armor', esc(n.get('armor', 'UNVERIFIED'))), ('Weapons', esc(n.get('weapons', 'UNVERIFIED'))),
            ('Races (official)', esc(', '.join(races) or 'UNVERIFIED')),
            ('Class stat modifier', esc(C.get('modifier') or 'not stated on wiki')),
            ('Main stat', esc(n.get('stat', 'UNVERIFIED')))]
    h = '<div class="qi-sec"><h3>Class at a glance <span class="badge fact">fact</span></h3><table class="kv">%s</table>' % ''.join(
        '<tr><th>%s</th><td>%s</td></tr>' % (k, v.replace('UNCONFIRMED', '<span class="badge unc">unverified</span>').replace('UNVERIFIED', '<span class="badge unc">unverified</span>')) for k, v in rows)
    if C.get('bonus_advice'):
        h += '<details><summary>Bonus-point advice (wiki)</summary><p>%s</p></details>' % esc(C['bonus_advice'])
    if rec and len(rec) != len(races):
        h += '<p class="dim"><span class="badge strat">strategy</span> Race picks this guide suggests: %s (large races left out).</p>' % esc(', '.join(rec))
    return h + '</div>'

def class_spells_band(cls, lo, hi):
    C = CLASSES[cls]; li = []
    for s in sorted(C['spells'], key=lambda s: s.get('level') or 0):
        lv = s.get('level') or 0
        if lo <= lv <= hi:
            nm = s.get('spell name') or s.get('ability name') or s.get('name') or ''
            d = (s.get('spell description') or s.get('description') or '').strip()
            if len(d) > 110: d = d[:107].rsplit(' ', 1)[0] + '…'
            loc = s.get('location') or ''
            li.append('<li><b>L%s %s</b>%s%s</li>' % (lv, esc(nm), (' <span class="dim">(%s)</span>' % esc(loc)) if loc else '', (' — ' + esc(d)) if d else ''))
    body = '<ul class="tight">%s</ul>' % ''.join(li) if li else '<p class="dim"><span class="badge unc">unverified</span> The wiki lists no %s spells/abilities for levels %d–%d.</p>' % (esc(cls), lo, hi)
    return '<div class="qi-sec"><h3>Spells &amp; abilities %d–%d <span class="badge fact">fact</span></h3>%s<p class="src">Wiki <a class="ext" target="_blank" rel="noopener" href="%s">%s</a> rev %s. Wiki levels can lag patches.</p></div>' % (lo, hi, body, C['url'], esc(cls), esc(C.get('revid')))

def _best_by_slot(code, cap, floor, weights):
    best = {}
    for it, lv, k in easy_items(code):
        if lv is None or lv > cap or lv < floor: continue
        if len(class_codes(it)) == 18 and not any(s in ('Ear', 'Neck', 'Finger', 'Back', 'Wrist', 'Waist') for s in slots_of(it)): continue
        sc = item_score(it, weights)
        if sc <= 0: continue
        for s in slots_of(it):
            if s in ('Ammo', 'Shirt'): continue
            cur = best.get(s)
            if not cur or (sc, lv) > (cur[0], cur[1]): best[s] = (sc, lv, it)
    return best

def class_gear_band(cls, lo, hi):
    code = CABBR[cls]
    weights = SHAMAN_W if code == 'SHM' else GENERIC_W
    now = _best_by_slot(code, lo, max(1, lo - 12), weights)
    end = _best_by_slot(code, hi, max(1, lo - 12), weights) if hi > lo else {}
    def fmt(t):
        _, lv, it = t; acq = acquisitions(it)
        return '%s <span class="dim">(lvl %s)</span> — %s' % (item_link(it['name']), esc(lv), acq[0][2] if acq else '')
    li = []
    for s in ARMOR_SLOTS + WEAPON_SLOTS:
        a, b = now.get(s), end.get(s)
        if not a and not b: continue
        if a and b and a[2]['name'] != b[2]['name']:
            li.append('<li><b>%s:</b> %s<br><span class="up">by %d →</span> %s</li>' % (esc(s), fmt(a), hi, fmt(b)))
        elif a:
            li.append('<li><b>%s:</b> %s</li>' % (esc(s), fmt(a)))
        else:
            li.append('<li><b>%s:</b> <span class="up">from lvl %s →</span> %s</li>' % (esc(s), esc(b[1]), fmt(b)))
    body = '<ul class="tight gearlist">%s</ul>' % ''.join(li) if li else '<p class="dim"><span class="badge unc">unverified</span> No wiki-sourced %s items with a known level for this band. Check the <a href="/gear/index.html">gear pages</a>.</p>' % esc(cls)
    return ('<div class="qi-sec"><h3>Gear to equip %d–%d <span class="badge fact">items: fact</span> <span class="badge strat">pick: strategy</span></h3>'
            '<p class="dim">What to wear per slot when you enter the band, and the upgrade to grab by level %d. Items and sources are from the wiki (quest, vendor, craft or drop — no auction needed). Hover an item for its stats.</p>%s</div>') % (lo, hi, hi, body)

def zones_band(lo, hi):
    zs = sorted(zones_for_band(lo, hi), key=lambda x: -len(x[1]))[:7]
    if not zs: return '<div class="qi-sec"><h3>Where to level</h3><p class="dim">No wiki mob rows with levels in this band.</p></div>'
    li = ''.join('<li>%s <span class="dim">(zone lvl %s; %d listed camps in band)</span></li>' % (zlink(z), esc(ZONES[z]['level'] or '?'), len(c)) for z, c in zs)
    return '<div class="qi-sec"><h3>Where to level %d–%d <span class="badge fact">fact</span></h3><ul class="tight">%s</ul><p class="src">Zones whose wiki mob tables overlap the band. Full camp lists: <a href="/leveling.html">Leveling by band</a>.</p></div>' % (lo, hi, li)

def class_role_keys(cls):
    r = (OFFICIAL.get(cls, {}).get('roles') or '').lower()
    keys = []
    for k in ('tank', 'healer', 'pet', 'support'):
        if k in r: keys.append(k)
    if 'dps' in r and not keys: keys.append('dps')
    return keys or ['dps']

def class_tips(cls):
    O = OFFICIAL.get(cls, {}); n = CLASS_NOTES.get(cls, {})
    h = '<div class="qi-sec"><h3>Tips</h3>'
    if O.get('traits'):
        h += '<p><span class="badge fact">fact</span> Official class page — defining traits:</p><ul class="tight">%s</ul>' % ''.join('<li>%s</li>' % esc(t) for t in O['traits'])
    if O.get('changing'):
        h += '<details><summary>What the devs say is changing</summary>%s%s%s</details>' % (
            ''.join('<p>%s</p>' % esc(p) for p in O['changing']),
            ('<p><b>More:</b> %s</p>' % esc('; '.join(O['more']))) if O.get('more') else '',
            ('<p><b>Less:</b> %s</p>' % esc('; '.join(O['less']))) if O.get('less') else '')
    for k, lab in (('solo', 'Solo'), ('group', 'Group')):
        v = n.get(k)
        if v and 'UNCONFIRMED' not in v:
            h += '<p><b>%s:</b> %s</p>' % (lab, esc(v))
    partners = []
    for k in class_role_keys(cls):
        for p in ROLE_PARTNERS[k]:
            if p != cls and p not in partners: partners.append(p)
    h += '<p><span class="badge strat">strategy</span> <b>Duo partners:</b> %s — chosen to cover what %s lacks (%s).</p>' % (
        ', '.join('<a href="%s">%s</a>' % (class_url(p), esc(p)) for p in partners[:4]), esc(cls), esc(O.get('roles') or 'role unverified'))
    h += '<p><a href="%s">Full %s guide →</a></p>' % (class_url(cls), esc(cls))
    return h + '</div>'

def class_quick(cls, lo, hi, shaman_html=None):
    parts = [class_glance(cls)]
    if shaman_html is not None:
        parts.append('<div class="qi-sec">%s</div>' % shaman_html)
        parts.append(class_gear_band(cls, lo, hi))
    else:
        parts += [class_spells_band(cls, lo, hi), class_gear_band(cls, lo, hi), zones_band(lo, hi)]
    parts.append(class_tips(cls))
    return ''.join(parts)

def g_classbands(arg, ctx):
    cls = arg.strip(); out = [class_glance(cls)]
    for key in RANGE_ORDER:
        lo, hi = [int(x) for x in key.split('-')]
        out.append('<h3 id="band-%s">Levels %d–%d</h3>' % (key, lo, hi) + class_spells_band(cls, lo, hi) + class_gear_band(cls, lo, hi) + zones_band(lo, hi))
    out.append(class_tips(cls))
    return ''.join(out)

def g_classquick(arg, ctx):
    cls, lo, hi = [a.strip() for a in arg.split(',')]
    return class_quick(cls, int(lo), int(hi))
# ------------------------------------------------------------------ dungeons section
DUNGEONS = json.load(open(os.path.join(CONTENT, 'dungeons.json'), encoding='utf8'))
DUNGEON_ORDER = ['Tomb of the Last Wyrmsbane', 'Infested Crypt', 'Ancient Crypt', 'Sunken Resort', 'Grain Cellar', 'Caves of Irem', 'Glinting Hollow', 'Grimtide Sanctum', 'Blind Midden']
def dungeon_url(d): return '/dungeons/%s.html' % slug(d)

def _lvl_range(d):
    Z = ZONES[d]; m = re.findall(r'\d+', Z.get('level') or '')
    mobs = []
    for e in Z['npcs'] + Z['named']:
        for x in re.findall(r'\d+', e.get('level') or ''):
            if 1 <= int(x) <= 60: mobs.append(int(x))
    if m:
        lo = int(m[0]); hi = int(m[1]) if len(m) > 1 else max([lo] + mobs)
        return lo, hi, 'wiki zone level: %s' % Z['level']
    if mobs: return min(mobs), max(mobs), 'from wiki mob levels (zone level not stated)'
    return None, None, 'not stated on the wiki'

def _legend(d):
    L = ' '.join(ZONES[d].get('legend') or [])
    if not L.strip() or len(L) < 8: return [], []
    rooms, feats = (L.split('___') + [''])[:2]
    r = re.findall(r'(\d+)\.\s*(.*?)(?=\s+\d+\.\s|$)', rooms.strip())
    f = re.findall(r'\b([A-Z])\.\s*(.*?)(?=\s+[A-Z]\.\s|$)', feats.strip())
    return [(a, b.strip()) for a, b in r if b.strip()], [(a, b.strip()) for a, b in f if b.strip()]

def _areas(d):
    """group sourced NPC location strings into top-level areas (floors/regions)"""
    out = {}
    for e in ZONES[d]['npcs'] + ZONES[d]['named']:
        loc = (e.get('location') or '').strip()
        if loc in ('', '-', 'Location') or loc.lower().startswith('give '): continue
        top = re.split(r'[,.]', loc)[0].replace('(Presumed) ', '').strip()
        sub = loc[len(top):].strip(' ,.') if loc.startswith(top) else loc
        out.setdefault(top, set())
        if sub: out[top].add(sub[:60])
    return out

def _wrap(t, n):
    words, lines, cur = t.split(), [], ''
    for w in words:
        if len(cur) + len(w) + 1 > n and cur: lines.append(cur); cur = w
        else: cur = (cur + ' ' + w).strip()
    if cur: lines.append(cur)
    return lines[:3]

def dungeon_svg(d):
    """Own schematic: boxes for sourced landmarks only. Not to scale; links between boxes are not sourced unless stated."""
    rooms, feats = _legend(d)
    W = 440; y = 34; parts = []
    def box(x, y, w, h, label, sub, cls):
        ls = _wrap(label, int(w / 6.6))
        t = ''.join('<tspan x="%d" dy="%d">%s</tspan>' % (x + 6, 14 if i == 0 else 13, esc(l)) for i, l in enumerate(ls))
        return '<g class="%s"><rect x="%d" y="%d" width="%d" height="%d" rx="5"/><text x="%d" y="%d">%s</text>%s</g>' % (
            cls, x, y, w, h, x + 6, y + 2, t, ('<text class="sm" x="%d" y="%d">%s</text>' % (x + 6, y + h - 6, esc(sub))) if sub else '')
    adj = ZONES[d]['adjacent']
    parts.append(box(10, y, W - 20, 30, 'Entrance / zone lines: ' + (', '.join(adj) or 'not stated'), '', 'ent')); y += 42
    if rooms or feats:
        parts.append('<text class="hd" x="10" y="%d">Numbered rooms (wiki map key)</text>' % (y + 4)); y += 12
        cw = (W - 30) // 2
        for i, (n, t) in enumerate(rooms):
            x = 10 + (i % 2) * (cw + 10)
            parts.append(box(x, y, cw, 46, '%s. %s' % (n, t), '', 'room'))
            if i % 2 == 1 or i == len(rooms) - 1: y += 54
        if feats:
            parts.append('<text class="hd" x="10" y="%d">Features (wiki map key)</text>' % (y + 4)); y += 12
            for i, (n, t) in enumerate(feats):
                x = 10 + (i % 2) * (cw + 10)
                cls = 'trap' if 'trap' in t.lower() else 'feat'
                parts.append(box(x, y, cw, 46, '%s. %s' % (n, t), '', cls))
                if i % 2 == 1 or i == len(feats) - 1: y += 54
        note = 'Key diagram from the wiki map legend. Positions and links are not to scale or sourced.'
    else:
        areas = _areas(d)
        if not areas: return ''
        def fl(k):
            m = re.match(r'(\d+)', k); return (0, -int(m.group(1))) if m else (1, k)
        keys = sorted(areas, key=fl) if any(re.match(r'\d', k) for k in areas) else sorted(areas, key=lambda k: (not k.lower().startswith('top'), k))
        stacked = any(re.match(r'\d|top floor|basement', k, re.I) for k in keys)
        for k in keys:
            subs = sorted(areas[k])[:4]
            h = 30 + 13 * len(subs)
            g = box(10, y, W - 20, h, k, '', 'floor' if stacked else 'room')
            g += ''.join('<text class="sm" x="22" y="%d">· %s</text>' % (y + 30 + 13 * i, esc(s[:62])) for i, s in enumerate(subs))
            parts.append(g); y += h + 8
        note = ('Floors stacked top to bottom as named in wiki NPC locations.' if stacked else 'Areas named in wiki NPC locations; arrangement is not sourced.') + ' Not to scale.'
    y += 4
    parts.append('<text class="sm" x="10" y="%d">%s</text>' % (y + 8, esc(note)))
    H = y + 18
    return ('<figure class="dmap"><svg viewBox="0 0 %d %d" role="img" aria-label="%s schematic" xmlns="http://www.w3.org/2000/svg">'
            '<text class="hd" x="10" y="20">%s — schematic</text>%s</svg><figcaption>Original schematic drawn for this site from wiki text (CC BY-SA 4.0). '
            'Not a copy of any map image.</figcaption></figure>') % (W, H, esc(d), esc(d), ''.join(parts))

def _loot_cells(e):
    items = [x.strip() for x in (e.get('loot') or '').split(',') if x.strip() and x.strip() != '-']
    return items

def dungeon_loot(d):
    rows = []
    for e in ZONES[d]['named']:
        if e['name'] in ('Raid Named', 'Example Item'): continue
        items = _loot_cells(e)
        if not items: continue
        codes = set()
        for x in items:
            if x in ITEMS: codes |= set(class_codes(ITEMS[x]))
        loc = e.get('location') if e.get('location') not in (None, '-', 'Location') else ''
        rows.append('<tr data-c="%s"><td><b>%s</b>%s</td><td>%s</td><td>%s</td></tr>' % (
            ' '.join(sorted(codes)), esc(e['name']), ('<br><span class="dim">%s</span>' % esc(loc)) if loc else '', esc(e.get('level') if e.get('level') not in ('-', None) else '?'),
            ', '.join(item_link(x) if x in ITEMS else esc(x) for x in items)))
    if not rows: return '<p class="dim"><span class="badge unc">unverified</span> No loot listed on the wiki.</p>'
    return ('<p class="dim">Rows with gear your selected class can use are highlighted (class picker in the top bar). Hover an item for stats.</p>'
            '<div class="tw"><table class="grid sortable dloot"><thead><tr><th>Named (where)</th><th>Lvl</th><th>Known loot (wiki)</th></tr></thead><tbody>%s</tbody></table></div>') % ''.join(rows)

def dungeon_camps(d):
    rows = [e for e in ZONES[d]['npcs'] if lvl_num(e.get('level')) is not None and e['name'] != 'Example Item']
    if not rows: return '<p class="dim"><span class="badge unc">unverified</span> No mob levels on the wiki.</p>'
    rows.sort(key=lambda e: lvl_num(e['level']))
    return '<ul class="tight">%s</ul>' % ''.join('<li><b>%s</b> (lvl %s)%s</li>' % (esc(e['name']), esc(e['level']), (' — ' + esc(e['location'])) if e.get('location') not in (None, '-', 'Location') else '') for e in rows[:30])

def dungeon_page(d):
    Z = ZONES[d]; X = DUNGEONS.get(d, {}); lo, hi, lsrc = _lvl_range(d)
    def lab(s):
        s = esc(s)
        for k, c in (('FACT', 'fact'), ('STRATEGY', 'strat'), ('UNVERIFIED', 'unc')):
            s = s.replace(k + ' ', '<span class="badge %s">%s</span> ' % (c, k.lower()), 1) if s.startswith(k) else s
        return s
    rooms, feats = _legend(d)
    o = ['<div class="dhead" data-lo="%s" data-hi="%s"><table class="kv"><tr><th>Levels</th><td>%s <span class="dim">(%s)</span></td></tr><tr><th>Connects to</th><td>%s</td></tr><tr><th>Named listed</th><td>%d</td></tr></table></div>' % (
        lo or '', hi or '', ('%s–%s' % (lo, hi)) if lo else '<span class="badge unc">unverified</span>', esc(lsrc), ', '.join(zlink(a) for a in Z['adjacent']) or '—', len([e for e in Z['named'] if e['name'] not in ('Raid Named', 'Example Item')]))]
    o.append('<div class="call note"><p class="dim" style="margin:0">Zone page with full mob table and wiki maps: %s</p></div>' % zlink(d))
    o.append('<h2 id="map">Map</h2>' + (dungeon_svg(d) or '<p class="dim">No sourced layout to draw.</p>'))
    o.append('<h2 id="access">Getting in <span class="badge fact">fact</span></h2><ul class="tight">%s</ul>' % ''.join('<li>%s</li>' % lab(a) for a in X.get('access', [])))
    dirs = []
    for n, t in rooms: dirs.append('<li><b>%s</b> — map key %s</li>' % (esc(t), n))
    for n, t in feats: dirs.append('<li>%s <span class="dim">(key %s)</span></li>' % (esc(t), n))
    locs = [(e['name'], e['location']) for e in Z['named'] + Z['npcs'] if e.get('location') not in (None, '-', 'Location', '') and not e['location'].lower().startswith('give ')]
    for nm, l in locs[:25]: dirs.append('<li><b>%s</b>: %s</li>' % (esc(nm), esc(l)))
    if Z.get('travel') and d == 'Glinting Hollow':
        dirs += ['<li>%s</li>' % esc(t) for t in Z['travel']]
    o.append('<h2 id="directions">Directions to key camps <span class="badge fact">fact</span></h2>%s' % (('<ul class="tight">%s</ul><p class="src">From the wiki map legend and NPC location column. Where the wiki gives no location, none is shown.</p>' % ''.join(dirs)) if dirs else '<p class="dim"><span class="badge unc">unverified</span> The wiki gives no camp locations for this dungeon.</p>'))
    o.append('<h2 id="loot">Notable loot <span class="badge fact">fact</span></h2>' + dungeon_loot(d))
    o.append('<h2 id="camps">Mobs by level <span class="badge fact">fact</span></h2>' + dungeon_camps(d))
    o.append('<h2 id="special">Special info</h2><ul class="tight">%s</ul>' % ''.join('<li>%s</li>' % lab(s) for s in X.get('special', [])))
    if X.get('tips'):
        o.append('<h2 id="tips">Pathing and pull tips <span class="badge strat">strategy</span></h2><ul class="tight">%s</ul>' % ''.join('<li>%s</li>' % lab(s) for s in X['tips']))
    src = ['Wiki: %s (rev %s)|%s' % (d, Z.get('revid'), Z['url'])] + X.get('sources', [])
    ctx = {'toc': [('map', 'Map'), ('access', 'Getting in'), ('directions', 'Directions'), ('loot', 'Loot'), ('camps', 'Mobs'), ('special', 'Special'), ('tips', 'Tips')]}
    return ''.join(o), src, ctx

def dungeon_index():
    cards = []
    for d in DUNGEON_ORDER:
        lo, hi, _ = _lvl_range(d)
        nm = [e['name'] for e in ZONES[d]['named'] if e['name'] not in ('Raid Named', 'Example Item')]
        cards.append('<div class="dcard" data-lo="%s" data-hi="%s"><h3><a href="%s">%s</a> <span class="dim">%s</span></h3><p>%s</p><p class="dim">%d named · %s</p></div>' % (
            lo or '', hi or '', dungeon_url(d), esc(d), ('%s–%s' % (lo, hi)) if lo else 'levels unverified', esc((ZONES[d].get('intro') or '')[:160]), len(nm), esc(', '.join(nm[:4]))))
    return ('<p>Dungeons with sourced info, sorted by level. Cards that overlap your level range (top bar) are highlighted. <span class="badge fact">fact</span> = wiki or patch notes; <span class="badge strat">strategy</span> = advice; <span class="badge unc">unverified</span> = not confirmed.</p>'
            '<div class="dcards">%s</div>'
            '<h2 id="gaps">Not covered</h2><ul class="tight"><li><b>The Hidden Grotto</b> (Shallow Shoals, underwater): the wiki page only has placeholder rows. <span class="badge unc">unverified</span></li>'
            '<li><b>Night Harbor Sewers</b>: the wiki says the sewers are closed (dev-confirmed during closed beta, April 2026) with no return date.</li></ul>') % ''.join(cards)


# ------------------------------------------------------------------ patch notes digest
PSUM = json.load(open(os.path.join(CONTENT, 'patch_summaries.json'), encoding='utf8')) if os.path.exists(os.path.join(CONTENT, 'patch_summaries.json')) else {}
PATCHES = json.load(open(os.path.join(DATA, 'patches.json'), encoding='utf8')) if os.path.exists(os.path.join(DATA, 'patches.json')) else []
SYSTEMS = [('PvP', r'\bpvp\b'), ('UI', r'\bui\b|hotbar|window|tooltip|chat'), ('Tradeskills', r'tradeskill|crafting|smith|tailor|carpent|brew|fletch|jewel|enchanting|harvest|mining|lumber|fishing'),
           ('Housing', r'housing|\bhouse\b|plot'), ('Items', r'\bitems?\b|loot|drop'), ('Quests', r'\bquests?\b'), ('Combat', r'threat|aggro|damage|\bheal|resist|\bmana\b|combat'),
           ('Factions', r'faction'), ('Travel', r'boat|zone ?line|portal|teleport|lift|mount'), ('Economy', r'economy|merchant|vendor|price|coin'),
           ('Art & sound', r'\bart\b|animation|lighting|vfx|sound|music'), ('Encounters', r'encounter|named|raid|boss'), ('Characters', r'character|race|creation')]
def _cls_re(c):
    return re.compile(r'\b%s(s)?\b' % re.escape(c).replace('\\ ', '[ -]?'), re.I)
CLS_RES = None
def patch_tags(p):
    global CLS_RES
    if CLS_RES is None: CLS_RES = [(c, _cls_re(c)) for c in CLASS_LIST]
    blob = ' '.join([sec['h'] + ' ' + ' '.join(sec['items']) for sec in p['sections']])
    cl = [c for c, r in CLS_RES if r.search(blob)]
    zn = [z for z in sorted(ZONES) if re.search(re.escape(z).replace("\\'", "'?"), blob, re.I)]
    sy = [n for n, r in SYSTEMS if re.search(r, blob, re.I)]
    return cl, zn, sy
def patches_page():
    o = ['<p>Every official patch, newest first. The change lists are the official text, grouped as published <span class="badge fact">fact</span>. The one-line digest and the tags are worked out automatically from that text by keyword, so a tag can miss or over-match <span class="badge unc">unverified</span>. Our own plain-English summaries, written only from the official wording, cover the latest 10 patches and are marked <span class="badge strat">summary</span>. Patches that mention your selected class (top bar) are highlighted. Use "Filter this page" for a zone, system or spell name.</p>',
         '<p class="dim">Patch note pages missing from the official site (numbers %s) are not listed.</p>' % ', '.join(str(n) for n in sorted(set(range(1, PATCHES[0]['n'])) - {x['n'] for x in PATCHES})) if PATCHES else '']
    for p in PATCHES:
        cl, zn, sy = patch_tags(p)
        nitems = sum(len(x['items']) for x in p['sections'])
        big = sorted(p['sections'], key=lambda x: -len(x['items']))[:3]
        dig = '%d change%s, mostly %s.' % (nitems, '' if nitems == 1 else 's', ', '.join('%s (%d)' % (x['h'].strip('* '), len(x['items'])) for x in big))
        tags = ''.join('<a class="tag tcls" href="%s">%s</a>' % (class_url(c), esc(c)) for c in cl) + ''.join('<a class="tag tzone" href="%s">%s</a>' % (zone_url(z), esc(z)) for z in zn) + ''.join('<span class="tag tsys">%s</span>' % esc(x) for x in sy)
        secs = ''.join('<h4>%s</h4><ul class="tight">%s</ul>' % (esc(x['h'].strip('* ')), ''.join('<li>%s</li>' % esc(i) for i in x['items'])) for x in p['sections'])
        o.append('<details class="patch" id="p%d" data-cls="%s"><summary><b>%s</b> <span class="dim">%s</span><br>%s<span class="pdig">%s</span><span class="ptags">%s</span></summary>%s<p class="dim"><a class="ext" target="_blank" rel="noopener" href="%s">Official patch note</a></p></details>' % (
            p['n'], esc('|'.join(cl)), esc(p['title']), esc(p['date']), ('<span class="psum"><span class="badge strat">summary</span> %s</span>' % esc(PSUM[str(p['n'])])) if str(p['n']) in PSUM else '', esc(dig), tags, secs, esc(p['url'])))
    return ''.join(o)
# ------------------------------------------------------------------ spell lookup
def spells_page():
    rows = []
    for c in CLASS_LIST:
        page = '/shaman/spells.html' if c == 'Shaman' else class_url(c)
        for sp in CLASSES[c]['spells']:
            nm = sp.get('spell name')
            if not nm: continue
            lv = sp.get('level') or 0
            u = page + ('#lvl-%s' % lv if c == 'Shaman' else '')
            rows.append((c, lv, nm, '<tr data-cls="%s" data-lo="%s" data-hi="%s"><td><strong>%s</strong></td><td>%s</td><td><a href="%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                esc(c), lv, lv, esc(nm), lv or '?', u, esc(c), esc(sp.get('spell description') or ''), esc(sp.get('mana') or ''), esc(sp.get('location') or ''))))
    rows.sort(key=lambda r: (r[1] or 0, r[0], r[2]))
    return ('<p>All %d class spells and abilities listed on the class pages of the community wiki <span class="badge fact">fact</span>, sorted by level. Rows for your selected class are outlined; rows in your level range are marked. Tick "Only my class" to hide the rest, and use "Filter this page" to search by name or effect. The class link opens that class\'s quick reference. Levels and costs can lag behind patches <span class="badge unc">unverified</span>; check the patch digest for recent changes.</p>'
            '<p class="sptools"><label><input type="checkbox" id="sp-mine"> Only my class</label> <label><input type="checkbox" id="sp-band"> Only my level range</label></p>'
            '<div class="tw"><table class="grid sortable spelllook"><thead><tr><th>Spell / ability</th><th>Lvl</th><th>Class</th><th>Description (wiki)</th><th>Mana</th><th>Source</th></tr></thead><tbody>%s</tbody></table></div>'
            '<script>(function(){var m=document.getElementById("sp-mine"),b=document.getElementById("sp-band");function go(){document.querySelectorAll("table.spelllook tbody tr").forEach(function(r){r.classList.toggle("sphide",(m.checked&&!r.classList.contains("clsok"))||(b.checked&&!r.classList.contains("inband")));});}'
            '[m,b].forEach(function(e){e.addEventListener("change",go)});document.getElementById("mnm-class").addEventListener("change",function(){setTimeout(go,0)});document.getElementById("mnm-range").addEventListener("change",function(){setTimeout(go,0)});})();</script>') % (len(rows), ''.join(r[3] for r in rows))

GENS.update(classquick=g_classquick, classbands=g_classbands)
# ------------------------------------------------------------------ zone guide finder + dangers
def _zone_named_sorted(Z):
    return sorted([e for e in Z['named'] if e['name'] not in ('Raid Named', 'Example Item')], key=lambda e: lvl_num(e['level']) or 0)
def zone_dangers(z):
    Z = ZONES[z]; lo, hi, src = _lvl_range(z); out = []
    nm = [e for e in _zone_named_sorted(Z) if lvl_num(e['level'])]
    if nm:
        top = nm[-3:][::-1]
        out.append('<li><span class="badge fact">fact</span> Highest-level named on the wiki list: %s.</li>' % ', '.join('%s (%s)' % (esc(e['name']), esc(e['level'])) for e in top))
    if Z.get('monster_types'): out.append('<li><span class="badge fact">fact</span> Monster types (wiki): %s.</li>' % esc(Z['monster_types']))
    if lo and hi and hi - lo >= 15:
        out.append('<li><span class="badge strat">strategy</span> The zone spans levels %s–%s, so higher mobs share the map with low ones; check con colors before pulling near the named above.</li>' % (lo, hi))
    if not out: out.append('<li><span class="badge unc">unverified</span> No danger info on the wiki page yet.</li>')
    return '<h2 id="dangers">Dangers</h2><ul class="tight">%s</ul>' % ''.join(out)
def zone_travel(z):
    Z = ZONES[z]; t = [x.strip(' ;') for x in Z.get('travel', []) if x.strip(' ;')]
    if not t: return ''
    return '<h2 id="travel-wiki">Travel (wiki)</h2><ul class="tight">%s</ul><p class="dim"><span class="badge fact">fact</span> Listed in the wiki zone infobox; boat and portal stops are as written there.</p>' % ''.join('<li>%s</li>' % (zlink(x) if x in ZONES else esc(x)) for x in t)
def g_zoneguide(arg, ctx):
    rows = []
    for z in sorted(ZONES, key=lambda z: (_lvl_range(z)[0] or 99, z)):
        Z = ZONES[z]; lo, hi, src = _lvl_range(z)
        nm = [e for e in _zone_named_sorted(Z) if lvl_num(e['level'])]
        lv = esc(Z['level']) if Z['level'] else ('%s–%s <span class="badge unc">from mob levels</span>' % (lo, hi) if lo else '<span class="badge unc">unknown</span>')
        rows.append('<tr data-lo="%s" data-hi="%s"><td><a href="%s"><strong>%s</strong></a><br><span class="dim">%s</span></td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            lo or '', hi or '', zone_url(z), esc(z), esc(ZEXTRA.get(z, {}).get('type', '')), lv, ', '.join(zlink(a) for a in Z['adjacent']) or '—',
            esc(', '.join('%s (%s)' % (e['name'], e['level']) for e in nm[:4])) or '—'))
    return ('<h2 id="zone-finder">Zone finder</h2><p><span class="badge fact">fact</span> Level, connections and named camps from each wiki zone page. Rows overlapping your level range (top bar) are outlined. Open a zone for its full named list, dangers, travel and map.</p>'
            '<div class="tw"><table class="grid sortable zfind"><thead><tr><th>Zone</th><th>Levels</th><th>Connects to</th><th>Named camps (lvl)</th></tr></thead><tbody>%s</tbody></table></div>') % ''.join(rows)
GENS['zoneguide'] = g_zoneguide


RANGEBAR_HTML = (
    '<div class="rangebar" id="mnm-rangebar">'
    '<div class="rangebar-in">'
    '<label class="rb-f"><span class="range-lab">Class</span><select id="mnm-class" aria-label="Class"></select></label>'
    '<label class="rb-f"><span class="range-lab">Levels</span><select id="mnm-range" aria-label="Level range"></select></label>'
    '<a class="range-qi" id="mnm-range-qi" href="/index.html#mnm-quickinfo">Quick info</a>'
    '<input id="mnm-filter" class="pagefilter" type="search" placeholder="Filter this page…" aria-label="Filter this page">'
    '</div></div>'
)

# ------------------------------------------------------------------ layout
NAV = [('Home', '/index.html', 'home'), ('Classes', '/classes/index.html', 'classes'), ('Shaman', '/shaman/index.html', 'shaman'),
       ('Gear', '/gear/index.html', 'gear'), ('Dungeons', '/dungeons/index.html', 'dungeons'), ('Spells', '/spells.html', 'spells'), ('Zones', '/zones/index.html', 'zones'), ('Leveling', '/leveling.html', 'leveling'),
       ('Farming', '/farming.html', 'farming'), ('Economy', '/economy.html', 'economy'), ('Tradeskills', '/tradeskills.html', 'tradeskills'),
       ('Factions', '/factions.html', 'factions'), ('Quests', '/quests.html', 'quests'), ('Patches', '/patches.html', 'patches'), ('Changelog', '/changelog.html', 'changelog')]

def left_nav(section):
    def ul(title, items):
        return '<div class="box nav"><h3>%s</h3><ul>%s</ul></div>' % (esc(title), ''.join('<li><a href="%s">%s</a></li>' % (u, esc(t)) for t, u in items))
    if section == 'shaman':
        return ul('Shaman', SHAMAN_NAV) + ul('Other classes', [(c, class_url(c)) for c in CLASS_LIST if c != 'Shaman'])
    if section == 'classes':
        return ul('Classes', [(c, class_url(c)) for c in CLASS_LIST])
    if section == 'gear':
        return ul('Gear', GEAR_NAV)
    if section == 'dungeons':
        return ul('Dungeons', [('All dungeons', '/dungeons/index.html')] + [(d, dungeon_url(d)) for d in DUNGEON_ORDER])
    if section == 'zones':
        return ul('Zones', [('All zones & world map', '/zones/index.html')] + [(z, zone_url(z)) for z in sorted(ZONES)])
    return ul('Classes', [(c, class_url(c)) for c in CLASS_LIST]) + ul('Reference', [('Gear by level', '/gear/index.html'), ('Zones', '/zones/index.html'), ('Quests', '/quests.html'), ('Sources', '/sources.html')])

SHAMAN_NAV = [('Overview', '/shaman/index.html'), ('Spells by level', '/shaman/spells.html'), ('Leveling', '/shaman/leveling.html'),
              ('Gear (easy BiS)', '/gear/shaman.html'), ('Playbook: solo, group, hotbar', '/shaman/playbook.html'), ('Quests', '/shaman/quests.html'), ('Gathering route', '/shaman/tradeskills.html'), ('Mats for crafters', '/shaman/guild-mats.html'), ('Quick info by band', '/shaman/quickinfo.html')]
GEAR_NAV = [('Gear overview', '/gear/index.html'), ('Shaman easy BiS', '/gear/shaman.html'), ('Cloth casters', '/gear/cloth.html'), ('Leather wearers', '/gear/leather.html'),
            ('Chain hybrids', '/gear/chain.html'), ('Plate tanks & healers', '/gear/plate.html'), ('Weapons & shields', '/gear/weapons.html'),
            ('All-class jewelry & cloaks', '/gear/all-class.html'), ('Vendor & crafted (any level)', '/gear/vendor-crafted.html'), ('Crafted armor sets', '/gear/crafted-sets.html')]

TEMPLATE = '''<!doctype html>
<html lang="en" data-root="{root}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive">
<title>{title} — {site}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="{root}assets/site.css">
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
</head>
<body class="sec-{section}">
<header class="top">
  <div class="topin">
    <a class="logo" href="{root}index.html"><span class="sig">&#x2735;</span> <span class="lt">{site}</span><span class="ls">Monsters &amp; Memories · Early Access</span></a>
    <form class="search" onsubmit="return false" role="search"><input id="q" type="search" placeholder="Search spells, zones, items, camps…" autocomplete="off" aria-label="Search"><div id="qres" class="qres" hidden></div></form>
    <button class="burger" aria-label="Menu" onclick="document.body.classList.toggle('navopen')">&#9776;</button>
  </div>
  <nav class="mainnav">{nav}</nav>
  {rangebar}
</header>
<div class="crumbs">{crumbs}<span class="ver">Content verified: {verified}</span></div>
<div class="wrap">
  <aside class="left">{left}</aside>
  <main class="main"><h1>{h1}</h1>{body}
  {sources}
  </main>
  <aside class="right">{facts}{toc}<div class="box"><h3>Legend</h3><p><span class="badge unc">unconfirmed</span> / <span class="badge unc">unverified</span> not verified in a source<br><span class="badge fact">fact</span> from a cited source<br><span class="badge strat">strategy</span> a recommendation, not a game fact<br><span class="itm q-magic">Magic item</span> hover for wiki stats</p></div></aside>
</div>
<footer class="foot">Community quick reference · built {built} · Facts from the <a href="https://monstersandmemories.miraheze.org/" target="_blank" rel="noopener">M&amp;M Wiki</a> (CC BY-SA 4.0) and <a href="https://monstersandmemories.com/" target="_blank" rel="noopener">monstersandmemories.com</a>. Not affiliated with the Monsters &amp; Memories developers. · <a href="{root}sources.html">Sources</a></footer>
<div id="tip" class="tip" hidden></div>
<script src="{root}assets/search-index.js"></script>
<script src="{root}assets/item-tips.js"></script>
<script src="{root}assets/range-data.js"></script>{quickjs}
<script src="{root}assets/site.js"></script>
</body>
</html>
'''

def relink(htmls, depth):
    root = '../' * depth
    def fix(m):
        attr, url = m.group(1), m.group(2)
        return '%s="%s%s"' % (attr, root, url[1:])
    return re.sub(r'(href|src)="(/(?!/)[^"]*)"', fix, htmls)

def add_page(path, title, body_md=None, section='home', meta=None, body_html=None, h1=None, sources=None, verified=None, desc=None):
    ctx = {}
    body = body_html if body_html is not None else md(body_md, ctx)
    PAGES.append(dict(path=path, title=title, section=section, body=body, ctx=ctx, meta=meta or {}, h1=h1 or title,
                      sources=sources, verified=verified or (meta or {}).get('verified') or BUILD_DATE, desc=desc or title))

def crumbs_for(p):
    parts = p['path'].split('/')
    c = ['<a href="/index.html">Home</a>']
    sec = {'shaman': ('Shaman', '/shaman/index.html'), 'classes': ('Classes', '/classes/index.html'), 'gear': ('Gear', '/gear/index.html'), 'zones': ('Zones', '/zones/index.html'), 'dungeons': ('Dungeons', '/dungeons/index.html')}
    if len(parts) > 1 and parts[0] in sec and parts[1] != 'index.html':
        c.append('<a href="%s">%s</a>' % (sec[parts[0]][1], sec[parts[0]][0]))
    if p['path'] != 'index.html': c.append('<span>%s</span>' % esc(p['title']))
    return ' › '.join(c)

def render_all():
    if os.path.exists(OUT):
        for f in os.listdir(OUT):
            if f in ('img',): continue
            fp = os.path.join(OUT, f)
            shutil.rmtree(fp) if os.path.isdir(fp) else os.remove(fp)
    os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
    for f in glob.glob(os.path.join(ROOT, 'static', '*')):
        shutil.copy(f, os.path.join(OUT, 'assets'))
    RANGES_CACHE = load_ranges()
    PANELS = write_range_data(RANGES_CACHE)
    index = []
    for p in PAGES:
        depth = p['path'].count('/')
        root = '../' * depth
        nav = ''.join('<a href="%s"%s>%s</a>' % (u, ' class="on"' if k == p['section'] else '', t) for t, u, k in NAV)
        toc = p['ctx'].get('toc') or []
        toch = '<div class="box toc"><h3>On this page</h3><ul>%s</ul></div>' % ''.join('<li><a href="#%s">%s</a></li>' % (a, esc(t)) for a, t in toc) if len(toc) > 1 else ''
        src = ''
        srcs = p['sources'] or [s.strip() for s in p['meta'].get('sources', '').split(';') if s.strip()]
        if srcs:
            lis = []
            for s in srcs:
                if '|' in s:
                    t, u = s.split('|', 1); lis.append('<li><a class="ext" target="_blank" rel="noopener" href="%s">%s</a></li>' % (esc(u.strip()), esc(t.strip())))
                else:
                    lis.append('<li>%s</li>' % inline(s))
            src = '<section class="sources"><h2 id="sources">Sources for this page</h2><ul>%s</ul></section>' % ''.join(lis)
        rb = RANGEBAR_HTML
        body_html = p['body']
        if 'id="mnm-quickinfo"' in body_html:
            dk = 'Fighter|' + RANGE_DEFAULT
            body_html = body_html.replace(
                '<div id="mnm-quickinfo" class="quickinfo" data-mnm-quick="full"></div>',
                '<div id="mnm-quickinfo" class="quickinfo" data-mnm-quick="full"><div class="qi-head"><h2 style="margin-top:0">Quick info · Fighter · %s</h2><p class="dim">Pick your class and level range in the bar at the top (remembered in this browser).</p></div>%s</div>' % (
                    esc(RANGES_CACHE[RANGE_DEFAULT]['label']), PANELS[dk]))
        h = TEMPLATE.format(root=root, title=esc(p['title']), site=esc(SITE_NAME), desc=esc(p['desc']), section=p['section'], nav=nav,
                            crumbs=crumbs_for(p), verified=esc(p['verified']), left=left_nav(p['section']), h1=inline(p['h1']), body=body_html,
                            sources=src, facts=p['ctx'].get('facts', ''), toc=toch, built=BUILD_DATE, rangebar=rb,
                            quickjs=('<script src="{0}assets/quick-data.js"></script>'.format(root) if 'id="mnm-quickinfo"' in body_html else ''))
        h = relink(h, depth)
        fp = os.path.join(OUT, p['path']); os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, 'w', encoding='utf8').write(h)
        # search index entries
        txt = re.sub(r'<[^>]+>', ' ', p['body']); txt = html.unescape(re.sub(r'\s+', ' ', txt))
        index.append({'t': p['title'], 'u': p['path'], 's': p['section'], 'x': txt[:6000]})
        for hid, ht in re.findall(r'<h[23] id="([^"]+)">(.*?)</h[23]>', p['body']):
            index.append({'t': re.sub('<[^>]+>', '', html.unescape(ht)), 'u': p['path'] + '#' + hid, 's': p['title'], 'x': ''})
    # spells and items into search
    for cname, C in CLASSES.items():
        page = 'shaman/spells.html' if cname == 'Shaman' else class_url(cname).lstrip('/')
        for sp in C['spells']:
            nm = sp.get('spell name') or sp.get('ability name') or sp.get('name')
            if not nm: continue
            lv = sp.get('level') or 0
            index.append({'t': nm, 'u': page + ('#lvl-%s' % lv if cname == 'Shaman' else ''), 's': '%s spell · L%s' % (cname, lv), 'x': (sp.get('spell description') or sp.get('description') or '')[:200]})
    for nm, it in ITEMS.items():
        if not it.get('slot'): continue
        index.append({'t': nm, 'u': it['url'], 'e': 1, 's': 'item · ' + (it.get('slot') or ''), 'x': stat_str(it)[:160] if stat_str(it) else ''})
    open(os.path.join(OUT, 'assets', 'search-index.js'), 'w', encoding='utf8').write('window.MNM_INDEX=' + json.dumps(index, ensure_ascii=False, separators=(',', ':')) + ';')
    tips = {}
    for n in USED_ITEMS:
        it = ITEMS[n]
        flags = ' '.join(x for x in ('MAGIC' if it.get('magic') else '', 'LORE' if it.get('lore') else '', 'NO DROP' if it.get('nodrop') else '') if x)
        acq = [re.sub('<[^>]+>', '', d) for _, _, d in acquisitions(it)][:4]
        tips[n] = [it['name'], flags, ', '.join(slots_of(it)), stat_str(it), classes_short(it).replace('<span class="badge unc">', '').replace('</span>', ''), it.get('weight') or '', acq, it.get('wiki_ts')]
    open(os.path.join(OUT, 'assets', 'item-tips.js'), 'w', encoding='utf8').write('window.MNM_ITEMS=' + json.dumps(tips, ensure_ascii=False, separators=(',', ':')) + ';')
    open(os.path.join(OUT, 'robots.txt'), 'w').write('User-agent: *\nDisallow: /\n')
    open(os.path.join(OUT, '.nojekyll'), 'w').write('')
    print('pages', len(PAGES), 'items w/ tips', len(tips), 'index', len(index))

# ------------------------------------------------------------------ content assembly
def build_content():
    # hand-written markdown pages
    for f in sorted(glob.glob(os.path.join(CONTENT, '**', '*.md'), recursive=True)):
        rel = os.path.relpath(f, CONTENT).replace('\\', '/')
        if rel.startswith('_') or rel.startswith('ranges/') or rel.startswith('ranges\\'): continue
        meta, t = read_md(f)
        path = rel[:-3] + '.html'
        add_page(path, meta.get('title', rel), t, meta.get('section', path.split('/')[0] if '/' in path else 'home'), meta, desc=meta.get('desc'))
    # generated class pages (all except shaman which is hand-written)
    tpl = open(os.path.join(CONTENT, '_class_template.md'), encoding='utf8').read()
    for c in CLASS_LIST:
        if c == 'Shaman': continue
        n = CLASS_NOTES.get(c, {})
        t = tpl
        extra = n.get('extra_md', '')
        rep = {'CLASS': c, 'CODE': CABBR[c], 'SLUG': slug(c), 'ROLE': n.get('role', 'UNCONFIRMED'), 'ARMOR': n.get('armor', 'UNCONFIRMED'),
               'WEAPONS': n.get('weapons', 'UNCONFIRMED'), 'STAT': n.get('stat', 'UNCONFIRMED'), 'EXTRA': extra, 'SOLO': n.get('solo', 'UNCONFIRMED'),
               'GROUP': n.get('group', 'UNCONFIRMED'), 'ROUTE': n.get('route', ''), 'FAMILY': n.get('family', ''), 'WIKIURL': CLASSES[c]['url'],
               'DDURL': DD.get(slug(c), {}).get('url', ''), 'MOD': CLASSES[c].get('modifier') or 'UNCONFIRMED', 'BONUS': CLASSES[c].get('bonus_advice') or 'Not stated on the wiki.',
               'DESC': CLASSES[c].get('description', '')[:900], 'OFFURL': 'https://monstersandmemories.com/class-' + slug(c)}
        for k, v in rep.items(): t = t.replace('%%' + k + '%%', v)
        meta, body = read_md_text(t)
        add_page('classes/%s.html' % slug(c), c, body, 'classes', meta, desc='%s class guide' % c)
    # dungeon pages
    add_page('dungeons/index.html', 'Dungeons', body_html=dungeon_index(), section='dungeons', sources=['Wiki: Category:Dungeons|%sCategory:Dungeons' % WIKI], desc='Dungeon guides')
    for d in DUNGEON_ORDER:
        b, src, cx = dungeon_page(d)
        add_page(dungeon_url(d).lstrip('/'), d, body_html=b, section='dungeons', sources=src, desc='%s dungeon guide' % d)
        PAGES[-1]['ctx'].update(cx)
    add_page('patches.html', 'Patch notes digest', body_html=patches_page(), section='patches', sources=['Official patch notes|https://account.monstersandmemories.com/community/patch_notes'], desc='Patch notes digest')
    add_page('spells.html', 'Spell lookup', body_html=spells_page(), section='spells', sources=['Wiki class pages (spell tables)|%sCategory:Classes' % WIKI], desc='Spell lookup by class and level')
    # zone pages
    ztpl = open(os.path.join(CONTENT, '_zone_template.md'), encoding='utf8').read()
    for z, Z in ZONES.items():
        X = ZEXTRA.get(z, {})
        body = zone_page(z, Z, X)
        add_page('zones/%s.html' % slug(z), z, body_html=body[0], section='zones', sources=body[1], desc='%s zone guide' % z)
        PAGES[-1]['ctx'].update(body[2])

def read_md_text(t):
    meta = {}
    if t.startswith('---'):
        _, fm, t = t.split('---', 2)
        for l in fm.strip().split('\n'):
            if ':' in l:
                k, v = l.split(':', 1); meta[k.strip()] = v.strip()
    return meta, t

def zone_page(z, Z, X):
    ctx = {}
    facts = [('Wiki level', esc(Z['level'] or 'not stated')), ('Region', esc(X.get('region', 'UNCONFIRMED'))),
             ('Type', esc(X.get('type', '—'))), ('Monsters', esc(Z.get('monster_types') or '—')),
             ('Connects to', ', '.join(zlink(a) for a in Z['adjacent']) or '—'), ('Named listed', str(len(Z['named']))), ('Quests listed', str(len(Z['quests'])))]
    ctx['facts'] = '<div class="box facts"><h3>Quick Facts</h3><table>%s</table></div>' % ''.join('<tr><th>%s</th><td>%s</td></tr>' % (k, inline(v) if 'UNCONFIRMED' in v else v) for k, v in facts)
    toc = [('overview', 'Overview'), ('map', 'Map')]
    o = ['<p class="lead">%s</p>' % esc(Z.get('intro') or '')]
    if X.get('notes'):
        o.append(md(X['notes'], ctx))
    o.append('<h2 id="map">Map</h2>')
    o.append(g_maps(z, ctx))
    if Z.get('legend'):
        o.append('<div class="call note"><div class="call-t">Map legend (from the wiki map box)</div><p>%s</p></div>' % esc(' '.join(Z['legend']))[:3000])
    if Z['named']:
        toc.append(('named', 'Named mobs'))
        o.append('<h2 id="named">Named mobs</h2><div class="tw"><table class="grid sortable filt-text"><thead><tr><th>Named</th><th>Lvl</th><th>Race / class</th><th>Where</th><th>Known loot (hover)</th></tr></thead><tbody>%s</tbody></table></div>' % ''.join(
            '<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (esc(e['name']), esc(e['level'] or '?'), esc(' / '.join(x for x in (e.get('race'), e.get('class')) if x and x != '-')), esc(e.get('location') or ''),
            ', '.join(item_link(x.strip()) if x.strip() in ITEMS else esc(x.strip()) for x in (e.get('loot') or '').split(',') if x.strip() and x.strip() != '-')) for e in sorted(Z['named'], key=lambda e: lvl_num(e['level']) or 99)))
    if Z['npcs']:
        toc.append(('mobs', 'Mobs & NPCs'))
        rows = sorted(Z['npcs'], key=lambda e: (lvl_num(e['level']) is None, lvl_num(e['level']) or 0, e['name']))
        o.append('<h2 id="mobs">Mobs &amp; NPCs (camps by level)</h2><p class="dim">Rows with a level are huntable camps; rows without are usually town NPCs or not yet documented.</p><div class="tw"><table class="grid sortable filt-text"><thead><tr><th>Name</th><th>Lvl</th><th>Race</th><th>Class</th><th>Where</th><th>Notes</th></tr></thead><tbody>%s</tbody></table></div>' % ''.join(
            '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (esc(e['name']), esc(e['level'] or ''), esc(e.get('race') or ''), esc(e.get('class') or ''), esc(e.get('location') or ''), esc(' '.join(x for x in (e.get('desc'), e.get('loot')) if x and x != '-'))) for e in rows))
    if Z['quests']:
        toc.append(('quests', 'Quests'))
        o.append('<h2 id="quests">Quests</h2><div class="tw"><table class="grid"><thead><tr><th>Quest</th><th>Reward</th><th>Giver</th><th>Min lvl</th></tr></thead><tbody>%s</tbody></table></div>' % ''.join(
            '<tr><td><a class="ext" target="_blank" rel="noopener" href="%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td></tr>' % (wiki(q['name']), esc(q['name']), ', '.join(item_link(x.strip()) if x.strip() in ITEMS else esc(x.strip()) for x in (q.get('reward') or '').split(',') if x.strip()), esc(q.get('giver') or ''), esc(q.get('min_level') or '')) for q in Z['quests']))
    # farmable gear list: items that drop here
    drops = [it for it in ITEMS.values() if any(d.get('zone') == z for d in it.get('drops', []))]
    if drops:
        toc.append(('drops', 'Drops worth farming'))
        drops.sort(key=lambda it: (item_level(it) or 99))
        o.append('<h2 id="drops">Gear that drops here</h2><div class="tw"><table class="grid gear sortable filt-text">%s<tbody>%s</tbody></table></div>' % (GEAR_HEAD % '<th>Classes</th>', ''.join(gear_row(it, item_level(it)) for it in drops[:120])))
    if Z.get('merchants'):
        toc.append(('merchants', 'Merchants'))
        o.append('<h2 id="merchants">Merchants (wiki list)</h2><div class="tw"><table class="grid filt-text"><thead><tr><th>Where</th><th>Merchant</th></tr></thead><tbody>%s</tbody></table></div>' % ''.join('<tr><td>%s</td><td>%s</td></tr>' % (esc(m['location']), esc(m['merchant'])) for m in Z['merchants']))
    toc.append(('dangers', 'Dangers')); o.append(zone_dangers(z))
    if Z.get('travel'): toc.append(('travel-wiki', 'Travel')); o.append(zone_travel(z))
    if Z.get('travel') or Z['adjacent']:
        toc.append(('travel', 'Connections'))
        o.append('<h2 id="travel">Connections</h2><ul>%s</ul>' % ''.join('<li>%s</li>' % zlink(a) for a in (Z['adjacent'] or Z.get('travel', []))))
    ctx['toc'] = toc
    o.insert(0, '<span id="overview"></span>')
    src = ['Wiki: %s (rev %s)|%s' % (z, Z.get('revid'), Z['url']), 'Item data: individual wiki item pages (hover any item)|%sCategory:Items' % WIKI]
    src += X.get('sources', [])
    return ''.join(o), src, ctx

# ------------------------------------------------------------------ module plugins (modules/*.py extend the build)
for _mf in sorted(glob.glob(os.path.join(ROOT, 'modules', '*.py'))):
    exec(compile(open(_mf, encoding='utf8').read(), _mf, 'exec'), globals())

if __name__ == '__main__':
    build_content()
    render_all()

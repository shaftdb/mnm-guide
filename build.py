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
SITE_NAME = "Brew's M&M Codex"
BUILD_DATE = datetime.date.today().isoformat()

def J(name):
    return json.load(open(os.path.join(DATA, name + '.json'), encoding='utf8'))

ZONES = J('zones'); ITEMS = J('items'); QUESTS = J('quests'); MERCH = J('merchants')
CLASSES = J('classes'); DD = J('deepdives'); IMAGES = J('images'); SETS = J('armor_sets')
FACTIONS = J('factions'); TRADES = J('tradeskills')
PROFILE = json.load(open(os.path.join(CONTENT, 'profile.json'), encoding='utf8'))
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
    payload = {
        'order': RANGE_ORDER,
        'default': RANGE_DEFAULT,
        'character': 'Brewsham',
        'panels': {k: {'label': v['label'], 'title': v.get('title', v['label']), 'html': v['html']} for k, v in ranges.items()},
    }
    js = 'window.MNM_RANGES=' + json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + ';'
    open(os.path.join(OUT, 'assets', 'range-data.js'), 'w', encoding='utf8').write(js)

RANGEBAR_HTML = (
    '<div class="rangebar" id="mnm-rangebar" hidden>'
    '<div class="rangebar-in">'
    '<span class="range-lab">Brewsham band</span>'
    '<select id="mnm-range" aria-label="Brewsham Shaman level range"></select>'
    '<a class="range-qi" id="mnm-range-qi" href="#">Quick info</a>'
    '<span class="range-hint">Remembers your last pick in this browser</span>'
    '</div></div>'
)

# ------------------------------------------------------------------ layout
NAV = [('Home', '/index.html', 'home'), ('Shaman', '/shaman/index.html', 'shaman'), ('Classes', '/classes/index.html', 'classes'),
       ('Gear', '/gear/index.html', 'gear'), ('Zones', '/zones/index.html', 'zones'), ('Leveling', '/leveling.html', 'leveling'),
       ('Farming', '/farming.html', 'farming'), ('Economy', '/economy.html', 'economy'), ('Tradeskills', '/tradeskills.html', 'tradeskills'),
       ('Factions', '/factions.html', 'factions'), ('Quests', '/quests.html', 'quests'), ('Changelog', '/changelog.html', 'changelog')]

def left_nav(section):
    def ul(title, items):
        return '<div class="box nav"><h3>%s</h3><ul>%s</ul></div>' % (esc(title), ''.join('<li><a href="%s">%s</a></li>' % (u, esc(t)) for t, u in items))
    if section == 'shaman':
        return ul('Shaman', SHAMAN_NAV) + ul('My characters', [('Shadow Knight (Goblin)', '/classes/shadow-knight.html')])
    if section == 'classes':
        return ul('Classes', [(c, class_url(c)) for c in CLASS_LIST])
    if section == 'gear':
        return ul('Gear', GEAR_NAV)
    if section == 'zones':
        return ul('Zones', [('All zones & world map', '/zones/index.html')] + [(z, zone_url(z)) for z in sorted(ZONES)])
    return ul('Shaman quick links', SHAMAN_NAV) + ul('Reference', [('Gear by level', '/gear/index.html'), ('Zones', '/zones/index.html'), ('Quests', '/quests.html'), ('Sources', '/sources.html')])

SHAMAN_NAV = [('Overview', '/shaman/index.html'), ('Spells by level', '/shaman/spells.html'), ('Leveling', '/shaman/leveling.html'),
              ('Gear (easy BiS)', '/gear/shaman.html'), ('Playbook: solo, group, hotbar', '/shaman/playbook.html'), ('Quests', '/shaman/quests.html'), ('Gathering (no craft)', '/shaman/tradeskills.html'), ('Mats for guild crafters', '/shaman/guild-mats.html'), ('Quick info by band', '/shaman/quickinfo.html')]
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
  <aside class="right">{facts}{toc}<div class="box"><h3>Legend</h3><p><span class="badge unc">unconfirmed</span> / <span class="badge unc">unverified</span> not verified in a source<br><span class="badge strat">strategy</span> my recommendation, not a game fact<br><span class="itm q-magic">Magic item</span> hover for wiki stats</p></div></aside>
</div>
<footer class="foot">Private reference for Brewologist · built {built} · Facts from the <a href="https://monstersandmemories.miraheze.org/" target="_blank" rel="noopener">M&amp;M Wiki</a> (CC BY-SA 4.0) and <a href="https://monstersandmemories.com/" target="_blank" rel="noopener">monstersandmemories.com</a>. Not affiliated with the Monsters &amp; Memories developers. · <a href="{root}sources.html">Sources</a></footer>
<div id="tip" class="tip" hidden></div>
<script src="{root}assets/search-index.js"></script>
<script src="{root}assets/item-tips.js"></script>
<script src="{root}assets/range-data.js"></script>
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
    sec = {'shaman': ('Shaman', '/shaman/index.html'), 'classes': ('Classes', '/classes/index.html'), 'gear': ('Gear', '/gear/index.html'), 'zones': ('Zones', '/zones/index.html')}
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
    write_range_data(RANGES_CACHE)
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
        show_range = p['section'] in ('home', 'shaman')
        rb = RANGEBAR_HTML if show_range else ''
        body_html = p['body']
        if show_range and 'id="mnm-quickinfo"' in body_html and RANGE_DEFAULT in RANGES_CACHE:
            seed = RANGES_CACHE[RANGE_DEFAULT]['html']
            body_html = body_html.replace(
                '<div id="mnm-quickinfo" class="quickinfo" data-mnm-quick="full"></div>',
                '<div id="mnm-quickinfo" class="quickinfo" data-mnm-quick="full" data-seed="%s"><div class="qi-head"><h2 style="margin-top:0">Quick info · %s</h2><p class="dim" style="margin:.2em 0 .8em">Default band — change anytime in the header selector.</p></div>%s</div>' % (
                    RANGE_DEFAULT, esc(RANGES_CACHE[RANGE_DEFAULT]['label']), seed))
        h = TEMPLATE.format(root=root, title=esc(p['title']), site=esc(SITE_NAME), desc=esc(p['desc']), section=p['section'], nav=nav,
                            crumbs=crumbs_for(p), verified=esc(p['verified']), left=left_nav(p['section']), h1=inline(p['h1']), body=body_html,
                            sources=src, facts=p['ctx'].get('facts', ''), toc=toch, built=BUILD_DATE, rangebar=rb)
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
               'DESC': CLASSES[c].get('description', '')[:900]}
        for k, v in rep.items(): t = t.replace('%%' + k + '%%', v)
        meta, body = read_md_text(t)
        add_page('classes/%s.html' % slug(c), c, body, 'classes', meta, desc='%s class guide' % c)
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
    if Z.get('travel') or Z['adjacent']:
        toc.append(('travel', 'Connections'))
        o.append('<h2 id="travel">Connections</h2><ul>%s</ul>' % ''.join('<li>%s</li>' % zlink(a) for a in (Z['adjacent'] or Z.get('travel', []))))
    ctx['toc'] = toc
    o.insert(0, '<span id="overview"></span>')
    src = ['Wiki: %s (rev %s)|%s' % (z, Z.get('revid'), Z['url']), 'Item data: individual wiki item pages (hover any item)|%sCategory:Items' % WIKI]
    src += X.get('sources', [])
    return ''.join(o), src, ctx

if __name__ == '__main__':
    build_content()
    render_all()

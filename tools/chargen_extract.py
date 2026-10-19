#!/usr/bin/env python3
"""Build data/chargen/races.json from cached wiki pages (run tools/wikifetch.py first):
  "Starting City by Race, Class, and Deity", race pages (Human, Deep Elf, ...), Template:Traits.
Only values written on those pages are kept; '??' / 'unknown' stay as null."""
import json, os, re
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RAW = os.path.join(ROOT, 'raw', 'wiki')
WIKI = 'https://monstersandmemories.miraheze.org/wiki/'
def page(t): return json.load(open(os.path.join(RAW, t.replace('/', '_') + '.json'), encoding='utf8'))
def unlink(s): return re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]', r'\1', s).strip()
CITY = {'AV': "Ail'Vorith", 'FA': 'Faelindral', 'NH': 'Night Harbor', 'UD': 'Underdocks'}
STATS = ['STR', 'STA', 'DEX', 'AGI', 'INT', 'WIS', 'CHA']
RACES = ['Deep Elf', 'Deep Gnome', 'Dwarf', 'Gnome', 'Goblin', 'Halfling', 'Human', 'Ogre', 'Wood Elf', 'Deep Dwarf', 'High Elf', 'Troll']
LARGE = ['Ogre', 'Troll']

# ---- start-city table
P = page('Starting City by Race, Class, and Deity')
head = None; combos = {}
for line in P['text'].split('\n'):
    if line.startswith('!'): head = [h.strip() for h in line[1:].split('!!')]
    elif line.startswith('| [['):
        c = [x.strip() for x in line[1:].split('||')]
        race, cls = unlink(c[0]), unlink(c[1])
        for deity, cell in zip(head[2:], c[2:]):
            for ab in re.findall(r'\b(AV|FA|NH|UD)\b', cell):
                combos.setdefault(race, {}).setdefault(cls, {}).setdefault(CITY[ab], []).append(deity)

def basic(t, key):
    m = re.search(r"\*<b>%s[^<]*:</b>\s*(.*)" % key, t)
    return unlink(m.group(1)) if m else None
def stat_tables(t):
    base, start = None, {}
    i = t.find('==Base Stats=='); j = t.find('==Starting Stats==')
    if i >= 0:
        nums = re.findall(r'<td align="center" >\s*([0-9?]+)\s*</td>', t[i:j if j > i else i + 2000])
        if len(nums) >= 7: base = dict(zip(STATS, [int(x) if x.isdigit() else None for x in nums[:7]]))
    if j >= 0:
        for row in re.findall(r'<tr[^>]*>(.*?)</tr>', t[j:], re.S):
            m = re.search(r'\[\[([^\]|]+)', row)
            if not m: continue
            nums = re.findall(r'<td align="(?:center|right)" >\s*([0-9?]+)\s*</td>', row)
            if len(nums) >= 8:
                start[m.group(1)] = {'stats': dict(zip(STATS, [int(x) if x.isdigit() else None for x in nums[:7]])), 'bonus': int(nums[7]) if nums[7].isdigit() else None}
    return base, start
races = {}
for r in RACES:
    try: d = page(r)
    except FileNotFoundError: continue
    t = d['text']; base, start = stat_tables(t)
    cities = basic(t, 'Starting Cities')
    note = re.search(r'\nNote: ([^\n]+)', t)
    races[r] = {'url': WIKI + r.replace(' ', '_'), 'revid': d['revid'], 'ts': d.get('ts'),
                'alignment': (basic(t, 'Faction Alignment') or '').replace('??', '') or None,
                'racial': (lambda v: None if not v or v.lower() in ('unknown', '???') else v)(basic(t, r'Racial\(s\)')),
                'resists': (lambda v: None if not v or 'undetermined' in v.lower() else v)(basic(t, r'Resistances')),
                'cities_page': cities, 'base': base, 'start': start, 'large': r in LARGE,
                'note': unlink(note.group(1)) if note else None,
                'playable_ea': r in combos}
# ---- traits
T = page('Template:Traits')['text']; traits = {}; sec = None
for line in T.split('\n'):
    m = re.match(r'==\s*(.+?)\s*==', line)
    if m: sec = m.group(1); continue
    if line.startswith('| ') and '||' in line and sec:
        c = [unlink(x) for x in line[2:].split('||')]
        if len(c) >= 4: traits.setdefault(sec, []).append({'name': c[0], 'race': c[1], 'cls': c[2], 'desc': c[3]})
# ---- city pages: class trainers / guild masters (NPC tables), adjacency
CLASSES = ['Archer','Bard','Beastmaster','Cleric','Druid','Elementalist','Enchanter','Fighter','Inquisitor','Monk','Necromancer','Paladin','Ranger','Rogue','Shadow Knight','Shaman','Spellblade','Wizard']
cities = {}
for cname in CITY.values():
    d = page(cname); t = d['text']; tr = {}
    for row in t.split('\n|-'):
        cells = [unlink(c) for c in re.split(r'\|\||\n\|', row) if c.strip()]
        s2 = ' '.join(cells)
        if not re.search(r'trainer|guild ?master', s2, re.I): continue
        for c in CLASSES:
            if re.search(r'\b%s (trainer|guild ?master)' % c, s2, re.I) and len(cells) >= 5:
                tr.setdefault(c, []).append({'npc': cells[0].strip('| '), 'where': cells[4] if cells[4] not in ('-', '') else None, 'note': cells[-1]})
    adj = re.search(r'\|AdjacentZones\s*=\s*(.*)', t)
    cities[cname] = {'url': WIKI + cname.replace(' ', '_').replace("'", '%27'), 'revid': d['revid'], 'ts': d.get('ts'), 'trainers': tr,
                     'adjacent': [unlink(x) for x in re.findall(r'\[\[[^\]]+\]\]', adj.group(1))] if adj else []}
out = {'_source': {'start_table': {'url': WIKI + 'Starting_City_by_Race,_Class,_and_Deity', 'revid': P['revid'], 'ts': P.get('ts')},
                   'traits': {'url': WIKI + 'Traits', 'revid': page('Template:Traits')['revid']}},
       'cities': list(CITY.values()), 'large': LARGE, 'combos': combos, 'city_info': cities, 'races': races, 'traits': traits}
json.dump(out, open(os.path.join(ROOT, 'data', 'chargen', 'races.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print('races', len(races), 'combo races', len(combos), 'trait groups', {k: len(v) for k, v in traits.items()})

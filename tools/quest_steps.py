#!/usr/bin/env python3
"""raw/wiki quest pages (tools/wikifetch.py Category:Quests) -> data/quest_steps.json"""
import json, glob, re, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
def clean(s):
    s = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', s); s = re.sub(r"'''?", '', s); s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()
def tparams(t, name):
    m = re.search(r'\{\{%s\s*\n(.*?)\n\}\}' % name, t, re.S)
    if not m: return {}
    return {k.strip(): v.strip() for k, v in re.findall(r'^\|\s*([^=\n]+?)\s*=(.*)$', m.group(1), re.M)}
out = {}
for f in glob.glob(os.path.join(R, 'raw', 'wiki', '*.json')):
    d = json.load(open(f, encoding='utf8'))
    if 'Quests' not in d.get('cats', []): continue
    t = d['text']; P = tparams(t, 'Quest')
    w = t.split('== Walkthrough ==', 1)[1] if '== Walkthrough ==' in t else t
    steps = []
    for line in w.split('\n'):
        line = line.strip()
        m = re.match(r'^(={2,4})\s*(.*?)\s*\1$', line)
        if m: steps.append(['h', clean(m.group(2))]); continue
        for kind, rx in (('do', r'\{\{QuestNote\|(.*)\}\}'), ('info', r'\{\{QuestInfo\|(.*)\}\}'), ('get', r'\{\{ReceiveItem\|(.*?)\}\}'),
                         ('fac', r'\{\{[Ff]action\|(.*?)\}\}'), ('xp', r'\{\{[Ee]xp\}\}'), ('do', r'^[#*]\s*(.+)$')):
            m = re.search(rx, line)
            if m:
                v = clean(m.group(1).replace('|', ' ')) if m.groups() else 'Experience'
                if kind == 'fac': v = re.sub(r'\s*([+-])$', r' (\1)', v)
                if v: steps.append([kind, v])
                break
    while steps and steps[-1][0] == 'h': steps.pop()
    steps = [s for i, s in enumerate(steps) if not (s[0] == 'h' and (i + 1 == len(steps) or steps[i + 1][0] == 'h'))]
    cls = [c[:-7] for c in d['cats'] if c.endswith(' Quests') and c[:-7] in ('Archer', 'Bard', 'Beastmaster', 'Cleric', 'Druid', 'Elementalist', 'Enchanter', 'Fighter', 'Inquisitor', 'Monk', 'Necromancer', 'Paladin', 'Ranger', 'Rogue', 'Shadow Knight', 'Shaman', 'Spellblade', 'Wizard')]
    zone = [c[:-7] for c in d['cats'] if c.endswith(' Quests') and c[:-7] not in cls and not c.startswith('All ')]
    blob = (d['title'] + ' ' + P.get('Quest Rewards', '')).lower()
    kinds = (['class'] if cls else []) + (['armor'] if re.search(r'armou?r|breastplate|tunic|helm|greaves|boots|gloves|bracer', blob) else []) + \
            (['spell'] if re.search(r'spell|scroll|tome|ability', blob) else []) + (['access'] if re.search(r'\bkey\b|access|pass\b|entry|portal', blob) else [])
    out[d['title']] = {'title': d['title'], 'revid': d['revid'], 'ts': d['ts'][:10], 'giver': clean(P.get('Quest Giver', '')), 'zone': clean(P.get('Start Zone', '')) or (zone[0] if zone else ''),
                       'min': clean(P.get('Minimum Level', '')), 'classes': cls, 'rewards': clean(P.get('Quest Rewards', '')), 'kinds': kinds,
                       'needsinfo': '{{NeedsInfo' in t, 'steps': steps[:80]}
json.dump(out, open(os.path.join(R, 'data', 'quest_steps.json'), 'w', encoding='utf8'), indent=0, ensure_ascii=False)
import collections; print(len(out), collections.Counter(k for q in out.values() for k in q['kinds']), sum(1 for q in out.values() if not q['steps']), 'without steps')

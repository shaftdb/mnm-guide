#!/usr/bin/env python3
"""Writes data/startcities/night-harbor.json (partial: the Night Harbor notes that used to sit in the band panels, plus its wiki
starter quests), and stub files for Underdocks and Faelindral that say 'no sourced data yet'. Fill these in later branches."""
import json, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'startcities')
W = 'https://monstersandmemories.miraheze.org/wiki/'
def w(t): return W + t.replace(' ', '_').replace("'", '%27')
QS = json.load(open(os.path.join(OUT, '..', 'quest_steps.json'), encoding='utf8'))
def it(label, text, *src, **kw):
    d = {'label': label, 'text': text, 'src': list(src)}; d.update(kw); return d
FAQ = ['Official Early Access FAQ (starting areas)', 'https://monstersandmemories.com/early-access-faq']

def stub(city, slug, faq):
    return {'city': city, 'slug': slug, 'status': 'stub', 'updated': '2026-10-18', 'generated_by': 'tools/startcity_stubs.py',
            'sources': {'faq': FAQ, 'city': ['Wiki: %s' % city, w(city)]},
            'intro': [it('FACT', faq, 'faq'), it('UNVERIFIED', 'No curated early route for %s yet: no sourced data yet. The zone and camp lists below the route box are for every start city.' % city)],
            'faction': [], 'travel': [], 'money': [], 'trainers': {}, 'quests': {}, 'bands': []}

# Night Harbor: class starter quests + city quests from the wiki quest data, and the NH lines from the old band panels
nh = stub('Night Harbor', 'night-harbor', 'Good and neutral race/faith/class combinations can start here.')
nh['status'] = 'partial'
nh['sources'].update({'nh': ["Wiki: Night Harbor", w('Night Harbor')], 'tomb': ['Wiki: Tomb of the Last Wyrmsbane', w('Tomb of the Last Wyrmsbane')],
                      'sd': ['Wiki: Shaded Dunes', w('Shaded Dunes')], 'qs': ['Wiki quest walkthroughs (quest helper)', '/quest-helper.html']})
nh['intro'] = [it('FACT', 'Good and neutral race/faith/class combinations can start here.', 'faq'),
               it('UNVERIFIED', 'Partial route: class starter quests and the Night Harbor camps that were in the old band notes. A full curated Night Harbor route is not written yet: no sourced data yet for the other bands.')]
Q, starters = {}, []
for t, q in sorted(QS.items()):
    if q['zone'] == 'Night Harbor' and t.endswith('(Night Harbor)') and q['kinds'] and 'class' in q['kinds']:
        qid = 's-' + q['classes'][0].lower().replace(' ', '-')
        Q[qid] = {'auto': t, 'classes': q['classes'], 'tag': 'Recommended', 'why': 'Your class starter quest in Night Harbor.', 'src': ['qs']}
        starters.append(it('FACT', 'Class starter quest:', 'qs', quest=qid, classes=q['classes']))
for qid, t, why, tag in [('scarab', 'Scarab Armor Quests', 'Starter armor set for any class.', 'Recommended'),
                         ('tails', 'Ashira Tails Quest', 'Tattered Rawhide armor from Old Rankle.', 'Optional'),
                         ('ryland', 'Bone Chips for Squire Ryland', 'Repeatable Penitent Knights of the Hospice faction.', 'Optional'),
                         ('cinder', 'Cinder Beetle Armor Quests', 'Next armor set (minimum level 14 on the Night Harbor page).', 'Recommended'),
                         ('heads', 'Ashira Infiltrator Heads', 'Repeatable Red Mantles faction (~15).', 'Optional')]:
    if t in QS: Q[qid] = {'auto': t, 'classes': [], 'tag': tag, 'why': why, 'src': ['nh']}
nh['quests'] = Q
nh['bands'] = [
 {'lo': 1, 'hi': 5, 'title': 'Starter quests', 'steps': starters + [
   it('FACT', 'Trainer', 'nh', trainer=True),
   it('FACT', 'City armor quest:', 'nh', quest='scarab'), it('FACT', 'City quest:', 'nh', quest='tails'), it('FACT', 'Faction quest:', 'nh', quest='ryland')]},
 {'lo': 6, 'hi': 10, 'title': 'Outskirts', 'steps': [
   it('FACT', 'Night Harbor outskirts, the Underdocks, Tomb of the Last Wyrmsbane (3-15) and early Shaded Dunes (moved from the old 6-10 band note).', 'nh', 'tomb', 'sd')]},
 {'lo': 11, 'hi': 15, 'title': 'City camps', 'steps': [
   it('FACT', 'Night Harbor (wiki levels): diseased bats 10, cracked and diseased beetles 12-14, decrepit to cackling skeletons 12-15 (moved from the old 11-15 band note).', 'nh'),
   it('FACT', 'Armor quest:', 'nh', quest='cinder'), it('FACT', 'Faction quest:', 'nh', quest='heads')]},
]
os.makedirs(OUT, exist_ok=True)
for d in (nh, stub('Underdocks', 'underdocks', 'Some neutral and evil race/faith/class combinations have the option of starting here (a port district far below Night Harbor).'),
          stub('Faelindral', 'faelindral', 'Wood Elves and Halflings have the option of starting here.')):
    json.dump(d, open(os.path.join(OUT, d['slug'] + '.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print(d['slug'], d['status'], len(d['quests']), 'quests')

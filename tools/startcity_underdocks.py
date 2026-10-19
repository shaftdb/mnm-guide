#!/usr/bin/env python3
"""Writes data/startcities/underdocks.json: the Underdocks start route, levels 1-60 (local 1-20, then the Deep or the surface).
Sources: wiki zone, quest and faction pages (miraheze), the Per-Level Hunting Guide, monstersandmemories.wiki player-tracked
stats, storiesofmnm, monme.no, official patch notes, forum and Reddit. Researched 2026-10-18 (America/New_York).
Re-run after editing: python3 tools/startcity_underdocks.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from startcity_common import *

CITY = 'Underdocks'
S = dict(S_COMMON); S.update(S_MID)
S.update({
 'ud': ['Wiki: Underdocks (rev 82552, 2026-10-17)', w('Underdocks')],
 'udsq': ['Wiki: Underdocks Starter Quest (rev 82503, 2026-10-16)', w('Underdocks Starter Quest')],
 'udrog': ['Wiki: Rogue Starter Quest (Underdocks) (rev 80340)', w('Rogue Starter Quest (Underdocks)')],
 'uddru': ['Wiki: Druid Starter Quest (Underdocks) (rev 82416)', w('Druid Starter Quest (Underdocks)')],
 'udclr': ['Wiki: Cleric Starter Quest (Underdocks) (rev 75141)', w('Cleric Starter Quest (Underdocks)')],
 'udshd': ['Wiki: Shadow Knight Starter Quest (Underdocks) (rev 79359)', w('Shadow Knight Starter Quest (Underdocks)')],
 'udshm': ['Wiki: Shaman Starter Quest (Underdocks) (rev 79808)', w('Shaman Starter Quest (Underdocks)')],
 'udwiz': ['Wiki: Wizard Starter Quest (Underdocks) (rev 79672)', w('Wizard Starter Quest (Underdocks)')],
 'wfc': ['Wiki: Wererat Fight Club (rev 81100)', w('Wererat Fight Club')],
 'picks': ['Wiki: Mining Picks for Hull (rev 76278)', w('Mining Picks for Hull')],
 'delilah': ["Wiki: Find Delilah's Pet (rev 81994)", w("Find Delilah's Pet")],
 'trem': ['Wiki faction: The Trembling Hand', w('The Trembling Hand')],
 'sos': ['storiesofmnm: Mindless blightspore', 'https://storiesofmnm.com/wiki/npc/mindless-blightspore/'],
 'irem': ['Wiki: Caves of Irem', w('Caves of Irem')],
 'av': ["This Codex: Ail'Vorith route", '/walkthrough.html?city=Ail%27Vorith'],
 'dg': ['Wiki: Deep Gnome (race page)', w('Deep Gnome')],
 'monme': ["monme.no camps (Petrichor's database)", 'https://monme.no/camps'],
})
races, classes = who_starts(CITY)
intro = [
 it(F, 'The Underdocks is a port district far below Night Harbor: a circular cavern with an underground lake, the Citadel building in the middle and a ring of stone walkway around it. The wiki gives the zone as level 1-50.', 'ud', 'faq'),
 it(F, 'The start-city table allows these races to start here: %s. The zone page calls it the main start for Deep Elves and Deep Gnomes.' % ', '.join(races), 'start', 'ud'),
 it(F, 'Set chat to Common Tongue for Marshal Harding (he could not understand Deep Tongue as of 2026-09-10). Patch 0.30.2.0 made the relevant Underdocks NPCs speak both Common and Deep Common.', 'udsq', 'p302'),
 mw('Underdocks'),
 it(ST, 'Underdocks starts are short on local content past about 15: do your class starter, the repeatable bounties and wererats, then either head up into Night Harbor and the surface route or, as a Deep Elf, take the boat to the Deep.', 'ud', 'hunt'),
]
faction = [
 it(F, 'Deepcut bandit bounties, mushroom farmer and Thieves Guild bounties all raise The Descendian Order and Citizens of Underdocks (quest walkthroughs). The Descendian Order and Citizens of Underdocks have no wiki faction page yet: no sourced data yet for what lowers them.', 'qs'),
 it(F, 'Killing Deepcut bandits lowers Citizens of Ail\'Vorith (Ail\'Vorith faction page). That matters if you plan to use Ail\'Vorith later as a Deep Elf.', 'cav', races=['Deep Elf']),
 it(F, 'Necromancer starter: The Trembling Hand + and The Dreaming Dawn −. Shaman starter: Rot of Gorm +. Mining Picks for Hull raises the Delvestone Mining Company, The Underwatch and Citizens of Underdocks. Wererat Fight Club raises The Fight Club.', 'qs', 'trem', 'picks', 'wfc'),
 it(F, 'Deep Gnomes con Disdain at worst in Night Harbor and Evershade Weald, but are KoS to everyone in Ail\'Vorith.', 'dg', races=['Deep Gnome']),
 it(U, 'A Deep Gnome taken to the Ail\'Vorith Foreign Quarter found every NPC there KoS (forum, 2026-09-18), which matches the race page.', 'f551', races=['Deep Gnome']),
 it(U, 'How Night Harbor and Faelindral treat Goblins and other Underdocks races: no sourced data yet.'),
] + DE_KOS
travel = [
 it(F, 'Up: lifts to Overreach and the upper city, and on to Night Harbor. Down the river: the Caves of Irem, north along the river (a long way) or by boat. The boat continues through the Great Cavern Sea to Ail\'Vorith.', 'ud'),
 it(F, 'Inside the Citadel: teleporter pads and tunnels under them lead to the east shore and the west bank; there are raft docks and a ferry. Jumping off the walkway at the entrance to Crown Reach drops you in front of the bank.', 'ud'),
 it(F, 'The newbie hunting area is through the north gate (Underdocks wall). The Deepcut bandit camps are east of North Gate East, past the wererat camp.', 'udsq', 'deepcut'),
]
money = [
 it(F, 'Player-tracked coin in the Underdocks averages 29cp a kill (1cp-4sp 88cp; most hunting at level 9).', 'mw-underdocks'),
 it(F, 'Repeatable coin quests: Deepcut Bandit Bounty (8 silver per 6 hands), Mining Picks for Hull (2sp 18cp plus a random Patched Rawhide or Patched Cloth piece), Mushroom Farmers and Thieves Guild bounties (1 silver), Wererat Fight Club (50 copper a head).', 'qs', 'picks', 'wfc', 'ud'),
 it(F, 'The Underdocks sells no smelting molds (nearest: the Night Harbor Night Market) and has no loom, so tailoring recipes with 7+ ingredients cannot be made here. Banks are on the third floor (Citadel Exchange). The basement baths give Fair and Fresh (+10 CHA for 20 minutes).', 'ud'),
 it(F, "Karsh Spoonthrower (east island) buys the latest patch's drops. Gaden Shale buys everything at a reduced price, and Keen Strikemore pays more for weapons.", 'ud'),
]
trainers = {
 'Cleric': {'npc': 'Sister Marwen (trainer); Soren Akedd starts the quest', 'where': 'On the porch of the Temple of Ygorath chapel (red glow inside)', 'src': ['udclr', 'ud'], 'label': F},
 'Necromancer': {'npc': 'Soren Akedd (starter quest)', 'where': 'Next to the Temple of Ygorath; Abbot Harrow takes part in the quest', 'src': ['udclr', 'qs'], 'label': F, 'note': 'No Necromancer trainer or spell vendor is named on the wiki Underdocks page: no sourced data yet.'},
 'Shadow Knight': {'npc': 'Father Fyod (after Soren Akedd)', 'where': 'Balcony upstairs in the Soren Akedd building, left of centre facing the yard', 'src': ['udshd'], 'label': F},
 'Shaman': {'npc': 'Picci Manifold', 'where': 'Rotten Hollow, the Rot of Gorm cavern west of the palace', 'src': ['udshm', 'ud'], 'label': F},
 'Druid': {'npc': 'Luskmit', 'where': 'Rotten Hollow (Rot of Gorm cavern west of the palace): east to the Dry Docks, right along the water, through the vine tunnel, keep right to a camp up a hill', 'src': ['uddru', 'ud'], 'label': F},
 'Rogue': {'npc': 'Slylara Llumare', 'where': 'Thieves guild on the west docks, behind the herbalist (path behind the purple-glow enchanter buildings, then up the stairs)', 'src': ['udrog'], 'label': F},
 'Archer': {'npc': 'Simrut the Green (after Marshal Harding)', 'where': 'Eastern District, a goblin by the tall stones next to the archery range', 'src': ['udsq'], 'label': F},
 'Ranger': {'npc': 'Simrut the Green (after Marshal Harding)', 'where': 'Eastern District, by the archery range', 'src': ['udsq', 'ud'], 'label': F, 'note': 'Xeldrin Waymark sells Ranger spell and ability scrolls (wiki NPC table).'},
 'Beastmaster': {'npc': 'Gunder Dinnig (after Marshal Harding)', 'where': 'Eastern District, a halfling just up the stairs from Simrut', 'src': ['udsq'], 'label': F},
 'Fighter': {'npc': 'Gunder Dinnig (after Marshal Harding)', 'where': 'Eastern District, up the stairs from Simrut', 'src': ['udsq'], 'label': F},
 'Enchanter': {'npc': 'Maude Astarace (after Marshal Harding)', 'where': 'Eastern District, a gnome in the building next to the quartermaster', 'src': ['udsq', 'ud'], 'label': F, 'note': "Nyssara Mesmerin, Caster's Guild, is the Enchanter spell vendor."},
 'Elementalist': {'npc': 'Maude Astarace (after Marshal Harding)', 'where': 'Eastern District, next to the quartermaster', 'src': ['udsq'], 'label': F},
 'Wizard': {'npc': 'Maude Astarace (after Marshal Harding)', 'where': 'Eastern District, next to the quartermaster', 'src': ['udsq', 'udwiz'], 'label': F},
 'Bard': {'npc': 'Crescindy (sells Bard songs)', 'where': 'Bellowing Bards, across from The High Note (Crown Reach, 5th floor)', 'src': ['ud'], 'label': F, 'note': 'Bards cannot start in the Underdocks (start-city table).'},
}
Q = {}
for t, e in sorted(QS.items()):
    if e['zone'].lower() == 'underdocks' and 'Starter' in t and t != 'Underdocks Starter Quest' and 'class' in (e['kinds'] or []):
        Q['s-' + '-'.join(c.lower().replace(' ', '-') for c in e['classes'])] = auto(t, 'Recommended', 'Your class starter quest: first gear, guild faction and your trainer.', ('qs', 'ud'))
Q['s-wizard-enchanter'] = Q.pop('s-enchanter-wizard', None) or auto('Wizard Starter Quest (Underdocks)', 'Recommended', 'Points Wizards (and Enchanters) to the Underdocks Starter Quest.', ('qs', 'udwiz'))
Q['s-wizard-enchanter']['why'] = 'Same opening as the Underdocks Starter Quest (Recruitment Notice to Marshal Harding); the quest page lists Musty Tunic and Hammered Iron Ring.'
Q['udsq'] = auto('Underdocks Starter Quest', 'Recommended', 'Musty Tunic and Hammered Iron Ring at 1-2, then a class follow-up for Polished Iron Ring and 10 silver (Archer/Ranger), and at 12-14 Ratkiller.',
  ('udsq', 'qs'), where='Marshal Harding, Eastern District: take a lift down to the Citadel, head east (swim or take the raft), then climb the stairs across from the raft dock',
  prereq='Recruitment Notice (new Archer, Ranger, Beastmaster, Fighter, Enchanter, Elementalist or Wizard). Chat language: Common Tongue.',
  mobs=[{'item': 'Deep Beetle Carapace x6', 'from': 'a deep beetle (2-4), outside the gate to the newbie area; kill dusky rats and young shadewings (1-2) first'},
        {'item': "Riddrick's Ring (Archer/Ranger, 5+)", 'from': 'wererats (rare drop), encampment along the north wall from the newbie gate'},
        {'item': "Riddrick's Head (Archer/Ranger, 12-14)", 'from': 'Riddrick the Cursed (14, rare wererat spawn; may need a group)'},
        {'item': 'Crystals (Enchanter/Elementalist/Wizard, 4+)', 'from': 'Deepcut miners in the Darrowdwell mines'}],
  turnin='Marshal Harding, then Simrut the Green, Gunder Dinnig or Maude Astarace by class; the paymaster is Elara Venn',
  notes=[it(F, 'Faction: The Descendian Order + at every step.', 'udsq')])
Q.update({
 'bounty': auto('Deepcut Bandit Bounty', 'Recommended', '8 silver plus XP and Descendian Order and Citizens of Underdocks faction per 6 Deepcut Bandit\'s Hands. Group content at 10-16.',
                where='Traven Keldress takes the hands; Elara Venn, the paymaster, redeems the receipt at the East Docks Bounty Office',
                mobs=[{'item': "Deepcut Bandit's Hand x6", 'from': 'Deepcut bandits (miners 3-5, overseers 5-6, marksmen and others) at the 5-8 camps east of North Gate East, past the wererats'}]),
 'mush': auto('Mushroom Farmers Bounty Quest', 'Optional', 'Repeatable coin (the wiki says 2 silver, the walkthrough 1) plus Descendian Order and Citizens faction.',
              notes=[it(U, 'Coin differs: 2 silver on the Underdocks quest table, 1 silver in the walkthrough.', 'ud', 'qs')]),
 'thieves': auto('Thieves Guild Bounty Quest', 'Optional', 'Repeatable 1 silver plus Descendian Order and Citizens faction.'),
 'arson': auto('The Small Problem of Deepcut Arsonists', 'Optional', '1 silver plus faction. Arsonists are an uncommon spawn in the Deepcut mining cave, and their oil is an uncommon drop.'),
 'wfc': auto('Wererat Fight Club', 'Recommended', 'Repeatable 50 copper and The Fight Club faction per Severed Wererat Head (about 30% drop from 5-8 wererats in the newbie area).', ('wfc', 'qs'),
             where='Draznax, centre of the mercenary camp by the wagons, south-east of the upper city'),
 'picks': auto('Mining Picks for Hull', 'Recommended', 'Repeatable 2sp 18cp, a random Patched Rawhide or Patched Cloth piece, and Delvestone, Underwatch and Citizens faction.', ('picks', 'qs'),
               where='Hull Orbel, near the Delvestone miners in the north-east of the upper city',
               mobs=[{'item': 'Delvestone Mining Pick (a Broken Mining Pick does not count)', 'from': 'Deepcut miners in the mines on the rafters level (elevator across from Hull)'}]),
 'delilah': auto("Find Delilah's Pet", 'Optional', 'Turtle Shell Shield plus Citizens of Underdocks faction. Patch 0.30.3.2 replaced the old Greater Turtle Shell Shield.', ('delilah', 'qs')),
 'syrsil': auto("Syrsil's Stolen Package", 'Optional', 'XP and House Varros faction (a Deep Elf house). Senior Apprentice Syrsil is in the Inn tavern.', ('qs', 'ud')),
})
Q.update(Q_MID)
ST_CLASS = [it(F, 'Class starter quest:', 'qs', quest=k, classes=v['classes']) for k, v in sorted(Q.items()) if k.startswith('s-')]
bands = [
 {'lo': 1, 'hi': 5, 'title': 'Recruitment notice or temple note, newbie yard', 'steps': [
   it(F, 'Underdocks Starter Quest (Archer, Ranger, Beastmaster, Fighter, Enchanter, Elementalist, Wizard):', 'udsq', quest='udsq', classes=['Archer', 'Ranger', 'Beastmaster', 'Fighter', 'Enchanter', 'Elementalist', 'Wizard']),
 ] + ST_CLASS + [
   it(F, 'Trainer', 'ud', trainer=True),
   it(F, 'Newbie yard through the north gate (wiki levels): undercap morels, dusky rats, young shadewings and decayed shadowbones 1-2; deepweb crawlers 2-3; deep beetles 2-4. Stay by the gate until level 2 (starter quest notes).', 'ud', 'udsq'),
   it(F, 'Delvestone and Deepcut miners (3-5) and Deepcut overseers (5-6); the Deepcut is east of North Gate East.', 'ud'),
   it(F, 'From level 4:', 'wfc', quest='wfc'),
   it(F, 'Repeatable coin:', 'picks', quest='picks'),
   it(F, 'Optional:', 'delilah', quest='delilah'),
 ]},
 {'lo': 6, 'hi': 10, 'title': 'Wererats, greater shadowbones, Deepcut bounties', 'steps': [
   it(F, 'Wererat encampment along the north wall from the newbie gate: plaguespreaders 8-12, the rest 10-12; the easiest wererats are 5-8 (Fight Club walkthrough). Greater shadowbones 7-9, smugglers 9-10.', 'ud', 'wfc'),
   it(F, 'Deepcut bandit camps (5-8 camps of 4-5) east of North Gate East, past the wererats. The faction page calls them 10-16 and mostly group content; the named Belot spawns at any camp or in the mine.', 'deepcut'),
   it(F, 'Bounty (from 8 on the zone table):', 'qs', quest='bounty'),
   it(F, 'Optional bounties:', 'qs', quest='mush'), it(F, 'Optional:', 'qs', quest='thieves'), it(F, 'Optional:', 'qs', quest='arson'),
   it(F, 'Surface alternative: Shaded Dunes smugglers and wererats beach party (6-9, Toma the Two-Faced) and the Tomb of the Last Wyrmsbane entrance (group 4-14), both through Night Harbor.', 'monme', 'hunt'),
   it(F, 'Optional, House Varros faction:', 'qs', quest='syrsil'),
 ]},
 {'lo': 11, 'hi': 15, 'title': 'Elder shadowbones, Sporefather, Riddrick, Night Harbor docks', 'steps': [
   it(F, 'Elder shadowbones (10-12) and wererats (10-12); named the Sporefather (13-14, Ironroot Fists), Riddrick the Cursed (14, Riddrick\'s Head for Ratkiller), Jumbe (14) and Munk (14).', 'ud'),
   it(U, 'storiesofmnm lists a mindless blightspore (Myconid, level 13) in a small cave in the northeast cavern of the Underdocks, tied to the Shaman starter quest and dropping a Blightspore Brain.', 'sos'),
   it(F, 'Deepcut camps and the mine (group 10-16). Jorlach the Fearless near the entrance drops Jorlach\'s Head, used in the Shadow Knight starter quest.', 'deepcut', 'ud'),
   it(F, 'Up in Night Harbor: the docks goblins by the cranes (no faction hit, solo 13-15, group 8-12), the Tel Ekir Ashira entrance (group 9-16), and the crypt by day (beetles and scarabs 10-15).', 'hunt', 'z-night-harbor'),
   it(F, 'Caves of Irem (wiki 13+; player-tracked 13-37, most at 13), north along the river from the Underdocks.', 'irem', 'mw-caves-of-irem'),
 ]},
 {'lo': 16, 'hi': 20, 'title': 'Abominable ghouls, then the Deep or the surface', 'steps': [
   it(F, 'Abominable ghouls (18-20, Shriveled Ghoul Heart) are the highest common mobs on the Underdocks page. Player-tracked hunting in the Underdocks tops out at 15.', 'ud', 'mw-underdocks'),
   it(F, 'Deep option: take the boat toward Ail\'Vorith and drop off in the Great Cavern Sea (player-tracked 16-24, most at 17). The Ail\'Vorith route covers the Cavern Sea outpost quests and the exile caves (15-22).', 'mw-great-cavern-sea', 'z-great-cavern-sea', 'av', races=['Deep Elf']),
   it(ST, 'Everyone else: go up into Night Harbor and follow the shared surface route below (Fallen Pass pit, Glass Flats goblins, Sungreet quarry).', 'hunt'),
 ]},
]
mb = mid_bands('ud')
bands[3]['steps'] += mb[0]['steps']
bands += mb[1:]
D = {'city': CITY, 'slug': 'underdocks', 'status': 'sourced', 'updated': '2026-10-18', 'researched': '2026-10-18 22:45 America/New_York',
     'generated_by': 'tools/startcity_underdocks.py', 'sources': S, 'intro': intro, 'faction': faction, 'travel': travel, 'money': money,
     'trainers': trainers, 'quests': Q, 'bands': bands}
write(D)

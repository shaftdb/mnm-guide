#!/usr/bin/env python3
"""Writes data/startcities/night-harbor.json: the Night Harbor start route, levels 1-60.
Sources: wiki zone, quest, NPC and faction pages (miraheze), the wiki Per-Level Hunting Guide, monstersandmemories.wiki
player-tracked stats, monme.no camps, the official FAQ and patch notes, and forum posts. Researched 2026-10-18 (America/New_York).
Re-run after editing: python3 tools/startcity_nh.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from startcity_common import *

CITY = 'Night Harbor'
S = dict(S_COMMON); S.update(S_MID)
S.update({
 'ench': ['Wiki: Enchanter (rev 82930, Human starting stats)', w('Enchanter')],
 'nh': ['Wiki: Night Harbor (rev 83168, 2026-10-18)', w('Night Harbor')],
 'monme': ["monme.no camps (Petrichor's database)", 'https://monme.no/camps'],
 'pk': ['Wiki faction: Penitent Knights of the Hospice', w('Penitent Knights of the Hospice')],
 'cw': ['Wiki faction: City Watch of Night Harbor', w('City Watch of Night Harbor')],
 'bends': ['Wiki faction: Residents of the Bends', w('Residents of the Bends')],
 'dg': ['Wiki: Deep Gnome (race page)', w('Deep Gnome')],
 'sqarc': ['Wiki: Archer Starter Quest (Night Harbor)', w('Archer Starter Quest (Night Harbor)')],
 'sqbst': ['Wiki: Beastmaster Starter Quest (Night Harbor)', w('Beastmaster Starter Quest (Night Harbor)')],
 'sqftr': ['Wiki: Fighter Starter Quest (Night Harbor)', w('Fighter Starter Quest (Night Harbor)')],
 'sqmnk': ['Wiki: Monk Starter Quest (Night Harbor) (rev 80330)', w('Monk Starter Quest (Night Harbor)')],
 'sqnec': ['Wiki: Necromancer Starter Quest (Night Harbor)', w('Necromancer Starter Quest (Night Harbor)')],
 'sqspb': ['Wiki: Spellblade Starter Quest (Night Harbor) (rev 80800)', w('Spellblade Starter Quest (Night Harbor)')],
 'sqwiz': ['Wiki: Wizard Starter Quest (Night Harbor) (rev 77199)', w('Wizard Starter Quest (Night Harbor)')],
 'sqinq': ['Wiki: Inquisitor Starter Quest (Night Harbor) (rev 74623)', w('Inquisitor Starter Quest (Night Harbor)')],
 'sqenc': ['Wiki: Enchanter Starter Quest (Night Harbor) (rev 80831)', w('Enchanter Starter Quest (Night Harbor)')],
 'sqpal': ['Wiki: Paladin Starter Quest (Night Harbor)', w('Paladin Starter Quest (Night Harbor)')],
 'sqclr': ['Wiki: Cleric Starter Quest (rev 79425)', w('Cleric Starter Quest')],
})
races, classes = who_starts(CITY)

intro = [
 it(U, "Human Enchanter is not on the wiki start-city table (rev 74855), but the official Enchanter page and the wiki Human and Enchanter pages (rev 82930) list it, so this Codex infers a Night Harbor start from the Enchanter guild there. The guild master and starter-quest NPC is Master Wincog (Night Harbor zone page and Enchanter Starter Quest). Deities: no sourced data yet.", 'ench', 'nh', 'sqenc', races=['Human'], classes=['Enchanter']),
 it(F, 'Night Harbor is the seat of the Langsdorfian League, a confederacy of guilds with a near monopoly on trade and transport. The wiki gives the zone as level 1-50, with Ashira, bats, goblins, jackals, rats, scarabs, skeletons and snakes.', 'nh'),
 it(F, 'The start-city table allows these races to start here: %s. Pick a combination with the Race, Class and Start boxes in the top bar.' % ', '.join(races), 'start'),
 it(F, 'Neighbouring zones: Shaded Dunes (west gate), Sungreet Strand (north gate), Tomb of the Last Wyrmsbane, the Night Harbor Sewers and the Underdocks (lift down).', 'nh'),
 mw('Night Harbor'),
 it(ST, 'Night Harbor has the most quests and camps of the four starts. A good first hour: your class starter quest, the free wooden weapon from the wise elder, scarab armor from the noob-yard scarabs, then the Tomb of the Last Wyrmsbane entrance at about 6-8.', 'nh', 'hunt', 'qs'),
]
faction = [
 it(F, 'The Night Harbor faction pages (Citizens, Red Mantles, Steel Talons, Garrison, City Watch, Merchants, the Bends) all start with "Not much is known". Only the raise and lower lists below are filled in.', 'cnh', 'redm', 'steel', 'nhg', 'cw'),
 it(F, 'Citizens of Night Harbor rise in 9 zones (Night Harbor, Shaded Dunes, Tel Ekir, Sungreet Strand, Fallen Pass, Glass Flats, Keeper\'s Bight, Vale of Zintar, Shallow Shoals) from Blacktide orcs, witchguard, Muggrah goblins, Dustrend orcs and others, plus the Laundry Day Quest. They drop when you kill Whiskey, Mayana or Jumthem.', 'cnh'),
 it(F, 'Red Mantles rise from crypt beetles and scarabs (cracked, dusty, hardened, pristine), Dhajr Spitemaw in Shaded Dunes, Sangrel in Keeper\'s Bight, and the Wanted: Ayip & Yapala and Ashira Infiltrator Heads quests. Steel Talons and the Garrison rise from Ashira, bandits, smugglers and grave robbers in Shaded Dunes, Tel Ekir and Fallen Pass.', 'redm', 'steel', 'nhg'),
 it(F, 'Ashira Infiltrator Heads: the walkthrough warns that killing Mayana and Jumthem too often costs a lot of Citizens of Night Harbor standing, and the quest itself lowers Seafarers Consortium.', 'qs', 'cnh'),
 it(F, 'The Bends: killing Sahir Muzalal or a smuggler lowers Residents of the Bends. Riverbend Gang Wars raises Bends Garrison and Cult of the Living City but lowers the Ten Hooks and Waterdogs gangs.', 'bends', 'qs'),
 it(F, 'Penitent Knights of the Hospice (Clerics and Paladins, Wayfarer\'s Hospice): Bone Chips for Squire Ryland is the easy repeatable. At Amicable the hospice NPCs give 30-minute pet buffs.', 'pk'),
 it(F, 'Deep Gnomes con Disdain at worst in Night Harbor and Evershade Weald, and are KoS to everyone in Ail\'Vorith (race page note).', 'dg', races=['Deep Gnome']),
 it(U, 'How Night Harbor treats Goblins and other Underdocks races: no sourced data yet.'),
] + DE_KOS
travel = [
 it(F, 'Gates: Shaded Dunes through the west gate, and Sungreet Strand to the north. Boat: Night Harbor to Keeper\'s Bight (Penshaw Village), 4 stops, including two Shallow Shoals docks (Player Island, Zaedin\'s Landing).', 'nh'),
 it(F, 'The Underdocks are below the city. The Deep (Caves of Irem, the boat to Ail\'Vorith) is reached through the Underdocks.', 'nh', 'z-underdocks'),
 it(F, 'Shaded Dunes connects to Tel Ekir, the Caves of Irem, the Ancient Crypt, the Infested Crypt and Fallen Pass. Sungreet Strand connects to Tel Ekir, Glass Flats and the Grain Cellar.', zk('Shaded Dunes'), zk('Sungreet Strand')),
]
money = [
 it(F, 'Player-tracked coin in Night Harbor averages 1sp a kill (1cp-6sp 69cp). Nearby: Shaded Dunes 25cp, Sungreet Strand 48cp, Tel Ekir 36cp, Tomb 18cp, Ancient Crypt 42cp.', 'mw-night-harbor', 'mw-shaded-dunes', 'mw-sungreet-strand', 'mw-tel-ekir', 'mw-tomb-of-the-last-wyrmsbane', 'mw-ancient-crypt'),
 it(F, 'Free gear and supplies: the wise elder (stone building north of the West Bank) gives a wooden weapon; Pests at the Farm pays rations, water and torches; Cloth Scraps gives Tattered Cloth and a Pouch.', 'qs'),
 it(F, 'Vendors and tradeskills are in the city: the tannery, Blackfeather Bazaar (pelts and hides, used armor, general goods, alchemy), smelting, blacksmithing, weaponsmithing and tailoring trainers.', 'nh'),
 it(F, 'Vale of Zintar corrupted Ashira drops sell for 30s-1g (hunting guide, 26-30). Sungreet quarry cinder worker loot feeds the Cinder Beetle Armor Quests.', 'hunt'),
]
trainers = {
 'Beastmaster': {'npc': 'Leila Ghasem', 'where': 'Seekers of the Lost Eye guild, Saltbreeze Park (Beastmaster Spell Merchant in the same guild)', 'src': ['sqbst', 'nh'], 'label': F, 'note': 'Takes your starting note in the Beastmaster starter quest.'},
 'Fighter': {'npc': 'Fedamius Steele III', 'where': 'Steel Talons Martial Academy, south-west Night Harbor, on the wall above the courtyard', 'src': ['sqftr'], 'label': F, 'note': 'Starter-quest NPC who sends you on to Lurinda and Elrind Steele. The wiki names no Fighter guild master or spell vendor: no sourced data yet.'},
 'Monk': {'npc': 'Chahaya Tam', 'where': 'School of the Fourfold Path, Twilight Harbor, south of Saltbreeze Park (look for floating elementals)', 'src': ['sqmnk', 'nh'], 'label': F, 'note': 'Leads the order with Tenebrim Tam. A Monk Spell Merchant is listed in the city.'},
 'Necromancer': {'npc': 'Marvion Hallows, then Sekhmet', 'where': 'Concourse of Souls (library, then the morgue below), carved into the necropolis mountainside north of Sageside; Necromancer Spell Merchant on the second floor', 'src': ['sqnec', 'nh'], 'label': F},
 'Spellblade': {'npc': 'Njau Hansou', 'where': 'Spellbinders Spire training yard, Sageside (via the translocation devices under the wizard tower); Jaffar Jhaym takes your note first', 'src': ['sqspb', 'nh'], 'label': F, 'note': 'A Spellblade Spell Merchant is listed in the city.'},
 'Wizard': {'npc': 'Olvin Viscus', 'where': 'Chartered Academy of Arcane Inquiry, the floating wizard tower in Sageside (north-east), via the translocation devices', 'src': ['sqwiz'], 'label': F, 'note': 'Admissions officer for the Wizard starter quest. Which NPC sells Wizard scrolls: no sourced data yet.'},
 'Inquisitor': {'npc': 'Petra Gyle', 'where': 'Spellbinders Spire, Sageside; Jaffar Jhaym at the top of the Spire takes your note first', 'src': ['sqinq'], 'label': F,
                'note': "Resolved: the quest table names Jaffar Jhaym and the quest page names Petra Gyle because both are right. Jaffar takes the Rune-Etched Note and says 'you will be under the tutelage of Petra Gyle'. Who sells Inquisitor scrolls in Night Harbor: no sourced data yet."},
 'Paladin': {'npc': 'Trey Fulton', 'where': "Wayfarer's Hospice, first floor (Travelers Ward, north of the West Gate); Thibald Burlond greets you first", 'src': ['sqpal', 'nh'], 'label': F},
 'Cleric': {'npc': 'Dalinder Grammanoot', 'where': "Wayfarer's Hospice, ground floor near Thibald Burlond (Sojourner camp next to the West Bank)", 'src': ['sqclr', 'nh'], 'label': F},
 'Enchanter': {'npc': 'Master Wincog', 'where': "Wincog's Curious Goods, on the long stairs between Sageside and Saltbreeze Park", 'src': ['sqenc', 'nh'], 'label': F},
}
Q = {}
for t, e in sorted(QS.items()):
    if e['zone'] == CITY and t.endswith('(Night Harbor)') and 'class' in (e['kinds'] or []):
        Q['s-' + e['classes'][0].lower().replace(' ', '-')] = auto(t, 'Recommended', 'Your class starter quest: first armor or a class item, guild faction and your trainer.', ('qs', 'nh'))
Q.update({
 'perilous': auto('Perilous to Leave by Oneself', 'Recommended', 'A free wooden weapon at level 1.', where='large stone building just north of the West Bank'),
 'scarab': auto('Scarab Armor Quests', 'Recommended', 'Five-piece starter armor set from noob-yard dunes scarabs (3).', where='rear of the Sojourner Camp',
                mobs=[{'item': 'Scarab Carapace, Scarab Leg, Scarab Thorax Plate, Scarab Elytron Plate', 'from': 'a dunes scarab (3), noob yards outside the north and west gates'}]),
 'cloth': auto('Cloth Scraps Quest', 'Optional', 'Tattered Cloth and a Pouch (bag) for 6 Cloth Scraps from Ashira or skeletons. Casters get the most out of it.', where='ruined building just outside the west gate'),
 'pests': auto('Pests at the Farm', 'Optional', 'Rations, water and torches from noob-yard drops (random reward).', where='farm north-east of the caster tower outside the North Gate'),
 'tails': auto('Ashira Tails Quest', 'Optional', 'Tattered Rawhide armor for Ashira Tails, which any Ashira can drop.', where='Tannery, second floor of a building on the north wall'),
 'bracer': auto('Ashira Warrior Bracer Quest', 'Optional', 'Tattered Rawhide plus Steel Talons faction; the bracer is an uncommon drop.', where='Watch Captain Badawi roams the upper garrison; turn in to Quartermaster Obaid'),
 'ryland': auto('Bone Chips for Squire Ryland', 'Optional', 'Repeatable Penitent Knights faction (5 Bone Chips a turn-in). Worth it for Clerics and Paladins.', where="Wayfarer's Hospice near the Paladin trainers"),
 'laundry': auto('Laundry Day Quest', 'Optional', 'Crude silk shirts and Citizens of Night Harbor, City Watch, Smallfolk and Azure Veils faction.'),
 'tamsah': auto('Little Tamsah, Big Appetite', 'Optional', 'XP and Seekers of the Lost Eye faction (the Shaman and Beastmaster guild).'),
 'winged': auto('A Winged Terror', 'Optional', 'Kill the Night Terror (8), which spawns at night in the Necropolis yard, so come back at 8+.',
                notes=[it(U, 'The reward is listed two ways: the walkthrough says Necklace of Night, and the Night Harbor quest table says Mantle of Night and Tunic of Night. Not resolved.', 'qs', 'nh')]),
 'key': auto('Night Harbor Cemetery Key Quest', 'Recommended', 'The key opens the cemetery at night (skeletons 12-16 and named). Part 1 uses crypt rats and bats (10).', where='Gatekeeper Nusder at the Red Mantle Keep entrance to the cemetery'),
 'ayip': auto('Wanted: Ayip & Yapala', 'Optional', 'Red Mantles faction and The Impaler for two Tel Ekir named (13).'),
 'gang': auto('Riverbend Gang Wars Quest', 'Optional', 'Bends Garrison faction, at the cost of the Ten Hooks and Waterdogs gangs.'),
 'badge': auto('Platinum Badge of the Living City Quest', 'Optional', 'Heads of the Bends named (Cormac Renshaw ~17 and others). A group quest.'),
 'cinder': auto('Cinder Beetle Armor Quests', 'Recommended', 'The armor set after scarab. The Night Harbor page lists it at 14. Cinder workers (16-18) in the Sungreet quarry drop the parts (hunting guide).', where='Hult Beetlewrangler, Sojourner Camp'),
 'heads': auto('Ashira Infiltrator Heads', 'Optional', 'Red Mantles faction, but it costs Citizens of Night Harbor if you over-kill Mayana and Jumthem.', notes=[it(F, 'Starts after The Yowling.', 'qs')]),
 'chompers': auto("Chompers' Hide Tunic Quest", 'Optional', 'A tunic from Chompers (16), a crocodile that spawns randomly on the Shaded Dunes beach.'),
 'aashir': auto('Escort Head Researcher Aashir', 'Optional', "Aashir's Earring (15+, Shaded Dunes). An escort, so bring a group."),
 'bowl': auto("Hult's Beetle Bowl (Quest)", 'Optional', "Hult's Beetle Bowl from Hult Beetlewrangler for 2 Fire Beetle Carapace.", where='Hult Beetlewrangler, rear of the Sojourner Camp',
             mobs=[{'item': 'Fire Beetle Carapace x2', 'from': 'a fire beetle (2), noob yards'}]),
})
Q.update(Q_MID)
Q['s-enchanter'].update(giver='Master Wincog (hand him the Torn Note you start with)',
    where="Wincog's curious goods shop, on the long stairs between Sageside and Saltbreeze Park. On the registered path you go to Registrar Vauquelin, ground floor of the Spellbinders Spire",
    rewards='Dusty Violet Robe (Wincog path) or Rough Cut Robe (Vauquelin path); later a Braided Crystal Ring and a no-drop Scroll: Invisibility versus Undead (wiki rev 80831)',
    faction='House of Candor (−) at one step; no other faction changes listed', src=['qs', 'sqenc'])
ST_CLASS = [it(F, 'Class starter quest:', 'qs', quest=k, classes=v['classes']) for k, v in sorted(Q.items()) if k.startswith('s-')]
bands = [
 {'lo': 1, 'hi': 5, 'title': 'Class starter quest, noob yards, scarab armor', 'steps': ST_CLASS + [
   it(F, 'Trainer', 'nh', trainer=True),
   it(F, 'Free weapon:', 'qs', quest='perilous'),
   it(F, 'Noob yards outside the north and west gates (wiki levels): large rat, rotting skeleton, desert bat and jackal pup 1; spiderling, fire beetle and ashira scout 2; dunes scarab 3; jackal and curious jackal 4.', 'nh'),
   it(F, 'In town: Shaded Bloom Inn basement (beetles and rats, solo 1-3), Saltbreeze Park (bats at night), the Necropolis front yard (rats, bats, spiders, beetles, skeletons; the Night Terror, level 8, spawns at night) and the Garrison Boatyard rats.', 'hunt'),
   it(F, 'Starter armor:', 'qs', quest='scarab'),
   it(F, 'Optional, same NPC:', 'qs', quest='bowl'),
   it(F, 'Crocodile hatchlings (non-hostile; Snar the egg collector is the named) by the shore outside the west gate and tucked away right of the north gate. Hunting guide: solo 4-6. monme.no: 3-7.', 'hunt', 'monme'),
   it(F, 'Optional city quests:', 'qs', quest='cloth'), it(F, 'Optional:', 'qs', quest='pests'), it(F, 'Optional:', 'qs', quest='tails'),
   it(F, 'Faction (Clerics and Paladins):', 'pk', quest='ryland', classes=['Cleric', 'Paladin']),
   it(F, 'Optional faction:', 'qs', quest='laundry'), it(F, 'Optional faction:', 'qs', quest='tamsah'),
 ]},
 {'lo': 6, 'hi': 10, 'title': 'Tomb of the Last Wyrmsbane, Shaded Dunes Ashira, smuggler beach', 'steps': [
   it(F, 'Tomb of the Last Wyrmsbane (wiki 3-15), next to Night Harbor: skeletal fighters 3-10, warriors 4-11, cavaliers 6-10. Named Timmon Bell and Jakob Geffrey (~8), Lieutenant Gregan Snyde and Ariblast the Wicked (10). Hunting guide: solo 8, group 4-14, good gear drops. Player-tracked: most at 13.', 'hunt', zk('Tomb of the Last Wyrmsbane'), 'mw-tomb-of-the-last-wyrmsbane'),
   it(F, 'Several class quests run through the Tomb: the Paladin starter (Engraved Coin upstairs), Wizard (4) and Necromancer and Shaman (8) steps.', zk('Tomb of the Last Wyrmsbane')),
   it(F, 'Shaded Dunes: the Ashira camps near the Tel Ekir zone line (group 6-10), with the zone line handy if pulls go wrong. Dhajr Spitemaw (8+) is at the large Ashira camp and raises Red Mantles.', 'hunt', zk('Shaded Dunes'), 'redm'),
   it(F, 'Shaded Dunes smugglers and wererats beach party, the furthest camp west along the south coast (6-9), with Toma the Two-Faced (9+).', 'monme', zk('Shaded Dunes')),
   it(F, 'Sungreet Strand (north gate): Ashira warriors 6-7, giant fire beetles 7-8, a hired thug 9-10 at Ameen Farm.', zk('Sungreet Strand')),
   it(F, 'Night Harbor docks: goblin troublemakers (9) and squatters (10).', 'nh'),
   it(F, 'Infested Crypt (wiki 8-16, off Shaded Dunes): crypt guardians, creepers and spiderlings 8-9, broodmistress 10-12.', zk('Infested Crypt')),
   it(F, 'Optional:', 'qs', quest='bracer'),
   it(F, 'Night Terror (8):', 'qs', quest='winged'),
 ]},
 {'lo': 11, 'hi': 15, 'title': 'Crypt by day and night, Tel Ekir Ashira, docks goblins', 'steps': [
   it(F, 'Night Harbor docks goblins, west of the twilight harbor by the cranes: no faction hit, but social. Hunting guide: solo 13-15, group 8-12.', 'hunt'),
   it(F, 'Night Harbor crypt by day: diseased bats and catacombs rats (10), dusty scarabs (11), cracked beetles (12), hardened scarabs (13), diseased beetles (14). Named: a sanguine bat 12, a pristine beetle 13, an old scarab 14, an ornate beetle 15. The beetles and scarabs raise Red Mantles.', 'nh', 'redm'),
   it(F, 'Cemetery key (opens the crypt at night):', 'qs', quest='key'),
   it(F, 'Crypt by night (needs the key): skeletons 12-15 (decrepit, risen, stumbling, cackling) with named noble 13, bejeweled 14, majestic 15 and crowned 16; skeletal priests 18-19 and Malchiok the Priest 25-26. Hunting guide: solo 12?, group 10-14?.', 'nh', 'hunt'),
   it(F, 'Tel Ekir, Ashira entrance: younglings 9-11, skinners 10-11, oracles and wanderers ~12-14, alphas ~14, and named Roa the Huntress 12, Ayip and Yapala 13, Hadhraman 17. The alpha camp is higher. Hunting guide: group 9-16. Player-tracked: most at 13.', 'hunt', zk('Tel Ekir'), 'mw-tel-ekir'),
   it(F, 'Tel Ekir named bounty:', 'qs', quest='ayip'),
   it(F, 'Sungreet Strand beach, past the Ashira camps: thugs, acolytes and skintakers (~11-14). Damage is high, so bring a tank and a healer. Hunting guide: solo 12?, group 8-12.', 'hunt', zk('Sungreet Strand')),
   it(F, 'Infested Crypt, larger spiders 12-14 and a frenzied crypt guardian (~12). The crypt broodmother is 16.', zk('Infested Crypt')),
   it(F, 'Next armor set:', 'qs', quest='cinder'),
   it(F, 'Optional, the Bends:', 'qs', quest='gang'),
   it(F, 'Optional faction:', 'qs', quest='heads'),
   it(F, 'Optional, Shaded Dunes:', 'qs', quest='chompers'),
 ]},
]
mb = mid_bands('nh')
mb[0]['steps'] = [
   it(F, 'Night Harbor: the hidden cultist cave (mad prophets, Shon Ibn Lail, Guardians Crepus and Noctus, 16-18) and the Bends named (Cormac Renshaw ~17).', 'nh'),
   it(F, 'The Bends named bounty:', 'qs', quest='badge'),
   it(F, 'Escort (15+):', 'qs', quest='aashir'),
] + mb[0]['steps']
bands += mb
D = {'city': CITY, 'slug': 'night-harbor', 'status': 'sourced', 'updated': '2026-10-18', 'researched': '2026-10-18 22:30 America/New_York',
     'generated_by': 'tools/startcity_nh.py', 'sources': S, 'intro': intro, 'faction': faction, 'travel': travel, 'money': money,
     'trainers': trainers, 'quests': Q, 'bands': bands}
write(D)

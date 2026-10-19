#!/usr/bin/env python3
"""Writes data/startcities/ailvorith.json: the curated Ail'Vorith early route (Deep Elf start).
Every line carries a label (FACT = wiki/official page, STRATEGY = this Codex's suggestion, UNVERIFIED = community report or
conflicting/missing data) and source keys. Researched 2026-10-18 from the community wikis, official patch notes, the official forum and Reddit.
Re-run after editing: python3 tools/startcity_ailvorith.py"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from startcity_common import DE_KOS, SRC_KOS, S_COMMON
W = 'https://monstersandmemories.miraheze.org/wiki/'
def w(t): return W + t.replace(' ', '_').replace("'", '%27')
S = {
 'av': ["Wiki: Ail'Vorith (rev 83176, 2026-10-18)", w("Ail'Vorith")],
 'avsq': ["Wiki: Ail'Vorith Starter Quest", w("Ail'Vorith Starter Quest")],
 'avsq2': ["monstersandmemories.wiki: Ail'Vorith Starter Quest (step list)", 'https://monstersandmemories.wiki/quests/ailvorith-starter-quest'],
 'avcq': ["Wiki: Ail'Vorith Class Quests", w("Ail'Vorith Class Quests")],
 'xal': ["Wiki: House Xal'tharn (Quest) (rev 82660, 2026-10-17)", w("House Xal'tharn (Quest)")],
 'klavel': ["Wiki: Klavel Sul (rev 82871, 2026-10-17)", w('Klavel Sul')],
 'klavel2': ['monstersandmemories.wiki: Klavel Sul', 'https://monstersandmemories.wiki/npcs/klavel-sul'],
 'cuirass': ['Wiki: Dull Iron Cuirass (item page created 2026-10-07)', w('Dull Iron Cuirass')],
 'pendant': ["Wiki: Xal'tharn Pendant (item page, last edited 2026-09-26)", w("Xal'tharn Pendant")],
 'xalh': ["Wiki edit history: House Xal'tharn (Quest)", 'https://monstersandmemories.miraheze.org/w/index.php?title=House_Xal%27tharn_(Quest)&action=history'],
 'avh': ["Wiki edit history: Ail'Vorith", 'https://monstersandmemories.miraheze.org/w/index.php?title=Ail%27Vorith&action=history'],
 'nurvolh': ['Wiki edit history: Nurvol Cereveth', 'https://monstersandmemories.miraheze.org/w/index.php?title=Nurvol_Cereveth&action=history'],
 'p291': ['Official patch notes 0.29.0.1 (2026-09-11)', 'https://account.monstersandmemories.com/community/patch_notes/45'],
 'p3021': ['Official patch notes 0.30.2.1 (2026-09-30)', 'https://account.monstersandmemories.com/community/patch_notes/52'],
 'p3023': ['Official patch notes 0.30.2.3', 'https://account.monstersandmemories.com/community/patch_notes/54'],
 'p3025': ['Official patch notes 0.30.2.5 (2026-10-07)', 'https://account.monstersandmemories.com/community/patch_notes/56'],
 'npg': ['Official New Player Guide', 'https://monstersandmemories.com/new-player-guide'],
 'f1533': ["Forum: The horrific Ail'Vorith Economy (2026-10-03)", 'https://forum.monstersandmemories.com/d/1533'],
 'f551': S_COMMON['f551'],
 'shoreb': ['Wiki: a shore beetle (15)', w('A shore beetle')], 'shelb': ['Wiki: a shelter bat (16)', w('A shelter bat')], 'shalb': ['Wiki: a shallows basilisk (17)', w('A shallows basilisk')],
 'morgak': ['Wiki: Morgak Foamscar (rev 83094, 2026-10-18)', w('Morgak Foamscar')],
 'mwgcs': ['monstersandmemories.wiki: Great Cavern Sea (player-tracked levels and coin)', 'https://monstersandmemories.wiki/zones/great-cavern-sea'],
 'nurvol': ["Wiki: Nurvol Cereveth", w('Nurvol Cereveth')],
 'miniel': ["Wiki: Miniel Ubast", w('Miniel Ubast')],
 'fungal': ["Wiki: Fungal Armor Quests", w('Fungal Armor Quests')],
 'fcoat': ["Wiki: Fungal Coat (class list)", w('Fungal Coat')],
 'varsup': ["Wiki: House Varros Supplies", w('House Varros Supplies')],
 'survey': ["Wiki: Survey the Creatures of the Cavern Sea", w('Survey the Creatures of the Cavern Sea')],
 'gcs': ["Wiki: Great Cavern Sea (rev 83098, 2026-10-18)", w('Great Cavern Sea')],
 'irem': ["Wiki: Caves of Irem", w('Caves of Irem')],
 'bm': ["Wiki: Blind Midden (rev 83212)", w('Blind Midden')],
 'bmmerit': ["Wiki: Mark of Merit", w('Mark of Merit')],
 'bmshiv': ["Wiki: Crude Prison Shiv (Quest)", w('Crude Prison Shiv (Quest)')],
 'gir': ["Wiki: Goblin Island Records", w('Goblin Island Records')],
 'irs': ["Wiki: Island Ruin Stones", w('Island Ruin Stones')],
 'than': ["Wiki: Thanetal's Samples", w("Thanetal's Samples")],
 'rothold': ["Wiki: Rothold", w('Rothold')],
 'cav': ["Wiki faction: Citizens of Ail'Vorith", w("Citizens of Ail'Vorith")],
 'exiles': ["Wiki faction: Ail'vorith Exiles", w("Ail'vorith Exiles")],
 'deepbite': ["Wiki: Cook Deepbite", w('Cook Deepbite')],
 'drezq': ["Wiki: House Drezzorith (Quest)", w("House Drezzorith (Quest)")],
 'jerek': ["Wiki: Head of Jerek D'shadow", w("Head of Jerek D'shadow")],
 'xalfac': ["Wiki faction: House Xal'tharn", w("House Xal'tharn")],
 'sigil': ["Wiki: Sigil of a Lesser House (Gold)", w('Sigil of a Lesser House (Gold)')],
 'ud': ["Wiki: Underdocks", w('Underdocks')],
 'de': ["Wiki: Deep Elf", w('Deep Elf')],
 'pq': ["Wiki: Popular Quests for Faction", w('Popular Quests for Faction')],
 'avwiki2': ["monstersandmemories.wiki: Ail'Vorith (player kill/coin stats)", 'https://monstersandmemories.wiki/zones/ailvorith'],
 'p29': ['Official patch notes 0.29.0.0 (2026-09-10)', 'https://account.monstersandmemories.com/community/patch_notes/44'],
 'p301': ['Official patch notes 0.30.0.1 (2026-09-19)', 'https://account.monstersandmemories.com/community/patch_notes/47'],
 'p302': ['Official patch notes 0.30.2.0 (2026-09-25)', 'https://account.monstersandmemories.com/community/patch_notes/51'],
 'f771': ['Forum: Deep Elf to NH without KoS (2026-09-10/12)', 'https://forum.monstersandmemories.com/d/771-deep-elf-to-nh-without-kos'],
 'f1514': ['Forum: NH factions frozen for Deep elf (2026-10-03/04)', 'https://forum.monstersandmemories.com/d/1514-nh-factions-frozen-for-deep-elf'],
 'f1616': ['Forum: Deep Elf Non-KOS Night Harbor (2026-10-04)', 'https://forum.monstersandmemories.com/d/1616-deep-elf-non-kos-night-harbor'],
 'f1647': ['Forum: Faction Hostility in Night Harbor is broken', 'https://forum.monstersandmemories.com/d/1647-faction-hostility-in-night-harbor-is-broken'],
 'f2007': ["Forum: Citizens of Ail'Vorith rep with our house (2026-10-11)", 'https://forum.monstersandmemories.com/d/2007-citizens-of-ailvorith-rep-with-our-house'],
 'r1': ['Reddit: Dark Elves and Night Harbor (2026-09-24)', 'https://www.reddit.com/r/MonstersAndMemories/comments/1wpcpke/dark_elves_and_night_harbor/'],
 'r2': ["Reddit: Starting Ail'vorith as a new player (2026-09-28)", 'https://www.reddit.com/r/MonstersAndMemories/comments/1ws687w/starting_ailvorith_as_anew_player/'],
}
F, ST, U = 'FACT', 'STRATEGY', 'UNVERIFIED'
def it(label, text, *src, **kw):
    d = {'label': label, 'text': text, 'src': list(src)}; d.update(kw); return d
INQ_MNK = ['Inquisitor', 'Monk']

intro = [
 it(F, "Ail'Vorith is the Deep Elf starting zone (wiki level range 1-50). You start as a 'shadowless' exile who is only welcome in the Foreign Quarter; the starter quest and your class House quest earn your way into the city.", 'av', 'avsq'),
 it(F, "Switch your chat language to Deep Common (right-click the main chat window > Languages), or Deep Elf quest NPCs may not answer you.", 'p29', 'fungal'),
 it(F, "The zone was in its first iteration at the Deep's beta launch: 'a starter zone akin to Evershade Weald, with multiple newbie yards as well as hunting grounds ranging from level 1 to 20 plus strewn about higher level camps (up to 50)'.", 'p29'),
 it(U, "Community reports call Ail'Vorith the hardest of the four starts: Foreign Quarter merchants price badly until you have city access, and it is a long way from the surface hubs.", 'r2'),
]
faction = [
 it(F, "Ail'Vorith city guards (level 50+) are listed as 'KoS to all until you prove yourself (pending changes)'. Your starting parchment warns that entering any district past the Foreign Quarter means 'immediate extermination'. Do not cross into the inner city until your House quest grants access.", 'av', 'avsq', races=['Deep Elf']),
 it(F, "House Xal'tharn Part 1 rewards 'Access to the city (Update 0.30.0.0)'. Klavel Sul also warns that the city guards 'will not suffer an exile to pass the gates'.", 'xal', classes=INQ_MNK),
 it(U, "Forum (2026-10-11): you are KoS to the city before the House quest line. Finishing it gets you to Disdain, which lets you past the guards. Fungal armor turn-ins and killing outcasts raise you further, and 'it doesn't take long' to be able to bank and use vendors.", 'f2007'),
 it(F, "Citizens of Ail'Vorith goes up with the Fungal Armor Quests and by killing Deepgulp goblins. It goes down when you kill Deepcut bandits (Deepcut marksman, basher, miner and others, plus Jorlach the Fearless). The wiki lists the Underdocks as the zone where it can be lowered.", 'cav'),
 it(F, "Provost Xan'shorn: 'the Houses are not in alignment. Pledging with one will earn the scorn of others.' Which House hits which is not listed: no sourced data yet.", 'avsq2'),
 it(U, "Underdocks: several players report it is not KoS for Deep Elves; a forum player says Agnostic Deep Elves are not KoS in either Ail'Vorith or the Underdocks, apart from the city guards. Patch 0.30.2.0 made the relevant Underdocks NPCs speak both Common and Deep Common (that part is FACT).", 'r1', 'f551', 'p302', races=['Deep Elf']),
 it(U, "Faelindral: one forum player (2026-09-18) says 'Deep elves hated everywhere'. There is no Faelindral-specific test in the sources: no sourced data yet beyond that.", 'f551', races=['Deep Elf']),
 it(U, "Other races in Ail'Vorith: a Deep Gnome taken to the Foreign Quarter altar found every NPC there KoS (forum, 2026-09-18). How Goblins or other surface races fare: no sourced data yet.", 'f551'),
 it(ST, "Treat Night Harbor as hostile. Use the Underdocks as your surface hub, and only start a Night Harbor faction grind when you have a group or a friend to buy spells and sell loot for you (what the Reddit and forum posters did). Do not kill Deepcut bandits for Underdocks or Night Harbor rep without knowing they cost you Citizens of Ail'Vorith (wiki faction page).", 'cav', 'r1', 'r2', races=['Deep Elf']),
]
faction = faction[:5] + DE_KOS + faction[5:]
for k in SRC_KOS: S.setdefault(k, S_COMMON[k])
travel = [
 it(F, "The boat stops at docks in a cave under Ail'Vorith and runs to the Underdocks via the Great Cavern Sea and the Caves of Irem. Gate Captain Xaros stands at the last dock before leaving town.", 'av', 'ud'),
 it(F, "You can jump off the Underdocks-Ail'Vorith boat into the Great Cavern Sea, or follow the boat's path on foot and by swimming.", 'gcs'),
 it(U, "Before you have city access: the boat docks under the restricted side of the city. A player reached it by swimming in carefully, then rode the Underdocks elevator up toward Night Harbor (forum 2026-09-10).", 'f771'),
 it(F, "Blind Midden (dungeon) connects to Ail'Vorith. The wiki gives a short route (through the secret wall at Cook Vashuk) and a long route (along the starter-quest tunnel).", 'av', 'bm'),
 it(F, "Rothold (wiki level 30-45) is entered from the western edge of the Great Cavern Sea. Its teleporter NPC was disabled in 0.29.0.0.", 'rothold', 'p29'),
]
money = [
 it(F, "Spell scrolls: 0.29.0.1 made the Foreign Quarter spell vendors 'less greedy'. 0.30.2.0 added a Ranger spell vendor to the Obsidian Academy. From 0.30.2.1 every class pays the same total per 5-level range (4sp 5cp for all of levels 1-5), and 0.30.2.3 and 0.30.2.5 lowered prices again.", 'p291', 'p302', 'p3021', 'p3023', 'p3025'),
 it(U, "Forum (2026-10-03): after the House quest you are Disdain in the upper city and still cannot shop. At Uneasy (about level 10 for that player) the upper-city vendors sell at 'normal' prices. Spells were still 'wacky expensive', and the city has no ingot molds and no hides. Beetle eyes from the cook were nerfed from 70cp to 9cp.", 'f1533'),
 it(F, "Player-tracked coin drops in Ail'Vorith: 3-60 copper per kill, average 9 copper (1,927 kills; most players hunt there at levels 3-18, peak 17).", 'avwiki2'),
 it(F, "House Varros Supplies (repeatable, level 1): Apprentice Esveth pays 25 copper plus XP and House Varros faction per full stack of 20 Bone Chips (decayed skeletons drop them).", 'varsup'),
 it(F, "Deepgulp goblins drop about 5-13 copper. Cook Deepbite (14-15) shares their loot table and can drop a Crude Gatorhide Cap.", 'deepbite'),
 it(F, "Most-gathered resources in Ail'Vorith (player counts): Copper Ore, Resin, Shroomwood, Tin Ore, Ghost Poppy, Lionleaf and Brittle Stone, with Silver Ore and chipped gems more rarely.", 'avwiki2'),
 it(F, "Blind Midden: /take crate near Custodian Merique has given 1 silver, Copper Ore, a Crude Prison Shiv, a Smuggled Wand or a Charred Mudfish.", 'bm'),
 it(F, "Goblin Island Records (level 19, Great Cavern Sea) pays 5 silver and 3 Velgarrith Diver's Draughts (not repeatable).", 'gir'),
 it(ST, "Sell loot only once you can reach normal city vendors (after your House quest). Until then keep mats and vendor trash in your bags. The Foreign Quarter 'swindle' prices are a community report.", 'r2', 'f2007'),
]
trainers = {
 'Inquisitor': {'npc': 'Nurvol Cereveth', 'where': 'Foreign Quarter, most likely the Military Outpost with the other melee trainers; check the Obsidian Academy if he is not there', 'src': ['av', 'nurvol', 'avh', 'nurvolh'], 'label': U,
                'note': "UNVERIFIED. The same editor added both wiki pages on 2026-10-17. The zone page's trainer table (rev 82862, 23:18 UTC) says Military Outpost, but the NPC page (created 22:57 UTC, re-edited 23:30 UTC) still says Obsidian Academy. The zone page wins for now because it places him with Klavel Sul, the other Xal'tharn (Inquisitor/Monk) NPC, but it is not settled. Scrolls: patch 0.29.0.1 made 'Foreign Quarter spell vendors' less greedy, and the official guide says scrolls are sold near your class guild hall. The NPC who sells Inquisitor scrolls is not named in any source: no sourced data yet. Buy each spell when you reach its level (list per band below)."},
 'Monk': {'npc': 'Klavel Sul', 'where': 'Military Outpost, Foreign Quarter: the building on the left past the Foreign Quarter bridge and gate, back of the room with the melee trainers', 'src': ['av', 'klavel', 'klavel2', 'xal'], 'label': F,
          'note': "Resolved: the NPC page (rev 82871, 2026-10-17) and the zone page both say Military Outpost, and the fan wiki says 'room with Melee Trainers'. The quest page's 'Obsidian Academy' dates from its first version (2026-09-23) and describes the same room (the building on the left, with the melee instructors), whose melee trainers the zone page lists in the Military Outpost."},
 'Archer': {'npc': 'Lurithos Kest', 'where': 'Military Outpost', 'src': ['av'], 'label': F},
 'Ranger': {'npc': "Laren Drin'dar", 'where': 'Military Outpost', 'src': ['av'], 'label': F},
 'Fighter': {'npc': 'Tharkan Inathar', 'where': 'Military Outpost', 'src': ['av'], 'label': F},
 'Paladin': {'npc': 'Mentvar Drezzorith', 'where': 'Military Outpost, 2nd floor', 'src': ['av'], 'label': F},
 'Spellblade': {'npc': "Ilnara Hal'kareth", 'where': 'Military Outpost, 2nd floor', 'src': ['av'], 'label': F},
 'Enchanter': {'npc': "Amarah Ith'vayen", 'where': 'Obsidian Academy', 'src': ['av'], 'label': F},
 'Necromancer': {'npc': 'Vaslir Naiyth', 'where': 'Obsidian Academy', 'src': ['av'], 'label': F},
 'Cleric': {'npc': 'Zalethra Drezzorith', 'where': 'Obsidian Academy, 2nd floor', 'src': ['av'], 'label': F},
 'Elementalist': {'npc': 'Lothur Varros', 'where': 'Obsidian Academy, 2nd floor', 'src': ['av'], 'label': F},
 'Wizard': {'npc': "Vhasilla Hal'kareth", 'where': 'Obsidian Academy, 2nd floor', 'src': ['av'], 'label': F},
 'Shadow Knight': {'npc': 'Vhalrek Velgarrith', 'where': 'Under the Inn in the Foreign Quarter', 'src': ['av'], 'label': F},
 'Rogue': {'npc': 'Zorvanna Velgarrith', 'where': 'Under the Inn in the Foreign Quarter', 'src': ['av'], 'label': F},
}
Q = {}
Q['avsq'] = {
 'name': "Ail'Vorith Starter Quest", 'wiki': "Ail'Vorith Starter Quest", 'helper': True, 'giver': 'Toilmaster Verith or Toilmistress Rallvessa',
 'where': 'A few feet from where new Deep Elves spawn, outside the Foreign Quarter footbridge', 'level': '1', 'classes': [], 'tag': 'Recommended',
 'why': 'Required: the Obsidian Shackle it gives unlocks every House class quest, and through them city access.',
 'prereq': "New Deep Elf character started in Ail'Vorith (you spawn holding the Imbued Parchment). Set chat language to Deep Common.",
 'faction': 'No faction change listed on the wiki pages: no sourced data yet.',
 'steps': [
  {'text': 'Read the Imbued Parchment and hand it to Toilmaster Verith or Toilmistress Rallvessa.'},
  {'text': "Use /look crate and /take pickaxe on the crate labelled REPAIRED to get a Slave Pickaxe (the BROKEN crate's pickaxe fails and Verith slaps you for 2 damage). Hand it in; it is given back."},
  {'text': 'Go south into the water and follow the wall right to a small quarry cave. Equip the pickaxe and mine 20 Fragile Quarry Rock (nodes respawn in 5-10 seconds).'},
  {'text': 'Hand in the 20 rock and the pickaxe for a Pack of Stone (you become encumbered). Carry it across the footbridge to Supplier Jul, the first building on the left in the Foreign Quarter.'},
  {'text': "Agree to make sharpening stones ('I will do it'). You get a Sharpening Stone Satchel and Recipe: Fragile Sharpening Stone (right-click to learn). Take 5-8 Fragile Quarry Rock from the crate next to Jul (/take rock)."},
  {'text': 'Through the market gate, right through the tunnel, right fork, first building on the right: use the grinding wheel by Blacksmith Zorvek to make 5 Fragile Sharpening Stones. Put them in the satchel and combine.'},
  {'text': 'Return the Full Sharpening Stone Satchel to Jul for the Sharpening Stone Delivery Satchel, then give it to Verith. Answer that you made them, then that you are prepared, to receive a Small Leather Hunting Satchel.'},
  {'text': 'Hunt the newbie yard for 2 each: Bone Chips (a decayed skeleton), Deep Beetle Legs (a small beetle, a deep beetle), Damaged Fungus Cap (a cave sporeling). Put them in the satchel in single stacks and combine.'},
  {'text': 'Hand the Filled Leather Hunting Satchel to Verith for the Satchel of Questionable Spoils. Deliver it to Cook Vashuk (inn past the courtyard fountain, back-right doorway, downstairs, kitchen).'},
  {'text': "Hail Verith, say Yes to rejoining the Houses, and take Verith's Recommendation to Provost Xan'shorn (walks in circles on the left of the courtyard)."},
  {'text': 'He clasps the Obsidian Shackle on your wrist. Enter the Obsidian Academy and find your House representative (see the House quest for your class).'},
 ],
 'mobs': [{'item': 'Fragile Quarry Rock x20', 'from': 'Stone Ore veins in the quarry cave (mining)'}, {'item': 'Bone Chips x2', 'from': 'a decayed skeleton (2-3)'},
          {'item': 'Deep Beetle Legs x2', 'from': 'a small beetle (2-3), a deep beetle (3-4)'}, {'item': 'Damaged Fungus Cap x2', 'from': 'a cave sporeling (2-3)'}],
 'turnin': "Provost Xan'shorn, Foreign Quarter courtyard",
 'rewards': {'xp': 'Experience at several steps', 'item': 'Obsidian Shackle (wrist: AC 1, HP +5, Mana +5; magic, unique, no drop)', 'coin': 'none listed', 'faction': 'none listed'},
 'src': ['avsq', 'avsq2'], 'label': F}
Q['xal'] = {
 'name': "House Xal'tharn (Quest)", 'wiki': "House Xal'tharn (Quest)", 'helper': True, 'giver': 'Klavel Sul',
 'where': 'Foreign Quarter, Military Outpost: the building on the left past the bridge and gate, back of the room with the melee trainers (the quest page calls it the Obsidian Academy; see the Monk trainer note)', 'level': 'Part 1: 8+, Part 2: 13+',
 'classes': INQ_MNK, 'tag': 'Recommended', 'why': 'Your class House quest: chest armor at 8, city access, House Xal\'tharn faction and the Iron Render weapon.',
 'prereq': "Obsidian Shackle from the Ail'Vorith Starter Quest. Deep Common language.",
 'faction': "Part 1 grants city access (wiki). Part 2 turn-in: 'You gain faction with House Xal'tharn'. Other faction hits are marked as unknown on the wiki: no sourced data yet.",
 'steps': [
  {'text': "Part 1 (8+): hail Klavel Sul; say 'The Queen', then 'I would be a cenobite', then 'Do you have a task for me?'. You receive the Remnant Satchel (6 slots)."},
  {'text': 'Swim around the west of the city, where elementals and skulls patrol the west island shores. Kill a separated skull and a spectral remnant (both 8-11) for 6 Lost Skull.'},
  {'text': "Combine the satchel and hand it to Klavel Sul (XP). Say 'I swear allegiance to the Queen!' (XP). Inquisitors receive the Dull Iron Cuirass; Monks the Simple Chestwrap."},
  {'text': "Part 2 (13+): before 13, Klavel says you lack the skill. At 13, hail him and say 'I accept.' He gives a summons for Lady Miniel in the Shol'tar, beneath the Queen's arena: take the road on the right into the Dark City and go through the dungeon gates near the bank."},
  {'text': "Give the summons to Miniel Ubast in the Inquisitor's Guildhall (NPC page: enter the main city, turn right, up the ramp, the prison guarded by Inquisitors, up one floor and through the door). Ask about the duty and where the exiles are."},
  {'text': 'Go to the exile camps to the south, by the river into the Great Cavern Sea: past the waterfall where snakes gather, on the bottom floor past the invisible hired thug. Kill exiles until you have one each of the Unknown, Silver and Gold Sigil of a Lesser House (unique: one of each).'},
  {'text': "Keep killing the bottom-floor exiles until Gullach Otal'qar (16-17, named Fighter) spawns in their place, then kill him for Gullach's Head."},
  {'text': 'Hand the 3 sigils and the head to Miniel Ubast.'},
 ],
 'mobs': [{'item': 'Lost Skull x6', 'from': 'a separated skull (8-11, Enchanter: Mesmerize, Silence), a spectral remnant (8-11, Fighter), west island shores'},
          {'item': 'Sigil of a Lesser House (Unknown, Silver, Gold)', 'from': 'exiles: a starving outcast, a runaway, a praying exile (exile mobs are 15-22)'},
          {'item': "Gullach's Head", 'from': "Gullach Otal'qar (16-17), bottom floor of the exile area behind the hired thug"}],
 'turnin': "Part 1: Klavel Sul. Part 2: Miniel Ubast (Shol'tar, inside the city)",
 'rewards': {'xp': 'XP at both Part 1 turn-ins and at the Part 2 turn-in', 'item': 'Inquisitor: Dull Iron Cuirass (chest AC 9, STA +1, INT +1, HP +5) and Iron Render (1H slash 7/30, STR +2, STA +1, INT +1, HP +5, Mana +5). Monk: Simple Chestwrap and Tarnished Iron Bo.', 'coin': 'none listed', 'faction': "City access (Part 1); House Xal'tharn + (Part 2)"},
 'src': ['xal', 'klavel', 'miniel', 'sigil'], 'label': F,
 'notes': [it(F, "Reward conflict resolved, Cuirass wins. The quest page listed a Xal'tharn Pendant from its first version (2026-09-23, beta 0.30.0.0) until rev 78132 (2026-10-07, after the 0.30.2.1 release patch), when an editor replaced it with the Dull Iron Cuirass for Inquisitors. That editor created the Dull Iron Cuirass item page with full stats four minutes later. The Pendant item page was last touched 2026-09-26, and the Ail'Vorith Class Quests summary page that still says Pendant was never updated. The newer first-hand edit with an item page wins over the older summary.", 'xal', 'xalh', 'cuirass', 'pendant', 'avcq'),
           it(U, "Whether Monks (or pre-release characters) still get the Pendant as well: no sourced data yet. No talk page exists for the quest.", 'xal', 'pendant'),
           it(ST, "Do Part 2 at about 15-17, not 13: the sigil exiles are 15-22 and Gullach is 16-17 (wiki levels). Bring a group or a healer.", 'av')]}
Q['fungal'] = {
 'name': 'Fungal Armor Quests', 'wiki': 'Fungal Armor Quests', 'helper': True, 'giver': 'Leatherworker Vex', 'where': "Foreign Trader's Market, Foreign Quarter", 'level': '5',
 'classes': [], 'tag': 'Recommended', 'why': 'Four armor pieces for 14 classes, including Inquisitor, plus Citizens of Ail\'Vorith faction toward banking and vendors.',
 'prereq': "Deep Common language. The class list on the items is ARC BRD BST CLR DRU FTR INQ MNK PAL RNG ROG SHD SHM SPB (no pure casters).",
 'faction': "Each piece: House Velgarrith + and Citizens of Ail'Vorith + (wiki).",
 'steps': [
  {'text': "Hail Leatherworker Vex, then ask 'What is something that could keep me alive longer?' and say 'I seek protection.'"},
  {'text': "Ask 'What Coat?', 'What Helm?', 'What Leggings?' or 'What Boots?' for each piece's recipe."},
  {'text': 'Coat: 3 Perfect Fungus Cap, 2 Strong Fungus Hyphea, 1 Perfect Fungus Stem. Helm: 2 Cap, 1 Hyphea. Leggings: 2 Stem, 2 Hyphea, 2 Perfect Fungus Volva. Boots: 2 Volva, 2 Hyphea.'},
  {'text': 'Hand each set of parts to Vex to receive that piece (XP and faction each).'},
 ],
 'mobs': [{'item': 'Full set: 7 Strong Fungus Hyphea, 5 Perfect Fungus Cap, 4 Perfect Fungus Volva, 3 Perfect Fungus Stem', 'from': 'a cave myconid (5-7)'}],
 'turnin': 'Leatherworker Vex', 'rewards': {'xp': 'Experience per piece', 'item': 'Fungal Coat (AC 7), Fungal Helm (AC 5), Fungal Leggings (AC 6), Fungal Boots (AC 4)', 'coin': 'none listed', 'faction': "House Velgarrith +, Citizens of Ail'Vorith +"},
 'src': ['fungal', 'fcoat'], 'label': F}
Q['varsup'] = {
 'name': 'House Varros Supplies', 'wiki': 'House Varros Supplies', 'helper': True, 'giver': 'Apprentice Esveth', 'where': 'Obsidian Academy courtyard, under a light post across from the academy',
 'level': '1 (repeatable)', 'classes': [], 'tag': 'Optional', 'why': 'Small steady coin (25 copper a stack) from Bone Chips you pick up anyway. It raises House Varros, and pledging one House can anger others, so non-Varros classes may want to skip it (UNVERIFIED).',
 'prereq': 'Deep Common language.', 'faction': 'House Varros + per stack.',
 'steps': [{'text': 'Hand Apprentice Esveth a full stack of 20 Bone Chips (a single chip is refused).'}, {'text': 'Ghoul Skin and corpse turn-ins are listed but undocumented: no sourced data yet.', 'label': U}],
 'mobs': [{'item': 'Bone Chips x20', 'from': 'a decayed skeleton (2-3) and other skeletons'}], 'turnin': 'Apprentice Esveth',
 'rewards': {'xp': 'Experience', 'item': 'none', 'coin': '25 copper per 20 Bone Chips', 'faction': 'House Varros +'}, 'src': ['varsup'], 'label': F}
Q['survey'] = {
 'name': 'Survey the Creatures of the Cavern Sea', 'wiki': 'Survey the Creatures of the Cavern Sea', 'helper': True, 'giver': "Sereth Vael'xirith",
 'where': "Great Cavern Sea, the outpost right outside Ail'Vorith (turn right as you enter the zone)", 'level': '16 (recommended 15)', 'classes': [], 'tag': 'Recommended',
 'why': 'Quick neck upgrade (AC 2, HP +10, Mana +10). All targets are visible from the quest giver.', 'prereq': 'None listed.', 'faction': "House Vael'xirith +",
 'steps': [{'text': "Hail Sereth and ask 'What watch line?', then say 'I will do a survey.'"}, {'text': 'Kill a shore beetle, a shelter bat and a shallows basilisk near the outpost for 4 Shore Beetle Samples, 3 Shelter Bat Wings and 2 Shallows Basilisk Scales.'}, {'text': 'Hand all of them in at once; a partial count is refused.'}],
 'mobs': [{'item': '4 Shore Beetle Sample, 3 Shelter Bat Wing, 2 Shallows Basilisk Scale', 'from': 'a shore beetle (15), a shelter bat (16), a shallows basilisk (17), all visible from Sereth'}],
 'turnin': "Sereth Vael'xirith", 'rewards': {'xp': 'Experience', 'item': "Shore Surveyor's Charm", 'coin': 'none listed', 'faction': "House Vael'xirith +"}, 'src': ['survey', 'gcs', 'shoreb', 'shelb', 'shalb'], 'label': F,
 'notes': [it(F, "Mob levels come from the wiki mob pages, written on 2026-10-09 by the same editor who wrote the walkthrough. The quest's minimum is 16 and the zone page recommends 15, which matches 15-17 targets.", 'shoreb', 'shelb', 'shalb', 'survey')]}
Q['gir'] = {
 'name': 'Goblin Island Records', 'wiki': 'Goblin Island Records', 'helper': False, 'giver': 'Halveth Velgarrith', 'where': "Great Cavern Sea outpost outside Ail'Vorith", 'level': '19 (recommended 20-25)',
 'classes': [], 'tag': 'Optional', 'why': 'Coin (5 silver) and water-breathing draughts for the sea, if you hunt goblin island anyway.', 'prereq': 'None listed. Not repeatable.', 'faction': 'House Halveth Velgarrith + (as written on the wiki)',
 'steps': [{'text': 'Hail Halveth Velgarrith and accept.'}, {'text': 'Kill a goblin stone-sorter (22-23) on the bony goblin island for 4 Bundle of Copied Marks.'}, {'text': 'Hand in the 4 bundles.'}],
 'mobs': [{'item': 'Bundle of Copied Marks x4', 'from': 'a goblin stone-sorter (22-23)'}], 'turnin': 'Halveth Velgarrith',
 'rewards': {'xp': 'Experience', 'item': "3 Velgarrith Diver's Draught", 'coin': '5 silver', 'faction': 'House Halveth Velgarrith +'}, 'src': ['gir', 'gcs'], 'label': F}
Q['irs'] = {'name': 'Island Ruin Stones', 'wiki': 'Island Ruin Stones', 'helper': False, 'giver': "Isrothen Vael'xirith", 'where': "Great Cavern Sea outpost outside Ail'Vorith", 'level': 'not listed',
 'classes': [], 'tag': 'Optional', 'why': 'Reward unknown on the wiki.', 'prereq': 'None listed.', 'faction': 'no sourced data yet',
 'steps': [{'text': 'Look over the marked stones in three places in the goblin-worked island ruins, then report back at the docks.'}, {'text': 'Further steps: no sourced data yet.', 'label': U}],
 'mobs': [], 'turnin': "Isrothen Vael'xirith", 'rewards': {'xp': 'no sourced data yet', 'item': 'no sourced data yet', 'coin': 'no sourced data yet', 'faction': 'no sourced data yet'}, 'src': ['irs'], 'label': F}
Q['merit'] = {'name': 'Mark of Merit', 'wiki': 'Mark of Merit', 'helper': True, 'giver': "Receptionist Naleth'ra", 'where': 'Blind Midden ground floor (map point 1)', 'level': '1 (repeatable)',
 'classes': [], 'tag': 'Optional', 'why': 'XP and Marks of Merit for the Midden Mark Menu while you clear Blind Midden named mobs.', 'prereq': 'None listed.', 'faction': 'no sourced data yet',
 'steps': [{'text': 'Kill any named mob in Blind Midden and loot its corpse item (no drop).'}, {'text': "Turn the corpse in to Receptionist Naleth'ra."}],
 'mobs': [{'item': 'Corpse of <named>', 'from': 'any Blind Midden named (top floor named are 7-12, basement named 15+)'}], 'turnin': "Receptionist Naleth'ra",
 'rewards': {'xp': 'Experience', 'item': 'Blind Midden Mark of Merit (Midden Mark Menu rewards are random)', 'coin': 'none listed', 'faction': 'no sourced data yet'}, 'src': ['bmmerit', 'bm'], 'label': F}
Q['shiv'] = {'name': 'Crude Prison Shiv (Quest)', 'wiki': 'Crude Prison Shiv (Quest)', 'helper': True, 'giver': 'Kalessa Velgarrith', 'where': 'Just inside Blind Midden, opposite Nibs Mudknuckle', 'level': 'not listed',
 'classes': [], 'tag': 'Optional', 'why': 'House Unheard faction grind (about 125 shivs from Indifferent to Amicable, per the wiki); 10 copper each. Only worth it if you want Blind Midden faction.', 'prereq': 'Reputation gate with House Unheard (exact level unknown).', 'faction': 'House Unheard +',
 'steps': [{'text': 'Buy the Shale Hilt and Crude Prison Shiv recipes from Kalessa.'}, {'text': 'Use /take water by any Blind Midden water for Shale Chunks and Rusty Metal Shards, then craft a shiv.'}, {'text': 'Hand in a Crude Prison Shiv.'}],
 'mobs': [], 'turnin': 'Kalessa Velgarrith', 'rewards': {'xp': 'Experience', 'item': 'none', 'coin': '10 copper', 'faction': 'House Unheard +'}, 'src': ['bmshiv'], 'label': F}
Q['than'] = {'name': "Thanetal's Samples", 'wiki': "Thanetal's Samples", 'helper': True, 'giver': 'Thanetal (Deep Gnome)', 'where': 'Paths to the Foreign Quarter, beyond the cultists', 'level': '1 (zone page lists Thanetal as 13+)',
 'classes': ['Cleric', 'Paladin'], 'tag': 'Optional', 'why': 'Only useful for House Drezzorith (Cleric and Paladin): the samples are used in that quest.', 'prereq': 'One Deep Beer (where to buy it: no sourced data yet) and 10 silver.', 'faction': 'no sourced data yet',
 'steps': [{'text': 'Hand Thanetal 1 Deep Beer and 10 silver pieces.'}], 'mobs': [], 'turnin': 'Thanetal',
 'rewards': {'xp': 'no sourced data yet', 'item': '6 Sample of Mind Control Substance', 'coin': 'costs 10 silver', 'faction': 'no sourced data yet'}, 'src': ['than'], 'label': F}
# other class House quests: steps come from the quest helper data (wiki walkthroughs)
for qid, title, cls, why in [
 ('drez', 'House Drezzorith (Quest)', ['Cleric', 'Paladin'], 'Your class House quest (city access, the Lexicon of Mysteries line for Clerics).'),
 ('ith', "House Ith'vayen (Quest)", ['Enchanter', 'Rogue'], 'Your class House quest (belt reward, city access).'),
 ('hal', "House Hal'kareth (Quest)", ['Spellblade', 'Wizard'], "Your class House quest (Hal'kareth Signet Ring)."),
 ('vael', "House Vael'xirith (Quest)", ['Archer', 'Ranger'], 'Your class House quest.'),
 ('varros', 'House Varros (Quest)', ['Elementalist', 'Necromancer'], 'Your class House quest (House Varros faction).'),
 ('velg', 'House Velgarrith (Quest)', ['Shadow Knight'], 'Your class House quest (Frayed Cloak of House Velgarrith).'),
 ('gems', 'Stolen Gems', ['Ranger', 'Archer', 'Fighter'], 'Class weapon (Legion Recurve or Legion Longsword) from goblin camp gems.')]:
    Q[qid] = {'auto': title, 'classes': cls, 'tag': 'Recommended', 'why': why, 'src': ['avcq', 'av']}

bands = [
 {'lo': 1, 'hi': 5, 'title': "Newbie yard and the starter quest", 'steps': [
   it(F, "Do the Ail'Vorith Starter Quest from the spawn point: quarry rock, then Supplier Jul, the grinding wheel, the newbie-yard hunt, Cook Vashuk and the Provost.", 'avsq', quest='avsq'),
   it(F, 'Newbie yard mobs (wiki levels): a small beetle 2-3, a decayed skeleton 2-3, a cave sporeling 2-3, a deep beetle 3-4, a juvenile snake 3-4. An aspirant wanders the yard fighting other mobs.', 'av'),
   it(F, 'Trainer', 'av', trainer=True),
   it(ST, "Stay in the Foreign Quarter and the newbie yard. Do not cross into the inner city: it is KoS until your House quest.", 'av', 'avsq'),
   it(F, 'Optional coin: save Bone Chips in stacks of 20 for House Varros Supplies.', 'varsup', quest='varsup'),
   it(F, 'Blind Midden ground floor has 3-4 mobs (a sullen outcast, sentient sewage and others). Almost nothing on the ground floor is KoS except the deep gnome NPCs and sentient sewage.', 'bm'),
 ]},
 {'lo': 6, 'hi': 10, 'title': 'Fungal armor, House quest Part 1, Blind Midden top floor', 'steps': [
   it(F, "Start your class House quest with your Obsidian Shackle (Obsidian Academy or Military Outpost).", 'avcq', quest='xal', classes=INQ_MNK),
   it(F, 'House quest for your class:', 'avcq', quest='drez', classes=['Cleric', 'Paladin']),
   it(F, 'House quest for your class:', 'avcq', quest='ith', classes=['Enchanter', 'Rogue']),
   it(F, 'House quest for your class:', 'avcq', quest='hal', classes=['Spellblade', 'Wizard']),
   it(F, 'House quest for your class:', 'avcq', quest='vael', classes=['Archer', 'Ranger']),
   it(F, 'House quest for your class:', 'avcq', quest='varros', classes=['Elementalist', 'Necromancer']),
   it(F, 'House quest for your class:', 'avcq', quest='velg', classes=['Shadow Knight']),
   it(F, "From level 5: farm cave myconids (5-7) for the Fungal Armor Quests.", 'fungal', quest='fungal'),
   it(F, 'Camps (wiki levels): a cave myconid 5-7, a bubbling oozeling 5-7, a Deepgulp runt and a Deepgulp explorer 6-7 (their kills raise Ail\'vorith Exiles), a skeleton 6-7, a cave snake 7-9, cultists 6-7 (cave along the water\'s edge, right of the Toilmaster).', 'av', 'exiles', 'drezq'),
   it(F, "At 8+: the west island shores (swim around the west of the city) have a separated skull and a spectral remnant (8-11) for Xal'tharn Part 1, plus elementals and spirits (9-11).", 'xal', 'av', classes=INQ_MNK),
   it(F, 'Blind Midden top floor: 6-7 prisoners and outcasts, and named mobs at level 7 (Gorgeous, Flavic the Fisher, Mucky Morgurah, Forager Davra, Sethrine the Unblinking) with gear drops.', 'bm', quest='merit'),
   it(ST, "Order: fungal pieces while you level on myconids (5-8), then Xal'tharn Part 1 at 8-9 for the Dull Iron Cuirass and city access. Visit Nurvol Cereveth every time you reach a spell level.", 'fungal', 'xal', classes=['Inquisitor']),
 ]},
 {'lo': 11, 'hi': 15, 'title': 'Goblins, spirits, House quest Part 2 begins', 'steps': [
   it(F, "Camps (wiki levels): spirits and elementals 9-11 (a torn spirit, a wandering soul, a forsaken soul, rogue/stray/swift elementals), a failed experiment 10-11, Deepgulp warrior/scavenger/hunter 10-11, Deepgulp berserker/mystic 12-13, a floating skull 13-15.", 'av'),
   it(F, "Named: Gloweye 10-11 (Deepgulp goblin camp), The Discarded 10+ (lighthouse: Uneven Mantle, Shroomwood Staff, Rough-Forged Leggings), Bubbles 10+ (oozes by the deep gnome researchers: Charming Talisman, Cave Mitts), Cook Deepbite 14-15 (back of the Deepgulp caves: Crude Gatorhide Cap).", 'av', 'deepbite'),
   it(F, "Deepgulp kills raise Citizens of Ail'Vorith and Ail'vorith Exiles (and lower Clan Deepgulp).", 'cav', 'exiles', 'deepbite'),
   it(F, "At 13: Klavel Sul sends you to Miniel Ubast in the Shol'tar for Xal'tharn Part 2 (needs the city access from Part 1).", 'xal', quest='xal', classes=INQ_MNK),
   it(F, "Stolen Gems (min level 10, Archer/Ranger/Fighter): goblin camp gems for a class weapon.", 'avcq', quest='gems', classes=['Ranger', 'Archer', 'Fighter']),
   it(F, 'Blind Midden: 10-13 mobs on the top floor, named at 12 (Underboss Vekrizin, Cedrius the Cutter, Blacksmith Jerictus, Wikket Two-Wands, Reviver Vlarek, Mother Gummer). Basement named start at 15.', 'bm', quest='merit'),
   it(U, "Great Cavern Sea, Blacktide Orc Cove: a Blacktide hauler, hull hauler and lookout (11-14?), a cargo guard (15-17?), Morgak Foamscar (15-17?). The question marks are the wiki's own; the mob pages have no levels (rev 83094, 2026-10-18), so this is still unresolved. Morgak's page adds one FACT: he dropped Blacktide Chain Leggings (AC 13, STR +2, STA +2).", 'gcs', 'morgak'),
   it(F, 'Great Cavern Sea, player-tracked: hunting levels 16-24, most at 17; coin per kill 8cp-2sp 25cp, average 87cp (361 kills). This is the best measured range for the zone as a whole, not per camp.', 'mwgcs'),
   it(U, "Surface option: wererats outside the Underdocks (wiki 10-12) were used for Night Harbor faction (forum). Do not kill Deepcut bandits: they lower Citizens of Ail'Vorith (wiki).", 'f1616', 'ud', 'cav', races=['Deep Elf']),
 ]},
 {'lo': 16, 'hi': 20, 'title': 'Exile caves, Cavern Sea outpost quests', 'steps': [
   it(F, "Exile caves and islands near the Great Cavern Sea entrance: a starving outcast, a hired thug (invisible), an injured runaway, a hunted exile (sees invisible) 15-22; a praying exile (Cleric, sees invisible), an Ail'trist reject and an Ail'trist believer 20-22.", 'av'),
   it(F, "Named: Gullach Otal'qar 16-17 (Gullach's Head), Jerek D'shadow 16 (his head is used in House Ith'vayen), Nyxa'ira 20-21 (Balanced Chain Hood), Bonescraper Zekkir 20+.", 'av', 'jerek'),
   it(F, "Finish Xal'tharn Part 2 here: 3 sigils plus Gullach's Head for the Iron Render.", 'xal', quest='xal', classes=INQ_MNK),
   it(F, "Survey the Creatures of the Cavern Sea (16) at the outpost just outside Ail'Vorith.", 'survey', quest='survey'),
   it(F, "Great Cavern Sea: Boss Gurrok 18 (Gurrok's Barnacled Dagger, Diving Harness, Diving Boots); Overseer Vashruk 20? (Blacktide Order Packet).", 'gcs'),
   it(F, 'Blind Midden basement: named at 15 (Enthraller Gnorah, Flashfreeze Fraegra, Biomass, Gelmother Jiggol, Ferg the Filthy and more), mobs 15-19, Skizik the Schemer 19. From the top floor almost everything there is KoS except the eyeballs; from the back entrance most things are not, except rats and ghosts.', 'bm', quest='merit'),
   it(U, "Killing outcasts 'will help out in a big way' with Citizens of Ail'Vorith (forum, 2026-10-11).", 'f2007'),
 ]},
 {'lo': 21, 'hi': 25, 'title': 'Goblin island and the Caves of Irem', 'steps': [
   it(F, 'Great Cavern Sea goblin island (bony architecture): a camp raider 19-23, a goblin shoreguard 21, a goblin diver and stone-sorter 22-23; named Foreman Vikkit, Skerrick and Tibbek (19-24?). Wasp and Beetle Island: a strand beetle 22-23, a strand wasp 24-26.', 'gcs'),
   it(F, 'Goblin Island Records (19) from Halveth Velgarrith; Island Ruin Stones from Isrothen Vael\'xirith (same outpost).', 'gir', 'irs', quest='gir'),
   it(F, 'Island Ruin Stones:', 'irs', quest='irs'),
   it(F, "Caves of Irem: a lake-fed razorwing 22-23, a Skri'Var tracker 23-25, a Skri'Var war beetle 24, Grukk'Tal the Ravener 24 (Rat Beach), Swarmcaller Skarr'Vokk 25.", 'irem'),
   it(F, "Ail'Vorith: fanatic cultists (watcher, warrior, cultist, priestess, over 21, KoS) are left at the goblin bridge; an enslaved elf 23-24.", 'av'),
   it(F, 'Blind Midden: King Jekom the Ancient 22; Andrew the Framed and Red Hands Ellison (over 20) in the basement back entrance.', 'bm'),
 ]},
 {'lo': 26, 'hi': 30, 'title': 'Basilisks, spiders, Pyramid Road', 'steps': [
   it(F, 'Great Cavern Sea: a recess basilisk 27-28 (Basilisk Island), a strand spider 29-30 (Spider Cave). The Great Cavern Sea Spider Caves quest is recommended for 30-35? (wiki, giver Mae\'vith Ith\'vayen; no walkthrough page yet).', 'gcs'),
   it(F, "Ail'Vorith: spiders on the ledge after the fanatics (a predatory spider ~26 invisible, a venerated spider 28, a dark widow 30, all KoS).", 'av'),
   it(F, "Caves of Irem Pyramid Road: a parched skeleton 25, a dire jackal 25, wisps, spectres, asps and creepers ~27, Sael'vyrin 30.", 'irem'),
   it(F, 'Blind Midden: Chaplain Cranely (over 25), in the altar room behind the slimes.', 'bm'),
 ]},
 {'lo': 31, 'hi': 40, 'title': 'Rothold and the Roostbound giants', 'steps': [
   it(F, 'Rothold (wiki level 30-45), entered from the western edge of the Great Cavern Sea.', 'rothold'),
   it(F, 'Caves of Irem: Nurabek Brinehand 35 (Green Lake), Highblade 36 and Vashkur Roostbound 37 (Roostbound Giants).', 'irem'),
   it(U, "Reddit (2026-09-28): you can reach Blacktide Bay from the Deep side and be 'set till 35'. The wiki adjacency lists do not show that link: no sourced data yet.", 'r2'),
 ]},
 {'lo': 41, 'hi': 60, 'title': 'Pyramid Ruins', 'steps': [
   it(F, 'Caves of Irem Pyramid Ruins: enthralled mercenaries, explorers, rangers and casters (~40+), an enthralled giant ~45, Baron Xio 44 (Lensed Horn Bow, Clouded Mail Gauntlets, Clear Lens Blade).', 'irem'),
   it(U, 'Above about 45: no sourced Deep route yet (the wiki lists Vhaleth Hal\'kareth, level 60, in the Great Cavern Sea as a named mob, not a camp).', 'gcs'),
 ]},
]
D = {'city': "Ail'Vorith", 'slug': 'ailvorith', 'status': 'sourced', 'updated': '2026-10-18', 'researched': '2026-10-18 22:00 America/New_York',
     'generated_by': 'tools/startcity_ailvorith.py', 'sources': S, 'intro': intro, 'faction': faction, 'travel': travel, 'money': money,
     'trainers': trainers, 'quests': Q, 'bands': bands}
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'startcities', 'ailvorith.json')
json.dump(D, open(out, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print('wrote', out, sum(len(b['steps']) for b in bands), 'steps', len(Q), 'quests')

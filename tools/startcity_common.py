"""Shared pieces for the start-city generators (tools/startcity_*.py): label helpers, common sources, the Deep Elf
Night Harbor KoS block (shown for a Deep Elf in every start city, not only Ail'Vorith), the player-tracked zone stats from
monstersandmemories.wiki, and the shared surface mid-level route (levels 16-60) that Night Harbor, the Underdocks and
Faelindral all lead into. Researched 2026-10-18 (America/New_York). Every line: FACT = wiki or official page,
STRATEGY = this Codex's suggestion, UNVERIFIED = community report, conflicting or missing data."""
import json, os
W = 'https://monstersandmemories.miraheze.org/wiki/'
def w(t): return W + t.replace(' ', '_').replace("'", '%27')
F, ST, U = 'FACT', 'STRATEGY', 'UNVERIFIED'
def it(label, text, *src, **kw):
    d = {'label': label, 'text': text, 'src': list(src)}; d.update(kw); return d
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'startcities')
QS = json.load(open(os.path.join(OUT, '..', 'quest_steps.json'), encoding='utf8'))

def write(D):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, D['slug'] + '.json')
    json.dump(D, open(p, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print('wrote', p, D['status'], sum(len(b['steps']) for b in D['bands']), 'steps', len(D['quests']), 'quests')

# ---- sources used by more than one city
S_COMMON = {
 'faq': ['Official Early Access FAQ (starting areas)', 'https://monstersandmemories.com/early-access-faq'],
 'npg': ['Official New Player Guide (scrolls are sold near your class guild hall)', 'https://monstersandmemories.com/new-player-guide'],
 'start': ['Wiki: Starting City by Race, Class, and Deity', w('Starting City by Race, Class, and Deity')],
 'hunt': ['Wiki: Per-Level Hunting Guide (rev 73595, 2026-09-22; marked work in progress)', w('Per-Level Hunting Guide')],
 'qs': ['Wiki quest walkthroughs (quest helper)', '/quest-helper.html'],
 'p29': ['Official patch notes 0.29.0.0 (2026-09-10)', 'https://account.monstersandmemories.com/community/patch_notes/44'],
 'p291': ['Official patch notes 0.29.0.1 (2026-09-11)', 'https://account.monstersandmemories.com/community/patch_notes/45'],
 'p300': ['Official patch notes 0.30.0.0 (2026-09-19)', 'https://account.monstersandmemories.com/community/patch_notes/46'],
 'p302': ['Official patch notes 0.30.2.0 (2026-09-25)', 'https://account.monstersandmemories.com/community/patch_notes/51'],
 'p3021': ['Official patch notes 0.30.2.1 (2026-09-30)', 'https://account.monstersandmemories.com/community/patch_notes/52'],
 'p3024': ['Official patch notes 0.30.2.4 (2026-10-04)', 'https://account.monstersandmemories.com/community/patch_notes/55'],
 'p3025': ['Official patch notes 0.30.2.5 (2026-10-07)', 'https://account.monstersandmemories.com/community/patch_notes/56'],
 'p3028': ['Official patch notes 0.30.2.8 (2026-10-11)', 'https://account.monstersandmemories.com/community/patch_notes/59'],
 'f551': ['Forum: Necromancer v Elves? (race standing in Faelindral and Ail\'Vorith, 2026-08-25 to 09-18)', 'https://forum.monstersandmemories.com/d/551-necromancer-v-elves'],
 'f771': ['Forum: Deep Elf to NH without KoS (2026-09-10/12)', 'https://forum.monstersandmemories.com/d/771-deep-elf-to-nh-without-kos'],
 'f1514': ['Forum: NH factions frozen for Deep elf (2026-10-03/04)', 'https://forum.monstersandmemories.com/d/1514-nh-factions-frozen-for-deep-elf'],
 'f1616': ['Forum: Deep Elf Non-KOS Night Harbor (2026-10-04)', 'https://forum.monstersandmemories.com/d/1616-deep-elf-non-kos-night-harbor'],
 'f1647': ['Forum: Faction Hostility in Night Harbor is broken', 'https://forum.monstersandmemories.com/d/1647-faction-hostility-in-night-harbor-is-broken'],
 'r1': ['Reddit: Dark Elves and Night Harbor (2026-09-24)', 'https://www.reddit.com/r/MonstersAndMemories/comments/1wpcpke/dark_elves_and_night_harbor/'],
 'r2': ["Reddit: Starting Ail'vorith as a new player (2026-09-28)", 'https://www.reddit.com/r/MonstersAndMemories/comments/1ws687w/starting_ailvorith_as_anew_player/'],
 'cav': ["Wiki faction: Citizens of Ail'Vorith", w("Citizens of Ail'Vorith")],
 'deepcut': ['Wiki faction: Deepcut Bandits', w('Deepcut Bandits')],
 'cnh': ['Wiki faction: Citizens of Night Harbor', w('Citizens of Night Harbor')],
 'redm': ['Wiki faction: Red Mantles', w('Red Mantles')],
 'steel': ['Wiki faction: Steel Talons', w('Steel Talons')],
 'nhg': ['Wiki faction: Night Harbor Garrison', w('Night Harbor Garrison')],
 'races': ['Wiki: start-city table race notes (Deep Gnome standing)', w('Starting City by Race, Class, and Deity')],
}
# player-tracked hunting levels and coin per kill (monstersandmemories.wiki zone pages, fetched 2026-10-18)
MW = {
 'Night Harbor': ('night-harbor', 'levels 2-40, most at 17; coin per kill 1cp-6sp 69cp, average 1sp (5,242 kills)'),
 'Underdocks': ('underdocks', 'levels 2-15, most at 9; 1cp-4sp 88cp, average 29cp (7,046 kills)'),
 'Evershade Weald': ('evershade-weald', 'levels 3-30, most at 22; 1cp-4sp 98cp, average 18cp (2,886 kills)'),
 "Keeper's Bight": ('keepers-bight', 'levels 17-34, most at 29; 11cp-5sp 10cp, average 1sp (4,394 kills)'),
 'Blacktide Bay': ('blacktide-bay', 'levels 12-31, most at 27; 11cp-3sp 64cp, average 2sp (2,172 kills)'),
 'Shaded Dunes': ('shaded-dunes', 'levels 3-18, most at 6; 1cp-4sp 77cp, average 25cp (3,148 kills)'),
 'Sungreet Strand': ('sungreet-strand', 'levels 5-27, most at 7; 1cp-2sp 83cp, average 48cp (6,868 kills)'),
 'Tel Ekir': ('tel-ekir', 'levels 8-19, most at 13; 2cp-1sp 58cp, average 36cp (5,641 kills)'),
 'Tomb of the Last Wyrmsbane': ('tomb-of-the-last-wyrmsbane', 'levels 6-23, most at 13; 3cp-52cp, average 18cp (6,162 kills)'),
 'Ancient Crypt': ('ancient-crypt', 'levels 13-18, most at 15; 9cp-1sp 32cp, average 42cp (1,297 kills)'),
 'Caves of Irem': ('caves-of-irem', 'levels 13-37, most at 13; 33cp-5sp 55cp, average 1sp (224 kills)'),
 'Great Cavern Sea': ('great-cavern-sea', 'levels 16-24, most at 17; 8cp-2sp 25cp, average 87cp (361 kills)'),
 'Fallen Pass': ('fallen-pass', 'levels 16-50, most at 49; 10cp-7sp 59cp, average 2sp (11,906 kills)'),
 'Glass Flats': ('glass-flats', 'levels 16-49, most at 49; 8cp-9sp 75cp, average 2sp (6,085 kills)'),
 'Vale of Zintar': ('vale-of-zintar', 'levels 24-33, most at 27; 33cp-5sp 93cp, average 2sp (2,775 kills)'),
 'Scarwood': ('scarwood', 'levels 26-42, most at 34; 39cp-6sp 29cp, average 3sp (3,099 kills)'),
 'Shallow Shoals': ('shallow-shoals', 'levels 27-42, most at 39; 66cp-6sp 56cp, average 3sp (782 kills)'),
 'Grain Cellar': ('grain-cellar', 'levels 28-34, most at 32; 58cp-4sp 9cp, average 1sp (310 kills)'),
 'Rothold': ('rothold', 'levels 34-39, most at 37; 1sp 16cp-5sp 9cp, average 2sp (180 kills)'),
 'Blind Midden': ('blind-midden', 'levels 7-19, most at 17; 9cp-1sp 13cp, average 43cp (701 kills)'),
}
for z, (sl, _) in MW.items(): S_COMMON['mw-' + sl] = ['monstersandmemories.wiki: %s (player-tracked levels and coin)' % z, 'https://monstersandmemories.wiki/zones/' + sl]
def mw(zone):
    sl, txt = MW[zone]; return it(F, 'Player-tracked hunting in %s: %s.' % (zone, txt), 'mw-' + sl)
WZ = ['Night Harbor', 'Underdocks', 'Faelindral', 'Evershade Weald', "Keeper's Bight", 'Blacktide Bay', 'Shaded Dunes', 'Sungreet Strand', 'Tel Ekir',
      'Tomb of the Last Wyrmsbane', 'Night Harbor Sewers', 'Infested Crypt', 'Ancient Crypt', 'Caves of Irem', 'Glinting Hollow', 'Scarwood', 'Vale of Zintar',
      'Fallen Pass', 'Shallow Shoals', 'Glass Flats', 'Grain Cellar', 'Sunken Resort', 'Great Cavern Sea']
for z in WZ: S_COMMON['z-' + z.lower().replace(' ', '-').replace("'", '')] = ['Wiki: %s' % z, w(z)]
def zk(z): return 'z-' + z.lower().replace(' ', '-').replace("'", '')

# ---- Deep Elf and Night Harbor: shown (race-filtered) in every start city's faction box
DE = ['Deep Elf']
DE_KOS = [
 it(F, "Night Harbor: the wiki has no standing table for Deep Elves. Patch 0.30.2.0 (2026-09-25) says 'Night Harbor factions should now be easier to gain'.", 'p302', races=DE),
 it(U, "Night Harbor is effectively KoS for a Deep Elf, whatever city you started in. Players report seething or KoS with the Red Mantle and Steel Talon guards, Harbor guards, patrolmen and citizens; an Agnostic deity did not stop the named guards. The guards at the Underdocks tunnel entrance and the Sojourners were fine.", 'f771', 'r1', 'f1647', 'f551', races=DE),
 it(U, "Getting out of KoS in Night Harbor is a long grind: from about 500 faction kills after the patch (hearsay) to 7-8 hours of wererats in Shaded Dunes to reach Disdain (2026-10-04) or about 6 hours of wererats outside the Underdocks. Several players report the faction bar not moving at all (2026-10-03). The Bard and Rogue guilds stayed KoS, and the North Bank guards and bankers stayed hostile for one player at Amicable citizens.", 'r1', 'f1514', 'f1616', 'f1647', races=DE),
 it(U, "A Reddit player (2026-09-28) says the Night Harbor faction has to be ground around that city (Ashira in Sungreet Strand and Tel Ekir), not in the Deep, and that entering Night Harbor from the Underdocks puts you in The Bends with no KoS guards right at the zone line.", 'r2', races=DE),
 it(ST, "As a Deep Elf, treat Night Harbor as hostile until your own faction check (/con a guard) says otherwise. Use the Underdocks as your surface hub, and get a friend to buy Night Harbor spells or sell loot for you if you need the city early.", 'r1', 'r2', races=DE),
]
SRC_KOS = ['p302', 'f771', 'r1', 'f1647', 'f551', 'f1514', 'f1616', 'r2']

# ---- shared surface route, levels 16-60 (Night Harbor side; Faelindral and the Underdocks feed into it)
def mid_bands(origin):
    """origin: 'nh', 'ud' or 'fae' (only changes the travel line at the top of the first band). Camp levels quote the
    Per-Level Hunting Guide as 'solo X / group Y'; mob levels come from the zone pages' NPC tables."""
    via = {'nh': 'From Night Harbor', 'ud': 'From the Underdocks (up into Night Harbor, then out of a gate)', 'fae': "From Faelindral (Evershade Weald, then Keeper's Bight or the Night Harbor side)"}[origin]
    return [
 {'lo': 16, 'hi': 20, 'title': 'Fallen Pass pit, Glass Flats goblins, Sungreet quarry', 'steps': [
   it(ST, '%s: the start cities meet here. Shaded Dunes leads to Fallen Pass, and Sungreet Strand leads to Glass Flats, the quarry and the Grain Cellar.' % via, zk('Shaded Dunes'), zk('Sungreet Strand')),
   it(F, "Fallen Pass: the pit just inside the zone (don't go up the ramp). Dusty skeletons, about 16-19 per the guide, are easy single pulls, and anywhere along the wall is generally safe. Solo 17-20, group 15.", 'hunt', zk('Fallen Pass')),
   it(F, 'Glass Flats: the goblin camp (turn left as you zone in from Sungreet Strand), with Baron Bigtent (20) as the named. Solo 18, group 16-20.', 'hunt', zk('Glass Flats')),
   it(F, 'Sungreet Strand quarry: cinder workers (16-18). Their loot feeds the Cinder Beetle Armor quests. Solo 24, group 16-20. The Ashira camp by the Glass Flats zone line is solo 21+, group 18-23; the guide asks for a level check.', 'hunt', zk('Sungreet Strand')),
   it(F, 'Ancient Crypt (wiki 12-22): the entrance, kitchen, commander, library and researcher skeleton camps. You need a tank and a healer. Solo 21?, group 13-18.', 'hunt', zk('Ancient Crypt'), 'mw-ancient-crypt'),
   it(F, 'Tel Ekir, Bloodynose goblin side: captains (16), voodooists and stabbers (~16-18), and General Overlord Bloodynose (20+). You need a tank and a healer. Solo 17+, group 10-15.', 'hunt', zk('Tel Ekir')),
   it(F, "Keeper's Bight: the deadwood spiders on the spider log (recluses 11-14, then the matriarch and Widow Vethra at 16). A Reddit player calls the log 'great til 20', with the Sangrels behind it.", zk("Keeper's Bight"), 'rkb'),
 ]},
 {'lo': 21, 'hi': 25, 'title': 'Fallen Pass ramp, Glass Flats beach, Sungreet quarry goblins', 'steps': [
   it(F, 'Fallen Pass pit: bone carver beetles (24) and Necroferius (25, a named beetle in the NW corner of the pit). Solo 27, group 20-25.', 'hunt', zk('Fallen Pass')),
   it(F, 'Fallen Pass, up the ramp to the left: skeletons and ghouls (restless adepts 22-23). The ghoul adepts nuke for about 200 (blaze), so interrupt them. Solo 28, group 20-25.', 'hunt', zk('Fallen Pass')),
   it(F, 'Glass Flats beach (straight ahead after you enter): Szuurian vipers (24-26) and beetles, single pulls, but watch for roaming named 30+. Solo 28, group 20-24.', 'hunt', zk('Glass Flats')),
   it(F, 'Sungreet Strand quarry goblins: miners ~20-21, spellshooters ~20, and Taskmasters Gitch ~18 and Urka 19. Big pulls with casters, so it is dangerous, but there are several quests. Group 18-23.', 'hunt', zk('Sungreet Strand')),
   it(F, "Keeper's Bight: Blacktide orcs (23-25) and a Bloodchain overseer (25).", zk("Keeper's Bight")),
   it(F, 'Quest (20+) in Glass Flats:', 'qs', quest='viper'),
   it(F, 'Quest (20) in Sungreet Strand:', 'qs', quest='hulg'),
 ]},
 {'lo': 26, 'hi': 30, 'title': 'Vale of Zintar Ashira, Scarwood bandits, Sungreet cellar', 'steps': [
   it(F, 'Vale of Zintar: the corrupted Ashira camp. Hug the right wall to the tents by a lake under the corrupted floating castle (Onis the Elder 27, Fernic the Cur 28, Seshena ~27+). Drops sell for 30s-1g. Solo 32, group 22-28.', 'hunt', zk('Vale of Zintar')),
   it(F, 'Vale of Zintar: the Dustrend orc camp by the Fallen Pass entrance in the north-west (foot soldiers ~27-30). Better XP than the Ashira, worse loot. Solo 32-35, group 26-30.', 'hunt', zk('Vale of Zintar')),
   it(F, 'Scarwood: the bandit island in the middle of the river (bandits 26; Garran and Thorne Grinholdt 28). There may not be enough mobs for a full group. Solo 27, group 22-27.', 'hunt', zk('Scarwood')),
   it(F, 'Sungreet Strand: the secret cellar in the third farm building (double-click the wall) and the pirates in the fourth. Solo 26-32, group 22-28.', 'hunt', zk('Sungreet Strand')),
   it(F, 'Blacktide Bay (wiki 10-30): Bloodchain Champion 23, Taskmaster Murkraal 28, Captain Kruush 29.', zk('Blacktide Bay'), 'mw-blacktide-bay'),
 ]},
 {'lo': 31, 'hi': 40, 'title': "Keeper's Bight poachers, Grain Cellar, Fallen Pass Plagueborn", 'steps': [
   it(F, "Keeper's Bight poacher camps (poachers 28-30; Tolan >35). Named poachers drop a tunic, leggings, boots and a dagger, which go to the undead NPC in the bear cave (Left Behind). Solo ~32+, group 28-35.", 'hunt', zk("Keeper's Bight"), quest='left'),
   it(F, 'Grain Cellar (wiki 32-36, off Sungreet Strand): undead and cultists, full of casters. Group 29-35.', 'hunt', zk('Grain Cellar')),
   it(F, 'Vale of Zintar tomb burrowers (~31-34; silver and gold devourers ~35+ are named). They are not KoS but will social, and they dig away and pop up elsewhere. Solo 32-35 / group 32-35, then 36-39 / 36-38 for the elder and ancient burrowers.', 'hunt', zk('Vale of Zintar')),
   it(F, "Fallen Pass Plagueborn undead citizens (~34-37). The ramp down is on the far side of the cliffs. A restless parade comes down at night to fight them, and the constable patrols are higher level. Solo 36+, group 30-35. The Skri'Var rat camps NE past the stables have many named: solo 38-44, group 34-38.", 'hunt', zk('Fallen Pass')),
   it(F, "Shallow Shoals: the basilisk island across from the Zaedin's Landing boat dock (water basilisks ~36-38), good for mining iron and some gold. Solo 38+, group 30-35.", 'hunt', zk('Shallow Shoals')),
   it(F, 'Scarwood: poachers 34-35, wisps 36-38, treants 38+, black drakes 40-41.', zk('Scarwood')),
 ]},
 {'lo': 41, 'hi': 60, 'title': 'Glass Flats cultists, Shoals Orc Fortress, Saman, Giant City', 'steps': [
   it(F, 'Glass Flats outer cultists: single mobs spread through the canyons, getting denser near the building. Solo 45-52, group 42-48. The south-west part is solo 48-52, group 45-50.', 'hunt', zk('Glass Flats')),
   it(F, "Shallow Shoals Orc Fortress (the Black Shoals Fortress, named ~45), a large island not too far from the Keeper's Bight docks. Solo 48+, group 41-48.", 'hunt', zk('Shallow Shoals')),
   it(F, 'Glinting Hollow (wiki 38+, off Evershade Weald): named by floor, from Softpaws and Thornbark 41 on the 1st floor, through goblings ~42 and dryads ~44, to Gazer 47 on the 6th.', zk('Glinting Hollow')),
   it(F, 'Endgame camps: Glass Flats undead tower (group 45-50, then 51-60); Fallen Pass elder drakes (~49-51, group 45-52); Lower Saman and the stables (group 51-60); Upper Saman (group 53-60); Vale of Zintar Giant City (group 55-60; most solo players cannot).', 'hunt', zk('Glass Flats'), zk('Fallen Pass'), zk('Vale of Zintar')),
 ]},
]
S_MID = {'rkb': ['Reddit: Levelling location near Evershade Weald level 13 (2026-08-10)', 'https://www.reddit.com/r/MonstersAndMemories/comments/1vkskp0/levelling_location_near_evershade_weald_level_13/']}
Q_MID = {
 'viper': {'auto': "Viper's Kick Recipe", 'classes': [], 'tag': 'Optional', 'why': 'Reward is the Viper\'s Kick recipe item plus XP. Only worth it if you are in Glass Flats anyway.', 'src': ['qs']},
 'hulg': {'auto': "Captain Hulg's Mug", 'classes': [], 'tag': 'Optional', 'why': 'XP and 5 silver while you work the quarry.', 'src': ['qs']},
 'left': {'auto': 'Left Behind', 'classes': [], 'tag': 'Recommended', 'why': "Fendris the Forsaken (30+) turns the named poachers' drops into armor and a weapon. The Keeper's Bight wiki lists Debtcarver, Leggings of Reckoning, Boots of Vengeful Resolve and Vest of Shattered Duty (from Poachers Tolan and Garrus).", 'src': ['qs', 'z-keepers-bight']},
}

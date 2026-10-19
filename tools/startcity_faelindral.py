#!/usr/bin/env python3
"""Writes data/startcities/faelindral.json: the Faelindral (Evershade Weald) start route, levels 1-60 (local 1-20, then the
shared surface route). Sources: wiki zone, quest and faction pages (miraheze), the Per-Level Hunting Guide,
monstersandmemories.wiki player-tracked stats, the official forum and Reddit. Researched 2026-10-18 (America/New_York).
Re-run after editing: python3 tools/startcity_faelindral.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from startcity_common import *

CITY = 'Faelindral'
S = dict(S_COMMON); S.update(S_MID)
S.update({
 'fae': ['Wiki: Faelindral (rev 83070, 2026-10-18)', w('Faelindral')],
 'ew': ['Wiki: Evershade Weald (rev 83151, 2026-10-18)', w('Evershade Weald')],
 'farc': ['Wiki: Archer Starter Quest (Faelindral) (rev 75499)', w('Archer Starter Quest (Faelindral)')],
 'fbrd': ['Wiki: Bard Starter Quest (Faelindral) (rev 80008)', w('Bard Starter Quest (Faelindral)')],
 'fbst': ['Wiki: Beastmaster Starter Quest (Faelindral) (rev 82724, 2026-10-17)', w('Beastmaster Starter Quest (Faelindral)')],
 'fdru': ['Wiki: Druid Starter Quest (Faelindral) (rev 80229)', w('Druid Starter Quest (Faelindral)')],
 'ffig': ['Wiki: Fighter Starter Quest (Faelindral) (rev 82595, 2026-10-17)', w('Fighter Starter Quest (Faelindral)')],
 'frng': ['Wiki: Ranger Starter Quest (Faelindral) (rev 75338)', w('Ranger Starter Quest (Faelindral)')],
 'frog': ['Wiki: Rogue Starter Quest (Faelindral) (rev 53204)', w('Rogue Starter Quest (Faelindral)')],
 'fshm': ['Wiki: Shaman Starter Quest (Faelindral) (rev 79993)', w('Shaman Starter Quest (Faelindral)')],
 'cfae': ['Wiki faction: Citizens of Faelindral', w('Citizens of Faelindral')],
 'dfae': ['Wiki faction: Defenders of Faelindral', w('Defenders of Faelindral')],
 'wyrd': ['Wiki faction: Wyrdguard', w('Wyrdguard')],
 'csum': ['Wiki faction: Court of Summer', w('Court of Summer')],
 'cwin': ['Wiki faction: Court of Winter', w('Court of Winter')],
 'cspore': ['Wiki faction: Circle of Spores', w('Circle of Spores')],
 'fell': ['Wiki faction: Fellstone Orcs', w('Fellstone Orcs')],
 'mwfae': ['monstersandmemories.wiki: Faelindral (zone summary)', 'https://monstersandmemories.wiki/zones/faelindral'],
})
races, classes = who_starts(CITY)
intro = [
 it(F, 'Faelindral is the Wood Elf (Faelewyn) home city, built in the trees above Evershade Weald. Only Wood Elves and Halflings can start here, and both can also start in Night Harbor.', 'fae', 'faq', 'start'),
 it(F, 'Classes that can start here: %s. Halflings can be Clerics or Paladins, but those two classes cannot start in Faelindral.' % ', '.join(classes), 'fae', 'start'),
 it(F, "You arrive at the top of the Traveler's Lift (the Newbie Lift). Ring the bell (double-click it) to call the lift, and double-click it again to send it. The city's areas include the Willows Whisper stage, the Traders Terrace, Sentinel's Terrace and Sentinel's Gaze (the garrison), Ranger's Rest (on Keeper's Terrace, past the inn toward the kennels), the Quiet Den kennel, the Balanced Branch (Shaman guild), the Lambent Lantern (inn and Bard guild, behind the bank), the Heartwood Archives above the bank, and the Well of Order (herbalism and first aid).", 'farc', 'ffig', 'fbst', 'fshm', 'frog', 'fdru', 'fae'),
 mw('Evershade Weald'),
 it(ST, 'Faelindral has plenty of early content: do your class starter (every class has one, with gear at level 1 and more at about 3-4 and 8), the Green Drakeling armor, and the city quests that need newbie-yard drops. Then move to the Fellstone orcs, wolves and spiders, and from about 11 to the Calafreyan ruins, Blacktide Bay or the Keeper\'s Bight spider log.', 'fae', 'ew', 'hunt'),
]
faction = [
 it(F, 'Citizens of Faelindral and Defenders of Faelindral both rise when you kill Fellstone orcs (warriors, shamans, scouts, Scout Grimgaze) and Mezzatrian spiders (broodlings, scions, Mezzatrian Boneweaver). Killing a summer pixie lowers Citizens. Quests: Mierra\'s Famed Cupcakes (Citizens), A Sweet Treat (Defenders), Decipher the Unintelligible Writings and the Green Drakeling armor (both).', 'cfae', 'dfae', 'qs'),
 it(F, 'Guild factions: the Wyrdguard rise from the Fighter and Archer starters and Culling the Fellstone. The Ardent Keepers rise from the Ranger and Beastmaster starters, Culling the Fellstone, Diseased Wolf Pelts and Poacher\'s Knives. The Preservers rise from the Shaman starter and Bone Chips for Moon Dances; the Rogue starter lowers them once. The Lambent Wanderers rise from the Rogue starter.', 'wyrd', 'qs', 'fshm', 'frog'),
 it(F, 'Fae courts: killing dawn pixies, trixie pixies, prowling or snarling wolves, Softpaws, treants or summer pixies lowers the Court of Summer (dawn and trixie pixies raise the Court of Winter). Six Eyes Too Many raises Summer and lowers Winter. In the Rogue starter (part 2d), killing Lilika Thinsticks lowers Citizens of Faelindral and the Court of Summer, and raises the Court of Winter.', 'csum', 'cwin', 'qs', 'frog'),
 it(F, 'Circle of Spores (the Sporehaven Karst myconids): raised by killing beguiled wolves, beguiled bluecaps, beguiled water elementals and fossergrim watchers, and lowered by killing docile bluecaps. Mushroom Menace raises it and lowers Naelira\'s Court. The myconids are aggressive at night (Shaman starter).', 'cspore', 'qs', 'fshm'),
 it(F, 'Fellstone Orcs: every starter step and orc kill lowers them, and the wiki knows of nothing that raises them. Poachers of Calafrey drop with the Beastmaster starter (part 5) and Poacher\'s Knives; monstersandmemories.wiki lists the poachers as hostile to the city.', 'fell', 'fbst', 'qs', 'mwfae'),
 it(U, 'Visitors: a Deep Gnome Necromancer, Agnostic or not, was fine in Faelindral straight away, including the bank and merchants (everyone "uneasy"; the upper platforms were not tried). One player thinks Goblins start at Disdain and are fine after killing a couple of orcs there, and that some races are KoS until they kill a few orcs (forum, 2026-09-14 to 09-18). Class alone does not get you attacked.', 'f551'),
 it(U, 'Deep Elves: one forum player (2026-09-18) says "Deep elves hated everywhere". There is no Faelindral-specific test in the sources: no sourced data yet beyond that.', 'f551', races=['Deep Elf']),
] + DE_KOS
travel = [
 it(F, "Faelindral connects to Evershade Weald by lifts and bridges: the Traveler's (Newbie) Lift, the Keeper's Lift (from Ranger's Rest), the Pixie Lift (down to the Druid's Circle, and the long northern lift into fae territory) and the Kennel Lift. The Temple Lift to the upper tiers does not work yet.", 'fae', 'farc', 'fbrd', 'fshm'),
 it(F, "Evershade Weald borders Keeper's Bight, Glinting Hollow and Blacktide Bay. The wiki also lists the Circle and the Ring of Evershade Weald as ways in and out.", 'ew'),
 it(F, "Keeper's Bight connects on to Scarwood, the Vale of Zintar and Shallow Shoals, which the shared route uses from about 26. The Druid starter (part 3) binds you and teleports you to the Sungreet Strand druid ring, then gives you the Gate scroll home.", 'z-keepers-bight', 'fdru'),
 it(U, "The overland path from Evershade Weald to Night Harbor and the 16-25 camps (Fallen Pass, Glass Flats, the Sungreet quarry): no sourced data yet. The A Sweet Treat quest sends you to Night Harbor's Smallfolk District but does not say how to get there.", 'qs'),
]
money = [
 mw("Keeper's Bight"), mw('Blacktide Bay'),
 it(F, 'Repeatable coin quests: Decipher the Unintelligible Writings pays 25 copper per Unintelligible Writings (Fellstone scouts, 3-6), and Diseased Wolf Pelts pays 75 copper per pelt (rabid wolves, 4-5; the wiki does not say if this one repeats). Hale\'s Haul in Keeper\'s Bight pays 20 silver for five sunken crates.', 'qs', 'ew'),
 it(F, 'Vendors: used weapon and armor dealers on the Traders Terrace (they buy as well as sell), and Merchant\'s Row for gear, bags and tradeskill supplies. Bone Chips for the Shaman starter and Moon Dances can often be bought from vendors.', 'fae', 'qs'),
]
trainers = {
 'Archer': {'npc': 'Captain Keyaryn Thornshade', 'where': "Sentinel's Terrace, above the Traders Terrace, in the centre of the giant trunk", 'src': ['farc', 'fae'], 'label': F,
            'note': "The quest page's infobox names Commander Elydris Stormbough as the giver, but the walkthrough and the zone table both hand the leafscroll to Keyaryn Thornshade. The walkthrough wins because it is the hand-in step."},
 'Bard': {'npc': 'Pine Brightreed (starter); Sylphrena Starfall and Laenyth Windharp', 'where': 'Lambent Lantern bard guild (Laenyth up the ramp across from the stage, Sylphrena upstairs). A composer above the Willows Whisper stage sells Bard songs', 'src': ['fbrd', 'fshm', 'fae'], 'label': F},
 'Beastmaster': {'npc': 'Captain Relgen Greenblade, then Aerin Mossfang', 'where': "Ranger's Rest on Keeper's Terrace (past the inn toward the kennels), then the Quiet Den kennel. Aerin and Baewyn Mossfang train skills, and a Beastmaster Spell Merchant is in the Quiet Den", 'src': ['fbst', 'fae'], 'label': F},
 'Druid': {'npc': 'High Gatekeeper Sylvarya Starveil', 'where': "Sentinel's Gaze, the garrison on Sentinel's Terrace (upper tier), one platform over from the Fae Lift", 'src': ['fdru', 'fae'], 'label': F, 'note': 'No Druid spell vendor is named on the Faelindral page: no sourced data yet.'},
 'Fighter': {'npc': 'Captain Vaelric Ironbark, then Craftguard Vinebrow', 'where': "Sentinel's Gaze garrison: behind the Willows Whisper stage, up to the Traders Terrace, then the central ramp. Vinebrow is at the garrison forge", 'src': ['ffig'], 'label': F, 'note': 'No Fighter skill trainer is named separately: no sourced data yet.'},
 'Ranger': {'npc': 'Captain Relgen Greenblade', 'where': "Ranger's Rest (Ardent Keepers), from the top of the Traveler's Lift. The Ranger Spell Merchant is with the Ardent Keepers", 'src': ['frng', 'fae'], 'label': F},
 'Rogue': {'npc': 'Elyndiir Nightshade', 'where': 'Lambent Lantern Inn, behind the bank; Myrielle Softglade is in the weapons and armor shop on the Traders Terrace', 'src': ['frog'], 'label': F, 'note': 'No Rogue spell or ability vendor is named on the Faelindral page: no sourced data yet.'},
 'Shaman': {'npc': 'Varilis Thornvine', 'where': "The Balanced Branch (Shaman guild), reached from the Ranger and Beastmaster platform. Moon Dances stands near the Shaman Spell Merchant there", 'src': ['fshm', 'qs'], 'label': F},
}
Q = {
 's-archer': auto('Archer Starter Quest (Faelindral)', 'Recommended', 'Novice Scout Bracer at 1, Weald Scout Bracer at 4, then a level 8 elemental-samples step and Scout\'s Longbow of the Wyrdguard at 15+. Wyrdguard + and Fellstone Orcs − at every step.', ('farc', 'qs'),
                  where="Captain Keyaryn Thornshade, Sentinel's Terrace (see the trainer note on the giver conflict)",
                  mobs=[{'item': 'Unintelligible Writings x6 (part 2)', 'from': 'Fellstone scouts (3-6)'},
                        {'item': 'Rune-Etched Bone x4 (part 3, level 4)', 'from': 'old elven skeletons'},
                        {'item': 'Docile Faefly (part 3, level 8)', 'from': 'an annoyed faefly (8): /take sample by the Calafreyan ruins spire after 6pm game time; avoid 3-6am, when a twisted fae patrols'},
                        {'item': 'Necrotic Ash, Letter of Correspondence, Dark Hood (part 4, 15+)', 'from': 'Calafreyan humanoids with the Blessing of the Forest Spirits buff, and a dark-robed figure'}],
                  notes=[it(F, 'Part 1 is a courier run to four scouts (Gladebow, Amberward at the foot of the Keeper\'s Lift, Faeweald by the Pixie Lift, Stonebranch by the Traveler\'s Lift); the wiki says it is worth five yellow bars of XP at level 1.', 'farc')]),
 's-bard': auto('Bard Starter Quest (Faelindral)', 'Recommended', 'Ring of Introduction at 1, the Lambent Lute at 4 and the Lute of the Charmed at 8.', ('fbrd', 'qs'),
                where='Pine Brightreed (read the Perfumed Letter you start with); later steps with Laenyth Windharp and Sylphrena Starfall in the Lambent Lantern',
                mobs=[{'item': 'Pixie Glitter (part 2 ingredients)', 'from': 'Six Eyes Too Many (6 Widow Eyes from black and elder widows)'},
                      {'item': 'Bundle of Strong Silk (part 3e)', 'from': "a deadwood matriarch (16), the Keeper's Bight spider log"}],
                notes=[it(F, 'Part 3 also involves Mistress Naelira, the naiad behind the waterfall deep in a cave.', 'fbrd', 'ew')]),
 's-beastmaster': auto('Beastmaster Starter Quest (Faelindral)', 'Recommended', 'Novice Claws of the Keeper (part 1) and Spirit-Blessed Shawl (part 4, level 4), then level 8 steps in Keeper\'s Bight. Ardent Keepers + throughout.', ('fbst', 'qs'),
                       where="Captain Relgen Greenblade at Ranger's Rest (hand him your Request for Aid), then Aerin Mossfang in the Quiet Den",
                       mobs=[{'item': 'Diseased Wolf Pelt x4 (part 4)', 'from': 'rabid wolves (4-5)'},
                             {'item': 'Blighted Orc Head (part 4)', 'from': 'Vorkuul Blighteye (7), who can spawn when you kill a Fellstone shaman'},
                             {'item': "3 Blood-Soaked Bear Claw, Poacher's Arrow, Fledgling Poacher's Bow (parts 5-6, level 8)", 'from': "Keeper's Bight; a fledgling poacher conned white at 12"},
                             {'item': 'Full Hunt Satchel contents (part 1)', 'from': 'no sourced data yet'}],
                       notes=[it(F, 'Eraeldor Lowmist (Shaman guild) cures rabies: target him and /say cleanse me.', 'fbst')]),
 's-druid': auto('Druid Starter Quest (Faelindral)', 'Recommended', 'Novice, then Aspirant Icon of the Gatekeeper and Scroll: Minor Frostbite at 1, a Gate trip and Sap-Stained Gloves at 4, and the Icon of the Gatekeeper at 8.', ('fdru', 'qs'),
                 where="High Gatekeeper Sylvarya Starveil, Sentinel's Gaze (upper tier)",
                 mobs=[{'item': 'Royal Jelly, Bat Wing, Bone Chips x2 each (part 2)', 'from': 'wasp drones, black bats and rotting skeletons (1)'},
                       {'item': 'Broken Shaman Idol x4 (part 3, level 4)', 'from': 'Fellstone shamans (7+)'},
                       {'item': 'Wasp Venom Sac, Widow Venom Sac (part 4, level 8)', 'from': 'wasps and Mezzatrian broodlings (10-12, the platform across the broken bridge)'},
                       {'item': 'Reekbog Focus (part 4)', 'from': 'Muleda Murktoe (level 13 Druid) after you /pour solution at the moss circle'}],
                 notes=[it(F, 'Part 3 binds you and teleports you to the Sungreet Strand druid ring; Almina Weepingwind gives you the Gate scroll back.', 'fdru')]),
 's-fighter': auto('Fighter Starter Quest (Faelindral)', 'Recommended', 'Tarnished Elven Blade and Novice Chain of the Wyrdguard at 1, a Bronzed blade and Striker\'s Chain at 4, and Tempered Blade of the Fae-Bound from part 3 (level 8 may be needed, untested).', ('ffig', 'qs'),
                   where="Captain Vaelric Ironbark, Sentinel's Gaze (hand in the Rolled Leafscroll signed by Commander Elydris Stormbough); Craftguard Vinebrow at the garrison forge",
                   mobs=[{'item': 'Shattered Skull x4 (part 1)', 'from': 'rotting skeletons (1) near the starting lift, or buy them'},
                         {'item': "Fellstone Warrior's Belt x4 and Scout Leader's Head (part 2, level 4)", 'from': 'Fellstone warriors (5-7) and Scout Leader Krindor (6, on the ridge past the Kennel Lift bridges)'},
                         {'item': "Orc Necromancer's Head (part 3)", 'from': 'Taeresh Deathcharmer (13?, Orc Cave)'},
                         {'item': 'Copper Bar x4, Cloth Scraps x2, Sylvine x6, Whispering Sage x2', 'from': 'tradeskill materials (sources not listed)'}],
                   notes=[it(U, 'The quest-helper walkthrough below is from an older revision (2026-05-26); the wiki page was rewritten on 2026-10-17 (rev 82595), and the summary above follows the new page.', 'ffig')]),
 's-ranger': auto('Ranger Starter Quest (Faelindral)', 'Recommended', 'Initiate Keepers Cloak at 1, Verdant Waistguard at 3, and Reach of the Ardent Keeper at 8.', ('frng', 'qs'),
                  where="Captain Relgen Greenblade, Ranger's Rest",
                  mobs=[{'item': 'Unintelligible Report (part 4, level 8; one is enough)', 'from': 'Fellstone trackers (8-10)'},
                        {'item': 'Part 4 boss', 'from': 'a mob that cons red to a level 8 Ranger (estimated 11), immune to snare; the wiki does not name it'}],
                  notes=[it(F, 'Researcher Fairgrove translates the report (Partially Translated Report, also the reward from Decipher the Unintelligible Writings).', 'frng', 'qs')]),
 's-rogue': auto('Rogue Starter Quest (Faelindral)', 'Recommended', 'Lambent Prospect Dagger at 1, Lambent Prospect Blade and Mask of the Forest Walker at 4, and Lambent Stiletto at 10+.', ('frog', 'qs'),
                 where='Elyndiir Nightshade, Lambent Lantern Inn (behind the bank)',
                 mobs=[{'item': 'Alpha Wolf Fang (part 3, level 4)', 'from': 'a beguiled alpha wolf (8-10), a rare spawn from beguiled wolves in the west wolf den; rare drop'},
                       {'item': "Copy of a Merchant's Ledger (part 4, 10+)", 'from': "/open trunk by the sleeping emissary at the Keeper's Bight inn at night (gone at 6am)"},
                       {'item': 'Part 4c', 'from': "the emissary (15) and two higher-level guards, walking from the Keeper's Bight treehouse to the Evershade Weald zone line around 7am"}],
                 notes=[it(F, 'Part 2d: killing Lilika Thinsticks costs Citizens of Faelindral and Court of Summer faction.', 'frog')]),
 's-shaman': auto('Shaman Starter Quest (Faelindral)', 'Recommended', 'Novice, then Apprentice Hoop of the Listener at 1, Spirit-Blessed Headdress at 4, and level 8 steps toward the Robes of the Listener.', ('fshm', 'qs'),
                  where='Varilis Thornvine, the Balanced Branch (read the Folded Leafscroll you start with)',
                  mobs=[{'item': 'Bone Chips x4, Shattered Skull x2', 'from': 'rotting skeletons (1), newbie area'},
                        {'item': 'Strange Toadstool', 'from': 'a mischievous faerie (2): /throw dust at the wolf den entrance; beware the high-level beguiled wolves'},
                        {'item': 'Green Drakeling Scale x5, Wasp Worker Wax x5 (level 4)', 'from': 'green drakelings (4-5) and wasp workers'},
                        {'item': 'Selstie Kelp x2, Fine Wood x4, Bight Serpent Skin x4 (part 5, level 8)', 'from': "Keeper's Bight (bight asps ~8-9; wood from lumberjacking), or the tanner"}],
                  notes=[it(F, 'Sporeweaver Underveil is in the Spore Caves (Sporehaven Karst); the myconids are aggressive at night, so bring invisibility if you go then.', 'fshm')]),
 'cupcakes': auto("Mierra's Famed Cupcakes", 'Recommended', 'Four Jelly Cupcakes and Citizens of Faelindral for 4 Royal Jelly. One cupcake starts A Sweet Treat.', ('qs', 'fae', 'cfae'),
                  where='Mierra Willowshade, in the building next to the inn by the Newbie Lift',
                  mobs=[{'item': 'Royal Jelly x4', 'from': 'wasp drones (1) or wasp workers (Wasp Ruins, solo 3+)'}]),
 'bones': auto('Bone Chips for Moon Dances', 'Optional', 'Tattered Cloth plus Preservers faction for 5 Bone Chips.', ('qs', 'fae'),
               where='Moon Dances, near the Shaman Spell Merchant in the Balanced Branch',
               mobs=[{'item': 'Bone Chips x5', 'from': 'rotting skeletons (1) and other skeletons, or vendors'}]),
 'cull': auto('Culling the Fellstone', 'Recommended', 'Tattered Rawhide plus Wyrdguard and Ardent Keepers faction for one Left Orc Ear.', ('qs', 'fae'),
              where='Wyrdguard Oakenpine, across the bridge from the tanner building',
              mobs=[{'item': 'Left Orc Ear', 'from': 'Fellstone warriors (5-7), necromancers (5-7), guards and trackers'}]),
 'decipher': auto('Decipher the Unintelligible Writings', 'Recommended', 'Repeatable 25 copper per Unintelligible Writings plus Defenders and Citizens of Faelindral faction. The Partially Translated Report is used in the Ranger starter.', ('qs', 'ew'),
                  where='Researcher Fairgrove, Heartwood Archives (the ramp just outside the bank, round the other side of the tree)',
                  mobs=[{'item': 'Unintelligible Writings (one at a time)', 'from': 'Fellstone scouts (3-6), the Scout Camp'}]),
 'pelts': auto('Diseased Wolf Pelts for Baewyn Mossfang', 'Optional', '75 copper plus Ardent Keepers faction per Diseased Wolf Pelt.', ('qs',),
               where="Baewyn Mossfang, the Beastmaster guild (Quiet Den)",
               mobs=[{'item': 'Diseased Wolf Pelt', 'from': 'rabid wolves (4-5)'}]),
 'drake': auto('Green Drakeling Scale Armor Quests', 'Recommended', 'Four-piece starter armor (coat, cloak, pants, boots) plus Defenders and Citizens of Faelindral faction.', ('qs', 'fae'),
               where='Takalea Scaletender, the tannery',
               mobs=[{'item': 'Green Drakeling Scale, Wing, Hide (coat 6/2/4, cloak 3/2/1, pants 4/2/2, boots 2/1/1)', 'from': 'green drakelings (4-5)'},
                     {'item': 'Green Drakeling Poison Duct (coat and pants)', 'from': 'Kyros Emeraldscale (8), across the river west of the Newbie Lift bridge'}]),
 'sixeyes': auto('Six Eyes Too Many', 'Optional', 'Pixie Glitter (used in the Bard starter) for 6 Widow Eyes. Court of Summer + and Court of Winter −.', ('qs', 'ew'),
                 where='Polietta Two-tone, up on the hill near the fae guardians (daytime only)',
                 mobs=[{'item': 'Widow Eye x6', 'from': 'black widows (4-5) and elder widows (7-8)'}]),
 'sweet': auto('A Sweet Treat', 'Optional', "A long chain from Faelindral to Night Harbor: Defenders, Citizens and Smallfolk Alliance faction, 55 silver in total, and the Stein of Baker's Scorn. Starts with one Jelly Cupcake for Guard Pippi Pinecone.", ('qs',),
               notes=[it(U, 'The wiki marks this quest as needing more information.', 'qs')]),
 'menace': auto('Mushroom Menace', 'Optional', 'Staff of Spores plus Circle of Spores faction (Naelira\'s Court −). The wiki gives the minimum level as 5 or lower, but the mobs are up to about 12.', ('qs', 'ew', 'cspore'),
                where='Sporeweaver Underveil, Sporehaven Karst (the mushroom cave near Faelindral)',
                mobs=[{'item': 'Prismatic Gills', 'from': 'a beguiled bluecap (~13-15), at night'},
                      {'item': 'Enchanted Water x4', 'from': 'a beguiled water elemental in the naiad cave upstream'}]),
 'hale': auto("Hale's Haul", 'Optional', "20 silver plus Langsdorfian League, Red Mantles and Village of Penshaw faction for five sunken crates. Great bight sharks (20-30, aggressive) patrol the bay.", ('qs', 'z-keepers-bight'),
              where="Captain Hale, the last ship on the Keeper's Bight docks"),
 'thurston': auto('Growing Threat of the Sangrel Fist', 'Optional', 'Sigil of Inquiry and a longer storyline, plus Red Mantles, Village of Penshaw and Ardent Keepers faction (Sangrel Fist −). 15+.', ('qs', 'z-keepers-bight'),
                  where="Reeve Thurston Winter, centre of Penshaw Village (Keeper's Bight)",
                  mobs=[{'item': 'Sangrel Fist Wraps x4', 'from': 'Sangrel strikers and related mobs'}]),
 'knives': auto("Poacher's Knives", 'Recommended', "High Keeper's Vambrace plus Ardent Keepers and Village of Penshaw faction (Poachers of Calafrey −) for 4 Poacher's Skinners.", ('qs', 'z-keepers-bight'),
                where="Ranger Rylin, the large treehouse in Keeper's Bight",
                mobs=[{'item': "Poacher's Skinner x4", 'from': 'poachers (28-30), poacher camps'}]),
 'ghkey': auto('Glinting Hollow Key Quest', 'Optional', 'The Glinting Hollow key (Glowing Fae Scale). 35+.', ('qs', 'ew'),
               where='Scout Brightleaf, stealthed outside the Glinting Hollow zone line, uphill from the druid ring',
               mobs=[{'item': 'Warped Scale', 'from': 'a warped fae (32), spawns at 2am game time by the druid mushroom circle'},
                     {'item': 'Twisted Scale', 'from': "a twisted fae, spawns at 3am game time up the ramp by the ruins near the Keeper's Bight zone line"}]),
}
Q.update(Q_MID)
ST_CLASS = [it(F, 'Class starter quest:', 'qs', quest=k, classes=v['classes']) for k, v in sorted(Q.items()) if k.startswith('s-')]
bands = [
 {'lo': 1, 'hi': 5, 'title': 'Class starter, newbie yard below the Traveler\'s Lift', 'steps': ST_CLASS + [
   it(F, 'Trainer', 'fae', trainer=True),
   it(F, "Newbie area at the foot of the Traveler's Lift (wiki levels): black bats, black wolf pups, rotting skeletons and wasp drones 1; large black bats and black widow hatchlings 2-3; dryad fawns 2-3; shrub bats ~3-4; skeletons, black widows, green drakelings and rabid wolves 4-5; dawn and solstice pixies 5.", 'ew'),
   it(F, 'Wasp Ruins, west along the main walkways: wasp workers, neutral but social (solo 3+, group 1-6). The named Wasp Hive Protector is 3-4.', 'hunt', 'ew'),
   it(F, 'Fellstone Scout Camp, near a fork in the main paths (spiders mean you are on the right path): 3 scouts, a roamer and one inside a tree, scouts 3-6 (solo 3+, group 1-6). They drop Unintelligible Writings; Scout Grimgaze (4-5) is the named.', 'hunt', 'ew'),
   it(F, 'Starter armor:', 'qs', quest='drake'),
   it(F, 'City quests from newbie drops:', 'qs', quest='cupcakes'),
   it(F, 'Optional:', 'qs', quest='bones'),
   it(F, 'Repeatable coin:', 'qs', quest='decipher'),
   it(F, 'Faction and Tattered Rawhide:', 'qs', quest='cull'),
   it(F, 'Optional:', 'qs', quest='pelts'),
 ]},
 {'lo': 6, 'hi': 10, 'title': 'Fellstone orcs, wolf den, widows', 'steps': [
   it(F, 'Fellstone orcs: warriors and necromancers 5-7, Fellstone shamans 7+, guards 8+, trackers 8-10, ragecallers 9+, defilers 10+. Named: Scout Leader Krindor (6, on the ridge past the Kennel Lift bridges) and Vorkuul Blighteye (7).', 'ew', 'fbst'),
   it(F, 'Wolves, west along the hillside path near the Druid Ring (solo 9, group 6-10; a good leather source): beguiled wolves ~7-8, a beguiled alpha wolf (8-10, named), and Rotmuzzle (9) with rabid wolves and skeletons.', 'hunt', 'ew'),
   it(F, 'Spiders: elder widows and widow matrons 7-8; Mezzatrian Boneweaver (7-9, a Necromancer spider).', 'ew'),
   it(F, 'Named: Kyros Emeraldscale (8, across the river west of the Newbie Lift bridge; drops the Poison Duct for the drakeling coat and pants). Fossergrim watchers 9-11, Meluli Dawnglow 8-12?.', 'ew'),
   it(F, "Keeper's Bight edge (by Evershade Weald): bight asps ~8-9, forest whelps 10-11, black bears 10-12.", 'z-keepers-bight'),
   it(F, 'Optional:', 'qs', quest='sixeyes'),
   it(F, 'Optional (long, travels to Night Harbor):', 'qs', quest='sweet'),
 ]},
 {'lo': 11, 'hi': 15, 'title': 'Calafreyan ruins, Mezzatrian spiders, Sporehaven, Blacktide Bay', 'steps': [
   it(F, 'Calafreyan ruins (south of Scout Amberward, over two bridges): Calafreyan soldiers and archers 11-13, an Elven Field Sergeant ~12, a fallen elven champion ~13.', 'ew', 'farc'),
   it(F, 'Mezzatrian broodlings and scions (10-12) on the platform across the broken bridge (across the fallen log, up the ramp, behind the waterfall, follow the bridges). A River Elemental (11-12) is in the pond by the Newbie Lift.', 'ew', 'fdru'),
   it(F, 'Sporehaven Karst myconids (~13-15), aggressive at night. Taeresh Deathcharmer (13?) is in the Orc Cave.', 'ew', 'fshm'),
   it(F, 'Optional:', 'qs', quest='menace'),
   it(F, 'Blacktide Bay (wiki 10-30): gloom widows 9-11, undead gnomish engineers, surveyors and architects 11-13, a net weaver 12, Gurowl the Beast, a Fellstone ritualist and Frimbus Darplefen 14, Commander Rursk 15.', 'z-blacktide-bay', 'mw-blacktide-bay'),
   it(F, "Keeper's Bight spider log: deadwood recluses 11-14. A Reddit player levelling at 13 near Evershade Weald was pointed there.", 'z-keepers-bight', 'rkb'),
   it(F, "Keeper's Bight docks:", 'qs', quest='hale'),
 ]},
 {'lo': 16, 'hi': 20, 'title': "Keeper's Bight spider log and Sangrels, then the shared route", 'steps': [
   it(F, "Keeper's Bight: the deadwood matriarch and Widow Vethra (16) on the spider log; Timberfang (20-25?) on the lower cliffs. Blacktide Bay: Prince Mali'Tik (18).", 'z-keepers-bight', 'z-blacktide-bay'),
   it(F, "Penshaw Village, Keeper's Bight:", 'qs', quest='thurston'),
 ]},
]
mb = mid_bands('fae')
bands[3]['steps'] += mb[0]['steps']
bands += mb[1:]
for b in bands:
    if b['lo'] == 31:
        b['steps'].insert(1, it(F, "Keeper's Bight poacher camps:", 'qs', quest='knives'))
        b['steps'].append(it(F, 'Evershade Weald fae: a warped fae (32) and the fae guardians, spellweavers and wanderers (~36). Glinting Hollow key at 35+:', 'ew', quest='ghkey'))
D = {'city': CITY, 'slug': 'faelindral', 'status': 'sourced', 'updated': '2026-10-18', 'researched': '2026-10-18 23:30 America/New_York',
     'generated_by': 'tools/startcity_faelindral.py', 'sources': S, 'intro': intro, 'faction': faction, 'travel': travel, 'money': money,
     'trainers': trainers, 'quests': Q, 'bands': bands}
write(D)

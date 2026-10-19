#!/usr/bin/env python3
"""Write data/chargen/<class>.json for every class except Inquisitor (hand-written).
FACT parts are read from data (wiki race pages via data/chargen/races.json, Template:Traits, data/classes.json, data/official_classes.json).
STRATEGY parts (builds, picks, reasons) are the SPEC table below. Trait picks are validated against Template:Traits race/class limits."""
import json, os, re, collections
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
def J(p): return json.load(open(os.path.join(ROOT, p), encoding='utf8'))
CG = J('data/chargen/races.json'); C = J('data/classes.json'); O = J('data/official_classes.json')
WIKI = 'https://monstersandmemories.miraheze.org/wiki/'
ABBR = {'Archer':'ARC','Bard':'BRD','Beastmaster':'BST','Cleric':'CLR','Druid':'DRU','Elementalist':'ELE','Enchanter':'ENC','Fighter':'FTR','Inquisitor':'INQ','Monk':'MNK','Necromancer':'NEC','Paladin':'PAL','Ranger':'RNG','Rogue':'ROG','Shadow Knight':'SHD','Shaman':'SHM','Spellblade':'SPB','Wizard':'WIZ'}
RCODE = {'Deep Dwarf':'DDF','Deep Elf':'DEF','Deep Gnome':'DGN','Dwarf':'DWF','Gnome':'GNM','Goblin':'GOB','High Elf':'HIE','Human':'HUM','Ogre':'OGR','Troll':'TRL','Halfling':'HFL','Wood Elf':'ELF'}
TR = {t['name']: dict(t, cat=cat) for cat, ts in CG['traits'].items() for t in ts}
def allowed(tn, cls=None, race=None):
    t = TR[tn]
    ok_c = cls is None or t['cls'].strip() == 'Any' or ABBR[cls] in [x.strip() for x in t['cls'].split(',')]
    ok_r = race is None or t['race'].strip() == 'Any' or RCODE[race] in [x.strip() for x in t['race'].split(',')]
    return ok_c and ok_r
STAT_FACTS = [
 ["STA", "Increases health and reduces chance to be dazed in combat (wiki Statistics; '1 STA = 1 HP' is marked 'need testing' there)."],
 ["AGI", "Provides damage mitigation (wiki Statistics)."],
 ["STR", "Increases melee and ranged weapon damage and shield block amounts; 1 STR = 2 weight (wiki Statistics)."],
 ["DEX", "Increases hit rate, weapon proc frequency and gives a channeling bonus to spellcasters (wiki Statistics)."],
 ["INT", "Mana pool size if INT is higher than WIS, and offensive spell damage (wiki Statistics)."],
 ["WIS", "Mana pool size if WIS is higher than INT, and healing done; 4 mana per WIS point for WIS-based classes (wiki Statistics)."],
 ["CHA", "Merchant prices and charm break rate on paper; the wiki notes CHA did not seem to affect vendor prices in beta (May 2026)."]]
RACIAL_WHY = {
 'Tenacity': 'Tenacity: +15% resistance to Mesmerize and Incapacitate, plus an active 15-second immunity',
 'Slippery': 'Slippery: +15% root resistance, plus an active 15-second Root/Snare immunity',
 'Stone Form': 'Stone Form: 15 seconds of +25% AC, -10% physical damage taken and Disease/Electricity/Poison cleanse',
 'Hide': 'Hide: become unseen while still (removed by moving or acting)',
 'Bribe': 'Bribe: make a target forget past wrongdoings',
 'Sneak': 'Sneak (race page)', 'Forage': 'Forage as a racial (race page), so no trait slot needed for it'}
COMMON_SRC = [["Wiki: Statistics (rev 82276)", WIKI + "Statistics"], ["Wiki: Traits (Template:Traits rev 79106)", WIKI + "Traits"],
              ["Wiki: Starting City by Race, Class, and Deity (rev 74855)", WIKI + "Starting_City_by_Race,_Class,_and_Deity"], ["Official Early Access FAQ: starting areas", "https://monstersandmemories.com/early-access-faq"]]
G = ['mining', 'smelting', 'lumberjacking']
GW = {'mining': 'Gathering for coin; pairs with the Miner trait (this Codex\'s default set).', 'smelting': 'Turns ore into sellable bars (separate skill on the wiki).', 'lumberjacking': 'Second gathering skill for coin, part of the default set.',
      'bind-wound': 'Bandaging between pulls cuts downtime for classes without strong self-heals.', 'fletching': 'Make your own arrows instead of buying them.', 'poison-making': 'Rogue-only skill on the wiki; your poisons are a core part of the class.',
      'fishing': 'Food supply and a relaxed gathering skill.', 'herbalism': 'Gathering skill that pairs with outdoor travel.'}
T4 = lambda pick, alt, why: {"cat": "Minor Non-Combat Traits", "pick": pick, "alt": alt, "why": why}
MINER = T4('Miner', ['Medic', 'Lumberjack'], "Miner starts Mining at 25 with a Trainee's Mining Pick and Pouch, matching the default gathering setup (Mining, Lumberjacking, Smelting) for early coin. Medic (Bind Wound 25 and bandages) is the safer pick if you expect downtime between fights. Blacksmith exists but smithing stays off by default here.")
FORAGE = lambda extra: {"cat": "Major Non-Combat Traits", "pick": "Forage", "alt": ["Infravision", "Ultravision", "Slow Metabolism"], "why": "Forage finds food and drink in the field, so fewer vendor runs. " + extra + " Infravision or Ultravision only if your race may take it (see the race note)."}
READY = lambda extra: {"cat": "Major Non-Combat Traits", "pick": "Readiness", "alt": ["Forage", "Infravision", "Ultravision"], "why": "Readiness gives a Cantrip slot from level 1, so one memorized spell survives death. " + extra}
SPEC = {
 'Archer': dict(key=['DEX', 'STR', 'AGI'], builds=[
   ("Damage (default)", {"DEX": 4, "STR": 4, "STA": 2}, "The official page calls the Archer physical ranged DPS with no magic. DEX raises hit rate and procs and STR adds ranged weapon damage (wiki Statistics), so most points go there; 2 STA as a cushion."),
   ("Safer kiter", {"DEX": 4, "AGI": 3, "STA": 3}, "Archers fire while moving and leap back when enemies close in (official). AGI mitigation and STA health help when a mob does reach you."),
   ("Heavy hitter", {"STR": 6, "DEX": 4}, "All-in on weapon damage and hit rate for groups where a tank holds aggro. Fragile when soloing.")],
  traits=[{"cat": "Major Combat Traits", "pick": "Dexterous", "alt": ["Strong", "Agile"], "why": "Dexterous: +5% DEX and a 15-second +50% DEX burst, your main hit-rate stat. Strong for more damage per hit."},
          {"cat": "Minor Combat Traits", "pick": "Bowman", "alt": ["Knife Thrower", "Defender"], "why": "Bowman starts Archery at 5, raises it 25% faster and gives a Trainee's Longbow, Hip Quiver and 1000 Trainee's Arrows, a big head start for your main weapon."},
          FORAGE("Archers may take it (Template:Traits)."), MINER],
  ts=G + ['fletching'], tsnote="Archer key abilities need specific arrowheads (official page), so Fletching is added to the gathering defaults. Smithing stays off."),
 'Bard': dict(key=['CHA', 'DEX', 'STA'], mana='CHA', builds=[
   ("Song power (default)", {"CHA": 6, "STA": 4}, "The wiki Bard page calls CHA the main attribute: song effectiveness and (now) mana are tied to it. Bards often pull, so the rest goes to STA to survive the run back."),
   ("Melee bard", {"CHA": 5, "DEX": 3, "STR": 2}, "Half on CHA, the rest on hit rate and weapon damage for soloing in melee. The wiki says DEX may affect missed notes, size unknown."),
   ("Max charisma", {"CHA": 8, "STA": 2}, "For charm-heavy play: the official page says Bards can temporarily charm enemies and the wiki ties charm break rate to CHA.")],
  traits=[{"cat": "Major Combat Traits", "pick": "Charismatic", "alt": ["Tough", "Dexterous"], "why": "Charismatic: +5% CHA, your song and mana stat, plus a 15-second +50% CHA burst."},
          {"cat": "Minor Combat Traits", "pick": "Vocalist", "alt": ["Virtuoso", "Swordsman"], "why": "Vocalist starts Singing at 50 and raises it 50% faster; the wiki spell list has 25 Singing songs, the biggest school for Bards. Virtuoso does the same for instruments and gives a Trainee's Recorder."},
          FORAGE("Bards may take it (Template:Traits)."), T4('Miner', ['Tracker', 'Medic'], "Miner for early gathering coin. Tracker (Bard, Druid, Ranger only) starts Tracking at 25 if you want to find camps faster.")],
  ts=G + ['bind-wound'], tsnote="Gathering defaults plus Bind Wound for pulling downtime. Smithing stays off."),
 'Beastmaster': dict(key=['STR', 'AGI', 'STA'], builds=[
   ("Brawler (default)", {"STR": 4, "STA": 3, "AGI": 3}, "Beastmasters fight in melee with two-handers or claws alongside a companion (official). STR for damage, STA and AGI to survive when the pet loses aggro."),
   ("Pet support", {"WIS": 4, "STA": 3, "STR": 3}, "For most playable races your WIS is higher than INT, so WIS is your mana stat (wiki Statistics; Deep Gnome is the exception, see the mana note). More mana for companion heals and buffs."),
   ("Hard hitter", {"STR": 5, "DEX": 3, "STA": 2}, "Weapon damage and hit rate when your companion tanks.")],
  traits=[{"cat": "Major Combat Traits", "pick": "Strong", "alt": ["Agile", "Wise"], "why": "Strong: +5% STR and a 15-second +50% STR burst for your melee."},
          {"cat": "Minor Combat Traits", "pick": "Alterer", "alt": ["Warrior", "Defender"], "why": "Alteration is the biggest Beastmaster school on the wiki spell list (35 of 74). Alterer starts it at 10 and raises it 25% faster. Warrior (Offense) if you play mostly melee."},
          FORAGE("Beastmasters may take it."), MINER],
  ts=G + ['bind-wound'], tsnote="Gathering defaults plus Bind Wound. Smithing stays off."),
 'Cleric': dict(key=['WIS', 'STA', 'DEX'], builds=[
   ("Healer (default)", {"WIS": 8, "STA": 2}, "Matches the wiki Cleric creation advice for most races: WIS is tied to heal strength and mana; STA next for HP and stun resistance."),
   ("Off-tank cleric", {"WIS": 5, "STA": 3, "AGI": 2}, "The official page says Clerics can off-tank in heavy armor while casting. More STA/AGI for that, still WIS-first."),
   ("Halfling split", {"WIS": 4, "STA": 4, "DEX": 2}, "The wiki's Halfling allocation, since Halflings already start with very high WIS (23).")],
  traits=[{"cat": "Major Combat Traits", "pick": "Wise", "alt": ["Tough", "Holy Resistant"], "why": "Wise: +5% base WIS and a 15-second +50% WIS burst, your heal and mana stat."},
          {"cat": "Minor Combat Traits", "pick": "Channeler", "alt": ["Alterer", "Shieldman"], "why": "Channeler keeps heals going while you are hit (starts at 10, +25% speed). The wiki Cleric spell list has no school column, so no school trait is suggested from data. Shieldman gives a buckler for off-tanking."},
          READY("Good insurance for a healer."), MINER],
  ts=G + ['bind-wound'], tsnote="Gathering defaults plus Bind Wound. Smithing stays off."),
 'Druid': dict(key=['WIS', 'CHA', 'DEX'], builds=[
   ("Healer-caster (default)", {"WIS": 7, "DEX": 2, "CHA": 1}, "The wiki Druid advice: WIS first (heals and mana), then CHA for the charm line, then DEX."),
   ("Charm soloer", {"WIS": 5, "CHA": 5}, "The official page calls Druids one of the strongest solo classes through animal control; the wiki ties charm to CHA."),
   ("Sturdy outdoorsman", {"WIS": 6, "STA": 4}, "More HP for soloing without a charm pet.")],
  traits=[{"cat": "Major Combat Traits", "pick": "Wise", "alt": ["Charismatic", "Tough"], "why": "Wise: +5% base WIS and a 15-second +50% WIS burst."},
          {"cat": "Minor Combat Traits", "pick": "Alterer", "alt": ["Evoker", "Channeler"], "why": "Alteration is by far the biggest Druid school on the wiki (82 of 146 spells): heals, buffs and snares. Evoker for the nukes (28)."},
          READY("Forage is not available to Druids (Template:Traits)."), T4('Miner', ['Tracker', 'Herbalist'], "Miner for early coin. Tracker (Druid, Bard, Ranger only) starts Tracking at 25.")],
  ts=G + ['herbalism'], tsnote="Gathering defaults plus Herbalism for outdoor travel. Smithing stays off."),
 'Elementalist': dict(key=['INT', 'STA', 'DEX'], builds=[
   ("Nuker (default)", {"INT": 7, "STA": 2, "DEX": 1}, "The wiki Elementalist advice (Human/Dwarf): INT for spell damage and mana, then STA, then DEX."),
   ("Pet tank solo", {"INT": 5, "STA": 3, "DEX": 2}, "The official page says Elementalists solo by letting the pet tank while casting from afar; a bit more STA for when adds come."),
   ("Max INT", {"INT": 8, "STA": 1, "DEX": 1}, "Biggest mana pool and damage for grouped play.")],
  traits=[{"cat": "Major Combat Traits", "pick": "Intelligent", "alt": ["Tough", "Fire Resistant"], "why": "Intelligent: +5% INT and a 15-second +50% INT burst."},
          {"cat": "Minor Combat Traits", "pick": "Conjurer", "alt": ["Channeler", "Evoker"], "why": "Conjuration is the biggest tagged Elementalist school on the wiki (45 spells; another 45 have no school listed). Conjurer starts it at 10 and raises it 25% faster."},
          READY("Elementalists also have Summon Food and Summon Drink (wiki spell list), so Forage adds little."), MINER],
  ts=G, tsnote="Gathering defaults. Smithing stays off."),
 'Enchanter': dict(key=['INT', 'CHA', 'STA'], builds=[
   ("Controller (default)", {"INT": 5, "CHA": 5}, "The wiki Enchanter advice for most races: INT (mana, damage) and CHA (charm and mesmerize) almost equally."),
   ("Mana battery", {"INT": 7, "CHA": 3}, "The wiki Human allocation: a bigger pool for buffs, mana regeneration and long fights."),
   ("Charmer", {"CHA": 6, "INT": 4}, "Charm break rate is tied to CHA (wiki Statistics); for soloing with charmed pets.")],
  traits=[{"cat": "Major Combat Traits", "pick": "Intelligent", "alt": ["Charismatic", "Tough"], "why": "Intelligent: +5% INT and a 15-second +50% INT burst. Charismatic if you lean on charm."},
          {"cat": "Minor Combat Traits", "pick": "Alterer", "alt": ["Channeler", "Abjurer"], "why": "Alteration is the biggest Enchanter school on the wiki (95 of 136 spells). Channeler keeps mesmerizes landing when you are hit."},
          READY(""), MINER],
  ts=G, tsnote="Gathering defaults. Smithing stays off."),
 'Fighter': dict(key=['STR', 'STA', 'AGI'], builds=[
   ("Tank (default)", {"STA": 4, "AGI": 3, "STR": 3}, "The official page gives Fighters the strongest aggro tools and shield tanking. STA health, AGI mitigation, STR weapon damage and shield block (wiki Statistics)."),
   ("Two-hander DPS", {"STR": 5, "DEX": 3, "STA": 2}, "For dual-wield or two-handed damage stances (official)."),
   ("Avoidance", {"AGI": 4, "STA": 4, "STR": 2}, "Even more mitigation for long dungeon pulls.")],
  traits=[{"cat": "Major Combat Traits", "pick": "Tough", "alt": ["Strong", "Agile"], "why": "Tough: +5% STA and a 15-second +50% STA emergency button."},
          {"cat": "Minor Combat Traits", "pick": "Shieldman", "alt": ["Defender", "Warrior"], "why": "Shieldman starts Block at 5 (+25% speed) with a Trainee's Buckler, which suits shield tanking from level 1."},
          FORAGE("Fighters may take it (Template:Traits)."), T4('Medic', ['Miner', 'Lumberjack'], "Medic starts Bind Wound at 25 with bandages: Fighters have no heals on the wiki spell list, so this cuts downtime most. Miner if you want coin first.")],
  ts=G + ['bind-wound'], tsnote="Gathering defaults plus Bind Wound. Smithing stays off by default even for a Fighter; switch it on in the Trades menu if you want to craft armor."),
 'Monk': dict(key=['AGI', 'DEX', 'STR'], builds=[
   ("Puller (default)", {"AGI": 4, "DEX": 3, "STA": 3}, "Monks pull with feign death and can avoidance off-tank (official). AGI mitigation and STA keep you alive on the pull; DEX for hit rate."),
   ("Damage", {"STR": 4, "DEX": 4, "AGI": 2}, "Fists and kicks scale with weapon damage and hit rate (wiki Statistics)."),
   ("Off-tank", {"AGI": 4, "STA": 4, "STR": 2}, "For dodge-based off-tanking.")],
  traits=[{"cat": "Major Combat Traits", "pick": "Agile", "alt": ["Dexterous", "Strong"], "why": "Agile: +5% AGI and a 15-second +50% AGI burst for avoidance."},
          {"cat": "Minor Combat Traits", "pick": "Brawler", "alt": ["Defender", "Warrior"], "why": "Brawler (Monk only) starts Dual Wield at 20 and raises it 25% faster."},
          FORAGE("Monks may take it."), T4('Medic', ['Miner', 'Survivalist'], "Medic for bandages between pulls; Monks can mend their own wounds (official) but Bind Wound still helps early. Miner for coin.")],
  ts=G + ['bind-wound'], tsnote="Gathering defaults plus Bind Wound. Smithing stays off."),
 'Necromancer': dict(key=['INT', 'DEX', 'STA'], builds=[
   ("Pet caster (default)", {"INT": 7, "STA": 2, "DEX": 1}, "The wiki Necromancer advice (Human): INT for spell damage and mana, then STA, then DEX."),
   ("Durable soloer", {"INT": 5, "STA": 4, "DEX": 1}, "The wiki Gnome allocation leans more on STA; good if you solo and take hits."),
   ("Max INT", {"INT": 8, "STA": 2}, "Biggest pool for DoTs and life drains in groups.")],
  traits=[{"cat": "Major Combat Traits", "pick": "Intelligent", "alt": ["Tough", "Corruption Resistant"], "why": "Intelligent: +5% INT and a 15-second +50% INT burst."},
          {"cat": "Minor Combat Traits", "pick": "Alterer", "alt": ["Conjurer", "Channeler"], "why": "Alteration (51) and Conjuration (41) are the two biggest Necromancer schools on the wiki."},
          READY(""), MINER],
  ts=G, tsnote="Gathering defaults. Smithing stays off."),
 'Paladin': dict(key=['STA', 'STR', 'WIS'], builds=[
   ("Tank (default)", {"STA": 4, "AGI": 3, "STR": 3}, "Paladins tank in plate with a shield (official). STA health, AGI mitigation, STR damage and block."),
   ("Healer-tank", {"STA": 4, "WIS": 4, "STR": 2}, "The official page describes fast emergency heals at a high mana cost. WIS raises healing, and mana for races whose WIS beats INT (see the mana note)."),
   ("Two-hander", {"STR": 5, "STA": 3, "DEX": 2}, "For two-handed DPS play (official).")],
  traits=[{"cat": "Major Combat Traits", "pick": "Tough", "alt": ["Wise", "Strong"], "why": "Tough: +5% STA and a 15-second +50% STA emergency button."},
          {"cat": "Minor Combat Traits", "pick": "Shieldman", "alt": ["Defender", "Channeler"], "why": "Shieldman: Block at 5 (+25%) and a Trainee's Buckler for shield tanking from level 1."},
          FORAGE("Paladins may take it."), MINER],
  ts=G + ['bind-wound'], tsnote="Gathering defaults plus Bind Wound. Smithing stays off."),
 'Ranger': dict(key=['DEX', 'AGI', 'STR'], builds=[
   ("Dual-wield and bow (default)", {"DEX": 4, "STR": 3, "AGI": 3}, "Rangers use a bow and dual blades (official). DEX for hit rate and procs, STR for weapon damage, AGI for off-tanking."),
   ("Outdoor utility", {"DEX": 3, "WIS": 4, "STA": 3}, "For most playable races WIS is at least as high as INT, so it is your mana stat for snares and travel spells (see the mana note for your race)."),
   ("Off-tank", {"STA": 4, "AGI": 4, "STR": 2}, "The official page says Rangers can off-tank with limited aggro control.")],
  traits=[{"cat": "Major Combat Traits", "pick": "Dexterous", "alt": ["Strong", "Agile"], "why": "Dexterous: +5% DEX and a 15-second +50% DEX burst."},
          {"cat": "Minor Combat Traits", "pick": "Bowman", "alt": ["Swordsman", "Defender"], "why": "Bowman: Archery at 5 (+25%), a Trainee's Longbow, Hip Quiver and 1000 arrows. Swordsman if you open in melee."},
          {"cat": "Major Non-Combat Traits", "pick": "Infravision", "alt": ["Ultravision", "Slow Metabolism"], "why": "Forage is not available to Rangers (they draw food from nature as a class ability, official). Infravision or Ultravision helps in caves at night; pick one your race may take."},
          T4('Tracker', ['Miner', 'Medic'], "Tracker (Ranger, Druid, Bard only) starts Tracking at 25 and raises it 25% faster; Rangers can track creatures (official). Miner for coin.")],
  ts=G + ['fletching'], tsnote="Gathering defaults plus Fletching for arrows. Smithing stays off."),
 'Rogue': dict(key=['DEX', 'AGI', 'STR'], builds=[
   ("Backstabber (default)", {"DEX": 4, "STR": 3, "AGI": 3}, "Rogues deal damage with dagger backstabs and thrown weapons (official). DEX for hit rate and procs, STR for damage, AGI to survive aggro."),
   ("Max damage", {"DEX": 5, "STR": 5}, "For groups where you never take aggro."),
   ("Solo sneak", {"AGI": 4, "STA": 3, "DEX": 3}, "More mitigation and HP for soloing and corpse runs.")],
  traits=[{"cat": "Major Combat Traits", "pick": "Dexterous", "alt": ["Strong", "Agile"], "why": "Dexterous: +5% DEX and a 15-second +50% DEX burst."},
          {"cat": "Minor Combat Traits", "pick": "Cutthroat", "alt": ["Knife Thrower", "Warrior"], "why": "Cutthroat starts Piercing at 5 (+25%) with a Trainee's Dirk: daggers are your main weapon. Knife Thrower gives 1000 throwing daggers."},
          FORAGE("Rogues may take it."), T4('Poison Maker', ['Miner', 'Medic'], "Poison Maker (Rogue only) starts Poison Making at 25 (+25% speed) with a kit; the official page makes poisons a core Rogue tool.")],
  ts=['poison-making'] + G, tsnote="Poison Making first, plus the gathering defaults. Smithing stays off."),
 'Shadow Knight': dict(key=['STR', 'STA', 'INT'], builds=[
   ("Tank (default)", {"STA": 4, "AGI": 3, "STR": 3}, "Shadow Knights tank in plate with fast short-range casts (official). STA, AGI mitigation and STR damage and block."),
   ("Drain caster", {"INT": 4, "STA": 3, "STR": 3}, "INT is higher than WIS for every playable race here, so it is your mana stat (wiki Statistics); more mana for life and strength drains."),
   ("Two-hander DPS", {"STR": 5, "DEX": 3, "STA": 2}, "Shadow Knights prefer two-handed weapons and out-damage Paladins (official).")],
  traits=[{"cat": "Major Combat Traits", "pick": "Tough", "alt": ["Strong", "Intelligent"], "why": "Tough: +5% STA and a 15-second +50% STA emergency button."},
          {"cat": "Minor Combat Traits", "pick": "Alterer", "alt": ["Shieldman", "Defender"], "why": "Alteration is the biggest Shadow Knight school on the wiki (25 of 77). Shieldman if you tank with a shield."},
          FORAGE("Shadow Knights may take it."), MINER],
  ts=G + ['bind-wound'], tsnote="Gathering defaults plus Bind Wound. Smithing stays off."),
 'Shaman': dict(key=['WIS', 'STA', 'DEX'], builds=[
   ("Healer-buffer (default)", {"WIS": 7, "STA": 2, "DEX": 1}, "The wiki Shaman advice (Human): WIS for heals and mana, then STA, then DEX."),
   ("Sturdy soloer", {"WIS": 6, "STA": 4}, "The wiki Goblin allocation; Shamans cannibalize health for mana (official), so extra HP pays twice."),
   ("Max WIS", {"WIS": 8, "DEX": 2}, "Biggest heals and pool for group play.")],
  traits=[{"cat": "Major Combat Traits", "pick": "Wise", "alt": ["Tough", "Cold Resistant"], "why": "Wise: +5% base WIS and a 15-second +50% WIS burst."},
          {"cat": "Minor Combat Traits", "pick": "Alterer", "alt": ["Channeler", "Conjurer"], "why": "Alteration is by far the biggest Shaman school on the wiki (87 of 123): buffs, slows and heals over time."},
          READY(""), MINER],
  ts=G, tsnote="Gathering defaults. Smithing stays off. See also the Shaman gathering route page."),
 'Spellblade': dict(key=['DEX', 'INT', 'STR'], builds=[
   ("Infusion fighter (default)", {"STR": 3, "DEX": 3, "INT": 4}, "Spellblades are melee DPS who cast infusions and fields (official). INT is higher than WIS for every playable race here, so it is your mana and spell damage stat; STR and DEX for weapon hits."),
   ("Melee-first", {"STR": 4, "DEX": 4, "STA": 2}, "If you mostly swing and use infusions for procs."),
   ("Caster-first", {"INT": 6, "DEX": 2, "STA": 2}, "For field and discharge damage; 56 of 61 wiki spells have a mana cost.")],
  traits=[{"cat": "Major Combat Traits", "pick": "Dexterous", "alt": ["Intelligent", "Strong"], "why": "Dexterous: +5% DEX and a 15-second +50% DEX burst for hit rate and procs."},
          {"cat": "Minor Combat Traits", "pick": "Swordsman", "alt": ["Evoker", "Channeler"], "why": "Swordsman starts Slashing at 5 (+25%) with a Trainee's Scimitar. Evocation is the biggest Spellblade school on the wiki (20 of 61) if you prefer a school trait."},
          FORAGE("Spellblades may take it."), MINER],
  ts=G, tsnote="Gathering defaults. Smithing stays off."),
 'Wizard': dict(key=['INT', 'DEX', 'STA'], builds=[
   ("Nuker (default)", {"INT": 7, "DEX": 2, "STA": 1}, "The wiki Wizard advice (Human/Dwarf): INT first, then DEX, then a little STA."),
   ("Survivor", {"INT": 5, "STA": 3, "DEX": 2}, "Wizards are fragile and mana-hungry (official); more HP for solo play; this is exactly the wiki Gnome allocation."),
   ("Max INT", {"INT": 8, "DEX": 2}, "Biggest nukes and pool in groups.")],
  traits=[{"cat": "Major Combat Traits", "pick": "Intelligent", "alt": ["Tough", "Magic Resistant"], "why": "Intelligent: +5% INT and a 15-second +50% INT burst."},
          {"cat": "Minor Combat Traits", "pick": "Evoker", "alt": ["Channeler", "Alterer"], "why": "Evocation is the biggest Wizard school on the wiki (52 of 121): direct damage and stuns."},
          READY(""), MINER],
  ts=G, tsnote="Gathering defaults. Smithing stays off."),
}

def class_mod(c):
    m = (C[c].get('modifier') or '').strip().rstrip('.').replace('+ ', '+')
    return '%s (wiki %s Creation Guide)' % (m, c) if m else 'not on the wiki class page: no sourced data yet'
def schools(c):
    return collections.Counter((s.get('class') or '').strip() for s in C[c]['spells'])
def mana_info(c, S):
    if S.get('mana') == 'CHA':
        return {'stat': 'CHA', 'text': 'The wiki Bard page says Bard mana is now tied to Charisma, not INT or WIS.', 'label': 'FACT'}
    n = sum(1 for s in C[c]['spells'] if re.match(r'^\d', str(s.get('mana') or '')))
    if n == 0 and 'mana' in ' '.join(O.get(c, {}).get('traits', [])).lower():
        return {'stat': None, 'text': 'The official %s page mentions mana costs, but no spell on the wiki list has a numeric mana cost, so which stat sets your mana is not sourced yet.' % c, 'label': 'UNVERIFIED'}
    if n == 0:
        return {'stat': None, 'text': 'No spell on the wiki %s list has a numeric mana cost.' % c, 'label': 'FACT'}
    return {'stat': 'INT/WIS', 'text': 'Your mana stat is whichever of INT or WIS is higher (wiki Statistics); %d of %d wiki %s spells cost mana.' % (n, len(C[c]['spells']), c), 'label': 'FACT'}

def race_cards(c, S):
    rs = {r: v for r, v in CG['combos'].items() if c in v and r not in CG['large']}
    st = {r: CG['races'][r]['start'][c]['stats'] for r in rs if CG['races'][r]['start'].get(c)}
    out = {}
    for r in rs:
        R = CG['races'][r]; pros, cons = [], []
        cities = sorted(CG['combos'][r][c])
        if r in st:
            for k in S['key']:
                vals = [st[x][k] for x in st]
                if len(st) > 1 and st[r][k] == max(vals) and max(vals) != min(vals): pros.append('Highest starting %s of the playable %s races (%d).' % (k, c, st[r][k]))
                if len(st) > 1 and st[r][k] == min(vals) and max(vals) != min(vals): cons.append('Lowest starting %s of the playable %s races (%d).' % (k, c, st[r][k]))
        else:
            cons.append('No %s starting stats on the wiki race page: no sourced data yet.' % c)
        rac = R.get('racial') or ''
        names = [n for n in RACIAL_WHY if re.search(r'\b%s\b' % n, rac)]
        if names: pros.append('Racial: ' + '; '.join(RACIAL_WHY[n] for n in names) + '.')
        else: cons.append('Racial ability not documented on the wiki race page.')
        res = R.get('resists')
        if res:
            for part in [p.strip() for p in res.split(',')]:
                (pros if '+' in part else cons).append('Resistance %s (race page).' % part)
        al = R.get('alignment')
        if al: (cons if al == 'Evil' else pros).append('%s alignment; starts as a %s in %s.' % (al, c, ', '.join(cities)) + (' Night Harbor is the start for good and neutral combinations (official FAQ); how it treats evil races is not sourced yet.' if al == 'Evil' else ''))
        else: cons.append('Alignment not on the wiki; starts as a %s in %s.' % (c, ', '.join(cities)))
        if R.get('note'): cons.append('Race page note: %s' % R['note'])
        if allowed('Ultravision', c, r) and r in ('Deep Elf', 'Deep Gnome'): pros.append('Can take the Ultravision trait.')
        out[r] = {'pros': pros, 'cons': cons}
    return out

def trait_entries(c, S):
    out = []
    for t in S['traits']:
        assert t['pick'] in TR, (c, t['pick']); assert allowed(t['pick'], c), (c, t['pick'])
        alt = [a for a in t['alt'] if a in TR and allowed(a, c)]
        e = dict(t, alt=alt, race_pick={})
        for r in CG['combos']:
            if c not in CG['combos'][r] or r in CG['large']: continue
            rac = CG['races'][r].get('racial') or ''
            if not allowed(t['pick'], c, r) or re.search(r'\b%s\b' % re.escape(t['pick']), rac):
                nxt = next((a for a in alt if allowed(a, c, r) and not re.search(r'\b%s\b' % re.escape(a), rac)), None)
                why = 'you already have %s as a racial' % t['pick'] if re.search(r'\b%s\b' % re.escape(t['pick']), rac) else '%s is not available to your race' % t['pick']
                e['race_pick'][r] = '%s (%s)' % (nxt, why) if nxt else 'none of the listed options (%s)' % why
        if not e['race_pick']: del e['race_pick']
        out.append(e)
    return out

for c, S in SPEC.items():
    for n, a, w in S['builds']: assert sum(a.values()) == 10, (c, n)
    O_ = O.get(c, {})
    src = [["Official class page: %s" % c, O_.get('url', '')], ["Wiki: %s (rev %s)" % (c, C[c].get('revid')), C[c]['url']]] + COMMON_SRC
    src += [["Wiki: %s (rev %s)" % (r, CG['races'][r]['revid']), CG['races'][r]['url']] for r in sorted(CG['combos']) if c in CG['combos'][r] and r not in CG['large']]
    planned = {r: 'Listed on the official %s page but not playable in Early Access (no wiki start-city row).' % c for r in [x.strip() for x in O_.get('races', '').split(',') if x.strip()] if r not in CG['combos']}
    D = {"class": c, "updated": "2026-10-18", "generated_by": "tools/chargen_classes.py", "sources": [s for s in src if s[1]],
         "stat_facts": STAT_FACTS, "class_mod": class_mod(c), "mana": mana_info(c, S),
         "wiki_advice": C[c].get('bonus_advice'),
         "builds": [{"name": n, "alloc": a, "why": w} for n, a, w in S['builds']],
         "build_caveat": "Point totals are from the wiki race pages (10 bonus points for every listed race/class). Whether a stat has a per-point cap or diminishing returns at creation is not documented on the wiki: UNVERIFIED.",
         "traits": trait_entries(c, S),
         "trait_caveat": "Trait text and race/class limits are from Template:Traits; picks that your race cannot take are swapped automatically in the race note. Which trait is 'best' is STRATEGY; no sourced numbers compare them.",
         "races": race_cards(c, S), "planned_races": planned,
         "tradeskills": {"recommend": S['ts'], "why": {s: GW[s] for s in S['ts']}, "note": S['tsnote'] + ' STRATEGY.'}}
    json.dump(D, open(os.path.join(ROOT, 'data', 'chargen', re.sub(r'[^a-z0-9]+', '-', c.lower()) + '.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print(c, 'races', len(D['races']), 'race-swaps', sum(len(t.get('race_pick', {})) for t in D['traits']))

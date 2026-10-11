---
title: Shaman playbook — solo, group, buffs, hotbars
section: shaman
desc: Shaman fight routines, buff/debuff order, hotbar and macro suggestions
sources: Wiki: Shaman Guides|https://monstersandmemories.miraheze.org/wiki/Shaman_Guides; Official deep dive|https://monstersandmemories.com/class-shaman-deep-dive; Wiki spell tables|https://monstersandmemories.miraheze.org/wiki/Shaman
---
:::tabs
=== Group
## Group routine (from the wiki Shaman Guides)
1. **Before the pull:** Berserker Spirit or Tribal Spirit on the group, Pact of Haste on melee, Ancestral Wisdom on yourself. Agree with the other healer who covers the tank.
2. **Tank has aggro → Omen of Lethargy.** If it's resisted, recast it.
3. **Pact of Renewal on the tank** *before* their health drops. Use Spirit Mending for quick top-ups.
4. **Hard target:** add Omen of Enfeeblement. Use Omen of Susceptibility when the group deals Disease, Holy or Magic damage.
5. **Group stable and mana spare:** add Malady and Ghostly Blight. Stop if the tank needs heals.
6. **Bad pull:** Rite of Mending (party HoT, long cooldown, L20+). At L40+, Ritual of Escape gets the party out.

=== Solo
## Solo routine
1. Self-buffs: Ancestral Wisdom, Berserker Spirit, Pact of Haste.
2. Pull → **Omen of Lethargy** → **Ghostly Blight** + **Malady** → Pact of Renewal on yourself → melee or kite.
3. If it goes wrong: **Root** (L12; often breaks early and can be broken by damage), then heal. Gate as a last resort.
4. Downtime: **Consume** only at high HP and out of combat. 45 s cooldown. At L12 it gives 48 mana for 98 HP (wiki).

:::warn Consuming Pact
Consuming Pact (L12) restores mana for HP but **greatly reduces incoming healing** (wiki). Never use it before or during a pull.
:::

=== Hotbars & macros
## Suggested hotbar (level 12–16) STRATEGY
| Key | Bar 1: fight | Bar 2: support / utility |
|---|---|---|
| 1 | Omen of Lethargy | Pact of Haste |
| 2 | Ghostly Blight | Berserker Spirit / Tribal Spirit |
| 3 | Malady / Greater Malady | Ancestral Wisdom |
| 4 | Pact of Renewal | Speed of the Wild |
| 5 | Spirit Mending | Invisibility vs Undead |
| 6 | Omen of Enfeeblement | Cure Disease / Dispel Magic |
| 7 | Spirit Bane III | Gate |
| 8 | Root | Soulbind |
| 9 | Consume | Summon Food / Drink |

UNCONFIRMED Macro syntax isn't documented on the wiki pages I pulled. Check the in-game macro window before copying chat macros from other games. A useful pattern if supported: an "incoming slow" party announcement bound to the Omen of Lethargy key.

=== Buff durations
## Buff and debuff durations (wiki)
| Spell | Duration | Notes |
|---|---|---|
| Berserker Spirit / Tribal Spirit | 35 min | +2 STR/STA/DEX/AGI (L1). Tribal is the group version |
| Pact of Haste | 35 min | +10% (L8) to 15% (L15) attack speed |
| Speed of the Wild | 35 min | +40% to 60% movement, outdoors only (wiki) |
| Omen of Lethargy | 1 min | 10% slow (L4). Greater 20% (L16) |
| Omen of Enfeeblement | 1 min | −4 STR/DEX/AGI (L12) |
| Malady | 1 min | 3 disease damage / 6 s |
| Ghostly Blight | 30 s | 7 + 10 / 6 s (L8) |
| Pact of Renewal | 18 s | 21 HP / 6 s (L8) |
:::

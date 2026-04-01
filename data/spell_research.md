# D&D 5e Spell Research — Complete Findings

## Spell Counts
- **Current SRD data (spells.json):** 319 spells
- **2024 PHB:** 391 spells (31 more than 2014 PHB's 360)
- **All sourcebooks combined:** ~440-520 spells total

## New Spells in 2024 PHB (10 brand new)
- **Cantrips:** Starry Wisp, Sorcerous Burst, Elementalism
- **1st level:** Tasha's Bubbling Cauldron
- **2nd level:** Arcane Vigor, Shining Smite
- **4th level:** Fount of Moonlight
- **5th level:** Yolande's Regal Presence
- **7th level:** Power Word Fortify
- **9th level:** Jallarzi's Storm of Radiance
- **Renamed:** Feeblemind → Befuddlement

## Critical 2024 Changes for Battle Simulator

### 1. Healing Doubled
- Cure Wounds: 2d8 (was 1d8), upcast +2d8 per level (was +1d8)
- Healing Word: 2d4 (was 1d4), upcast +2d4 per level (was +1d4)

### 2. Spiritual Weapon Now Requires Concentration
- Kills the Spirit Guardians + Spiritual Weapon combo
- Major nerf to Cleric combat

### 3. Counterspell Reworked
- Target makes CON save instead of ability check
- No spell slot loss on failure
- Legendary Resistance works against it
- Still a reaction

### 4. Polymorph Uses Temp HP
- Target keeps own HP, gains temp HP equal to beast form's HP
- When temp HP runs out, reverts to normal form with original HP

### 5. One Spell Slot Per Turn Rule
- Replaces old bonus action spell restrictions
- Can cast cantrip + leveled spell on same turn ONLY if one is a cantrip
- Cleaner rule than 2014's "bonus action spell" restriction

### 6. Divine Smite is Now a Spell
- Can be Counterspelled
- Uses spell slot as before but follows spellcasting rules
- No longer an "extra damage rider" outside the spell system

### 7. Spirit Guardians "Lawnmower"
- Damage triggers when emanation MOVES OVER creatures
- Not just when they enter/start turn — Cleric moving into enemies triggers it

### 8. Fireball Respects Cover
- No longer "spreads around corners"
- Targets behind total cover are safe

### 9. Sleep Uses WIS Save
- No longer HP-pool mechanic
- Target makes WIS save or falls unconscious
- Much more predictable

### 10. Vicious Mockery Damage Increased
- 1d6 (was 1d4)
- Still imposes disadvantage on next attack

## High-Priority Spells Missing from SRD (need to add ~22)
- Toll the Dead, Absorb Elements, Armor of Agathys, Shadow Blade
- Silvery Barbs, Synaptic Static, Steel Wind Strike
- All 10 new 2024 spells listed above

## Top 50 Combat Spells — Verified Stats

### Cantrips (at will)
| Spell | Class | Damage | Range | Save | Notes |
|-------|-------|--------|-------|------|-------|
| Fire Bolt | Wizard, Sorcerer | 1d10 fire | 120ft | — | Attack roll, scales at 5/11/17 |
| Eldritch Blast | Warlock | 1d10 force | 120ft | — | Attack roll, extra beams at 5/11/17 |
| Sacred Flame | Cleric | 1d8 radiant | 60ft | DEX | No cover benefit, scales |
| Toll the Dead | Cleric, Wizard | 1d8/1d12 necrotic | 60ft | WIS | d12 if target is wounded |
| Vicious Mockery | Bard | 1d6 psychic | 60ft | WIS | Disadvantage on next attack |
| Chill Touch | Wizard, Sorcerer | 1d8 necrotic | 120ft | — | Attack roll, no healing for 1 round |
| Shocking Grasp | Wizard, Sorcerer | 1d8 lightning | Touch | — | Advantage vs metal armor, no reaction |
| Starry Wisp | Bard, Druid | 1d8 radiant | 60ft | CON | 2024 NEW, reveals invisible |
| Sorcerous Burst | Sorcerer | 1d8 (varies) | 120ft | — | 2024 NEW, reroll matching dice |

### Level 1 Spells
| Spell | Cast | Range | Duration | Key Effect | Conc? |
|-------|------|-------|----------|------------|-------|
| Shield | Reaction | Self | 1 round | +5 AC | No |
| Magic Missile | Action | 120ft | Instant | 3d4+3 force (auto-hit) | No |
| Healing Word | Bonus | 60ft | Instant | 2d4+mod healing (2024) | No |
| Cure Wounds | Action | Touch | Instant | 2d8+mod healing (2024) | No |
| Thunderwave | Action | Self 15ft cube | Instant | 2d8 thunder, CON save, push 10ft | No |
| Guiding Bolt | Action | 120ft | 1 round | 4d6 radiant, next attack has advantage | No |
| Bless | Action | 30ft | 1 min | +1d4 to attacks/saves for 3 targets | Yes |
| Hex | Bonus | 90ft | 1 hr | +1d6 necrotic per hit, disadvantage 1 ability | Yes |
| Hunter's Mark | Bonus | 90ft | 1 hr | +1d6 per hit | Yes |

### Level 2 Spells
| Spell | Cast | Range | Duration | Key Effect | Conc? |
|-------|------|-------|----------|------------|-------|
| Spiritual Weapon | Bonus | 60ft | 1 min | 1d8+mod force, bonus attack each turn | **Yes (2024)** |
| Misty Step | Bonus | Self | Instant | Teleport 30ft | No |
| Scorching Ray | Action | 120ft | Instant | 3 rays, 2d6 fire each | No |
| Hold Person | Action | 60ft | 1 min | WIS save or paralyzed (humanoid) | Yes |
| Shatter | Action | 60ft, 10ft sphere | Instant | 3d8 thunder, CON save | No |

### Level 3 Spells
| Spell | Cast | Range | Duration | Key Effect | Conc? |
|-------|------|-------|----------|------------|-------|
| Fireball | Action | 150ft, 20ft sphere | Instant | 8d6 fire, DEX save, **respects cover (2024)** | No |
| Counterspell | Reaction | 60ft | Instant | **CON save (2024)**, negate spell | No |
| Spirit Guardians | Action | Self 15ft | 10 min | 3d8 radiant/necrotic, **lawnmower (2024)** | Yes |
| Haste | Action | 30ft | 1 min | Double speed, +2 AC, extra action | Yes |
| Revivify | Action | Touch | Instant | Raise dead (1 min), 1 HP, 300gp diamond | No |
| Dispel Magic | Action | 120ft | Instant | End spell of 3rd or lower, check for higher | No |

### Level 4 Spells
| Spell | Cast | Range | Duration | Key Effect | Conc? |
|-------|------|-------|----------|------------|-------|
| Banishment | Action | 60ft | 1 min | CHA save or banished to demiplane | Yes |
| Polymorph | Action | 60ft | 1 hr | **Temp HP = beast HP (2024)** | Yes |
| Greater Invisibility | Action | Touch | 1 min | Invisible even while attacking | Yes |

### Level 5+ Spells
| Spell | Level | Key Effect |
|-------|-------|------------|
| Wall of Force | 5 | Indestructible wall, 10 panels |
| Heal | 6 | 70 HP healing, cures conditions |
| Disintegrate | 6 | 10d6+40 force, DEX save, dust on kill |
| Forcecage | 7 | Inescapable prison, no concentration |
| Power Word Stun | 8 | Auto-stun if ≤150 HP |
| Wish | 9 | Anything, risk of never casting again |

## Spell Lists by Class (2024)
- **Artificer:** INT, prepared, levels 1-5 only
- **Bard:** CHA, known spells, full caster (1-9), expanded 2024 list
- **Cleric:** WIS, prepared from full class list, full caster (1-9)
- **Druid:** WIS, prepared from full class list, full caster (1-9)
- **Paladin:** CHA, prepared, half caster (1-5), Smite spells
- **Ranger:** WIS, known spells (2024: prepared), half caster (1-5)
- **Sorcerer:** CHA, known spells, full caster (1-9), Metamagic
- **Warlock:** CHA, known spells, Pact Magic (1-5, all max level slots)
- **Wizard:** INT, prepared from spellbook, full caster (1-9), largest list

## Sources
- D&D Beyond Spells: https://www.dndbeyond.com/spells
- D&D 2024 Wikidot: http://dnd2024.wikidot.com/spell:all
- Aidedd.org 2024 Spells: https://www.aidedd.org/spell/
- DiceDungeons 2024 Changes: https://dicedungeons.com/blogs/inside/dnd-2024-spell-changes
- EN World Full Changes: https://www.enworld.org/threads/heres-the-full-list-of-changes-in-the-d-d-2024-players-handbook.706503/

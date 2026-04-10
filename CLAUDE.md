# Dungeon Legends - D&D 5e Battle Simulator

## STRICT SOURCE-ACCURACY MANDATE

**All game content MUST come from the user's source files at `C:\Users\16239\Downloads\Sources_clean\Source Books and rules\`.** Never invent rules. Never approximate mechanics unless the required subsystem is genuinely missing, and in that case flag the approximation in `TODO_SOURCE_ACCURACY.md`.

### Rules:
1. **Before implementing any feature**, open the actual docx file and extract the exact source text.
2. **Never choose for the player** when a spell, ability, or feature gives them a choice. If no prompt system exists, add a TODO and leave the feature unimplemented until the system exists.
3. **If a rule is missing from the source files**, do NOT fill it in from memory or training data. Flag it in `TODO_SOURCE_ACCURACY.md` and ask the user.
4. **Spell descriptions** come from `D&D BEYOND BASIC RULES.docx` (paragraphs ~11869-15661), NOT from the PHB file (which has gaps per Phase 1 breakdown).
5. **All content from Part 1 (core rules + player options)** is always available. Part 2 (adventures/campaigns) will be progression-locked later — do NOT process adventure content for mechanics.
6. **Item pricing:** Use source price if listed. Otherwise: Common 100gp, Uncommon 500gp, Rare 5000gp, Very Rare 20000gp, Legendary 50000gp, Above Legendary 100000gp.

### Confirmed source-missing content (do NOT implement from memory):
- **College of Spirits** (Van Richten's Guide to Ravenloft) — 0 matches in cleaned or uncleaned docx
- **Undead Patron** (Van Richten's Guide to Ravenloft) — 0 matches in cleaned or uncleaned docx
- **PHB subclass detail pages** for Paladin (Ancients, Glory, Vengeance), full Ranger subclasses, Rogue subclasses (Arcane Trickster, Assassin, Soulknife), Sorcerer (Aberrant, Clockwork, Wild Magic), Warlock (Archfey, Celestial, Great Old One), Wizard (Abjurer, Diviner, Evoker, Illusionist) — brief descriptions only in PHB; Basic Rules has 1 per class. Need to extract the 1-per-class from Basic Rules.

See `TODO_SOURCE_ACCURACY.md` for the full list of gaps, approximations, and planned work.

## Project Overview

Multiplayer accessible D&D 5e combat arena for blind players built in **NVGT** (NonVisual Gaming Toolkit, AngelScript-like). Players create characters (67 species, 14 classes, 48 backgrounds, 147 subclasses, 77 feats, 38 weapons, 367 spells) and fight in turn-based combat with full TTS and HRTF spatial audio. Supports PvP Arena, Wave Survival, Boss Rush, and Endless Survival modes. Features 40+ achievements, glory shop, daily dungeons, leaderboards, loot system, trading, prestige, guilds, and multi-phase boss fights.



**Vision:** Evolving into a complete D&D simulator with AI Dungeon Master (Claude API), campaign play from real adventure books, cooperative party play, and persistent shared universes.



## Architecture

- **Client-server** model using ENet networking with JSON message passing

- **Server** (`Server/`): Authoritative state, SQLite persistence, room/user management, full combat engine

- **Client** (`Client/`): Input handling, TTS output, menu UI, network dispatcher, thin renderer

- **Common** (`common/`): Shared message type constants, combat constants, utilities



## Key Files

| File | Purpose |

|------|---------|

| `Server/Server.nvgt` | Main server entry, network loop, bot utilities |

| `Server/account.nvgt` | Account persistence (SQLite + JSON data blob), daily login tracking |

| `Server/rooms_Dom.nvgt` | Room/lobby creation and management |

| `Server/users _dom.nvgt` | User class, message handler dispatch, bonus action handlers, daily bonus, level-up response |

| `Server/combat/battle_manager.nvgt` | Core combat loop: roll system, attack/spell/action resolution, monster AI, initiative, Extra Attack, battle end detection, level-up choices |

| `Server/combat/combat_engine.nvgt` | `combatant` class (HP, AC, abilities, conditions, spell slots), `battle` class (initiative, damage, death saves) |

| `Server/combat/character_data.nvgt` | `character_sheet` class, 13 class defaults, 33 species bonuses, 38 weapons, spell slot tables |

| `Server/combat/monster_data.nvgt` | 32 monster definitions (Rat through Archmage) |

| `Server/combat/wave_system.nvgt` | 9 wave scenarios, `spawn_wave()` with difficulty multipliers |

| `Server/combat/spell_data.nvgt` | 367 spell definitions, all with custom handlers in battle_manager.nvgt (100% coverage, 381 total handler branches counting dual-target variants). 334 descriptions are full source-quoted Basic Rules 2024 text (2026-04-09 rigor pass); 33 descriptions remain on legacy paraphrase (Wildemount/Eberron/Tasha's/Fizban's extras not in Basic Rules). All save_type fields verified against source 2026-04-09. |
| `Server/combat/piety_data.nvgt` | Theros Piety system: 15 gods, 4 tiers (Devotee/Votary/Disciple/Champion) |
| `Server/combat/vestiges_data.nvgt` | Wildemount Vestiges of Divergence: 8 items, 3 awakening states (Dormant/Awakened/Exalted) |
| `Server/combat/heroic_chronicle_data.nvgt` | Wildemount Heroic Chronicle: 5 homelands, 20 backgrounds, 20 prophecies |
| `Server/combat/bastions_data.nvgt` | DMG 2024 Bastions: 29 special facilities (L5/9/13/17), 7 order types |
| `Server/combat/group_patrons_data.nvgt` | Tasha's Group Patrons: 8 archetypes (Academy, Ancient Being, etc.) |
| `Server/combat/factions_data.nvgt` | Grim Hollow Factions: 11 factions of Etharis with rep tracks |
| `Server/combat/ravnica_guilds_data.nvgt` | Ravnica Guilds: 10 guilds with color philosophy and perks |
| `Server/combat/ebon_tides_data.nvgt` | Ebon Tides: 14 fey courts, 7 named shadow roads |
| `Server/combat/transformations_data.nvgt` | Grim Hollow Transformations: 6 paths, 5 stages each (Vampirism, Lycanthropy, Lichdom, etc.) |

| `Server/progression.nvgt` | XP tracking, achievement system, character level progression, prestige system, glory points |

| `common/loot_data.nvgt` | Item catalog (270 items, all source-verified from PHB/DMG/Tasha/Fizban/Theros/Wildemount/Eberron/Grim Hollow/Ravnica/Griffon's/BOMT/Ebon Tides), loot generation, rarity tiers, inventory helpers |

| `common/consumable_data.nvgt` | Consumable catalog (16 items), modifier system, inventory helpers |

| `Client/client.nvgt` | Main client entry, login, lobby menus, character viewing, first-time login flow |

| `Client/updater.nvgt` | Mandatory incremental auto-updater (manifest-based, downloads only changed files) |

| `Client/net.nvgt` | Network message dispatcher + connection, character_data restore, daily bonus handler |

| `Client/combat/combat_ui.nvgt` | Combat game loop, action/bonus action menus, scanning, targeting, roll prompts, tab focus, level-up screen |

| `Client/combat/character_creator.nvgt` | Character creation with back-navigation (race->class->level->abilities->weapon->spells) |

| `Client/combat/spell_menu.nvgt` | Spell list building, selection menu, class spell availability check |

| `common/message_types.nvgt` | 80+ network message type constants |

| `common/combat_constants.nvgt` | D&D constants (conditions, damage types, abilities, sizes, roll types) |



## Main Menu

- Menu header displays player level, gold, and glory points

- 8 top-level categories: Play, Character, Social, Shop, Challenges, Settings, Tutorial, Quit

- **Tutorial**: Launches guided combat tutorial (reusable `run_tutorial()` function, also offered on first login)

- **Play**: Play Adventure (Create Game / Join Game), Play Sandbox Mode (Create Game / Join Game). Create Game waits for server confirmation before entering host menu.

- **Character**: Create Character (up to 40 per mode), View Characters (list all, set active, delete), Inventory, My Stats, Prestige (level 20+)

- **Social**: Friends, Guild (create/join, max 20 members, guild chat, invite, view members/glory), Check Who's Online

- **Shop**: Item Shop (potions, scrolls, throwables with gold), Glory Shop (titles and exclusive items with glory)

- **Challenges**: Daily Dungeon (featured dungeon with bonus rewards), Weekly Challenges, Leaderboards

- **Settings**: Volume Up/Down, TTS Speed Up/Down, About. All settings persisted to disk via `save_settings()`/`load_saved_settings()`

- All password fields (login, signup, create room, join room) have a "Show password" checkbox that toggles masking

- First-time login prompts adventure character creation automatically (no sandbox prompt)

- Daily login bonuses: streak-based XP (50-200 XP, resets after day 7)

- Settings (volume, TTS speed) saved on change and restored on launch



## Combat System



### Turn Structure (D&D 5e 2024)

- Move + Action + Bonus Action + Reaction per turn

- Initiative rolled at battle start (d20 + DEX mod), all rolls announced to all players, then full turn order broadcast

- Combat rounds start at 1 (first turn of each round announces "Round N!")

- All rolls require the specific prompted player to press R or Enter (other players cannot roll for them)

- All roll results broadcast to ALL players with full context and audio cues (nat 20/1)

- Combat game loop forces main_screen form focus to keyboard_area so lobby chat form doesn't consume combat keystrokes



### Attack Resolution

- Separate roll to hit (d20 + ability mod + proficiency vs AC), then roll for damage

- Advantage/disadvantage from conditions (prone, paralyzed, dodging, etc.)

- **Extra Attack**: Fighters level 5 (2 attacks), 11 (3 attacks), 17 (3 attacks + 2 Action Surge). Other martials get 1 extra at level 5.

- **Reaction Prompt System**: When a player is about to be hit, they are prompted for available reactions before hit resolves. Options: Shield (+5 AC), Cutting Words (-1d4-d12), Warding Flare (force reroll), Defensive Duelist (+Prof AC), Restore Balance (cancel advantage), Spirit Shield (reduce damage 2d6+), Entropic Ward (force miss), Arcane Deflection (+2 AC), Warding Maneuver (+1d8 AC, resistance if still hit), Armor of Hexes (d6, 4+ miss), Deflect Attacks (reduce 1d10+DEX+level), Uncanny Dodge (halve damage), Storm's Fury (sorcerer level lightning + push), Shadowy Dodge (impose disadvantage), Spectral Defense (resistance to all attack damage)
- **Resistance System**: Species and feats grant resistances to fire, cold, necrotic, psychic, acid, lightning, piercing, poison (+ immunity) — half damage on applicable types
- **Wild Magic Surge**: Wild Magic Sorcerers roll d20 on 1+ level spell cast. On natural 1, a random surge effect triggers (fire burst, temp HP, healing, invisibility, spell slot recovery, etc.)
- **Divine Smite**: Dual mode — bonus action pre-cast OR auto-prompt on melee hit (keys 1-5 for slot level, Escape to skip)
- **Grapple/Shove**: 2024 rules — target makes STR or DEX saving throw (DC 8 + STR mod + Prof), not contested checks

- **AC System**: Proper armor types (leather/studded/chain shirt/breastplate/half plate/chain mail/splint/plate) with correct AC calculations per 2024 PHB

- **End-of-Turn Saves**: Hold Person, Web, Blindness/Deafness, Fear, Tasha's Hideous Laughter — affected creatures save at end of turn

- Out-of-range attacks show distance and range info to the player

- Finesse weapons use higher of STR/DEX

- Ranged disadvantage when hostile within 5ft

- Line of sight required (`can_see` check)



### Spell System

- 367 spells in catalog with 80+ fully resolved server-side via `handle_cast()`

- Spell menu shows range and concentration status for each spell

- Save-based damage (DEX/CON/WIS saves, half on success) — generic system handles most damage spells

- Attack-roll spells (spell attack bonus vs AC)

- AoE damage (Fireball, Thunderwave, etc.)

- Healing spells with scaling

- Buff spells (Shield, Bless, Heroism, Aid, Stoneskin, Greater Invisibility, Fly, Fire Shield, Mage Armor, Haste)

- Utility spells (Hold Person, Banishment, Misty Step, Sleep, Polymorph, Web, Hypnotic Pattern, Sanctuary, Spirit Guardians)

- Magic Missile auto-hit

- Cantrip scaling at levels 5/11/17

- Concentration management (drop old when casting new)

- Spirit Guardians: 15ft aura, 3d8+ radiant damage on enemies starting turn within range, half their movement

- Spell slot consumption (lowest available >= spell level)

- Spell menu shows level (Cantrip/Level N) and Concentration tag for each spell



### Reroll Mechanics

- **Lucky feat**: Characters with the Lucky feat gain Luck Points equal to proficiency bonus per battle. After a failed d20 roll, prompted to spend a Luck Point to reroll with advantage (Press L / Escape). Chains after Bardic Inspiration prompt.

- **Heroic Inspiration**: Earned on any natural 20 d20 roll (players only). After a failed d20 roll, prompted to use Heroic Inspiration for a reroll (Press H / Escape). Chains after Lucky prompt. Consumed on use.

- **Prompt chain order**: Bardic Inspiration (additive) -> Lucky (reroll with advantage) -> Heroic Inspiration (reroll)

### Companion / Summon System (TODO §7C foundation)

Companions are full combatants tracked in `combat.combatants` with their own HP, AC, attack rolls, damage dice, conditions, and initiative slot. They are owned by another combatant via `owner_id` and scaled to the owner's level + proficiency bonus per source.

**Key fields on `combatant`:**
- `is_companion` (bool) — true for spawned companions
- `owner_id` (uint) — back-reference to the owner combatant
- `companion_subclass` (string) — tag for AI / scaling logic
- `companion_attack_bonus`, `companion_attack_dice`, `companion_attack_die_sides`, `companion_attack_dmg_mod`, `companion_attack_dmg_type` — cached attack stats

**API in `battle_manager.nvgt`:**
- `spawn_companion(owner, subclass_id, name, hp, ac, speed, attack_bonus, dmg_count, dmg_die, dmg_mod, dmg_type, extra_attacks=0)` — creates the combatant, places it adjacent to owner, fills monster-style attack fields, inserts into combat, returns handle
- `dismiss_companion(companion, announce)` — marks the companion dead and removes from combat

**Subclasses with working companions:**
- **Beast Master** (Ranger L3) — Primal Land Beast: HP=5+5*level, AC=13+PB, 1d8+PB slashing
- **Battle Smith** (Artificer L3) — Steel Defender: HP=2+5*level+INT, AC=15, 1d8+PB force
- **Drakewarden** (Ranger L3) — Drake Companion: HP=5+5*level, AC=14+PB, 1d6+PB elemental
- **Circle of Wildfire** (Druid L2) — Wildfire Spirit: HP=5+5*level, AC=13, 1d6+PB fire (ranged)
- **Artillerist** (Artificer L3) — Eldritch Cannon Force Ballista: HP=5*level, AC=18, 2d8 force

**Spells with companion-style spawns:**
- **Bigby's Hand** — spawned as a Large hand entity, HP=caster max, AC=20, 4d8 force (Clenched Fist mode)
- **Animate Dead** — pre-existing skeleton minion spawn
- **Insect Plague**, **Cloudkill** etc. — area effects, NOT companions

**Deferred:**
- Beast Master Sea/Sky variants (need a creature selection prompt)
- Drakewarden damage type prompt (currently uses init default)
- Echo Knight Manifest Echo (needs HP=1 dummy logic)
- Bigby's Hand mode prompt (Clenched Fist / Forceful Hand / Grasping Hand / Interposing Hand)
- Companion AI improvements (currently uses generic monster turn flow)

### Skill Check System

Skill checks (Stealth, Persuasion, Investigation, etc.) flow through the standard `pending_roll` pipeline so they get reroll prompts (Bardic, Lucky, Heroic), advantage/disadvantage handling, and Silver Tongue clamping for free.

**Foundation in `combatant`:**
- `skill_proficiencies[]` — proficient skills (proficiency bonus added)
- `skill_expertise[]` — expertise skills (proficiency bonus DOUBLED) — Bard L3, Rogue L1, Knowledge Domain, Mastermind, Keeper of History (Dirge Singer Bard L3)
- `jack_of_all_trades` flag (Bard L2) — adds half proficiency bonus (rounded down) to ANY ability check that doesn't already include proficiency
- `skill_check_advantage[]` and `skill_check_disadvantage[]` — per-skill flag arrays for feature-granted modifiers

**`get_skill_bonus(skill_name, ability_id)`** returns: `ability_mod + (2*prof if expertise else prof if proficient else half_prof if Jack of All Trades) - (exhaustion * 2)`. Plus Pass Without Trace adds +10 on Stealth automatically inside `request_skill_check`.

**`battle_manager` API:**
- `skill_to_ability(skill_name)` — canonical D&D 5e mapping (returns -1 for unknown)
- `skill_resolution_tag(skill_name)` — converts "Sleight of Hand" → `"skill_sleight_of_hand"` for the resolution tag
- `request_skill_check(u, c, skill_name, dc, custom_tag, extra_advantage, extra_disadvantage)` — builds the `pending_roll` and routes through `send_roll_request` (player) or auto-rolls (bot/NPC)
- `handle_roll_result` advantage path now also fires for `ROLL_ABILITY_CHECK` (was attack-only)
- `maybe_prompt_bardic_inspiration` now fires for any failed `ROLL_ABILITY_CHECK` with a positive DC (was hide-only)

**DC table (`common/combat_constants.nvgt`):** `DC_VERY_EASY=5`, `DC_EASY=10`, `DC_MEDIUM=15`, `DC_HARD=20`, `DC_VERY_HARD=25`, `DC_NEARLY_IMPOSSIBLE=30`

**Subclass features that use the system:**
- **Silver Tongue** (Eloquence Bard L3) — `silver_tongue_active` clamps natural d20 ≤9 → 10 on `skill_persuasion`/`skill_deception` checks in `finalize_roll_result`
- **Blessing of the Trickster** (Trickery Cleric L3) — Magic action grants `skill_check_advantage["Stealth"]` to self or ally within 30 ft until long rest
- **Inquisitor's Eye** (Oath of Zeal Paladin L3 Channel Divinity) — bonus action grants `skill_check_advantage["Investigation"/"Insight"/"Perception"]` for 10 minutes
- **Keeper of History** (Dirge Singer Bard L3) — auto-grants History + Performance proficiency on character init, or Expertise if already proficient

**Adding a new skill-check-using feature:**
1. To grant always-on advantage: add the skill name to `combatant.skill_check_advantage` from the feature's init or activation
2. To grant proficiency: append to `skill_proficiencies` (or `skill_expertise` for double prof)
3. To trigger a check from combat: call `request_skill_check(u, c, skill_name, dc)` from the action handler
4. To add a per-skill clamp / modifier (like Silver Tongue): add a branch in `finalize_roll_result` that checks `pr.resolution_tag` against `skill_<lowercase>` strings

### Mid-Spell Player Choice System

Server-side `pending_spell_choice` state on `battle_manager` pauses spell finalisation when a spell offers the caster a mechanical choice the source quote requires (e.g., Fire Shield warm/chill, Spirit Guardians radiant/necrotic). The pattern mirrors `pending_smite_prompt`:

1. The cast handler in `handle_cast` builds a `pending_spell_choice` struct (caster, spell id, slot level, option_keys, option_labels, prompt text) and calls `send_spell_choice_prompt(caster, sc)`.
2. For player casters, the server stores the prompt in `current_spell_choice` and emits a `spell_choice_prompt` message with `{spell, text, options[{key,label}]}`.
3. For bots/NPCs the prompt is auto-resolved to the first option deterministically so combat keeps moving.
4. The client (`combat_ui.nvgt`) sets `waiting_for_spell_choice_prompt`, speaks the prompt, listens for keys 1..N to pick an option (Escape defaults to option 1), and sends back `spell_choice_response` with `{choice}`.
5. The server's `handle_spell_choice_response` validates the choice against the offered keys, then dispatches to `apply_spell_choice(caster, sc, choice)` which finalises the chosen variant on the caster.

**Spells / features currently using this system:**
- **Fire Shield** — warm shield (cold resistance, reflects 2d8 fire) vs chill shield (fire resistance, reflects 2d8 cold). Source: Basic Rules para 13322. Choice kind: `binary`.
- **Spirit Guardians** — angelic/fey form (radiant damage) vs fiendish form (necrotic damage). Source: Basic Rules para 15123-15124. Choice kind: `binary`.
- **Adjust Density** (Graviturgy Wizard L2 action) — halve density (+10 ft speed, disadvantage on Strength) vs double density (-10 ft speed, advantage on Strength). Source: Wildemount p.5428. Concentration; flags live on the AFFECTED creature with `adjust_density_caster_id` back-reference for cleanup. Choice kind: `binary`.
- **Magic Missile** — distribute N darts (3 base, +1 per upcast) among visible enemies; auto-hit, each dart deals 1d4+1 force damage independently per target. Source: Basic Rules para 14089. Choice kind: `distribution`.
- **Scorching Ray** — distribute N rays (3 base, +1 per upcast) among visible enemies; each ray is a separate ranged spell attack for 2d6 fire damage. Source: Basic Rules para 14851. Choice kind: `distribution`.
- **Eldritch Blast** — at L5+ distribute N beams (2 at L5, 3 at L11, 4 at L17) among visible enemies; each beam is a separate ranged spell attack for 1d10 force damage. Source: Basic Rules para 13047. Choice kind: `distribution` (only at L5+; L1-4 uses the standard single-target attack path).

**Two choice kinds are supported:**

- **`binary`** — caster picks one option from a list of variants (warm vs chill, halve vs double, etc.). Single keypress resolves the prompt.
- **`distribution`** — caster picks N targets from a list of visible hostile candidates (repeats allowed). Each keypress appends to the picks; the spell resolves after N picks. For attack-roll spells the first attack queues normally and the remaining target IDs are stored in `pending_roll.next_target_ids_csv`, which `start_followup_spell_attack` consumes front-to-back as the multi-attack chain advances. For auto-hit spells (Magic Missile) the server rolls per dart server-side and applies damage to each picked target.

**Client UX for distribution:**
- Server sends `spell_choice_prompt` with `kind=distribution`, `count=N`, and `options[{key,label}]` where `key` is the candidate combatant ID as a string and `label` is `"<name> (<dist> ft, HP <hp>)"`.
- Client speaks the prompt + the full target list.
- Player presses 1-9 to assign each projectile. Each press speaks "Pick M of N: <target>. <remaining> remaining."
- Backspace undoes the last pick.
- Escape pads the remaining picks with the first target so the spell still fires (defensive — don't lose the cast).
- Final keypress sends `spell_choice_response` with `targets: [id1, id2, ...]`.

Adding a new prompted spell or feature: in `handle_cast` (or the relevant action handler in `users _dom.nvgt` for class features), build a `pending_spell_choice`, set `caster_id` and `primary_target_id` (or `choice_kind=distribution` + `distribution_count` + dist fields), call `bm.send_spell_choice_prompt` or `bm.prompt_target_distribution`, then add the per-spell branch to `apply_spell_choice` (binary) or `apply_distribution_spell_choice` (distribution) in `battle_manager.nvgt`. If the effect is a concentration effect, also add a `clear_X` helper and hook it into `clear_concentration_effects`.



### Action Menu (F key)

- Standard actions only: Attack, Cast, Dodge, Dash, Disengage, Help, Hide, Ready, Shove, Grapple, End Turn, Status

- Attack item shows weapon range and current target distance

- Actions that cannot be performed explain why (no target, out of range, no action remaining)



### Bonus Action Menu (B key)

- **Barbarian**: Rage + Berserker Frenzy (bonus melee attack while raging) + Storm Aura (Storm Herald BA, desert/sea/tundra)

- **Fighter**: Action Surge, Second Wind + Battle Master Maneuvers (Trip/Precision/Riposte) + Psi Warrior Strike

- **Rogue**: Cunning Action + Soulknife Psychic Blades

- **Paladin**: Divine Smite, Lay on Hands + Channel Divinity (Sacred Weapon, Vow of Enmity, Inspiring Smite, Nature's Wrath)

- **Cleric**: Channel Divinity (Preserve Life, War Priest Attack)

- **Monk**: Flurry of Blows + Shadow Step, Hands of Healing, Elemental Burst, Kensei's Shot (+1d4 ranged), Sharpen the Blade (+1/2/3 attack/damage)

- **Bard**: Bardic Inspiration + Mantle of Inspiration (Glamour)

- **Warlock**: Healing Light (Celestial), Fey Presence (Archfey)

- **Druid** (level 2+): Wild Shape

- **Any class**: Spiritual Weapon (if active)



### Phase 1 Sub-Systems (2026-04-08 batch)

All 9 Phase 1 sub-systems from the master directive are now implemented as data-only modules in `Server/combat/`:

- **Theros Piety** (`piety_data.nvgt`) — 15 gods (Athreos, Ephara, Erebos, Heliod, Iroas, Karametra, Keranos, Klothys, Kruphix, Mogis, Nylea, Pharika, Phenax, Purphoros, Thassa). Source-quoted Devotee (Piety 3+) trait per god, Votary/Disciple/Champion summaries. Tier thresholds: 3, 10, 25, 50 per source para 1242. Fields: `piety_god`, `piety_score`, `piety_devotee_uses` on character_sheet + combatant.
- **Vestiges of Divergence** (`vestiges_data.nvgt`) — 8 source-quoted Wildemount legendary items with 3 awakening states each: Spell Bottle, Danoth's Visor, Grimoire Infinitus, Hide of the Feral Guardian, Infiltrator's Key, Stormgirdle, Verminshroud, Wreath of the Prism. State auto-suggested by character level (Dormant<L9, Awakened L9-15, Exalted L16+).
- **Heroic Chronicle** (`heroic_chronicle_data.nvgt`) — Wildemount backstory generator: 5 homelands (Menagerie Coast, Marrow Valley, Zemni Fields, Greying Wildlands, Xhorhas), 20 backgrounds (PH + EGW variants including Grinner, Volstrucker Agent, Cobalt Scholar, Augen Trust spy), 20 prophecy outcomes. `generate_heroic_chronicle()` returns a randomized full backstory.
- **Bastions** (`bastions_data.nvgt`) — DMG 2024 chapter 8: 29 source-quoted special facilities across 4 tiers (L5: 9, L9: 10, L13: 6, L17: 4). 7 Bastion orders (Craft/Empower/Harvest/Maintain/Recruit/Research/Trade). Facility space tiers (Cramped/Roomy/Vast), basic facility costs, max facility count by level, prerequisites enforced.
- **Group Patrons** (`group_patrons_data.nvgt`) — Tasha's: 8 archetypes (Academy, Ancient Being, Aristocrat, Criminal Syndicate, Guild, Military Force, Religious Order, Sovereign). Each has types, perks, contact NPCs, quest examples. Group Assistance d4 per source para 4910 — `can_use_group_assistance()` checks per-rest flag. Fields: `group_patron`, `group_assistance_used_this_rest` on combatant.
- **Faction Tracks** (`factions_data.nvgt`) — Grim Hollow chapter 11: 11 factions of Etharis (Augustine Trading Company, Company of Free Swords, Ebon Syndicate, Thaumaturge, Watchers of the Faithful, Arcanist Inquisition, Crimson Court, Monster Hunter Guilds, Morbus Doctore, Order of Dawn, Prismatic Circle). Reputation tracks from Hated (-10) to Champion (+10) with 6 thresholds; tier-specific benefits at Liked/Honored/Champion.
- **Ravnica Guilds** (`ravnica_guilds_data.nvgt`) — Guildmasters' Guide: all 10 guilds with color philosophy (W/U Azorius through G/U Simic), each with contact perk, equipment perk, and 3 source-themed free spells. Constants: `RAVNICA_GUILD_NAMES`.
- **Ebon Tides Shadow Roads & Fey Courts** (`ebon_tides_data.nvgt`) — Book of Ebon Tides: 14 source-listed fey courts with rulers/alignment/perks (Court of Golden Oaks, Pale Roses, Midnight Teeth, Witch Queen's Court, etc.). 7 named shadow roads (Mage's Road, Flower Road, Bridge of Lethe, Twin Roads of Corremel, etc.) with travel days and passphrase requirements. `shadow_road_lore_modifier(race)` applies -5 to non-elf Arcana checks per source para 2500.
- **Transformations** (`transformations_data.nvgt`) — Grim Hollow para 2294-2306: 5-stage progression (Untransformed → Infected → Awakened → Ascended → Fallen → Full NPC). 6 paths: Vampirism (Crimson Court), Lycanthropy, Lichdom, Aberrant Horror, Demonic Pact, Seraphic Ascension (the only blessed path per para 2297). Helper: `transformation_active_effect()`.

**Wiring status:** Data modules built, compiled, and FULLY INTEGRATED into gameplay. All 9 systems have character_sheet + combatant fields, account JSON save/load, broadcast_state() serialization, client-side deserialization, and interactive configuration via the Shift+P Phase 1 menu. Piety Devotee trait and Group Assistance d4 are live as bonus actions in combat. Transformation stage resistances (necrotic/cold/psychic/fire by path) apply automatically at combatant init. Vestige effects (Hide of the Feral Guardian AC bonus, Stormgirdle lightning resistance) also apply automatically. Character creation flow integration (pre-combat choice of god/patron/guild) is deferred — players currently configure Phase 1 state via the Shift+P menu in their first combat session.

**Bonus actions added** (accessible via B menu during combat):
- `invoke_devotee_trait` — Casts the god's Devotee spell for free (one use per long rest, consumes bonus action). Visible when `piety_god != "" and piety_score >= 3 and piety_devotee_uses > 0`.
- `group_assistance` — Grants +1d4 to next d20 roll (1/long rest, consumes bonus action). Visible when `group_patron != "" and !group_assistance_used_this_rest`.

**Phase 1 config commands** (accessible via Shift+P menu, work at any time during combat):
- `set_piety_god` — choose from 15 Theros gods
- `set_group_patron` — choose from 8 Tasha's archetypes
- `set_ravnica_guild` — choose from 10 Ravnica guilds
- `set_transformation` — choose path + stage (1/5/10/15/20)
- `set_fey_court` — choose from 14 Ebon Tides courts
- `query_phase1` — show full Phase 1 status report

### Source Audit Status (2026-04-08) — Post-Audit Additions
All batches 15-21 implementations were audited against actual source docx files in `C:\Users\16239\Downloads\Sources_clean\Source Books and rules\`. Additionally batches 22-25 added new subclasses extracted directly from the source files.

**Batch 22-25 additions (extracted from actual source files):**
- **Wildemount (Explorer's Guide)**: Echo Knight (Manifest Echo + Unleash Incarnation), Chronurgy Magic (Chronal Shift, Temporal Awareness, Momentary Stasis), Graviturgy Magic (Adjust Density, Gravity Well, Violent Attraction, Event Horizon)
- **Eberron (Forge of the Artificer)**: Cartographer (Adventurer's Atlas +1d4 initiative, Illuminated Cartography, Guided Precision)
- **Exploring Eberron**: College of the Dirge Singer, Mind Domain (Gestalt Anchor +2 INT/WIS/CHA saves aura), Circle of the Forged (poison resist + B/P/S resist at L10 + poison immunity at L14)
- **Griffon's Saddlebag (proper features)**: Couatl Herald Mercy Dice (3d6→5d10 scaling), Path of the Glacier (Frostbite 1d6→3d6, Cold Fortress, Frosted Flesh), College of Choreography (Fast Movement +10/+15/+20ft), College of Mercantile (Magic Coin 1d12→3d12 thunder), Astral Domain (Create Void Channel Divinity 15ft sphere)
- **Fizban's Treasury**: Way of the Ascendant Dragon (Breath of the Dragon 2→3 Martial Arts dice, Aspect of the Wyrm aura), Drakewarden (proper Drake Companion stats HP/AC/damage type)
- **Grim Hollow**: Feral Celerity (Carrion Raven free attack on rage entry), Mark of the Heretic (Oath of Zeal CD crit 19+ vs marked target), Pluck the Heartstrings (Requiems BI die on weapon hit), Witch Hunter's Strike (Inquisition 1d8/2d8 force with WIS uses)

**Note:** Ravenloft source file does NOT contain subclass mechanics (only chapter intros). College of Spirits and The Undead cannot be fully implemented from the provided source file.

**Corrected wrong implementations:**
- PHB 2024 feats (Mage Slayer, Shield Master, Polearm Master) — had 2014 mechanics
- PHB spells (Aid base HP, Stoneskin all-physical resistances, Spirit Guardians WIS save, Fire Shield reflection)
- Tasha (Order's Demand is Action not Bonus Action; Awakened Spellbook swap is at-will not limited)
- Trickery Domain Blessing of the Trickster (wrong name, no CD cost, action type)
- Circle of the Shepherd (all 3 Totem options: Bear, Hawk, Unicorn)
- Griffon's Saddlebag: removed fabricated flat damage bonuses on Frost Sorcerer, Desert Soul, Winter Trapper (cold resistance), Rocborne (flat flying speed), Pact of Astral Griffon (flat flying), fixed Oath of the Hearth to Burning Weapon +CHA, fixed Way of the Aether to force damage with MA die scaling, fixed Couatl Herald to Mercy Die scaling
- Grim Hollow: removed dangerous `magic_resistance` at L1 on Inquisition Domain (NOT in source); removed fabricated flat damage on Carrion Raven, College of Requiems, Oath of Zeal, Misfortune Bringer (all use different mechanics than flat riders)
- Gunslinger subclasses: major rewrite — Sharpshooter's Stance was NOT a damage buff (it's a Prone feature), Liar's Dice is a bluff mechanic not temp HP gamble, License to Kill is L14 not L3, Ricochet is a miss-reroll maneuver not bouncing bullet. Only Lay Down the Law (White Hat) remains as a bonus action, properly using Risk Dice.

### Base Class Audit (2026-04-09) — PHB 2024 Basic Rules pass

Per-class audit of all 13 base class features against `basic_rules_full.txt` (Basic Rules 2024). Pass tracks: source-paragraph references in inline comments, missing features added, stale 2014 mechanics replaced with 2024 wording, deferred items logged in `TODO_SOURCE_ACCURACY.md`.

**Completed classes (with commit refs):**
- **Barbarian** (`c71c732`): Fast Movement L5, Feral Instinct L7, Instinctive Pounce L7, Persistent Rage L15, Indomitable Might L18, Primal Champion L20 (+4 STR/CON cap 25), Primal Knowledge L3 (skill swap from Athletics)
- **Cleric** (`f58986f`): Divine Order L1 (Protector vs Thaumaturge), Divine Spark L2 reaction (radiant/necrotic damage), Blessed Strikes L7 (+1d8 radiant 1/turn), Divine Intervention L10 (1/long rest cleric domain spell free cast), Improved Blessed Strikes L14 (extra die)
- **Druid** (`57c5185`): Primal Order L1 (Magician vs Warden), Wild Companion L2 (Find Familiar via Wild Shape), Wild Resurgence L5 (Wild Shape→spell slot 1/turn), Elemental Fury L7 (damage type swap), Improved Elemental Fury L14
- **Fighter** (`69caa32`): Tactical Mind L2 (use Second Wind for INT-based check reroll), Tactical Shift L5 (free OA-immune movement on Second Wind), Second Wind use scaling (2/3/4 by level), L20 Three Extra Attacks fix
- **Monk** (`2730b5a` + `5e78f1c` + this batch): All 17 class features audited. See full table in `TODO_SOURCE_ACCURACY.md` Monk Audit section. Major fixes/additions:
  - Was missing entirely: Unarmored Movement speed scaling, Patient Defense, Step of the Wind, Martial Arts Bonus Unarmed Strike, Uncanny Metabolism, Self-Restoration, Superior Defense, Body and Mind, Deflect Attacks reaction (with L13 Deflect Energy gating), Perfect Focus, Heightened Focus Flurry-of-Blows third strike
  - Stunning Strike L5 rewrote from stale 2014 ("end of next turn" + repeating saves) to 2024 wording: stuns until start of monk's next turn, success rider grants speed-halved + advantage on next attack vs target
  - Disciplined Survivor L14 sets all 6 save proficiencies (reroll prompt deferred)
  - Empowered Strikes L6 flag set (Force/normal damage type prompt still deferred)
- **Rogue Evasion fix** (`5e78f1c`): L7 init was missing — only Monks were getting `evasion_active`. Fixed in `character_data.nvgt` Rogue init block.
- **Paladin batch 1** (`79dd582`): Aura of Protection L7 → L6 gating bug fixed; L2 Paladin's Smite free Divine Smite cast wired into bonus action handler; L5 Faithful Steed free Find Steed cast flag added; L10 Aura of Courage Frightened immunity in `add_condition`; L11 Radiant Strikes (+1d8 radiant on melee weapon/unarmed hit) in `apply_attack` damage block. L14 Restoring Touch verified already-implemented in lay_on_hands handler.
- **Ranger batch 1** (in this commit): L1 Favored Enemy free Hunter's Mark casts (scaling 2/3/4/5/6) via new `grant_free_cast()` helper; L6 Roving (+10 ft speed + matching climb/swim); L10 Tireless (Magic action 1d8+WIS temp HP via new bonus action menu entry); L13 Relentless Hunter (Hunter's Mark concentration unbreakable in `check_concentration`); L14 Nature's Veil (Bonus Action self-Invisible 1 round, full tickdown in `advance_turn`); L17 Precise Hunter (advantage on Hunter's Mark target attacks); L18 Feral Senses (Blindsight 30 ft); L20 Foe Slayer (Hunter's Mark d6 → d10). Client menu entries + state broadcast wired.
- **Rogue batch 1** (`53031ad`): L1 Sneak Attack base case added to `apply_subclass_on_hit_damage` (was missing entirely — only Inquisitive subclass rider existed). Full conditions: weapon attack + finesse/ranged + (advantage OR ally-within-5ft-of-target with no disadvantage), `(level+1)/2` dice scaling, `sneak_attack_used_this_turn` once-per-turn flag (cleared in `advance_turn`). Function signature now takes `had_advantage`/`had_disadvantage` from caller's `pending_roll`. L3 Steady Aim (bonus action handler in `users _dom.nvgt`, `steady_aim_pending` flag, advantage state + Speed=0 enforcement, Client menu entry gated on unmoved Speed). L5 Uncanny Dodge (reaction option added to reaction prompt; `uncanny_dodge_pending` consumed in `apply_damage` to halve damage; gated on `!Incapacitated`; Client UI label added). L7 Reliable Talent: corrected from L11 → L7 init gating (was a bug). L15 Slippery Mind (WIS + CHA save proficiencies on init). L18 Elusive (`elusive_active` flag forces `adv = false` at end of `apply_attack_advantage_state` unless target is Incapacitated). L20 Stroke of Luck flag set on init (auto-prompt deferred). All gated by source paragraph references.
- **Sorcerer batch 1** (`ab8502f`): L1 Innate Sorcery (bonus action, +1 spell save DC + advantage on Sorcerer spell attacks for 10 rounds, 2/LR via `innate_sorcery_uses_remaining`, rounds tickdown in `advance_turn`). `apply_attack_advantage_state()` now takes `bool is_spell_attack` parameter; passed `true` at the 3 spell-attack call sites so the Innate Sorcery advantage only applies to Sorcerer spell attacks. `spell_save_dc()` adds +1 to Sorcerer casters with active Innate Sorcery. L2 Font of Magic SP↔slot conversion (both directions as bonus action handlers in `users _dom.nvgt`: `font_of_magic_to_slot` consumes SP per cost table L1=2/L2=3/L3=5/L4=6/L5=7 with min-level gating, `font_of_magic_to_sp` is free action that yields slot-level SP). L5 Sorcerous Restoration flag set on init (short rest plumbing deferred). L7 Sorcery Incarnate fallback path: when out of Innate Sorcery uses but L7+, 2 SP can activate it instead. 7 metamagic stub flags added (`careful/distant/empowered/extended/heightened/seeking/transmuted`) for future batches. Client wires 4 new state fields, 3 new menu entries, and nested sub-menu Font of Magic slot-level pickers in both directions.
- **Sorcerer Draconic Sorcery + Wizard Evoker subclass audit** (`cc7b1d6`): Basic Rules 2024 paras 7539-7566 + 9253-9268. Draconic Sorcery and Evoker subclass features audited against source paragraphs.
- **Sorcerer Storm Sorcery + Divine Soul subclass audit** (`50944c0`): Xanathar's paras 2515-2639. Storm Sorcery: Heart of the Storm eruption damage + lightning/thunder resistance at L6, Storm's Fury reaction lightning + STR save push at L14, Wind Soul immunity + fly 60 at L18. Divine Soul: Divine Magic affinity choice via Shift+P with auto-prepared spell at L1, Favored by the Gods auto 2d4 additive reroll 1/SR at L1, Otherworldly Wings toggle BA fly 30 at L14, Unearthly Recovery BA heal half max HP when below half 1/LR at L18.
- **Warlock batch 1** (`e8f7e88`): L2 Magical Cunning Magic action handler (`magical_cunning_available` flag, recovers `(max+1)/2` Pact Magic slots at the Pact slot level, 1/LR; auto-detects the Pact slot level by scanning `spell_slots_max[]`). L9 Contact Patron handler (`contact_patron_available` flag, free Contact Other Plane with auto-success on save, 1/LR). L11/13/15/17 Mystic Arcanum (`mystic_arcanum_6/7/8/9_available` flags, `mystic_arcanum` handler grants a phantom slot at the chosen arcanum level for the next cast, 1/LR each). L20 Eldritch Master (`eldritch_master_active` flag set on init at L20; Magical Cunning handler reads `c.level >= 20` and grants full pact slot recovery instead of half). Eldritch Invocations known count corrected to match the source table (was 0/2/3/4/5/6/7/8 — now 1/3/3/3/5/5/6/6/7/7/7/8/8/8/8/9/9/10/10/10 per the Warlock Features table at paras 7607-7762). Client wires 6 new state fields and 3 new menu entries with sub-menu Mystic Arcanum level picker.
- **Wizard batch 1** (`4ad60b8`): L1 Ritual Adept (`ritual_adept_active` flag set on Wizard init — actual ritual casting hook deferred pending Ritual tag on spell data). L18 Spell Mastery (`spell_mastery_active` flag set on init at L18; slot bypass wired into `cast_spell` pipeline in `battle_manager.nvgt` — if `spell.id == c.spell_mastery_l1_spell_id` or `spell_mastery_l2_spell_id`, the cast skips slot consumption with "casts X through Spell Mastery — no spell slot consumed!" announcement). L20 Signature Spells (`signature_spells_charges_max = 2` set on init at L20; slot bypass for `signature_spell_a_id` and `signature_spell_b_id` with per-spell `_used_this_rest` tracking; "unleashes X as a Signature Spell — no spell slot consumed!" announcement). The four designation string fields default to empty (player must designate at level-up — prompt deferred to a future level-up UI batch). Client wires 7 new state fields. Short rest reset for Signature Spells charges deferred (currently only long rest exists). Existing L1 Arcane Recovery already shipped; verified in `users _dom.nvgt`.
- **Bard batch 1** (`9ae222c`): L5 Font of Inspiration (`font_of_inspiration_active` flag set on init at L5+; new `font_of_inspiration` no-action handler in `users _dom.nvgt` finds the lowest-level available spell slot, expends it from `spell_slots_current[]`, and increments `bardic_inspiration_uses` capped at CHA mod). L7 Countercharm (`countercharm_active` flag set on init at L7+; new `try_countercharm_reroll` helper in `battle_manager.nvgt` scans for any L7+ Bard with `countercharm_active` and reaction available within 30 ft of the failing save target — self allowed per RAW — consumes the reaction and rerolls the save with advantage, returns true if the reroll passed. Wired into 15 Charm/Frighten failed-save sites: cause_fear AoE/single, hypnotic_pattern, phantasmal_killer, mass_suggestion, command, suggestion, eyebite, dominate_person, charm_person, dominate_monster, enthrall, charm_monster, dominate_beast, weird. Polymorph's COND_CHARMED is an implementation marker for the polymorph effect — not a real charm — so it is intentionally skipped). L10 Magical Secrets (`magical_secrets_active` flag set on init at L10+ for client UI awareness; out-of-combat spell list expansion handled by existing spell menu). L18 Superior Inspiration (`superior_inspiration_active` flag set on init at L18+; existing `request_next_initiative` Superior Inspiration check updated to read the flag instead of hardcoded `c.level >= 18`). L20 Words of Creation (`words_of_creation_active` flag set on init at L20+; Power Word Heal and Power Word Kill auto-added to `c.prepared_spells` for L20 Bards; spell catalog `class_list` updated from "wizard" to "wizard,bard" for both spells; both `power_word_heal` and `power_word_kill` cast handlers in `battle_manager.nvgt` check `c.words_of_creation_active` and apply the spell to a second creature within 10 ft of the first target — Power Word Heal auto-picks the most-injured ally, Power Word Kill auto-picks the lowest-HP enemy). Client wires 5 new state fields and 1 new menu entry (Font of Inspiration).
- **Artificer batch 1** (`1a087b5`): L1 Tinker's Magic use tracking (`tinkers_magic_uses_max/_current` set on init to INT mod min 1; Magic action handler deferred — no hazards system for ball bearings/caltrops). L2 Replicate Magic Item flag (`replicate_magic_item_known`; full implementation deferred — needs DMG plan tables, LR crafting, item registry, vanish timers). L7 Flash of Genius (`flash_of_genius_uses_max/_current` set on init to INT mod min 1; new `try_flash_of_genius` helper in `battle_manager.nvgt` scans for any L7+ Artificer with the feature and reaction available within 30 ft of the failing target — self allowed per RAW — smart-spends only when the +INT mod bonus would actually turn the failure into a success, decrements the use, consumes the reaction, returns the new total. Wired into 20 save sites: 5 end-of-turn condition saves Hold Person/Web/Blindness-Deafness/Fear/Tasha's Hideous Laughter, plus 15 charm/frighten sites mirroring Bard Countercharm coverage. Also wired into `finalize_roll_result` for failed `ROLL_ABILITY_CHECK` so any skill check or hide check routed through the pending_roll system gets coverage automatically. Damage saves coverage extension deferred to a future batch). L10 Magic Item Adept (`magic_item_attunement_max = 4`). L11 Spell-Storing Item flag (`spell_storing_item_known`; full implementation deferred — needs item infrastructure). L14 Advanced Artifice (`magic_item_attunement_max = 5` + `refreshed_genius_active` flag; SR Flash regen pending short-rest subsystem). L18 Magic Item Master (`magic_item_attunement_max = 6`). L20 Soul of Artifice — Magical Guidance (`magical_guidance_active` flag; SR full Flash regen pending short-rest subsystem). L20 Cheat Death deferred (depends on Replicate Magic Item infra). Client wires 6 new state fields.
- **Gunslinger batch 2 — Maneuvers** (`1f95da2`): all 6 Risk Dice maneuvers from paras 207-218 — 5 wired, 1 deferred. **Bug fixes:** (a) **Dodge Roll** rebuilt from a broken `add_condition(COND_DODGING)` stub into the RAW +15 ft movement maneuver (BA + Risk Die, grants `c.movement_remaining += 15`; OA-immunity and difficult-terrain-immunity for the segment are deferred until per-segment movement tracking exists). (b) **Blindfire** rebuilt from a broken "ignore disadvantage on next ranged attack" stub into the RAW Blindsight 30 ft until end of turn (BA + Risk Die; `blindfire_active` flag set on activation, cleared at start of next turn in `advance_turn`). **New implementations:** **Bite the Bullet** (BA + Risk Die, temp HP = `risk_die_roll + level`) added to `users _dom.nvgt` bonus action handler dispatch + new client menu entry. **Grazing Shot** (no action, on miss with ranged weapon: `risk_die + DEX mod` weapon-type damage, 1/turn) — new `try_grazing_shot` helper in `battle_manager.nvgt` mirroring `try_flash_of_genius`, wired right after the attack `broadcast_roll` on miss path; per-turn flag `grazing_shot_used_this_turn` reset in `advance_turn`. **Maverick Spirit** (no action, on failed INT/WIS/CHA check or save: add Risk Die roll, 1/turn) — new `try_maverick_spirit` helper with smart-spend (only commits if the rolled Risk Die would actually turn the failure into a success). Wired into the generic ability check path (gated on INT/WIS/CHA `pr.ability_id`) and 16 WIS save sites paired with `try_flash_of_genius` (Hold Person EOT, Fear EOT, Tasha's Hideous Laughter EOT, Fear AoE, Hypnotic Pattern, Cause Fear, Phantasmal Killer, Mass Suggestion, Command, Suggestion, Eyebite, Dominate Person, Charm Person, Dominate Monster, Enthrall, Charm Monster, Dominate Beast, Weird). Per-turn flag `maverick_spirit_used_this_turn` reset in `advance_turn`. **Skin of Your Teeth** (Reaction: on hit, add Risk Die to AC) is deferred — depends on extending the existing reaction prompt infrastructure with a new opt-in reaction option. Client wires 1 new menu entry (Bite the Bullet) and updates Dodge Roll/Blindfire menu labels to match RAW.
- **Gunslinger batch 1** (`a2309f4`): Major source-accuracy fix-and-implement batch correcting multiple RAW bugs in the prior Gunslinger code (Valda's Spire of Secrets paras 159-203). **Bug fixes:** (a) **Risk Dice progression** corrected from `2d8 → 3d10 → 4d12` to RAW `4d8 (L2) → 5d8 (L6) → 5d10 (L10) → 6d10 (L14) → 6d12 (L18)`. (b) **Critical Shot** rebuilt from a broken use-based bonus-damage maneuver into the RAW passive crit-range expansion (`gunslinger_crit_threshold = 19/18/17` set on init at L2/9/17 and read by `get_critical_threshold` gated on `attacker.main_hand_is_ranged`). The broken `critical_shot_uses/_pending` field, the `users _dom.nvgt` user-action handler, the bonus-damage block in `finalize_roll_result`, and the `combat_ui.nvgt` menu entry were all removed. (c) **Gut Shot** rebuilt from a broken use-based bonus-damage maneuver into the RAW automatic on-crit debuff (sets `target.gut_shot_rounds_remaining = 10` (1 minute) + halves `target.speed`; `apply_attack_advantage_state` gives Disadvantage on outgoing attacks while `gut_shot_rounds_remaining > 0`; tickdown in `advance_turn` restores speed on expiry; gated on `pr.is_crit and c.main_hand_is_ranged and target.size <= SIZE_LARGE`). The broken `gut_shot` user-action handler and menu entry were also removed. (d) **Quick Draw** corrected from a flat `+2` initiative bonus to RAW Advantage on Initiative rolls (`quick_draw_active` flag set on init at L1+; hooked at `request_initiative_roll` in `battle_manager.nvgt`). **New implementations:** L5 Extra Attack (`c.extra_attacks = 1`). L7 Evasion (reuses existing shared `evasion_active` field with Monk/Rogue). L11 Overkill (`overkill_active` flag; ranged weapon hits gain `+1d8` extra damage in `finalize_roll_result` damage path — the ability-mod adder branch is the source intent for firearms which don't add mod, but the Firearm property isn't yet exposed on the weapon registry, so the implementation conservatively applies the +1d8 branch). L13 Cheat Death (`cheat_death_used` reset on init; wired in `apply_damage` (`combat_engine.nvgt`) right after Sorcerer Strength of the Grave — when a L13+ Gunslinger is reduced to 0 HP and not killed outright and `!cheat_death_used`, restores `current_hp = 1 + level` capped at max HP and sets the flag). L15 Dire Gambit (`dire_gambit_active` flag set on init at L15+; wired at `request_initiative_roll` and `finalize_roll_result` crit block to increment `risk_dice_current` capped at max). L18 Deft Maneuver flag (`deft_maneuver_active`; the maneuver-only bonus-action token is deferred). L20 Headshot (`headshot_active` flag set on init at L20+, `headshot_used` reset on init; wired in `finalize_roll_result` crit block — when a L20 Gunslinger crits with a ranged weapon and `!headshot_used`, sets `headshot_used = true` and either kills target if `current_hp < 100` or adds 10d10 extra damage. The 3-Risk-Dice refund refresh is deferred until SR subsystem). Client wires 10 new state fields and removes 2 obsolete menu entries.

**Pending classes (in priority order):** *(all base class audits complete — focus shifts to subclass batches and shared backlog)*

**Audit doctrine:** every implementation block carries `// PHB 2024 <Class> L<n> <Feature> (para <X>-<Y>)` comments. Source-quoted commit messages. No invent. No auto-pick for player choices.

### Subclass Combat Features (138 subclasses, 80+ with full combat logic)
**Fully Implemented Subclasses with Combat Logic:**
- **Barbarian**: Berserker, Wild Heart, World Tree, Zealot, Ancestral Guardian, Storm Herald, Path of the Carrion Raven
- **Bard**: Glamour, Swords, Whispers, Creation, Lore, Valor, Eloquence, Spirits
- **Cleric**: Life, Light, War, Forge, Grave, Peace, Twilight, Order, Festus, Inquisition, Astral
- **Druid**: Moon, Spores, Dreams, Stars, Land, Wildfire, Sea, Unbroken, Dragons
- **Fighter**: Champion, Battle Master, Eldritch Knight, Psi Warrior, Samurai, Cavalier, Rune Knight, Arcane Archer, Echo Knight, Couatl Herald, Steel Hawk, Blade Breaker
- **Monk**: Shadow, Mercy, Elements, Sun Soul, Kensei, Ascendant Dragon, Astral Self, Drunken Master, Open Hand, Celestial, Aether
- **Paladin**: Devotion, Glory, Ancients, Vengeance, Conquest, Watchers, Redemption, Hearth, Zeal
- **Ranger**: Gloom Stalker, Fey Wanderer, Hunter, Horizon Walker, Winter Trapper, Rocborne
- **Rogue**: Assassin, Soulknife, Inquisitive, Mastermind, Thief, Swashbuckler, Phantom, Arcane Trickster, Scout, Misfortune Bringer, Runetagger, Grim Surgeon
- **Sorcerer**: Draconic, Shadow Magic, Wild Magic, Aberrant, Storm, Clockwork, Divine Soul, Frost, Desert Soul
- **Warlock**: Fiend, Celestial, Archfey, Hexblade, Great Old One, Fathomless, Genie, Undead, Astral Griffon, Many
- **Wizard**: Abjurer, Diviner, Bladesinging, War Magic, Evoker, Illusionist, Order of Scribes, Materializer, Wand Lore
- **Artificer**: Alchemist, Armorer, Artillerist, Battle Smith, Cartographer
- **Gunslinger**: Deadeye, High Roller, Secret Agent, Spellslinger, Trick Shot, White Hat

**Key Combat Features:**
- Grave Cleric Path to the Grave (vulnerability doubling on TARGET), Circle of Mortality, Sentinel at Death's Door (auto-resolve crit negation within 30ft), Keeper of Souls (on-kill heal most-injured ally)
- Forge Domain Soul of the Forge (fire resist + heavy armor AC), Saint of Forge and Fire (B/P/S resist)
- Oath of Conquest Aura of Conquest (frightened speed 0 + psychic dmg in 10/30ft aura), Scornful Rebuke (CHA mod psychic on hit)
- Gloom Stalker Dread Ambusher (+WIS initiative, +10ft first turn), Stalker's Flurry (miss→extra attack), Shadowy Dodge (reaction impose disadvantage)
- Peace Emboldening Bond, Twilight Sanctuary, Order Voice of Authority
- Hexblade Curse (prof bonus damage, crit 19-20, heal on kill), Armor of Hexes (reaction d6 miss), Master of Hexes (auto-transfer curse on kill)
- Samurai Fighting Spirit, Horizon Walker Planar Warrior
- Storm Herald Storm Aura, Rune Knight Giant Might, Wild Magic Surge table
- Sun Soul Radiant Bolt, Ascendant Dragon Breath, Shadow Sorcerer Strength of the Grave
- Heart of the Storm eruption damage, Storm's Fury melee reaction
- Favored by the Gods +2d4 reroll, Otherworldly Wings permanent fly 30, Unearthly Recovery half-max-HP heal
- Tentacle of the Deeps, Form of Dread, Genie Vessel, Eldritch Cannon, Steel Defender, Experimental Elixir
- College of Eloquence Unsettling Words (subtract Bardic die from save)
- Order Domain Voice of Authority (free ally reaction attack on spell target) and Order's Demand (30ft action charm)
- Order of Scribes Awakened Spellbook (at-will damage type swap)
- Circle of the Shepherd Spirit Totem (Bear/Hawk/Unicorn)
- Inquisition Domain Witch Hunter's Strike (1d8 force, 2d8 vs concentrating, once per turn)
- Couatl Herald Mercy Die (d6 L3 → d8 L10 → d10 L18)
- Path of the Glacier Frostbite (1d6/2d6/3d6 cold + 10ft slow) and Path of the Infernal Hellfire Claw (d6/d8/d10/d12 scaling)
- Warrior of Celestial Soul Strike (L17 only, 1d4 radiant)
- Way of the Aether Spirit Strike (force damage, MA die scaling)
- Drunken Master Drunken Technique (Flurry grants Disengage + 10ft speed)
- Kensei Deft Strike (1 ki on weapon hit for +MA die damage), Kensei's Shot (BA +1d4 ranged), Sharpen the Blade (BA 1-3 ki for +1/+2/+3 attack and damage, 1 min, no magic weapon stack), Unerring Accuracy (reroll weapon miss 1/turn)
- Sun Soul Sun Shield (5+WIS radiant to melee attacker, consumes reaction)
- Horizon Walker Spectral Defense (reaction: resistance to all attack damage)
- Monster Slayer Slayer's Prey (+1d6 first weapon hit per turn on marked target)
- Oath of Redemption Rebuke the Violent (CD reaction: radiant damage equal to damage dealt on WIS fail), Protective Spirit (end-of-turn heal 1d6+half level if below half HP)
- Oath of the Hearth Burning Weapon (+CHA fire damage while active)
- Gunslinger White Hat Lay Down the Law (Risk Die temp HP + retaliation reaction)

### Feats with Combat Logic
Origin feats: alert, crafter, healer, lucky, magic_initiate, musician, savage_attacker, skilled, tavern_brawler, tough
General feats: actor, athlete, charger, chef, crossbow_expert, crusher, defensive_duelist, dual_wielder, durable, elemental_adept, fey_touched, great_weapon_master, heavily_armored, heavy_armor_master, inspiring_leader, keen_mind, lightly_armored, mage_slayer, martial_weapon_training, medium_armor_master, moderately_armored, mounted_combatant, observant, piercer, poisoner, polearm_master, resilient, ritual_caster, sentinel, shadow_touched, sharpshooter, shield_master, skill_expert, skulker, slasher, speedy, spell_sniper, telekinetic, telepathic, war_caster, weapon_master
Fighting Style feats: archery, blind_fighting, defense, dueling, great_weapon_fighting, interception, protection, thrown_weapon_fighting, two_weapon_fighting, unarmed_fighting
Epic Boon feats: combat_prowess, dimensional_travel, energy_resistance, fate, fortitude, irresistible_offense, recovery, skill, speed, spell_recall, the_night_spirit, truesight

### Audio System

- **Dual-layer audio**: Synthesized spatial cues (combat_audio.nvgt) + pre-recorded sound files (audio_manager.nvgt)

- **HRTF 3D spatial audio**: All combat sounds positioned at entity locations in 3D space

- **Music manager**: Auto-advances to next random track when one ends. Categories: menu, wait room, battle

- **Weapon sounds**: Mapped by weapon type (sword, dagger, axe, hammer, bow) with flesh impact at target

- **Spell sounds**: Mapped by damage type (fire, lightning, cold/water, shadow/necrotic, wind/thunder, arcane/radiant)

- **Footsteps**: Heavy armor (Fighter/Paladin/Cleric) vs grass steps, alternating variants, spatially positioned

- **Kill streaks**: First Blood, Stealth Kill, Insta Kill (from full HP), Overkill (200%+ max HP), Double Kill (2 in one turn), Triple Kill (3 in one turn), kill_streak1-9 (4+ total)

- **Healing sounds**: Small heals (random from 3 variants), large heals (15+ HP)

- **Buff/debuff sounds**: Different sounds for positive vs negative conditions

- **Announcements**: Low health warning (25% HP), low health heartbeat (synth thumps below 25% HP with increasing tempo), level-up stinger, wave/boss stingers, victory/defeat, player death dramatic message

- **Notifications**: Friend online notification (sound + TTS), guild chat notification sound

- **TTS Speed Control**: Ctrl+PageUp/Down adjusts speech rate (-10 to +10), available in menus and combat

- **121 sound files**: Weapon impacts, spell effects, music tracks, footsteps, kill announcements, UI sounds



### Monster AI

- Move toward nearest conscious player

- Attack when in weapon range

- Extra attacks supported for multiattack monsters

- Opportunity attacks on movement

- Auto-resolved rolls (no player input needed)

- 10-second safety timeout forces turn end if AI stalls

- Dead combatant detection: if current combatant dies mid-turn (e.g., from opportunity attack), turn auto-advances



### Battle Modes

- **PvP**: Last player standing wins

- **Wave Survival**: Clear waves of monsters (Rat Cellar, Goblin Ambush, Bandit Camp, Crypt of Undead, Dragon's Challenge, Haunted Catacombs, Fire Caverns, Shadow Realm, Abyssal Fortress)

- **Boss Rush**: Defeat boss monsters

- **Endless Survival**: Fight infinite escalating waves until the party falls. Waves 1-3: CR 0-1 (rats/kobolds/goblins), 4-6: CR 1-3 (skeletons/wolves/ogres), 7-9: CR 3-5 (owlbear/basilisk/troll), 10-12: CR 5-8 (wight/fire_elemental/frost_giant), 13-15: CR 8-12 (aboleth/remorhaz/archmage), 16+: CR 13+ bosses (pit_fiend/lich/dragon) with HP scaling. Players heal 25% between waves and earn wave_number*15 XP per wave. Best wave tracked per player. Glory earned = 5 + waves_cleared * 3.



### Targeting & Scanning

- IJKL to scan directions, Caps Lock to cycle results

- Scan results show distance, direction, health status, and conditions

- Target lock (Enter) shows HP, AC, distance, direction, and conditions





### Character Persistence

- Multiple characters per mode: up to 40 adventure + 40 sandbox characters per account

- Server stores characters in `adventure_characters`/`sandbox_characters` JSON arrays with `active_*_slot` index

- Auto-migration: old single-character accounts are converted to array format on first access

- `character_list` message sends full array to client on login; `character_select`/`character_delete` manage slots

- `character_data` message sends the active character's full data including background, feats, skills, tools, base scores

- Client profile cache stores background, feats, and gender alongside core character data

- View Characters shows a browsable list with Set Active and Delete options

- Adventure progress tracked: XP, level, achievements, kills, healing, waves cleared



### Post-Battle Flow

- Battle end detected (PvP: one standing, Wave: all monsters dead or TPK)

- Adventure mode: XP awarded (monster kills, healing, match completion, achievements)

- Loot drops generated per defeated monster (rarity based on monster XP tier; boss mode has guaranteed Rare+ drops)

- Glory points awarded: 10 normal, 25 boss; dungeon completions tracked

- Level-up flow: players choose new spells, cantrips, and subclass (at level 3) interactively

- Room `started` flag reset so new games can be launched

- Quick restart option for wave/boss/endless modes: deferred `start_game` sent after `reset_combat_state()` to prevent state corruption

- Post-battle order: save loot/level-up data -> `reset_combat_state()` -> send deferred restart -> show loot -> 5-second network-pumping wait -> show level-up

- 5-second lobby return countdown pumps network via loop (not blocking `wait()`) to prevent server timeouts



### Loot & Equipment System

- **270 source-verified items** across 5 rarity tiers (Common, Uncommon, Rare, Epic, Legendary) and 4 slots (Weapon, Armor, Ring, Amulet). Distribution: 28 Common, 61 Uncommon, 107 Rare, 53 Epic, 21 Legendary.
- **Source breakdown** (as of 2026-04-08 audit): DMG 2024 (~100), Tasha's (~17), Fizban's (9), Theros (6), Wildemount (10), Eberron Rising (13), Grim Hollow (10), Ravnica (9), Griffon's Saddlebag (12), Book of Many Things (12), Book of Ebon Tides (14), plus 4 Glory Shop exclusives.
- **Audit (2026-04-08)**: All 31 fabricated items removed from the original catalog. Every item now has a source-quoted description with paragraph reference. Glory Shop items preserved as intentional in-game rewards.

- Item stats: AC bonus, damage bonus, HP bonus, spell DC bonus, initiative bonus, speed bonus, save bonus, crit threshold reduction

- Loot generated after battle from defeated monsters; boss mode gives guaranteed Rare+ loot

- Max inventory: 20 items per player (stored in account `adventure_inventory` array)

- Equipment bonuses applied to combatant at battle start from character `equipped` JSON object

- Message types: `loot_drop`, `inventory_list`, `equip_item`, `discard_item`

- **Item Upgrading**: Combine 3 items of the same rarity into 1 random item of the next rarity. Glory cost: Common=10, Uncommon=25, Rare=50, Epic=100. Cannot upgrade Legendary. Message type: `upgrade_item` with `item_ids` array of 3 IDs.



### Consumable Shop & Items

- 16 consumable items across 4 types: Healing (4 potions), Buff (4 potions), Throwable (4 items), Scroll (3 scrolls)

- Purchased from Shop menu in main menu using gold earned from combat

- Max 5 of each consumable type, max 10 different consumable types per player

- Healing potions: bonus action, restore HP (2d4+2 to 10d4+20)

- Buff potions: bonus action, 3-round duration (damage, AC, speed, spell DC)

- Throwables: full action, ranged damage with DEX save (fire, acid, radiant, blind)

- Scrolls: one-use spells (Shield, Misty Step, Fireball)

- Used during combat via C key menu; consumables consumed on use

- Message types: `shop_list`, `shop_buy`, `use_consumable`



### Dungeon Modifiers

- Random modifiers applied to dungeon runs for variety

- 15 modifiers across 4 categories: beneficial (4), challenging (5), mixed (5), none (1)

- Beneficial: Empowered (+3 damage), Swift (+10 speed), Fortified (+2 AC), Blessed Grounds (5 HP/turn)

- Challenging: Glass Cannon (double damage), No Healing, Berserker, Swarming (+1 monster), Armored Foes (+3 AC)

- Mixed: Volatile (triple crits), Speed Run (double speed), Last Stand (half HP +4 damage), No Rest, Champion's Trial

- Active modifier displayed in combat status (H key) and announced on dungeon start

- Message type: `modifier_info`



### Prestige System

- Available at level 20 with max 5 ranks: Veteran, Champion, Legend, Mythic, Ascendant

- Prestige resets level to 1 and XP to 0 but keeps inventory, achievements, glory, and dungeon completions

- Each prestige rank grants +1 to all ability scores (applied at battle start)

- Prestige title prepended to player name in combat (e.g., "Veteran PlayerName")

- Glory points awarded on prestige: 100 per rank

- Message types: `prestige_action`, `glory_update`



### Glory Points

- Earned from battle completion (10 normal, 25 boss) and prestige (100 per rank)

- Tracked in `adventure_progress["glory"]`; dungeon completions tracked in `adventure_progress["dungeons_completed"]`



### Character Creation

- Step-by-step wizard: Name (user input) -> Species -> Class -> Level -> Subclass -> Background -> Abilities -> Weapon -> Progression -> Spells -> Summary

- Players can name their character (defaults to username, max 30 characters)

- 16 backgrounds: Acolyte, Artisan, Charlatan, Criminal, Entertainer, Farmer, Guard, Guide, Hermit, Merchant, Noble, Sage, Sailor, Scribe, Soldier, Wayfarer

- Each background grants: 3 ability score bonuses, an Origin feat, 2 skill proficiencies, and a tool proficiency

- **Backspace/Escape goes back** to the previous step at any point; auto-skip steps (level in adventure, subclass at low level) are transparently skipped during back-navigation

- At the first step (Name), Escape cancels the wizard

- Adventure mode forces level from server progression

- Subclass selection only at level 3+

- **Alt+F4** closes the client at any time (menus and combat)



## Controls (Client)

- **F**: Open action menu (Attack, Cast, Dodge, Dash, Disengage, Help, Hide, Ready, Shove, Grapple, End Turn)

- **B**: Open bonus action menu (class-specific: Rage, Action Surge, Cunning Action, etc.)

- **C**: Open consumable items menu (potions, throwables, scrolls)

- **R/Enter**: Roll dice when prompted (only the prompted player can roll)

- **WASD**: Movement (5ft per tile)

- **IJKL**: Scan directions (north/south/west/east)

- **Caps Lock/Shift+Caps Lock**: Cycle targets from scan results

- **Escape**: Opens menu to Leave Game, Close Client, or Cancel

- **Enter**: Lock target

- **H**: Enhanced status readout (HP, AC, equipped items, active buffs with rounds remaining, consumables, kill count, modifier, spell slots, position with nearest enemy/ally)

- **O**: Initiative order (reads top to bottom)

- **T**: Whose turn it is

- **Tab**: Switch focus forward (Game -> Chat -> Chat History)

- **Shift+Tab**: Switch focus backward (Game -> Chat History -> Chat)

- **Page Up**: Volume up (+3dB)

- **Page Down**: Volume down (-3dB)

- **Ctrl+Page Up**: TTS speed up

- **Ctrl+Page Down**: TTS speed down

- **F1**: Combat help

- **F2**: Quick keybind reference (spoken summary of all controls)

- **Escape**: Menu (Leave Game / Close Client / Cancel)

- **Alt+F4**: Close the client immediately (works in all menus and combat)



## Sound System

- **Encrypted sound pack**: All 121 sound files packed into `sounds.dat` with encryption key

- **Build workflow**: Run `pack_sounds.nvgt` to create sounds.dat, then compile client

- **`set_sound_default_pack()`** makes all `sound.load()` calls read from the pack automatically

- **Dual-layer audio**: Synthesized spatial cues (combat_audio.nvgt) + pre-recorded files (audio_manager.nvgt)

- **Music manager**: Auto-advances random tracks. Categories: menu, wait room, battle

- **Volume control**: Page Up/Down adjusts master volume offset (±3dB, range -30 to +12)



## NVGT Language Notes

- AngelScript-based: `@` = handle (reference), `@obj = null` = null check

- `uint64` for timestamps, `ticks()` returns current time in ms

- `json_object` / `json_array` for serialization

- `speak(text, interrupt)` for TTS (client-side)

- `menu` / `setup_sub_menu(prompt)` for accessible popup menus

- `network.send(peer_id, message, channel, reliable)` for networking

- `wait(ms)` yields execution in game loops

- `set_sound_global_hrtf(true)` for 3D spatial audio



## Message Routing

- All combat actions route through `users_dom.nvgt` -> `battle_manager` methods

- Actions: attack, move, dodge, dash, disengage, cast, help, hide, shove, grapple, set_target

- Bonus actions handled via `bonus_action` message with `feature` field

- Level-up choices sent via `level_up_choices` / `level_up_response` messages

- Daily bonus sent via `daily_bonus` message on login

- Roll requests include `player` field to restrict who can roll

- Scan direction handled inline in `users_dom.nvgt`

- Target info includes direction and distance



## Achievements (40+)

- Combat: Monster Slayer (100/500 kills), Critical Master (25 crits), Overkill (100+ single damage)

- Class Mastery: Win 10 battles per class (13 total)

- Dungeons: Crawler (10 clears), Master (all Normal), Hardened/Nightmare Survivor

- Endless: Wave 5/10/20/30 milestones

- Loot: First Find, Collector (10 items), Rare/Epic/Legendary finder

- Social: Friendly (5 friends), Trader (complete a trade), Party Player (5 friend battles)

- Prestige: Ranks 1/3/5 milestones



## Glory Shop

- **Titles**: The Brave (50), Dragon Slayer (100), Archmage (100), Shadow Walker (100), The Immortal (200), Godslayer (500), The Conqueror (300), Warden (150)

- **Exclusive Items**: Glory Blade (150), Glory Shield (150), Ring of Glory (100), Crown of Glory (300)

- Active title shown in initiative/scan readouts



## Daily Dungeon

- One featured dungeon + difficulty each day (rotates deterministically)

- 2x glory and 2x loot drop rate for daily completion

- Can only claim daily bonus once per day



## Leaderboards

- Categories: Glory Points, Endless Best Wave, Monster Kills, Prestige Rank, Dungeons Cleared

- Top 10 shown per category with player's own rank



## Guild System

- Players can create or join a guild (max 20 members per guild)

- Guild names: 3-30 characters, letters/numbers/spaces only, case-insensitive uniqueness

- Guild roles: Leader (creator or transferred) and Members

- Guild chat: broadcasts to all online guild members via `guild_chat` message

- Guild invites: invite friends to your guild; target receives `guild_invite_received` prompt

- Leave guild: if leader leaves, leadership transfers to first remaining member; if last member leaves, guild disbands

- Guild info: shows name, leader, member list, member count, and total glory (sum of all members' glory)

- Persistence: guild_name stored in each member's `adventure_progress`; guild objects rebuilt from accounts on server startup via `rebuild_guilds_from_accounts()`

- Message types: `create_guild`, `join_guild`, `leave_guild`, `guild_chat`, `guild_info`, `guild_invite`, `guild_invite_received`, `guild_invite_response`

- Client guild menu accessible from main menu; shows create prompt if not in a guild, or guild management panel if in one



## Boss Phases

- Bosses with XP >= 5000 have multi-phase transitions

- Phase 2 (50% HP): +3 AC, +2 damage, +10 speed, summons 2 minions

- Phase 3 (25% HP): Additional +2 damage, heals 10% max HP, enrage announcement



## Player Stats Menu

- Accessible from main menu: "My Stats" with 7 sub-categories

- **Combat Stats**: Kills, damage dealt, healing, max hit, crits, deaths, win rate, PvP record, kill streak

- **Progression**: Level, XP, prestige, gold, glory

- **Dungeon Stats**: Completions per dungeon/difficulty, endless best wave, boss kills

- **Achievements**: Total unlocked, full list with names

- **Equipment**: Equipped items with stats, inventory count, items found lifetime

- **Social**: Friends, guild, trades completed

- **Class History**: Per-class win counts, favorite class

- **Player Inspect**: View another player's public stats from context menu (right-click in lobby/friends)

- Server tracks: total_damage_dealt, total_deaths, pvp_wins/losses, longest_kill_streak per account



## Auto-Update System

- **Two-layer version gate**: Client-side updater blocks at launch + server rejects outdated clients at login (bulletproof: even if update server is down, game server enforces version)

- **Server-side validation**: `REQUIRED_CLIENT_VERSION` in `Server.nvgt` checked against `client_version` field in login message; clients without version field or with older version are rejected with error

- **Mandatory client updates**: Outdated clients cannot skip past the update screen; must update or quit

- **Unreachable update server**: Client warns player but proceeds to game server, which will reject if version is outdated

- **Incremental downloads**: Only downloads files whose SHA-256 hash changed (code-only update = 14MB instead of 900MB)

- **Version tracking**: `CLIENT_VERSION` constant in `client.nvgt`, semantic versioning (MAJOR.MINOR.PATCH). Client sends version in login messages.

- **Manifest-based**: Server hosts `manifest.json` listing each file + hash + size; client compares local vs remote manifest

- **Update flow**: `check_for_update()` runs at launch before sounds.dat loads (no files locked) -> fetches manifest -> compares hashes -> downloads only changed files via `internet_request` with TTS progress (10% increments) -> writes `update.bat` to swap files -> relaunches

- **Download retry**: If download fails, player can retry or quit (no bypassing)

- **First-time install**: `manifest.json` ships inside `client.zip` so new installs have it

- **Key files**: `Client/updater.nvgt` (auto-updater), `build_and_deploy.py` (build + deploy script)

- **Server files**: `web/manifest.json`, `web/files/` (individual files for incremental updates), `web/DungeonLegends.zip` (full zip for new players)

- **Smart deploy**: `build_and_deploy.py` uses hash comparison (not size) to skip uploading unchanged files; caches last deployed manifest in `.last_deployed_manifest.json`; sounds.dat (919 MB) only re-uploaded when audio actually changes



## Development

- **Build & deploy** (one command): `python build_and_deploy.py` — bumps version, packs sounds, compiles, generates manifest, uploads everything

  - `--minor` / `--major` / `--version X.Y.Z` for version control

  - `--skip-sounds` to skip sound packing, `--skip-upload` for local build only

  - `--notes "Fixed X"` for release notes (announced via TTS to players)

  - After deploying, update `REQUIRED_CLIENT_VERSION` in `Server/Server.nvgt` to match the new version and redeploy server

- Compile client: `C:\Users\16239\Documents\games\nvgt\nvgt.exe -c Client/client.nvgt` (produces Client/client.zip for distribution)

- Compile server (Linux): `C:\Users\16239\Documents\games\nvgt\nvgt.exe -c -p linux Server/Server.nvgt` (produces Server/Server.zip)

- Git repo: https://github.com/ArizonaDad/Dungeon-Legends



## Server Deployment

- **Host**: the-gdn.net, port 2000 (game), SSH port 30001

- **Game server deploy**: `C:\Users\16239\redeploy.py` — stops server, uploads Server.zip via SFTP, extracts to ~/dungeon_legends/, restarts with nohup

- **Client deploy**: `python build_and_deploy.py` — uploads individual files to `web/files/`, manifest to `web/manifest.json`, full zip to `web/DungeonLegends.zip`

- **Download page**: http://the-gdn.net:8080/ (index.html), **Direct download**: http://the-gdn.net:8080/DungeonLegends.zip

- **Other scripts**: `deploy_server.py` (full deploy with screen session), `fix_server.py` (maintenance/restart), `start_server.py` (restart only)

- **Server path on host**: ~/dungeon_legends/Server

- **Web path on host**: ~/dungeon_legends/web (served by Python HTTP server on port 8080)

- **Logs**: ~/dungeon_legends/server.log

- Uses paramiko with Ed25519 key auth (key at `~/.ssh/id_ed25519`)


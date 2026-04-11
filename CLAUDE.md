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

- Initiative rolled at battle start (d20 + DEX mod), all rolls announced to all players, then full turn order broadcast. Tie-breaking: DEX modifier (higher first), then random. Exhaustion penalty (-2 * level) applied to initiative rolls.

- Combat rounds start at 1 (first turn of each round announces "Round N!")

- All rolls require the specific prompted player to press R or Enter (other players cannot roll for them)

- All roll results broadcast to ALL players with full context and audio cues (nat 20/1)

- Combat game loop forces main_screen form focus to keyboard_area so lobby chat form doesn't consume combat keystrokes



### Attack Resolution

- Separate roll to hit (d20 + ability mod + proficiency vs AC), then roll for damage

- Advantage/disadvantage from conditions (prone, paralyzed, dodging, etc.)
- **Condition Mechanics**: Paralyzed/Unconscious → auto-crit on melee hit within 5ft. Incapacitated blocks actions/bonus actions/reactions (gated in handle_attack, handle_cast, bonus action handler). Stunned/Paralyzed/Unconscious auto-skip turns. Stunned/Paralyzed auto-fail STR/DEX saves (-100 in get_save_bonus). Frightened/Poisoned impose disadvantage on ability checks (request_skill_check). Frightened blocks movement toward fear source (`frightened_source_id` tracked at all 8 application sites, enforced in `handle_move` and monster AI). Restrained imposes disadvantage on DEX saves (-5 approx in get_save_bonus). Blinded target grants advantage to attackers (apply_attack_advantage_state). Petrified grants resistance to all damage + poison immunity (apply_damage + add_condition guard). Dodge grants advantage on DEX saves (+5 approx in get_save_bonus, gated on not Incapacitated). Grapple Escape action: Athletics/Acrobatics check vs DC 8+STR+Prof of grappler.
- **Crit at 0 HP**: Critical hits on unconscious creatures count as 2 death save failures (was_crit parameter in apply_damage).
- **Unconscious → Prone** (PHB 2024 para 16319): Creatures reduced to 0 HP automatically fall Prone alongside Unconscious at all 3 paths (instant death, player death saves, troll regen). Healing removes Unconscious but NOT Prone (must stand with half speed).
- **Sanctuary Enforcement** (Basic Rules 2024 para 14826): WIS save enforced on all 3 attack paths (handle_attack, start_monster_attack_sequence, start_player_bot_attack_sequence). Self-break when warded creature attacks or casts a spell affecting an enemy.
- **Bonus Action Spell Rule** (PHB 2024 para 7986-7989): If a bonus action spell is cast, only cantrips may be cast as the action. Tracked via `cast_ba_spell_this_turn` / `cast_leveled_spell_this_turn` flags. Quickened Spell counts as BA spell.

- **Extra Attack**: Fighters level 5 (2 attacks), 11 (3 attacks), 17 (3 attacks + 2 Action Surge). Other martials get 1 extra at level 5.

- **Reaction Prompt System**: When a player is about to be hit, they are prompted for available reactions before hit resolves. Options: Shield (+5 AC), Cutting Words (-1d4-d12), Warding Flare (force reroll), Defensive Duelist (+Prof AC), Restore Balance (cancel advantage), Spirit Shield (reduce damage 2d6+), Entropic Ward (force miss), Arcane Deflection (+2 AC), Warding Maneuver (+1d8 AC, resistance if still hit), Armor of Hexes (d6, 4+ miss), Deflect Attacks (reduce 1d10+DEX+level), Uncanny Dodge (halve damage), Storm's Fury (sorcerer level lightning + push), Shadowy Dodge (impose disadvantage), Spectral Defense (resistance to all attack damage)
- **Save Failure Reaction Chain**: At each condition-applying save failure site (24 total), the chain fires in order: `try_arcane_deflection_save` → `try_countercharm_reroll` (charm/frighten only) → `try_fanatical_focus` (EOT only) → `try_disciplined_survivor_reroll` → `try_flash_of_genius` → `try_maverick_spirit` → `try_mage_slayer_guarded_mind` → `try_boon_of_fate_bonus` → `try_stroke_of_luck_save` → condition application. All smart-spend (only fire when they could actually help). Arcane Deflection sets `arcane_deflection_no_spell_turns = 2` and blocks non-cantrip casts in `handle_cast` until expired.
- **Resistance System**: Species and feats grant resistances to fire, cold, necrotic, psychic, acid, lightning, piercing, poison (+ immunity) — half damage on applicable types. Elemental Adept bypasses resistance for chosen damage type via `ea_bypass` flag.
- **Wild Magic Surge**: Wild Magic Sorcerers roll d20 on 1+ level spell cast. On natural 1, a random surge effect triggers (fire burst, temp HP, healing, invisibility, spell slot recovery, etc.)
- **Divine Smite**: Dual mode — bonus action pre-cast OR auto-prompt on melee hit (keys 1-5 for slot level, Escape to skip)
- **Eldritch Smite**: Player prompt system (same UI pattern as Divine Smite). After weapon hit with pact weapon, Warlock is prompted to expend Pact Magic slot for (1+slot_level)d8 force damage + Prone. Bots auto-fire. Paladin/Warlock multiclass chains both prompts. `pending_smite_prompt.smite_type` distinguishes "divine" vs "eldritch".
- **Grapple/Shove**: 2024 rules — target makes STR or DEX saving throw (DC 8 + STR mod + Prof), not contested checks
- **Weapon Mastery** (PHB 2024 paras 10335-10352): All 8 properties wired to attack resolution. Push (10ft shove if Large or smaller), Sap (disadvantage on target's next attack), Slow (-10ft speed until attacker's next turn), Topple (CON save or Prone, DC 8+ability mod+prof), Vex (advantage on next attack vs same target), Cleave (free attack vs adjacent creature within 5ft of target, weapon damage no ability mod, once/turn), Graze (ability mod damage on miss), Nick (free off-hand attack as part of Attack action via TWF system). `main_hand_mastery` field on combatant, set from `character_data.nvgt` weapon table.
- **Two-Weapon Fighting** (PHB 2024 paras 10335-10352): Light weapon property on 7 weapons. Auto-equip off-hand when main weapon is Light melee or Dual Wielder feat. Bonus action off-hand attack (no ability mod to damage unless TWF fighting style or negative). Nick mastery triggers free off-hand attack after all extra attacks complete. Off-hand fields: `off_hand_damage_dice/count/type/range/finesse/is_light/mastery` on combatant.

- **AC System**: Proper armor types (leather/studded/chain shirt/breastplate/half plate/chain mail/splint/plate) with correct AC calculations per 2024 PHB

- **End-of-Turn Saves**: Hold Person/Monster, Web, Blindness/Deafness, Fear, Tasha's Hideous Laughter, Compulsion, Slow, Confusion, Power Word Stun — affected creatures save at end of turn with full save failure chains

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

- Buff spells (Shield, Bless, Heroism, Aid, Stoneskin, Greater Invisibility, Fly, Fire Shield, Mage Armor, Haste). **Haste**: doubles speed, +2 AC, advantage on DEX saves (+5 approx in `get_save_bonus`), +1 extra weapon attack (approximation of "Attack one weapon only" extra action, wired into all 3 attack paths: player/bot/monster). Lethargy: skips action/bonus/movement on Haste end turn.

- Utility spells (Hold Person, Banishment, Misty Step, Sleep, Polymorph, Web, Hypnotic Pattern, Sanctuary, Spirit Guardians)

- Misty Step: actual 30ft teleportation toward target using vector math (matching consumable Scroll of Misty Step pattern), not just a narrative announcement

- Magic Missile auto-hit

- Cantrip scaling at levels 5/11/17

- **Cantrip Spell Hit Riders** (`apply_spell_hit_effects` in battle_manager.nvgt): 7 cantrips with special on-hit effects beyond base damage. Guiding Bolt (advantage on next attack via `guiding_bolt_advantage`), Ray of Frost (-10ft movement), Shocking Grasp (lose reaction), Thorn Whip (pull 10ft closer), Chill Touch (healing prevention via `chill_touch_source_id` — blocks `apply_healing` until end of caster's next turn, 2-tick counter on caster turns), Starry Wisp (invisibility block via `starry_wisp_no_invis` — strips and blocks COND_INVISIBLE in `add_condition` until end of caster's next turn, 2-tick counter). Both Chill Touch and Starry Wisp use caster-turn-based expiry in `advance_turn` (loops all combatants with matching source_id on caster's turn-end).

- **Smite Spell System** (pending-rider pattern in `finalize_roll_result`): Smite spells set `_pending` + `_dice` flags on cast, consumed on next qualifying weapon hit. **Searing Smite** (Basic Rules 2024 para 14881): L1, melee-only, 1d6+upcast fire on hit + repeating fire DOT at target's turn start with CON save to end. Concentration spell. DOT tracking: `searing_smite_caster_id` + `searing_smite_dot_dice` on target, cleared on save success or concentration break. **Shining Smite** (Basic Rules 2024 para 14976): L2, any weapon, 2d6+upcast radiant on hit + target sheds light with advantage on all attacks against it (`shining_smite_debuff` flag + `apply_attack_advantage_state`), can't be invisible (reuses `starry_wisp_no_invis`). 10-round duration, ticks in `advance_turn`. Concentration. **Ballistic Smite** (Gun Slinger Class para 724): L1, ranged-only, 2d6+upcast force on hit. Instantaneous (no concentration). All three have cleanup in `clear_concentration_effects`.

- **Command Spell** (Basic Rules 2024 para 12421-12433): WIS save with full save failure chain. On fail, `command_effect` + `command_source_id` set on target. Turn-start execution in `advance_turn`: **Grovel** (Prone + end turn), **Halt** (no move/action/BA), **Flee** (Dash-speed movement away from caster with OA checks), **Approach** (move toward caster until within 5ft), **Drop** (announce + end turn). Bot AI auto-picks Grovel (Halt for concentrating targets). Cleared on Stunned/Paralyzed/Unconscious skip.

- **Shillelagh** (Basic Rules 2024 para 14966-14974): Transmutation cantrip, bonus action, 1 minute. `shillelagh_active` flag on combatant. Uses spellcasting ability instead of STR for melee attack/damage (`get_weapon_attack_ability_mod` — takes highest of STR/spellcasting mod). Damage die override: d8 (L1-4), d10 (L5-10), d12 (L11-16), 2d6 (L17+) via `get_attack_damage_dice` + `get_attack_damage_count`. Force damage by default (`get_attack_damage_type`). Duration countdown in `advance_turn` per-turn section. NOT concentration.

- **Flame Blade** (Basic Rules 2024 para 13334-13343): L2 Evocation, concentration. `flame_blade_active` + `flame_blade_dice` (3 base + upcast). Dedicated action menu entry + server handler follows Call Lightning pattern. Melee spell attack roll, 5ft range, Fire damage. Concentration cleanup clears active flag.

- **Aura of Life** (Basic Rules 2024 para 12166-12168): L4 Abjuration, concentration, 10 min. 30ft emanation. `aura_of_life_active` on caster. Allies in aura get necrotic resistance at turn start (tracked via `aura_of_life_necrotic_from` for cleanup). Ally at 0 HP regains 1 HP at turn start. Concentration cleanup removes aura-granted necrotic resistance from all targets.

- **Power Word Stun** (Basic Rules 2024 para 14671-14673): L8 Enchantment. If target HP ≤ 150: Stunned with CON save at end of each turn to break free (full save failure chain). If target HP > 150: Speed = 0 until start of caster's next turn. `power_word_stun_caster_id` tracks caster for save DC.

- **Remove Curse** (Basic Rules 2024 para 14774-14775): L3 Abjuration, touch. Removes Bestow Curse (breaks caster concentration), Hex (breaks concentration), and Hexblade's Curse from target.

- **Perforating Shot** (Gun Slinger Class para 730-735): L1 Evocation. Line AoE to weapon's range hitting all enemies. DEX save for weapon damage (+1d8/upcast), half on success. Full save failure chain.

- **Jam Weapon** (Gun Slinger Class para 736-738): L2 Transmutation. Jams target's weapon — can't attack until Utilize action (costs action). `weapon_jammed` flag on combatant. Monster AI auto-unjams. Client "Unjam Weapon" action menu entry.

- **Alter Self Natural Weapons** (Basic Rules 2024 para 12010-12012): L2 Transmutation, concentration. `alter_self_natural_weapons` flag on caster. Wired into all 3 attack pipeline functions: `get_attack_bonus_for_roll` (use higher of spellcasting mod or weapon mod), `get_damage_modifier_for_attack` (same), `get_attack_damage_dice` (floor at d6 for melee). Always beneficial — never downgrades existing better weapon stats. Concentration cleanup clears flag.

- **Foresight** (Basic Rules 2024 para 13025-13031): L9 Divination, Touch, 8 hours, NOT concentration. `foresight_active` flag on target. Advantage on ALL d20 tests: +5 save bonus in `get_save_bonus`, advantage in `request_skill_check`, advantage on attacks in `apply_attack_advantage_state`. Enemies have disadvantage on attacks against the target. "The spell ends early if you cast it again" — clears from all combatants before setting on new target.

- **Mind Blank** (Basic Rules 2024 para 13755-13761): L8 Abjuration, Touch, 24 hours, NOT concentration. `mind_blank_active` flag on target. Immunity to Psychic damage (checked in `apply_damage` before resistance). Immunity to Charmed condition (checked in `add_condition`). Removes existing Charmed on cast.

- **Glibness** (Basic Rules 2024 para 13139-13144): L8 Enchantment, Self, 1 hour, NOT concentration. `glibness_active` flag on caster. In `finalize_roll_result`, CHA ability checks can't roll below 15 (replaces natural roll before Silver Tongue check).

- **Antilife Shell** (Basic Rules 2024 para 11796-11803): L5 Abjuration, Self, Concentration. `antilife_shell_active` flag on caster. 10ft emanation blocks hostile non-Construct/non-Undead creatures from entering. Wired into `handle_move` (player movement blocked with error message) and monster AI approach loop (movement breaks). Caster moving toward enemies ends the spell (checked after player movement). Concentration cleanup clears flag.

- **Wish — Instant Health** (Basic Rules 2024 para 15081-15097): L9 Conjuration, Self, Instantaneous. Restores all allies to full HP and removes Blinded, Deafened, Paralyzed, Petrified, Poisoned, Stunned, and Charmed conditions (Greater Restoration effects). Full Wish spell options (Duplicate Spell, Resistance, etc.) deferred.

- **Telekinesis** (Basic Rules 2024 para 14871-14879): L5 Transmutation, Concentration. STR save or moved 30ft away from caster + Restrained in telekinetic grip until start of caster's next turn. Size limit Huge. `telekinesis_source_id` on target, cleared in advance_turn at caster's turn start + clear_concentration_effects on break. Approximated as STR save vs spell DC (source uses contested check). Save failure chain (Arcane Deflection, Flash of Genius, Boon of Fate, Stroke of Luck).

- **Feign Death** (Basic Rules 2024 para 13203-13212): L3 Necromancy, Touch, NOT concentration. Target appears dead. `feign_death_active` flag: Blinded + Incapacitated, Speed = 0, Resistance to all damage except Psychic (in `apply_damage`). No save (willing targets). `feign_death_original_speed` for restoration.

- **Psionic Sorcery** (Aberrant Mind L6): Psionic spells (from Psionic Spells list) can be cast using Sorcery Points instead of spell slots, at a cost of 1 SP per spell level. SP-cast psionic spells require no verbal or somatic components.

- **Geas** (Basic Rules 2024 para 13062-13072): L5 Enchantment, NOT concentration. WIS save with full chain (Arcane Deflection, Countercharm, Disciplined Survivor, Flash of Genius, Maverick Spirit, Mage Slayer, Boon of Fate, Stroke of Luck). On fail: COND_CHARMED + `geas_source_id` on target. Punishment: 5d10 psychic damage when charmed creature attacks (wired into `handle_attack` before range check).

- **Plane Shift** (Basic Rules 2024 para 14601-14608): L7 Conjuration, Touch. Melee spell attack + CHA save or banished from combat (removed). Save failure chain. Touch range (5ft) enforced.

- **Mislead** (COMPLETE_SPELL_CATALOG): L5 Illusion, Concentration. Caster gains COND_INVISIBLE + is_hidden. Invisibility breaks on attack/damage/spell per standard rules.

- **Investiture of Ice** (Xanathar's): L6 Transmutation, Concentration. Cold resistance (immunity approx), fire resistance. 10ft icy difficult terrain around caster (doubles movement cost in `handle_move`). `investiture_ice_active` flag.

- **Investiture of Stone** (Xanathar's): L6 Transmutation, Concentration. B/P/S nonmagical resistance via `resist_bps_nonmagical`. `investiture_stone_active` flag, properly cleared for players on concentration break.

- **Investiture of Wind** (Xanathar's): L6 Transmutation, Concentration. Ranged weapon attack disadvantage (in `apply_attack_advantage_state`). +30ft speed (fly approx). `investiture_wind_active` flag, speed restored on concentration break.

- **Investiture of Flame** concentration bug fixed: Now properly sets `is_concentrating`, `COND_CONCENTRATING`, and `concentration_spell`. All 4 Investiture spells added to spell_data.nvgt catalog (druid/sorcerer/warlock/wizard).

- **Arcane Archer Enfeebling Arrow wiring**: `arcane_enfeeble_source` halves weapon damage before `apply_damage` in `finalize_roll_result`. Gated on `pr.is_weapon_attack`.

- **Arcane Archer Grasping Arrow wiring**: 2d6 slashing on first voluntary movement per turn (once-per-turn via `arcane_grasping_damaged_this_turn`). Wired into both `handle_move` (player) and monster AI movement loop. Round countdown in `advance_turn` restores +10ft speed on expiry.

- Concentration management (drop old when casting new). Full cleanup in `clear_concentration_effects()`: clears Spirit Guardians, Divine Favor, Holy Weapon, Fire Shield, Stoneskin (B/P/S resistance flags), Fly, Ensnaring Strike, Sanctuary, Venomous Mark, Fog Cloud, Darkness, Hunter's Mark, Hex, Bane, Bless, Haste, Heroism, Pass Without Trace, Adjust Density, Silence, Blur, Conjure Minor Elementals, Conjure Woodland Beings, Polymorph, Heat Metal (+ clear `heat_metal_disadv` on target), Call Lightning, Flame Blade, Flaming Sphere, Swift Quiver, Extended Spell, Enhance Ability, Guidance, Resistance, Protection from Energy, Protection from Evil and Good, Expeditious Retreat, Levitate, Compulsion, Antimagic Field, Faerie Fire, Charm/Dominate/Hypnotic Pattern/Enthrall, Hold Person/Monster, Tasha's Hideous Laughter, Fear/Phantasmal Killer/Eyebite, Web/Entangle/Flesh to Stone, Sleep/Confusion/Otto's Irresistible Dance, Sunbeam, Slow (restore speed + AC), Investiture of Flame/Ice/Stone/Wind, Telekinesis, Mislead, Durable Magic AC bonus, Shield of Faith (AC -2 on target), Beacon of Hope (clear max-healing flag), Greater Invisibility (remove COND_INVISIBLE + is_hidden + flag), Aura of Life (remove aura-granted necrotic resistance), and all concentration-spell companions (Animate Objects, Giant Insect, Bigby's Hand, Conjure Animals/Elemental/Fey/Celestial, Summon Dragon).

- Spirit Guardians: 15ft aura, 3d8+ radiant damage on enemies starting turn within range OR entering the aura on movement (once per turn via `spirit_guardians_damaged_this_turn` flag). Halved movement while in aura — applied at turn start AND on movement entry (both player and monster paths). Movement entry trigger wired into both `handle_move` (player) and monster AI loop.

- **Concentration AoE Per-Turn Loop** (`advance_turn`): 12 concentration spells auto-apply per-turn effects when creatures start their turn in the area. Uses shared `conc_aoe_x/y/slot_level` fields (one concentration spell per caster). All per-turn save loops now have full save failure chains (Hound disadvantage, Bless bonus, Arcane Deflection, Flash of Genius, Boon of Fate, Stroke of Luck; condition-applying spells also get Disciplined Survivor). Spells: Cloudkill (CON, 5d8+upcast poison), Insect Plague (CON, 4d10+upcast piercing), Stinking Cloud (CON, Poisoned), Spike Growth (2d4 piercing, no save), Evard's Black Tentacles (STR, 3d6 bludgeoning + Restrained), Wall of Fire (DEX, 5d8+upcast fire, 10ft), Sleet Storm (DEX, Prone + lose concentration, 20ft), Flaming Sphere (DEX, 2d6+upcast fire, 5ft), Blade Barrier (DEX, 6d10 slashing, 10ft), Incendiary Cloud (DEX, 10d8 fire, 20ft). Moonbeam uses separate `moonbeam_active/x/y/slot_level` fields (5ft, CON, 2d10+upcast radiant). Investiture of Flame uses caster-centered 5ft emanation (1d10 fire, no save, `investiture_flame_active` flag). Spirit Guardians uses its own dedicated system.

- **Faerie Fire** (Basic Rules 2024 para 13167-13168): Concentration spell, 20ft cube. Failed DEX save → target outlined (persistent advantage on ALL attacks against them for duration). Uses dedicated `faerie_fire_outlined` bool + `faerie_fire_source_id` uint on combatant (NOT the single-use `guiding_bolt_advantage` flag). Removes Invisible condition. Concentration cleanup clears outlined effect from all affected targets. Full save failure chain on initial cast.

- **Polymorph HP restoration** (Basic Rules 2024 para 14624-14626): On concentration break, original HP/AC restored via `polymorph_caster_id` tracking in `clear_concentration_effects`. On 0 HP in beast form, excess damage carries over to original form (in `apply_damage`, mirroring Wild Shape pattern).

- **Heat Metal BA re-damage** (Basic Rules 2024 para 13734-13735): Concentration spell. Initial cast deals 2d8+upcast fire damage to metal-armored target. On subsequent turns, caster can use bonus action to re-deal the same damage. Tracked via `heat_metal_active`, `heat_metal_target_id`, `heat_metal_dice_count` on combatant. Cleared in `clear_concentration_effects`. Client menu entry in bonus action menu.

- **Hunter's Mark target transfer** (PHB 2024 para 13825-13826): When marked target dies, Hunter's Mark auto-transfers to nearest hostile within 90ft (following Hexblade Curse pattern in `maybe_apply_on_kill_features`).

- **Enlarge/Reduce** (Basic Rules 2024 para 12795-12800): L2 Transmutation, concentration. Full rewrite from broken damage-only implementation. Caster prompted via `pending_spell_choice` for Enlarge vs Reduce (bot AI: Reduce for hostiles, Enlarge for allies). Unwilling targets get CON save with full save failure chain. **Enlarge**: size +1, `enlarge_active` flag, +1d4 weapon damage (in `finalize_roll_result`), advantage on STR checks (`request_skill_check`) and STR saves (+5 approx in `get_save_bonus`). **Reduce**: size -1, `reduce_active` flag, -1d4 weapon damage (min 1), disadvantage on STR checks and STR saves (-5 approx). Tracking: `enlarge_reduce_caster_id` + `enlarge_original_size` on target. Concentration cleanup restores original size, clears all flags.

- **Hex ability check disadvantage** (Basic Rules 2024 para 13730): Hex cast now prompts caster for ability choice (STR/DEX/CON/INT/WIS/CHA) via `pending_spell_choice`. `hex_cursed_ability` field on caster stores the chosen ability. In `request_skill_check`, scans all living casters to check if any have `hex_target_id == target` with matching `hex_cursed_ability == ability_id`, applies disadvantage. Choice persists through hex target transfer on death. Cleared in concentration cleanup.

- **Stabilize action** (PHB 2024 para 4525): DC 10 Wisdom (Medicine) check to stabilize a dying creature at 0 HP within 5ft. Respects proficiency, expertise, Jack of All Trades. Consumes action. Client action menu entry.

- Spell slot consumption (lowest available >= spell level)

- Spell menu shows level (Cantrip/Level N) and Concentration tag for each spell

- **Bane spell** (Basic Rules 2024 para 12032): Random 1d4 penalty on attack rolls (via `roll_bane_penalty()` in battle_manager) and saving throws (via `random(1,4)` in `get_save_bonus`). Concentration with blanket-clear on break.

- **Blade Ward** (cantrip): Sets `blade_ward_active` for B/P/S resistance until start of caster's next turn. Half damage in `apply_damage`. Cleared in `advance_turn` at turn start.

- **Blur** (L2, concentration): Sets `blur_active`. Attackers who can see the target have disadvantage in `apply_attack_advantage_state`. Cleared in `clear_concentration_effects`.

- **Warding Bond** (L2, non-concentration, 1 hour): Basic Rules 2024 para 15561. Touch range (5ft), ally only. Target gains +1 AC, +1 to all saving throws (in `get_save_bonus`), and resistance to ALL damage (in `apply_damage`). When target takes damage, caster takes the same amount (post-resistance). Tracked via `warding_bond_active`, `warding_bond_source_id` (on target), `warding_bond_target_id` (on caster). Recursion-safe via `warding_bond_sharing` flag on the `battle` class. Bond ends if caster drops to 0 HP (cleared in `apply_damage` after sharing). Casting again on either creature ends the old bond. No concentration cleanup needed — duration-based only.

- **Vicious Mockery** (cantrip): Basic Rules 2024 para 15527. WIS save, 1d6 psychic (scales). On failed save, `vicious_mockery_disadv` flag set on target — grants disadvantage on next attack roll (consumed in `apply_attack_advantage_state`). No longer incorrectly reuses the `baned` flag.

- **Bane** (L1, concentration): Now uses per-caster tracking via `bane_source_id` field on targets. Concentration cleanup in `clear_concentration_effects` only clears targets where `bane_source_id == caster.id` (was blanket-clear).

- **Guidance** (cantrip, concentration): Sets `guidance_active` on target. +1d4 on next ability check in `finalize_roll_result` for `ROLL_ABILITY_CHECK`, auto-cleared after use.

- **Resistance** (cantrip, concentration): Sets `resistance_active` on target. +1d4 on next saving throw in `get_save_bonus`, auto-cleared after use.

- **Protection from Energy** (L3, concentration): Uses `pending_spell_choice` for 5 damage type options (Acid/Cold/Fire/Lightning/Thunder). Sets `protection_from_energy_active` + `protection_from_energy_type`. Half damage for matching type in `apply_damage`.

- **Protection from Evil and Good** (L1, concentration): Sets `protection_from_evil_and_good_active` on target with `pfeg_source_id`. Creatures of type aberration/celestial/elemental/fey/fiend/undead have disadvantage on attacks against target (in `apply_attack_advantage_state`). Charm/Frighten immunity enforced in `add_condition()` (blanket approximation — blocks COND_CHARMED and COND_FRIGHTENED on warded targets regardless of source creature type). `creature_type` field on combatant tracks type (default "humanoid", set from `monster_def.type` for monsters).

- **Shield of Faith** (L1, concentration): Basic Rules 2024 para 15004. Uses dedicated `shield_of_faith_active` + `shield_of_faith_caster_id` fields on combatant (NOT `shield_active`/`shield_ac_bonus` which are shared with Shield reaction and cleared at turn start). Applies `armor_class += 2` on cast. Concentration cleanup removes +2 AC via per-caster tracking. Self-cast and ally-cast variants. Re-casting replaces old bond.

- **Beacon of Hope** (L3, concentration): Basic Rules 2024 para 12201. Sets `beacon_of_hope_active` + `beacon_of_hope_caster_id` on all allies within 30ft. When active, healing spells restore maximum possible HP instead of rolling dice (Cure Wounds d8→8, Healing Word d4→4, Mass Healing Word d4→4, Prayer of Healing d8→8, Mass Cure Wounds d8→8). Multi-target heals check beacon per-target. **Death save advantage**: in `process_roll_result`, rolls a second d20 server-side and takes the higher when `beacon_of_hope_active` (works for both human and bot players). Concentration cleanup clears per-caster.

- **Heroism Frightened Immunity**: Basic Rules 2024 para 13767. Ongoing `heroism_source_id != 0` blocks COND_FRIGHTENED in `add_condition()`. Previously only removed Frightened on initial cast.

- **Greater Invisibility** (L4, concentration): Basic Rules 2024 para 13658. Uses dedicated `greater_invisibility_active` + `greater_invisibility_caster_id` fields. Sets COND_INVISIBLE + `is_hidden`. Unlike regular Invisibility, does NOT break on attack — `reveal_hidden_combatant` is bypassed at all 3 attack paths (player/bot/monster) when `greater_invisibility_active` is true. Concentration cleanup removes COND_INVISIBLE + is_hidden + flag.

- **Heat Metal Disadvantage** (L2, concentration): Basic Rules 2024 para 13734. Dedicated `heat_metal_disadv` field on target replaces old `baned = true` hack. Wired into `apply_attack_advantage_state` (attack disadvantage) and `request_skill_check` (ability check disadvantage). Expires at start of caster's next turn (cleared in `advance_turn` when Heat Metal caster's turn begins). Concentration cleanup also clears it.

- **See Invisibility** (L2, NOT concentration): Sets `see_invisibility_active`. Bypasses invisible disadvantage in `apply_attack_advantage_state` and `can_see`. No range limit.

- **Freedom of Movement** (L4, NOT concentration per 2024): Sets `freedom_of_movement_active`. Blocks COND_PARALYZED and COND_RESTRAINED in `add_condition`.

- **Enhance Ability** (L2, concentration): Sets `enhance_ability_active` with `enhance_ability_caster_id`. Grants advantage on ability checks in `request_skill_check`.

- **Silence** (L3, concentration): Places 20ft sphere at `silence_x/y`. Applies COND_DEAFENED to creatures in zone. Blocks spellcasting in `handle_cast` (Subtle Spell bypasses). Cleanup removes Deafened.

- **Swift Quiver** (L5, concentration): Sets `swift_quiver_active`. Bonus action for 2 ranged attacks via flurry-style chain (`attacks_remaining` + `resolution_tag = "swift_quiver"`). Client menu entry + bonus action handler.

- **True Seeing** (L6, NOT concentration): Sets `true_seeing_active`. Truesight 120ft — bypasses invisible in `apply_attack_advantage_state` and `can_see`.

- **Expeditious Retreat** (L1, concentration): Sets `expeditious_retreat_active`. Immediate Dash on cast + Dash as bonus action each turn. Client bonus action menu entry sends `expeditious_retreat_dash`. Server handler in `users_dom.nvgt` adds speed to movement. State synced via `my_expeditious_retreat_active`.

- **Levitate** (L2, concentration): CON save for unwilling targets (full save failure chain). Sets `levitate_active` + `levitate_source_id`. Blocks horizontal movement in `handle_move` and zeros movement at turn start in `advance_turn`.

- **Compulsion** (L4, concentration): AoE WIS save or Charmed with full save failure chain (including Countercharm). End-of-turn WIS re-save in `advance_turn` to break free. Concentration break clears Charmed from all targets.

- **Heroes' Feast** (L6, NOT concentration, 24 hours): Applies to all allies. +2d10 max HP and current HP (`heroes_feast_hp_bonus`). Poison damage resistance in `apply_damage`. Immunity to Frightened and Poisoned in `add_condition`. +5 WIS save advantage in `get_save_bonus`.

- **Resilient Sphere** (L4, NOT concentration, 1 min): DEX save for unwilling targets (full chain). Sets `resilient_sphere_trapped` + `resilient_sphere_rounds = 10`. Full damage immunity (return early in `apply_damage`) + COND_INCAPACITATED. Duration countdown at trapped creature's turn start in `advance_turn`. Auto-releases when rounds hit 0. Dispel Magic (L4+) can shatter it. Otiluke's variant now also uses the same system.

- **Dispel Magic** (L3): Basic Rules 2024 para 12905-12906. Targets one creature: auto-ends ongoing spells of level ≤ Dispel Magic slot level. For each spell of level > slot level, caster makes ability check (d20 + spellcasting mod vs DC 10 + spell level). Known buff spell levels hardcoded (Bless L1, Heroism L1, Bane L1, Shield L1, Haste L3, Fly L3, Stoneskin L4, Resilient Sphere L4). Concentration spells look up base level from `SPELL_DEFS` catalog. War Magic Power Surge gain on success.

- **Counterspell** (L3, reaction): Basic Rules 2024 para 12678. Implemented as readied reaction (cast on your turn, triggers on next enemy spell within 60ft). Target caster makes CON save vs counterspeller's spell save DC. On success: spell fizzles. **Slot preservation**: per 2024 source "If that spell was cast with a spell slot, the slot isn't expended" — countered caster's spell slot is refunded via `slot_consumed` tracking flag.

- **Goodberry** (L1): Practical combat approximation — heals caster 10 HP immediately (no berry inventory system).

- **Time Stop** (L9, instantaneous): Rolls 1d4+1, sets `time_stop_turns_remaining`. In `advance_turn`, if the previous combatant has turns remaining, the initiative order does NOT advance — instead their turn resources are reset and they take another full turn. Supports monster AI and bot players during extra turns.

- **Antimagic Field** (L8, concentration): Sets `antimagic_field_active`. 10ft emanation blocks all spellcasting — checked in `handle_cast` after Silence check. Own field doesn't block self. Cleared in `clear_concentration_effects`.

- **Globe of Invulnerability** (L6, concentration): Sets `globe_of_invulnerability_active` + `globe_of_invulnerability_level` (5 + upcast levels). 10ft emanation blocks spells of the protected level or lower cast from OUTSIDE the barrier — checked in `handle_cast` after Antimagic Field check. Spells from inside the globe work normally. Cleared in `clear_concentration_effects`.

- **Holy Aura** (L8, concentration): Sets `holy_aura_active`. 30ft emanation grants allies advantage on ALL saving throws (+5 approx in central spell save path) and imposes disadvantage on attack rolls against protected creatures (in `apply_attack_advantage_state`). Cleared in `clear_concentration_effects`.

- **Mind Sliver** (cantrip): Basic Rules 2024 para 14174. INT save, 1d6 psychic (scales at L5/11/17). On failed save, target subtracts 1d4 from their next saving throw. `mind_sliver_penalty_active` flag on target, consumed on first save in `get_save_bonus`. Applied before Bane penalty.

- **Eyebite** (L6, concentration): Basic Rules 2024 para 13145-13151. Full 3-way choice via `pending_spell_choice`: Asleep (COND_UNCONSCIOUS + COND_INCAPACITATED, wakes on damage via `eyebite_asleep_source_id` check in `apply_damage`), Panicked (COND_FRIGHTENED + `frightened_source_id`), Sickened (COND_POISONED + `eyebite_sickened_source_id`). WIS save with full chain including Countercharm for Panicked/Asleep. Concentration cleanup removes all 3 effect types. Per-turn retarget action deferred.

- **Bestow Curse** (L3, concentration): Basic Rules 2024 para 12219-12222. Full 9-option choice via `pending_spell_choice`: extra_damage (1d8 necrotic on caster's hits), attack_disadv (disadvantage on attacks against caster), forced_dodge (WIS save each turn or waste action), ability_str through ability_cha (disadvantage on saves and checks for that ability). Touch range (5ft), WIS save with full chain. Tracking: `bestow_curse_type` (string) and `bestow_curse_source_id` (uint) on the TARGET combatant. 6 wiring points: (1) ability curse -5 save penalty in `get_save_bonus`, (2) ability curse disadvantage in `request_skill_check`, (3) attack disadvantage in `apply_attack_advantage_state`, (4) forced dodge WIS save at turn start in `advance_turn`, (5) extra 1d8 necrotic in `finalize_roll_result`, (6) full cleanup in `clear_concentration_effects`. L4+ non-concentration mode deferred.

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
- **Animate Objects** — spawns spellcasting-ability-mod animated object companions (AC 14, HP 20, 1d4+4 bludgeoning)
- **Giant Insect** — spawns scaled companion (AC 14+PB, HP 10*slot_level+20, multiattack 2, 1d6+3+PB piercing)
- **Conjure Animals/Fey/Celestial/Elemental** — full companion spawns with source-scaled stats
- **Create Undead** — ghoul companion spawn (2d6+spell_mod piercing, multiattack)
- **Summon Dragon** — draconic spirit (3d8 fire, multiattack, HP 80+10*level)
- **Guardian of Faith** — invulnerable sentinel (HP 9999, AC 20, stationary, 20 radiant aura)
- **Mordenkainen's Faithful Hound** — magical hound (4d8 force, 60 HP, AC 18)

**Caster-centered emanation spells (NOT companions):**
- **Conjure Minor Elementals** — 15ft emanation, +2d8 elemental damage on attack hits (+2d8/upcast), concentration
- **Conjure Woodland Beings** — 10ft emanation, WIS save or 5d8 force per turn (+1d8/upcast), concentration

**Deferred:**
- Beast Master Sea/Sky variants (need a creature selection prompt)
- Drakewarden damage type prompt (currently uses init default)
- Echo Knight Manifest Echo (needs HP=1 dummy logic)
- Bigby's Hand mode prompt (Clenched Fist / Forceful Hand / Grasping Hand / Interposing Hand)
- Companion AI improvements (currently uses generic monster turn flow)

### Monster AI & Special Abilities (2026-04-10)

**Smart Targeting** (`find_nearest_target_for_monster`): Score-based system replaces pure-nearest targeting.
- Distance penalty (prefer closer targets, +50 bonus for already-in-melee-range)
- Focus fire: +80 for targets at ≤25% HP, +40 for ≤50%, +15 for ≤75%
- Target concentrating casters: +35
- Target healers (Cleric/Druid +25, Paladin/Bard +15)
- Avoid Resilient Sphere trapped: −200 
- Avoid dodging targets: −20
- Never targets downed (0 HP) players when conscious players exist

**Monster Traits** (`monster_def` fields, copied to `combatant` in `create_monster_combatant`):
- **Pack Tactics** (`pack_tactics`): Advantage on attacks when ally within 5ft of target. Applied in `apply_attack_advantage_state`. Used by: Kobold, Wolf, Dire Wolf.
- **Regeneration** (`regen_amount`): Heal N HP at start of turn in `advance_turn`. Blocked by fire/acid damage taken since last turn (`regen_blocked_this_round` set in `apply_damage`). Used by: Troll (10 HP/turn).
- **Knockdown** (`knockdown_dc`): On weapon hit, target STR save or Prone. Applied after damage in `finalize_roll_result`. Used by: Wolf (DC 11), Dire Wolf (DC 13).
- **Paralyzing Touch** (`paralyze_dc`): On weapon hit, target CON save or Paralyzed. Applied after damage in `finalize_roll_result`. Used by: Ghoul (DC 10).
- **Breath Weapon** (`breath_name/save_type/save_dc/dice/count/damage_type/range/recharge_min`): AoE action targeting all enemies in range. Full save failure chain (Arcane Deflection, Countercharm, Flash of Genius, etc.). AI uses breath when 2+ targets in range OR 1 target in range but not in melee. Recharges each turn start on d6 ≥ `recharge_min`. Used by: Young White Dragon (10d8 cold, DC 15 CON, 30ft), Young Red Dragon (16d6 fire, DC 17 DEX, 30ft), Adult Black Dragon (12d8 acid, DC 18 DEX, 60ft), Adult Red Dragon (18d6 fire, DC 21 DEX, 60ft).

**Damage Resistances/Immunities** (set via monster_def bools, mapped to existing combatant resistance fields):
- Skeleton: poison immunity + poisoned immunity
- Zombie: poison immunity + poisoned immunity
- Ghoul: poison/poisoned/charmed immunity
- Wight: poison/poisoned immunity, necrotic resistance, B/P/S nonmagical resistance
- Fire Elemental: fire immunity, poison/poisoned/paralyzed/charmed immunity
- Shadow Demon: cold/fire/lightning resistance, poison immunity
- Wraith: acid/cold/fire/lightning/thunder resistance, necrotic/poison immunity, poisoned/charmed/paralyzed immunity, B/P/S nonmagical resistance
- Frost Giant: cold immunity
- Pit Fiend: fire immunity, cold resistance, poison/poisoned/frightened immunity, B/P/S nonmagical resistance
- Lich: cold/lightning/necrotic resistance, poison/poisoned/charmed/frightened/paralyzed immunity, B/P/S nonmagical resistance
- Adult Dragons: fire/acid immunity (matching breath type), frightened immunity
- Beholder: poisoned condition immunity

**Condition Immunities** (`immune_poisoned/frightened/charmed/paralyzed/exhaustion` on combatant): Checked in `add_condition()` to prevent the condition from being applied.

**B/P/S Nonmagical Resistance** (`resist_bps_nonmagical`): In `apply_damage`, B/P/S damage is halved unless the source has `magic_weapon_bonus > 0`. Used by: Lich, Pit Fiend, Wraith, Wight.

**Ranged Monster Kiting**: Monsters with ranged primary attacks (range > 5ft) who find themselves in melee (5ft) will move AWAY from the target before attacking, avoiding disadvantage on ranged attacks. Executed before the normal approach loop.

**Troll Undeath** (`regen_amount > 0`): Trolls do NOT die at 0 HP unless `regen_blocked_this_round` is true (fire/acid damage was taken). Instead they fall unconscious at 0 HP. At turn start, regeneration brings them back. If regen is blocked when at 0 HP, they die permanently.

**Petrifying Gaze** (`petrify_dc`): On weapon hit, target CON save or Petrified. Applied after damage in `finalize_roll_result`. Used by: Basilisk (DC 12), Medusa (DC 14).

**Frightful Presence** (`frightful_presence_dc/range`): Fires once per combat on the dragon's first turn in `execute_monster_turn`. All players within range make WIS save (with full failure chain: Arcane Deflection, Countercharm, Flash of Genius) or become Frightened. Used by: Adult Black Dragon (DC 16, 120ft), Adult Red Dragon (DC 19, 120ft).

### Concentration Cleanup System (2026-04-10)

When a caster's concentration breaks, `clear_concentration_effects()` must remove all conditions that spell applied to targets. Per-caster tracking fields on `combatant` prevent removing conditions from a different caster's spell:

| Tracking field | Condition removed | Spells using it |
|---|---|---|
| `charm_spell_caster_id` | COND_CHARMED (+ COND_INCAPACITATED for Hypnotic Pattern) | Charm Person, Charm Monster, Dominate Person, Dominate Monster, Dominate Beast, Hypnotic Pattern, Enthrall |
| `hold_spell_caster_id` | COND_PARALYZED | Hold Person, Hold Monster |
| `laughter_spell_caster_id` | COND_INCAPACITATED + COND_PRONE | Tasha's Hideous Laughter |
| `frightened_source_id` (existing) | COND_FRIGHTENED | Fear, Phantasmal Killer, Eyebite |
| `restrained_spell_caster_id` | COND_RESTRAINED | Web, Entangle, Flesh to Stone |
| `incap_spell_caster_id` | COND_INCAPACITATED (+ COND_UNCONSCIOUS for Sleep) | Sleep, Confusion, Otto's Irresistible Dance |
| `blinded_spell_caster_id` | COND_BLINDED | Sunbeam |
| `faerie_fire_source_id` | `faerie_fire_outlined` (persistent advantage, NOT a condition) | Faerie Fire |
| `slow_spell_caster_id` | Speed halved + AC −2 + no reactions (restores `slow_original_speed` + AC +2) | Slow |
| `enlarge_reduce_caster_id` | Size change + STR adv/disadv + weapon damage modifier (restores `enlarge_original_size`, clears `enlarge_active`/`reduce_active`) | Enlarge/Reduce |
| `bestow_curse_source_id` | Curse effect (varies: extra damage, attack disadv, forced dodge, ability disadv). Clears `bestow_curse_type` + `bestow_curse_source_id` on target | Bestow Curse |
| `shield_of_faith_caster_id` | `shield_of_faith_active` + `armor_class -= 2` (dedicated AC field, NOT shield_active) | Shield of Faith |
| `beacon_of_hope_caster_id` | `beacon_of_hope_active` (max-healing flag, no condition) | Beacon of Hope |
| `greater_invisibility_caster_id` | `greater_invisibility_active` + COND_INVISIBLE + `is_hidden` (all three cleared) | Greater Invisibility |

**Pattern for new concentration spells:** In the spell handler, set the tracking field on the target (`target.xxx_caster_id = c.id`). In `clear_concentration_effects()`, add a name-matched block that loops combatants and removes the condition where the tracking ID matches. Compulsion uses blanket-clear (no per-target tracking) as a fallback.

### Damage-Breaks-Charm Mechanics (2026-04-10)

Implemented in `apply_damage()` in `combat_engine.nvgt`. Three categories of damage interaction with charm/dominate spells, each with distinct behavior per PHB:

**1. Dominate Person / Dominate Monster / Dominate Beast** — When a dominated target takes damage, they get a new WIS saving throw against the caster's spell save DC. On success: `COND_CHARMED` removed, `charm_spell_caster_id` cleared, caster's concentration broken. On failure: the domination continues. Source: PHB "each time the target takes damage" for Dominate spells.

**2. Charm Person / Charm Monster** — Any damage to the charmed target immediately ends the charm. `COND_CHARMED` removed, `charm_spell_caster_id` cleared, caster's concentration broken. No saving throw — damage is an automatic end condition. Source: PHB "The spell also ends if you or your companions deal damage to it."

**3. Hypnotic Pattern** — Damage to a charmed+incapacitated target ends the effect on THAT TARGET ONLY. `COND_CHARMED` + `COND_INCAPACITATED` removed, `charm_spell_caster_id` cleared. Does NOT break the caster's concentration — other affected targets remain charmed and incapacitated. Source: PHB "The charm ends if the creature takes any damage."

**Lookup order in `apply_damage()`:** The code checks `charm_spell_caster_id > 0` on the damaged target, then identifies which charm spell is active to select the correct branch (Dominate → save, Charm → instant end, Hypnotic Pattern → per-target end without concentration break).

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
- **Enlarge/Reduce** — Enlarge (size +1, +1d4 weapon damage, advantage STR) vs Reduce (size -1, -1d4 weapon damage, disadvantage STR). Bot AI auto-picks Reduce for hostiles, Enlarge for allies. CON save for unwilling targets with full chain. Source: Basic Rules para 12795-12800. Choice kind: `binary`.
- **Hex** — choose cursed ability (STR/DEX/CON/INT/WIS/CHA) for disadvantage on ability checks. 6 options. Source: Basic Rules para 13730. Choice kind: `binary`.
- **Magic Missile** — distribute N darts (3 base, +1 per upcast) among visible enemies; auto-hit, each dart deals 1d4+1 force damage independently per target. Source: Basic Rules para 14089. Choice kind: `distribution`.
- **Scorching Ray** — distribute N rays (3 base, +1 per upcast) among visible enemies; each ray is a separate ranged spell attack for 2d6 fire damage. Source: Basic Rules para 14851. Choice kind: `distribution`.
- **Eldritch Blast** — at L5+ distribute N beams (2 at L5, 3 at L11, 4 at L17) among visible enemies; each beam is a separate ranged spell attack for 1d10 force damage. Source: Basic Rules para 13047. Choice kind: `distribution` (only at L5+; L1-4 uses the standard single-target attack path).
- **Eyebite** — choose effect: Panicked (COND_FRIGHTENED), Asleep (COND_UNCONSCIOUS + COND_INCAPACITATED), or Sickened (COND_POISONED). WIS save. Source: Basic Rules para 13145-13151. Choice kind: `binary`.
- **Bestow Curse** — choose from 9 curse options: extra_damage (1d8 necrotic), attack_disadv, forced_dodge, ability_str through ability_cha. WIS save. Source: Basic Rules para 12219-12222. Choice kind: `binary`.

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

- **Barbarian**: Rage + Berserker Frenzy (bonus melee attack while raging) + Storm Aura (Storm Herald BA, desert/sea/tundra) + Brutal Strike (L9+ toggle: Forceful/Hamstring/Staggering/Sundering)

- **Fighter**: Action Surge, Second Wind + Battle Master Maneuvers (Trip Attack, Precision Attack, Riposte, Menacing Attack, Goading Attack, Pushing Attack, Disarming Attack, Distracting Strike, Sweeping Attack, Parry, Rally) + Psi Warrior Strike

- **Rogue**: Cunning Action + Soulknife Psychic Blades + Cunning Strike (L5+ toggle: Poison/Trip/Withdraw + L14 Daze/KnockOut/Obscure) + Panache (Swashbuckler L9) + Elegant Maneuver (Swashbuckler L13) + Sudden Strike (Scout L17) + Ghost Walk (Phantom L13)

- **Sorcerer**: Innate Sorcery, Font of Magic (SP↔Slot), Metamagic (10 options: Careful/Distant/Empowered/Extended/Heightened/Quickened/Seeking/Subtle/Transmuted/Twinned)

- **Paladin**: Divine Smite, Lay on Hands + Channel Divinity (Sacred Weapon, Vow of Enmity, Inspiring Smite, Nature's Wrath)

- **Cleric**: Channel Divinity (Preserve Life, War Priest Attack)

- **Monk**: Flurry of Blows + Shadow Step, Hands of Healing, Elemental Burst, Kensei's Shot (+1d4 ranged), Sharpen the Blade (+1/2/3 attack/damage)

- **Bard**: Bardic Inspiration + Mantle of Inspiration (Glamour) + Mantle of Majesty (Glamour L6, concentration free Command each turn as BA)

- **Warlock**: Healing Light (Celestial), Fey Presence (Archfey), Celestial Resilience (Celestial L10, distribute temp HP to 5 allies at battle start)

- **Druid** (level 2+): Wild Shape + Starry Form Archer (Stars L2, BA ranged spell attack 1d8+WIS, 2d8 at L10) + Starry Form Chalice (Stars L2, auto-heal ally 1d8+WIS after healing spells)

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
  - Disciplined Survivor L14 sets all 6 save proficiencies. L14 Disciplined Survivor save reroll: `try_disciplined_survivor_reroll` helper wired into all 22 save failure sites. Spends 1 FP, smart-spend only if nat 20 + bonus >= DC.
  - Empowered Strikes L6 flag set (Force/normal damage type prompt still deferred)
- **Rogue Evasion fix** (`5e78f1c`): L7 init was missing — only Monks were getting `evasion_active`. Fixed in `character_data.nvgt` Rogue init block.
- **Paladin batch 1** (`79dd582`): Aura of Protection L7 → L6 gating bug fixed; L2 Paladin's Smite free Divine Smite cast wired into bonus action handler; L5 Faithful Steed free Find Steed cast flag added; L10 Aura of Courage Frightened immunity in `add_condition`; L11 Radiant Strikes (+1d8 radiant on melee weapon/unarmed hit) in `apply_attack` damage block. L14 Restoring Touch verified already-implemented in lay_on_hands handler.
- **Ranger batch 1** (in this commit): L1 Favored Enemy free Hunter's Mark casts (scaling 2/3/4/5/6) via new `grant_free_cast()` helper; L6 Roving (+10 ft speed + matching climb/swim); L10 Tireless (Magic action 1d8+WIS temp HP via new bonus action menu entry); L13 Relentless Hunter (Hunter's Mark concentration unbreakable in `check_concentration`); L14 Nature's Veil (Bonus Action self-Invisible 1 round, full tickdown in `advance_turn`); L17 Precise Hunter (advantage on Hunter's Mark target attacks); L18 Feral Senses (Blindsight 30 ft); L20 Foe Slayer (Hunter's Mark d6 → d10). Client menu entries + state broadcast wired.
- **Rogue batch 1** (`53031ad`): L1 Sneak Attack base case added to `apply_subclass_on_hit_damage` (was missing entirely — only Inquisitive subclass rider existed). Full conditions: weapon attack + finesse/ranged + (advantage OR ally-within-5ft-of-target with no disadvantage), `(level+1)/2` dice scaling, `sneak_attack_used_this_turn` once-per-turn flag (cleared in `advance_turn`). Function signature now takes `had_advantage`/`had_disadvantage` from caller's `pending_roll`. L3 Steady Aim (bonus action handler in `users _dom.nvgt`, `steady_aim_pending` flag, advantage state + Speed=0 enforcement, Client menu entry gated on unmoved Speed). L5 Uncanny Dodge (reaction option added to reaction prompt; `uncanny_dodge_pending` consumed in `apply_damage` to halve damage; gated on `!Incapacitated`; Client UI label added). L7 Reliable Talent: corrected from L11 → L7 init gating (was a bug). L15 Slippery Mind (WIS + CHA save proficiencies on init). L18 Elusive (`elusive_active` flag forces `adv = false` at end of `apply_attack_advantage_state` unless target is Incapacitated). L20 Stroke of Luck flag set on init. L20 Stroke of Luck: now fires on failed saving throws as last resort in save chain. `try_stroke_of_luck_save` wired into all 22 save sites. All gated by source paragraph references.
- **Sorcerer batch 1** (`ab8502f`): L1 Innate Sorcery (bonus action, +1 spell save DC + advantage on Sorcerer spell attacks for 10 rounds, 2/LR via `innate_sorcery_uses_remaining`, rounds tickdown in `advance_turn`). `apply_attack_advantage_state()` now takes `bool is_spell_attack` parameter; passed `true` at the 3 spell-attack call sites so the Innate Sorcery advantage only applies to Sorcerer spell attacks. `spell_save_dc()` adds +1 to Sorcerer casters with active Innate Sorcery. L2 Font of Magic SP↔slot conversion (both directions as bonus action handlers in `users _dom.nvgt`: `font_of_magic_to_slot` consumes SP per cost table L1=2/L2=3/L3=5/L4=6/L5=7 with min-level gating, `font_of_magic_to_sp` is free action that yields slot-level SP). L5 Sorcerous Restoration flag set on init (short rest plumbing deferred). L7 Sorcery Incarnate fallback path: when out of Innate Sorcery uses but L7+, 2 SP can activate it instead. 7 metamagic stub flags added (`careful/distant/empowered/extended/heightened/seeking/transmuted`) for future batches. Client wires 4 new state fields, 3 new menu entries, and nested sub-menu Font of Magic slot-level pickers in both directions.
- **Sorcerer Draconic Sorcery + Wizard Evoker subclass audit** (`cc7b1d6`): Basic Rules 2024 paras 7539-7566 + 9253-9268. Draconic Sorcery and Evoker subclass features audited against source paragraphs.
- **Sorcerer Storm Sorcery + Divine Soul subclass audit** (`50944c0`): Xanathar's paras 2515-2639. Storm Sorcery: Heart of the Storm eruption damage + lightning/thunder resistance at L6, Storm's Fury reaction lightning + STR save push at L14, Wind Soul immunity + fly 60 at L18. Divine Soul: Divine Magic affinity choice via Shift+P with auto-prepared spell at L1, Favored by the Gods auto 2d4 additive reroll 1/SR at L1, Otherworldly Wings toggle BA fly 30 at L14, Unearthly Recovery BA heal half max HP when below half 1/LR at L18.
- **Warlock batch 1** (`e8f7e88`): L2 Magical Cunning Magic action handler (`magical_cunning_available` flag, recovers `(max+1)/2` Pact Magic slots at the Pact slot level, 1/LR; auto-detects the Pact slot level by scanning `spell_slots_max[]`). L9 Contact Patron handler (`contact_patron_available` flag, free Contact Other Plane with auto-success on save, 1/LR). L11/13/15/17 Mystic Arcanum (`mystic_arcanum_6/7/8/9_available` flags, `mystic_arcanum` handler grants a phantom slot at the chosen arcanum level for the next cast, 1/LR each). L20 Eldritch Master (`eldritch_master_active` flag set on init at L20; Magical Cunning handler reads `c.level >= 20` and grants full pact slot recovery instead of half). Eldritch Invocations known count corrected to match the source table (was 0/2/3/4/5/6/7/8 — now 1/3/3/3/5/5/6/6/7/7/7/8/8/8/8/9/9/10/10/10 per the Warlock Features table at paras 7607-7762). Client wires 6 new state fields and 3 new menu entries with sub-menu Mystic Arcanum level picker.
- **Wizard batch 1** (`4ad60b8`): L1 Ritual Adept (`ritual_adept_active` flag set on Wizard init — actual ritual casting hook deferred pending Ritual tag on spell data). L18 Spell Mastery (`spell_mastery_active` flag set on init at L18; slot bypass wired into `cast_spell` pipeline in `battle_manager.nvgt` — if `spell.id == c.spell_mastery_l1_spell_id` or `spell_mastery_l2_spell_id`, the cast skips slot consumption with "casts X through Spell Mastery — no spell slot consumed!" announcement). L20 Signature Spells (`signature_spells_charges_max = 2` set on init at L20; slot bypass for `signature_spell_a_id` and `signature_spell_b_id` with per-spell `_used_this_rest` tracking; "unleashes X as a Signature Spell — no spell slot consumed!" announcement). The four designation string fields default to empty (player must designate at level-up — prompt deferred to a future level-up UI batch). Client wires 7 new state fields. Short rest reset for Signature Spells charges deferred (currently only long rest exists). Existing L1 Arcane Recovery already shipped; verified in `users _dom.nvgt`.
- **Bard batch 1** (`9ae222c`): L5 Font of Inspiration (`font_of_inspiration_active` flag set on init at L5+; new `font_of_inspiration` no-action handler in `users _dom.nvgt` finds the lowest-level available spell slot, expends it from `spell_slots_current[]`, and increments `bardic_inspiration_uses` capped at CHA mod). L7 Countercharm (`countercharm_active` flag set on init at L7+; new `try_countercharm_reroll` helper in `battle_manager.nvgt` scans for any L7+ Bard with `countercharm_active` and reaction available within 30 ft of the failing save target — self allowed per RAW — consumes the reaction and rerolls the save with advantage, returns true if the reroll passed. Wired into 15 Charm/Frighten failed-save sites: cause_fear AoE/single, hypnotic_pattern, phantasmal_killer, mass_suggestion, command, suggestion, eyebite, dominate_person, charm_person, dominate_monster, enthrall, charm_monster, dominate_beast, weird. Polymorph's COND_CHARMED is an implementation marker for the polymorph effect — not a real charm — so it is intentionally skipped). L10 Magical Secrets (`magical_secrets_active` flag set on init at L10+ for client UI awareness; out-of-combat spell list expansion handled by existing spell menu). L18 Superior Inspiration (`superior_inspiration_active` flag set on init at L18+; existing `request_next_initiative` Superior Inspiration check updated to read the flag instead of hardcoded `c.level >= 18`). L20 Words of Creation (`words_of_creation_active` flag set on init at L20+; Power Word Heal and Power Word Kill auto-added to `c.prepared_spells` for L20 Bards; spell catalog `class_list` updated from "wizard" to "wizard,bard" for both spells; both `power_word_heal` and `power_word_kill` cast handlers in `battle_manager.nvgt` check `c.words_of_creation_active` and apply the spell to a second creature within 10 ft of the first target — Power Word Heal auto-picks the most-injured ally, Power Word Kill auto-picks the lowest-HP enemy). Client wires 5 new state fields and 1 new menu entry (Font of Inspiration).
- **Artificer batch 1** (`1a087b5`): L1 Tinker's Magic use tracking (`tinkers_magic_uses_max/_current` set on init to INT mod min 1; Magic action handler deferred — no hazards system for ball bearings/caltrops). L2 Replicate Magic Item flag (`replicate_magic_item_known`; full implementation deferred — needs DMG plan tables, LR crafting, item registry, vanish timers). L7 Flash of Genius (`flash_of_genius_uses_max/_current` set on init to INT mod min 1; new `try_flash_of_genius` helper in `battle_manager.nvgt` scans for any L7+ Artificer with the feature and reaction available within 30 ft of the failing target — self allowed per RAW — smart-spends only when the +INT mod bonus would actually turn the failure into a success, decrements the use, consumes the reaction, returns the new total. Wired into 20 save sites: 5 end-of-turn condition saves Hold Person/Web/Blindness-Deafness/Fear/Tasha's Hideous Laughter, plus 15 charm/frighten sites mirroring Bard Countercharm coverage. Also wired into `finalize_roll_result` for failed `ROLL_ABILITY_CHECK` so any skill check or hide check routed through the pending_roll system gets coverage automatically. Damage saves coverage extension deferred to a future batch). L10 Magic Item Adept (`magic_item_attunement_max = 4`). L11 Spell-Storing Item flag (`spell_storing_item_known`; full implementation deferred — needs item infrastructure). L14 Advanced Artifice (`magic_item_attunement_max = 5` + `refreshed_genius_active` flag; SR Flash regen pending short-rest subsystem). L18 Magic Item Master (`magic_item_attunement_max = 6`). L20 Soul of Artifice — Magical Guidance (`magical_guidance_active` flag; SR full Flash regen pending short-rest subsystem). L20 Cheat Death deferred (depends on Replicate Magic Item infra). Client wires 6 new state fields.
- **Gunslinger batch 2 — Maneuvers** (`1f95da2`): all 6 Risk Dice maneuvers from paras 207-218 — 5 wired, 1 deferred. **Bug fixes:** (a) **Dodge Roll** rebuilt from a broken `add_condition(COND_DODGING)` stub into the RAW +15 ft movement maneuver (BA + Risk Die, grants `c.movement_remaining += 15`; OA-immunity and difficult-terrain-immunity for the segment are deferred until per-segment movement tracking exists). (b) **Blindfire** rebuilt from a broken "ignore disadvantage on next ranged attack" stub into the RAW Blindsight 30 ft until end of turn (BA + Risk Die; `blindfire_active` flag set on activation, cleared at start of next turn in `advance_turn`). **New implementations:** **Bite the Bullet** (BA + Risk Die, temp HP = `risk_die_roll + level`) added to `users _dom.nvgt` bonus action handler dispatch + new client menu entry. **Grazing Shot** (no action, on miss with ranged weapon: `risk_die + DEX mod` weapon-type damage, 1/turn) — new `try_grazing_shot` helper in `battle_manager.nvgt` mirroring `try_flash_of_genius`, wired right after the attack `broadcast_roll` on miss path; per-turn flag `grazing_shot_used_this_turn` reset in `advance_turn`. **Maverick Spirit** (no action, on failed INT/WIS/CHA check or save: add Risk Die roll, 1/turn) — new `try_maverick_spirit` helper with smart-spend (only commits if the rolled Risk Die would actually turn the failure into a success). Wired into the generic ability check path (gated on INT/WIS/CHA `pr.ability_id`) and 16 WIS save sites paired with `try_flash_of_genius` (Hold Person EOT, Fear EOT, Tasha's Hideous Laughter EOT, Fear AoE, Hypnotic Pattern, Cause Fear, Phantasmal Killer, Mass Suggestion, Command, Suggestion, Eyebite, Dominate Person, Charm Person, Dominate Monster, Enthrall, Charm Monster, Dominate Beast, Weird). Per-turn flag `maverick_spirit_used_this_turn` reset in `advance_turn`. **Skin of Your Teeth** (Reaction: on hit, add Risk Die to AC) is deferred — depends on extending the existing reaction prompt infrastructure with a new opt-in reaction option. Client wires 1 new menu entry (Bite the Bullet) and updates Dodge Roll/Blindfire menu labels to match RAW.
- **Gunslinger batch 1** (`a2309f4`): Major source-accuracy fix-and-implement batch correcting multiple RAW bugs in the prior Gunslinger code (Valda's Spire of Secrets paras 159-203). **Bug fixes:** (a) **Risk Dice progression** corrected from `2d8 → 3d10 → 4d12` to RAW `4d8 (L2) → 5d8 (L6) → 5d10 (L10) → 6d10 (L14) → 6d12 (L18)`. (b) **Critical Shot** rebuilt from a broken use-based bonus-damage maneuver into the RAW passive crit-range expansion (`gunslinger_crit_threshold = 19/18/17` set on init at L2/9/17 and read by `get_critical_threshold` gated on `attacker.main_hand_is_ranged`). The broken `critical_shot_uses/_pending` field, the `users _dom.nvgt` user-action handler, the bonus-damage block in `finalize_roll_result`, and the `combat_ui.nvgt` menu entry were all removed. (c) **Gut Shot** rebuilt from a broken use-based bonus-damage maneuver into the RAW automatic on-crit debuff (sets `target.gut_shot_rounds_remaining = 10` (1 minute) + halves `target.speed`; `apply_attack_advantage_state` gives Disadvantage on outgoing attacks while `gut_shot_rounds_remaining > 0`; tickdown in `advance_turn` restores speed on expiry; gated on `pr.is_crit and c.main_hand_is_ranged and target.size <= SIZE_LARGE`). The broken `gut_shot` user-action handler and menu entry were also removed. (d) **Quick Draw** corrected from a flat `+2` initiative bonus to RAW Advantage on Initiative rolls (`quick_draw_active` flag set on init at L1+; hooked at `request_initiative_roll` in `battle_manager.nvgt`). **New implementations:** L5 Extra Attack (`c.extra_attacks = 1`). L7 Evasion (reuses existing shared `evasion_active` field with Monk/Rogue). L11 Overkill (`overkill_active` flag; ranged weapon hits gain `+1d8` extra damage in `finalize_roll_result` damage path — the ability-mod adder branch is the source intent for firearms which don't add mod, but the Firearm property isn't yet exposed on the weapon registry, so the implementation conservatively applies the +1d8 branch). L13 Cheat Death (`cheat_death_used` reset on init; wired in `apply_damage` (`combat_engine.nvgt`) right after Sorcerer Strength of the Grave — when a L13+ Gunslinger is reduced to 0 HP and not killed outright and `!cheat_death_used`, restores `current_hp = 1 + level` capped at max HP and sets the flag). L15 Dire Gambit (`dire_gambit_active` flag set on init at L15+; wired at `request_initiative_roll` and `finalize_roll_result` crit block to increment `risk_dice_current` capped at max). L18 Deft Maneuver flag (`deft_maneuver_active`; the maneuver-only bonus-action token is deferred). L20 Headshot (`headshot_active` flag set on init at L20+, `headshot_used` reset on init; wired in `finalize_roll_result` crit block — when a L20 Gunslinger crits with a ranged weapon and `!headshot_used`, sets `headshot_used = true` and either kills target if `current_hp < 100` or adds 10d10 extra damage. The 3-Risk-Dice refund refresh is deferred until SR subsystem). Client wires 10 new state fields and removes 2 obsolete menu entries.

- **Rogue Cunning Strike** (`3665b4d`): L5 Cunning Strike (PHB 2024 para 6553-6560). Toggle via bonus action menu — forgo SA dice for rider effects on next Sneak Attack. L5 options: Poison (1d6 cost, CON save or Poisoned 1 min), Trip (1d6 cost, DEX save or Prone), Withdraw (1d6 cost, move half speed without OAs). L14 Devious Strikes: Daze (2d6 cost, CON save), Knock Out (6d6 cost, CON save or Unconscious), Obscure (3d6 cost, DEX save or Blinded). L11 Improved Cunning Strike allows two effects. DC = 8 + DEX mod + Prof.
- **Barbarian Brutal Strike** (`3665b4d`): L9 Brutal Strike (PHB 2024 para 2338-2353). Toggle via bonus action menu after Reckless Attack — forgo advantage on one STR attack for +1d10 damage + chosen effect. L9: Forceful Blow (push 15ft + half speed move), Hamstring Blow (-15ft speed). L13 Improved: Staggering Blow (disadvantage on next save + no OAs), Sundering Blow (+5 to next ally attack vs target). L17: 2d10 damage + two different effects.
- **Sorcerer Metamagic** (`c9e4e20`): All 10 PHB 2024 Metamagic options (paras 7011-7044) as toggle bonus actions with SP cost. Quickened (2 SP, cast action spell as bonus action), Distant (1 SP, double range), Careful (1 SP, allies auto-succeed AoE save), Heightened (2 SP, enemy disadvantage on save), Empowered (1 SP, reroll CHA mod damage dice), Transmuted (1 SP, swap damage type), Seeking (1 SP, reroll missed spell attack), Subtle (1 SP, flavor), Extended (1 SP, double duration), Twinned (spell level SP, targets a second creature with the same spell. Wired for: save-based damage spells via twinned_target_id on pending_roll, attack-roll spells via follow-up attack chain, healing spells duplicate healing, plus explicit Haste and Hold Person handlers. Auto-picks nearest valid second target. Extra SP charged at cast time.). Flags snapshot onto `pending_roll` at cast time.
- **Extended Spell Concentration Advantage** (`7665fb3`): PHB 2024 para 7029 — `extended_spell_concentration` flag set on combatant when casting with Extended Spell active. Grants advantage on concentration saves for that spell. Cleared in `clear_concentration_effects()`.
- **Weapon Mastery Properties** (`7665fb3`): All 7 PHB 2024 mastery properties (Push/Sap/Slow/Topple/Vex/Cleave/Graze) wired into attack resolution. `main_hand_mastery` field plumbed from weapon table through character_sheet to combatant. Per-turn flags for Cleave/Slow/Sap/Vex.
- **Staggering Blow + Daze Wiring** (`ae7e13c`): Barbarian L13 Staggering Blow disadvantage wired into 6 save sites (central spell save + 5 EOT condition saves). Rogue L14 Daze enforced at turn start (lose movement + bonus action).
- **Exhaustion** (PHB 2024 paras 16254-16257): Full 2024 system. -2 per level to ALL d20 Tests (attacks, saves, ability checks, initiative). -5 ft speed per level. Death at level 6. Wired in: `get_save_bonus`, `get_skill_bonus`, `get_attack_bonus`, initiative modifier, movement_remaining. Exhaustion -1 on short rest for Ranger L10 Tireless.
- **Concentration Cleanup** (`ddc77f1`): Fixed critical bug where 11 concentration spell flags (Spirit Guardians, Divine Favor, Holy Weapon, Fire Shield, Stoneskin, Fly, Ensnaring Strike, Sanctuary, Venomous Mark, Fog Cloud, Darkness) were NOT cleared when concentration broke. All now reset in `clear_concentration_effects()`. Fire Shield resistance fix: `clear_concentration_effects` now properly clears `cold_resistance` (warm) or `fire_resistance` (chill) before clearing `fire_shield_active` — prevents stale resistance persistence.
- **Short Rest System** (`6d36682`): `apply_short_rest()` fires between waves in endless and wave modes. 25% max HP heal + restore Fighter Action Surge/Second Wind, Warlock Pact Magic, Wizard Arcane Recovery/Signature Spells, Druid Wild Shape, Battle Master/Arcane Archer dice, Monk Focus Points, Bard Bardic Inspiration, Cleric/Paladin Channel Divinity, Sorcerer Sorcerous Restoration.
- **Mobile feat** (`81b63fb`): PHB 2024 para 7635 — blanket OA immunity approximation in check_opportunity_attacks. Strict RAW is per-creature-attacked-this-turn.
- **Sorcerous Restoration** (`81b63fb`): PHB 2024 para 7002-7003 — L5+ Sorcerers regain floor(level/2) SP on short rest via apply_short_rest, once per long rest.
- **Eldritch Invocations** (`86bd95d`+`a697c44`): PHB 2024 paras 7749-7837 — 12 invocations: Armor of Shadows (free Mage Armor), Eldritch Mind (concentration advantage), Agonizing Blast (+CHA to EB damage), Repelling Blast (push 10ft on EB hit), Devil's Sight (120ft darkvision), Eldritch Spear (EB range), Fiendish Vigor (12 temp HP), Thirsting Blade (Extra Attack L5+, Blade), Eldritch Smite (force+Prone, Blade), Lifedrinker (+1d6 necrotic, Blade L9+), Devouring Blade (3 attacks, Blade L12+), Gift of the Protectors (1 HP instead of 0, Tome L9+). **Player-chosen at level-up** via invocation_choices pipeline (server detect → client multi-pick menu with level/pact prereq filtering → server persist → character_data reads choices). Legacy chars with empty choices get default combat-optimal set.
- **Fighter Tactical Master** (`b962cb0`): PHB 2024 para 5125-5126 — L9+ Fighter bonus action to replace weapon mastery with Push/Sap/Slow for next attack. Override in weapon mastery block clears after one attack. Client sub-menu. main_hand_mastery broadcast to client.
- **Paladin Aura ally coverage** (`09a4b32`): PHB 2024 paras 5665-5669, 5682-5683 — refresh_paladin_auras() at turn start and after movement. Aura of Protection CHA mod to ALL ally saves within 10ft (30ft at L18). Aura of Courage Frightened immunity for allies in range.
- **Charger feat charge damage** (`2e4be7f`): PHB 2024 para 1394-1403 — +1d8 on first melee hit after Dash. charger_dash_active flag set on Dash, consumed on hit.
- **Fey Touched / Shadow Touched free casts** (`2e4be7f`): PHB 2024 paras 1793-1800, 3563-3570 — grant_free_cast for Misty Step/Bless and Invisibility/Blindness-Deafness (1/LR each).
- **Polearm Master Reactive Strike** (`2813154`): PHB 2024 para 7714 — entering-reach OA trigger alongside leaving-reach in check_opportunity_attacks. Gated on has_feat("polearm_master") + non-ranged.
- **Short rest 1/SR reset sweep**: Added 18 missing 1/SR feature resets (Hexblade Curse, Master Duelist, Favored by Gods, Cheat Death, Headshot, Magic User's Nemesis, Flash of Genius +1 via Refreshed Genius, Stroke of Luck, 10 Ebon Tides/Grim Hollow subclass flags). Ranger L10 Tireless exhaustion -1 on SR. Inspiring Leader temp HP re-grant on short rest.
- **Monk Uncanny Metabolism** (initiative): PHB 2024 para 5334-5336 — L2+ Monk regains all Focus Points + heals (level + Martial Arts die) when rolling initiative with 0 Focus Points. 1/LR.

**Pending classes (in priority order):** *(all base class audits complete — focus shifts to subclass batches and shared backlog)*

**Audit doctrine:** every implementation block carries `// PHB 2024 <Class> L<n> <Feature> (para <X>-<Y>)` comments. Source-quoted commit messages. No invent. No auto-pick for player choices.

### Subclass Combat Features (138 subclasses, 80+ with full combat logic)
**Fully Implemented Subclasses with Combat Logic:**
- **Barbarian**: Berserker, Wild Heart, World Tree, Zealot, Ancestral Guardian, Storm Herald, Shadow Gnawer, Path of the Carrion Raven, Path of the Glacier, Path of the Infernal
- **Bard**: Glamour, Swords, Whispers, Creation, Lore, Valor, Eloquence, Spirits, Dance, Shadow, Dirge Singer
- **Cleric**: Life, Light, War, Forge, Grave, Peace, Twilight, Order, Shadow Domain, Keeper, Festus, Inquisition, Astral
- **Druid**: Moon, Spores, Dreams, Stars, Land, Wildfire, Shadows, Sea, Unbroken, Dragons
- **Fighter**: Champion, Battle Master, Eldritch Knight, Psi Warrior, Samurai, Cavalier, Rune Knight, Arcane Archer, Echo Knight, Couatl Herald, Steel Hawk, Blade Breaker
- **Monk**: Shadow, Mercy, Elements, Sun Soul, Kensei, Ascendant Dragon, Astral Self, Drunken Master, Open Hand, Prophet, Celestial, Aether
- **Paladin**: Devotion, Glory, Ancients, Vengeance, Conquest, Watchers, Redemption, Hearth, Zeal
- **Ranger**: Gloom Stalker, Fey Wanderer, Hunter, Horizon Walker, Swarmkeeper, Monster Slayer, Beast Master, Drakewarden, Winter Trapper, Rocborne
- **Rogue**: Assassin, Soulknife, Inquisitive, Mastermind, Thief, Swashbuckler, Phantom, Arcane Trickster, Scout, Umbral Binder, Misfortune Bringer, Runetagger, Grim Surgeon
- **Sorcerer**: Draconic, Shadow Magic, Wild Magic, Aberrant, Storm, Clockwork, Divine Soul, Light Weaver, Frost, Desert Soul
- **Warlock**: Fiend, Celestial, Archfey, Hexblade, Great Old One, Fathomless, Genie, Undead, Astral Griffon, Many, Mother of Sorrows
- **Wizard**: Abjurer, Diviner, Bladesinging, War Magic, Evoker, Illusionist, Order of Scribes, Shadow Arcane Tradition, Chronurgy, Graviturgy, Materializer, Wand Lore
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
- Shadow Magic Hound of Ill Omen: save disadvantage (all 110+ spell save sites), start-of-turn psychic damage (half sorcerer level), hound death cleanup
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
- Storm Herald Storm Soul (passive resistance: desert=fire, sea=lightning, tundra=cold)
- Celestial Warlock Radiant Soul (radiant resistance at L6, +CHA to one fire/radiant spell damage roll per turn)
- Scout Survivalist (Nature+Survival proficiency+expertise), Superior Mobility (+10ft speed at L9), Ambush Master (L13: first hit in round 1 marks target for team-wide advantage)
- Swashbuckler Rakish Audacity (+CHA initiative, solo-engagement SA), Master Duelist (L17 miss reroll with advantage 1/SR)
- Inquisitive Eye for Weakness (+3d6 SA at L17 vs studied target); Insightful Fighting integrated as SA qualification path (fixed double-dip bug)
- Gloom Stalker Dread Ambusher (L3: +WIS initiative, +10ft round 1, extra attack with +1d8 on first turn)
- Aberrant Mind Psychic Defenses (advantage on charm/frighten saves at 12 spell save sites)
- Druid L20 Archdruid Evergreen Wild Shape (regain 1 Wild Shape use on initiative if at 0)
- Gunslinger White Hat Lay Down the Law (Risk Die temp HP + retaliation reaction)
- College of Dance Dazzling Footwork (Unarmored Defense 10+DEX+CHA, +10ft speed, Bardic Die melee damage), Tandem Footwork (BI die to initiative for allies), Leading Evasion (L14 DEX save extends to nearby allies)
- Mother of Sorrows Sickening Revenge (L6 EOT CON save poison), Touch of Sorrow (L14 paralysis on hit)
- College of Shadow Shade Step (teleport on BI grant), Night Music (L14 reaction frighten)
- Monster Slayer Supernatural Defense (+1d6 saves vs prey), Slayer's Counter (L15 reaction attack auto-succeeds save)
- Rune Knight Runic Juggernaut (L18 Huge + d10 + reach), Runic Shield (reaction reroll), Master of Runes (double invoke pool)

### Feats with Combat Logic
Origin feats: alert, crafter, healer, lucky, magic_initiate, musician, savage_attacker, skilled, tavern_brawler, tough
General feats: actor, athlete, charger, chef, crossbow_expert, crusher, defensive_duelist, dual_wielder, durable, elemental_adept, fey_touched, great_weapon_master, heavily_armored, heavy_armor_master, inspiring_leader, keen_mind, lightly_armored, mage_slayer, martial_weapon_training, medium_armor_master, moderately_armored, mounted_combatant, observant, piercer, poisoner, polearm_master, resilient, ritual_caster, sentinel, shadow_touched, sharpshooter, shield_master, skill_expert, skulker, slasher, speedy, spell_sniper, telekinetic, telepathic, war_caster, weapon_master
Fighting Style feats: archery, blind_fighting, defense, dueling, great_weapon_fighting, interception, protection, thrown_weapon_fighting, two_weapon_fighting, unarmed_fighting
Epic Boon feats: combat_prowess, dimensional_travel, energy_resistance, fate, fortitude, irresistible_offense, recovery, skill, speed, spell_recall, the_night_spirit, truesight

**Fully Implemented Feat Combat Mechanics:**
- **Elemental Adept** (PHB 2024 para 7610): Resistance bypass in `apply_damage` for Acid/Cold/Fire/Lightning/Thunder. Dice floor of 2 in `roll_single_attack_damage_die` for spell damage. Type chosen via Shift+P menu, persisted to account.
- **Mage Slayer Guarded Mind** (PHB 2024 para 7693): Auto-succeed INT/WIS/CHA save 1/SR. Wired into 22 save failure sites. Short rest reset.
- **Boon of Recovery** (PHB 2024 para 7879): BA heal half max HP, 1/LR. Server handler + client menu.
- **Boon of Spell Recall** (PHB 2024 para 7882): Free spell cast 1/LR. Inserted into spell slot consumption pipeline after Signature Spells.
- **Boon of Dimensional Travel** (PHB 2024 para 7876): Blink Steps — free teleport 30ft to target after Attack or Magic action. Available from bonus action menu. Per-turn flag.
- **Boon of Fate** (PHB 2024 para 7877): 2d4 bonus on ally save failures within 60ft. Smart-spend wired into 22 save sites (full extended save chain including Disciplined Survivor and Stroke of Luck). 1/SR reset.
- **Boon of Energy Resistance**: Not in source files (confirmed search of PHB 2024 + Basic Rules). Removed from TODO.

**Batch 2026-04-10 additions:**
- **GWM Proficiency Damage** (PHB 2024 para 7624-7625): Heavy weapon hit adds proficiency bonus damage. Gated on feat + Heavy + proficient + non-ranged.
- **Sentinel Guardian** (PHB 2024 para 7718-7720): Auto-resolved reaction OA when creature within 5ft attacks a different target. Halt (speed 0 on hit). Wired into all 3 attack paths (player/bot/monster).
- **Crusher Crit Advantage** (PHB 2024 para 7579): On bludgeoning crit, all attacks vs target have advantage until start of attacker's next turn.
- **Slasher Crit Disadvantage** (PHB 2024 para 7597): On slashing crit, target has disadvantage on attacks until start of attacker's next turn.
- **War Caster Concentration Advantage** (PHB 2024 para 7840): Proper advantage on concentration saves (was +5 approximation, now dual d20).
- **Skulker Sniper** (PHB 2024 para 7783): Missing with ranged attack while Hidden doesn't reveal. Reveal deferred to hit.
- **Observant +5 Passive** (PHB 2024 para 7696): +5 to passive Perception in `get_passive_perception`.
- **Interception Fighting Style** (PHB 2024 para 7864): Reaction reduces damage to adjacent ally by 1d10+prof. Auto-resolved.
- **Protection Fighting Style** (PHB 2024 para 7868): Reaction imposes disadvantage on attack vs adjacent ally. Requires shield. Auto-resolved before Elusive override.

**Batch 2026-04-10 continued (commit c9174d7):**
- **Crusher Push Size Check** (PHB 2024 para 7579): Push only works if target is no more than one size larger.
- **Slasher Hamstring Expiry** (PHB 2024 para 7597): -10ft speed now properly expires at start of attacker's next turn via `slasher_hamstring_active/source_id` tracking.
- **Piercer Non-Crit Reroll** (PHB 2024 para 7707): Once per turn on piercing hit, reroll lowest damage die (must use new roll). Wired in `roll_attack_damage_natural` before Savage Attacker.
- **Musician Origin Feat**: Grant Heroic Inspiration to prof+CHA allies within 30ft at battle start and short rest.
- **Chef Feat** (PHB 2024 para 7568): Extra 1d8 HP to up to 4+prof allies during short rest.
- **Hex Warrior** (Xanathar's paras 2275-2277): Hexblade Warlocks use highest of STR/DEX/CHA for non-two-handed melee attacks.
- **Shield Master +2 DEX Save** (PHB 2024 para 7796): Shield AC bonus added to DEX saves in `get_save_bonus`.
- **Shield Master Interpose** (PHB 2024 para 7797): Reaction on successful DEX save for half damage → take 0 damage. Costs reaction, only fires if no Evasion.
- **Athlete Free Stand** (PHB 2024 para 7557): Standing from prone costs 0 movement instead of half speed.

**Batch 2026-04-10 continued (commit df369e4):**
- **Central AoE Spell Save Path — Full Save Failure Chain**: The single central save-damage resolution path (~line 2410 in battle_manager.nvgt) that handles ALL standard multi-target damage-save spells (Fireball, Cone of Cold, Lightning Bolt, etc.) now has the complete save failure reaction chain: Indomitable Might STR floor → Arcane Deflection → Flash of Genius → Maverick Spirit → Mage Slayer Guarded Mind → Boon of Fate → Stroke of Luck. Covers all spells routed through the generic save-for-half pipeline.
- **Power Surge on Save-Damage Path** (PHB 2024 War Magic L6): War Magic Wizards now apply Power Surge bonus force damage (level/2, min 1) to save-based spell damage on the central AoE path. Previously only fired on spell attack hits in `finalize_roll_result`.

**Batch 2026-04-10 continued (mechanics batch):**
- **Save Failure Chain wired to 15 individual spell handlers**: Finger of Death, Disintegrate, Blight, Cone of Cold, Cloudkill, Call Lightning, Chain Lightning, Meteor Swarm, Vitriolic Sphere, Flame Strike (damage chain: Arcane Deflection → Flash of Genius → Maverick Spirit → Boon of Fate → Stroke of Luck). Blindness/Deafness, Slow, Polymorph, Evard's Black Tentacles, Feeblemind (condition chain: adds Disciplined Survivor + Mage Slayer where applicable).
- **Druid Beast Spells L18** (PHB 2024 para 4449): L18+ Druids can now cast spells while in Wild Shape form. `beast_spells_active` flag bypass in `handle_cast`.
- **Paladin Abjure Foes L9** (PHB 2024 para 5655-5657): Channel Divinity Magic action. Auto-targets nearest CHA mod (min 1) hostiles within 60ft. WIS save or Frightened. Full save failure chain. Client menu entry for all Paladins L9+.
- **Paladin Channel Divinity Uses Fix**: Paladins now correctly receive 2 CD uses at L3+ (was 0 — init was missing from character_data.nvgt). Fixes Sacred Weapon, Vow of Enmity, Nature's Wrath, and all CD features.
- **Save Failure Chain wired to 7 more spell handlers** (batch 3): Ice Storm, Circle of Death, Harm, Blade Barrier, Moonbeam (damage chain), Stinking Cloud (condition chain).
- **Save Failure Chain wired to final 6 spell handlers** (batch 4): Sickening Radiance (CON, condition chain — exhaustion), Phantasmal Force (INT, damage chain), Enlarge/Reduce (CON, condition chain), Sunbeam (CON, condition chain — Blinded), Sunburst (CON, condition chain — Blinded), Insect Plague (CON, damage chain). All individual spell save sites now covered (28+ total including central AoE path).
- **Coming Soon subclass labels fixed**: Removed stale "Coming Soon" from 4 shipped subclasses (Shadow Gnawer, College of Mercantile, Keeper Domain, Shadow Arcane Tradition). 9 truly unfinished subclasses retain the label.
- **TODO_SOURCE_ACCURACY.md sweep**: Marked 8 stale DEFERRED/PARTIAL items as RESOLVED (Beast Spells, Abjure Foes, Disciplined Survivor, Hex Warrior, Arcane Deflection save+restriction, Flash of Genius coverage, Druidic auto-prepare).
- **Save Failure Chain wired to 5 critical control spells** (batch 5): Sleep (WIS, Incapacitated), Tasha's Hideous Laughter (WIS, Incapacitated+Prone), Confusion (WIS, Confused), Flesh to Stone (CON, Restrained/Petrifying), Otto's Irresistible Dance (WIS, Incapacitated). WIS saves include Mage Slayer; CON saves omit it.
- **Save Failure Chain wired to 18 remaining unchained spell save sites** (batch 6 — COMPLETE COVERAGE): Condition spells: Bestow Curse (WIS), Faerie Fire (DEX), Bane (CHA, completed partial chain), Earthquake (DEX), Sleet Storm (DEX), Otiluke's Resilient Sphere (DEX), Divine Word (WIS). Damage spells: Vicious Mockery (WIS), Holy Word (WIS), Storm Sphere (STR), Gust of Wind (STR), Poison Spray (CON), Sacred Flame (DEX), Acid Splash (DEX), Contact Other Plane (INT), Mind Sliver (INT), Thunderclap (CON), Word of Radiance (CON). Plus Prismatic Wall (DEX) and Befuddlement (INT, fixed partial chain). **All spell save sites in the codebase now have reaction chains.**
- **TODO_SOURCE_ACCURACY.md second sweep**: Marked stale entries as RESOLVED — all 7 metamagic pipeline effects, Cunning Strike L5/L11/L14, Stroke of Luck save chain, all Fighting Style feats, all Epic Boon feats, 12+ complex feat effects (Polearm Master, Shield Master Interpose, Mage Slayer, Inspiring Leader, Elemental Adept, Telekinetic, Sharpshooter, Spell Sniper, Poisoner, Resilient, Charger, Fey/Shadow Touched). Flash of Genius coverage updated to 46+ sites.
- **Shield Master Push/Prone Choice** (PHB 2024 para 7797): Free-action toggle in B-menu lets player choose Push 5ft or Knock Prone for the automatic shove rider on melee hits. Server handler, combatant field, client sub-menu, battle_manager push logic all wired.
- **Telepathic Free Detect Thoughts** (PHB 2024 para 7820): 1/LR free cast via grant_free_cast, matching Fey Touched/Shadow Touched pattern.
- **Sharpshooter -5/+10 clarified**: PHB 2024 removed the -5/+10 trade (was 2014 only). TODO updated.
- **Medium Armor Master confirmed**: Already fully implemented (+3 DEX cap + stealth advantage). TODO updated.
- **Wizard Spell Mastery + Signature Spells designation** (PHB 2024 paras 8629-8635): Full Shift+P menu flow — L18 Wizards pick L1+L2 spells for at-will casting, L20 Wizards pick two L3 spells for 1/SR free casts. Server validates spell level, persists to account JSON, restores on reconnect via character_sheet fields. Client filters SPELL_CATALOG by level+class for the selection menus.
- **Order's Demand duration tracking** (Tasha's Order Domain): Charm now properly expires at end of caster's next turn via 2-tick counter in advance_turn. Also breaks on damage via apply_damage check. Previously charmed indefinitely.
- **Monk Deflect Attacks Redirect** (PHB 2024 para 5339): When Deflect Attacks reduces damage to 0, Monk auto-spends 1 Focus Point to redirect 2d8+DEX force damage at the attacker (DEX save negates). Uses existing deflect_attacks_reduced_to_zero flag as gate.

**Batch 3 subclass features (2026-04-11):**
- **Battle Master Maneuvers** (8 new, added to existing Trip Attack + Precision Attack + Riposte):
  - Menacing Attack — WIS save or Frightened, consumes superiority die
  - Goading Attack — WIS save or disadvantage on attacks vs others for 2 turns
  - Pushing Attack — STR save or push 15ft, consumes superiority die
  - Disarming Attack — STR save or weapon_jammed (must use Utilize action to unjam)
  - Distracting Strike — marks target, next ally attack has advantage
  - Sweeping Attack — on hit, deals die damage to adjacent creature
  - Parry — reaction, reduce melee damage by d8 + higher of STR/DEX mod, consumes superiority die
  - Rally — BA, nearest ally within 30ft gains temp HP = d8 + half Fighter level
- **Swashbuckler Panache** (L9): Action, contested CHA(Persuasion) vs WIS(Insight), on success target has disadvantage on attacks vs others + can't make OAs against panache source for 10 rounds
- **Swashbuckler Elegant Maneuver** (L13): BA, advantage on next Acrobatics/Athletics check this turn
- **Scout Sudden Strike** (L17): BA, make extra attack via flurry pattern, can benefit from SA even if already used this turn (but not vs same target)
- **Phantom Tokens of the Departed** (L9): Gain soul trinket when creature within 30ft dies (costs reaction). Trinkets grant: advantage on CON saves (+5 approx), advantage on death saves. Max trinkets = proficiency bonus.
- **Phantom Ghost Walk** (L13): BA toggle, fly 10ft + disadvantage on attacks against you. Activate costs ghost_walk_available OR consumes 1 soul trinket.
- **Storm Herald Shielding Storm** (L10): Allies within 10ft aura gain Storm Soul resistance type (desert=fire, sea=lightning, tundra=cold). Auto-applied/removed based on proximity.
- **Storm Herald Raging Storm** (L14): Auto-triggers per environment:
  - Desert: When hit by creature in aura, deals half-level fire damage (DEX save for half)
  - Sea: On weapon hit while target in aura, STR save or Prone
  - Tundra: On aura activation, nearest enemy STR save or speed=0

**Batch 4 subclass features (2026-04-11):**
- **Elegant Maneuver** (Swashbuckler L13): Wired into `request_skill_check` — grants advantage on next Acrobatics or Athletics check this turn
- **Scout Skirmisher** (Scout L3): Reaction movement in `advance_turn` — move up to half speed without provoking OAs when an enemy ends its turn within 5ft
- **Divine Soul Empowered Healing** (Divine Soul L6): Reroll below-average healing dice for 1 SP. Fires on healing spells when any die rolls below its average

**Batch 5 subclass features (2026-04-11):**
- **Telekinetic Thrust** (Psi Warrior L7): On Psionic Strike hit, target makes STR save or pushed 10ft + knocked Prone
- **Celestial Resilience** (Celestial Warlock L10): Distributes temp HP to up to 5 allies at battle start (level + CHA mod to self, half that to allies)
- **Drunkard's Luck** (Drunken Master L11): Cancel disadvantage on attacks or ability checks for 2 FP

**Batch 6 subclass features (2026-04-11):**
- **Starry Form Archer** (Circle of Stars L2): BA ranged spell attack dealing 1d8+WIS radiant damage (scales to 2d8 at L10). Available while in Starry Form
- **Starry Form Chalice** (Circle of Stars L2): After casting a healing spell, auto-heal an ally for 1d8+WIS HP. Available while in Starry Form

**Batch 7 subclass features (2026-04-11):**
- **Mantle of Majesty** (Glamour Bard L6): Concentration, free Command spell each turn as BA without expending a spell slot
- **Unbreakable Majesty** (Glamour Bard L14): CHA save or attacker's attack is cancelled and must choose a new target or waste the attack
- **Rune Knight Runes** (Rune Knight L3+): 6 runes with passive effects and invocable abilities (1/SR each):
  - Cloud Rune — passive: advantage on Deception/Sleight of Hand; invoke: redirect attack to different creature within 30ft
  - Fire Rune — passive: double proficiency on tool checks; invoke: extra 2d6 fire + Restrained (STR save at end of turn)
  - Frost Rune — passive: advantage on Animal Handling/Intimidation; invoke: +2 STR/CON saves for 10 min
  - Stone Rune — passive: advantage on Insight/darkvision 120ft; invoke: WIS save or Charmed (incapacitated, 0 speed)
  - Hill Rune — passive: advantage vs Poison/resistance to poison damage; invoke: resistance to B/P/S for 1 min
  - Storm Rune — passive: advantage on Arcana/can't be surprised; invoke: advantage or disadvantage on any attack/save/check within 60ft

**Batch 8 subclass features (2026-04-11):**
- **Psionic Sorcery** (Aberrant Mind L6): Cast psionic spells using SP instead of spell slots (1 SP per spell level), no verbal/somatic components required
- **Hold the Line** (Cavalier L10): Opportunity attacks reduce target's speed to 0 on hit for the rest of the turn
- **Swarmkeeper Ranger** (full subclass):
  - Gathered Swarm (L3) — 3 modes on weapon hit: deal 1d6 piercing, push target 15ft (STR save), or move self 5ft without OA
  - Writhing Tide (L7) — BA hover with 10ft fly speed for 1 min
  - Mighty Swarm (L11) — Gathered Swarm upgrade: damage becomes 1d8, push knocks Prone on failed save, self-move grants half cover
  - Swarming Dispersal (L15) — reaction on taking damage: become swarm, resist damage, teleport 30ft

**Batch 9 subclass features (2026-04-11):**
- **Redirect Attack** (Drunken Master L6): When an enemy misses the Monk with a melee attack, auto-redirect that attack to another enemy within 5ft of the Monk
- **Cosmic Omen** (Circle of Stars L6): At dawn/long rest, roll a die to determine Weal or Woe. Weal: reaction to add 1d6 to an ally's attack roll. Woe: reaction to subtract 1d6 from an enemy's attack roll
- **Aura of the Guardian** (Redemption Paladin L7): Reaction to absorb damage dealt to an ally within 10ft, taking it unreduced in place of the ally

**Batch 10 subclass features (2026-04-11):**
- **Rune Knight** (Fighter):
  - Cloud Rune invoke — redirect incoming attack to a different creature within 30ft, auto-fires
  - Stone Rune invoke — WIS save or charmed + incapacitated, end-of-turn saves to break free
  - Storm Rune invoke — BA prophetic state, reaction to force advantage/disadvantage on nearby rolls
  - Runic Shield (L7) — reaction forces attacker to reroll and use lower result, PB uses/LR
  - Master of Runes (L15) — double invoke pool; each rune gets 2 uses instead of 1 per LR
- **Stars Druid** (Circle of Stars):
  - Twinkling Constellations (L10) — form swap at turn start with player prompt in advance_turn
  - Cosmic Omen (L6) — weal/woe smart-spend in attack resolution, reaction auto-fires d6 add/subtract
  - Star Map free Guiding Bolt — tracked via free_cast system (Prof uses/LR, no spell slot consumed)
- **Sun Soul** (Monk):
  - Radiant Sun Bolt (L3) — full Attack action replacement at 30ft range, 1d4+DEX radiant, both player and bot paths
  - Searing Arc Strike (L6) — post-Attack BA, spend 2+ ki for Burning Hands with scaling damage
  - Searing Sunburst (L11) — AoE action 20ft-radius at 150ft, 2d6 radiant CON save, +2d6 per ki (up to 3)

**Batch 11 subclass features (2026-04-11):**
- **Psi Warrior** (Fighter):
  - Protective Field (L3) — ally-scan auto-fire within 30ft, psionic die + INT mod damage reduction
  - Guarded Mind (L10) — auto-clear Charmed/Frightened at turn start by spending psionic die
- **Emissary of Redemption** (Redemption Paladin L20): per-creature exclusion tracked via emissary_exclusion_ids string
- **Restore Balance** (Clockwork Soul L1): wider scope — ally-scan auto-fire within 60ft on any d20 test with advantage/disadvantage
- **Intoxicated Frenzy** (Drunken Master L17): multi-target Flurry of Blows with different-target enforcement, up to 3 additional strikes
- **Deflect Attacks redirect** (Monk L3): on damage reduced to 0, redirect deals 2x Martial Arts die + DEX mod of original damage type

**Batch 12 subclass features (2026-04-11):**
- **Eyes of the Dark** (Shadow Magic Sorcerer L3): SP-casting Darkness (2 SP) with see-through flag so caster sees through own Darkness
- **Blade Flourish variants** (College of Swords Bard L3): all 3 wired — Defensive (+AC), Slashing (AoE), Mobile (push + reaction movement to pushed target)
- **Mobile Flourish reaction movement**: reaction to move up to walking speed toward pushed target after Flourish push
- **Clockwork Cavalcade dispel** (Clockwork Soul L18): breaks concentration on spells L6 or lower on affected creatures
- **Rapid Strike** (Samurai L15): forgo advantage on one attack to gain an extra attack, 1/turn
- **Sorcery Incarnate multi-metamagic** (Sorcerer L7): 2 metamagic options per spell while Innate Sorcery is active
- **Arcane Archer 8 shots**: all 8 shot types (Banishing, Beguiling, Bursting, Enfeebling, Grasping, Piercing, Seeking, Shadow) with full effects, saves, and L18 upgrades
- **Supernatural Defense** (Monster Slayer L7): +1d6 to saves when Slayer's Prey target forces a save, wired in get_save_bonus
- **Curving Shot** (Arcane Archer L7): BA redirect on ranged miss to different target within 60ft
- **Magic Arrow** (Arcane Archer L7): arrows treated as magical at L7+ in apply_damage

**Batch 13 subclass features (2026-04-11):**
- **College of Dance** (Bard, full subclass):
  - Dazzling Footwork (L3) — Unarmored Defense (10+DEX+CHA), +10ft speed, Bardic Die damage rider on melee hit 1/turn
  - Tandem Footwork (L6) — BI die bonus to initiative for self and allies within 30ft
  - Inspiring Movement (L6) — reaction grants BI die bonus to ally save within 60ft
  - Leading Evasion (L14) — on DEX save success, nearby allies within 5ft also take no damage
- **Mother of Sorrows** (Warlock, Ebon Tides):
  - Sickening Revenge (L6) — end-of-turn CON save or take poison damage
  - Touch of Sorrow (L14) — on-hit paralysis rider with CON save
- **College of Shadow** (Bard, Ebon Tides):
  - Shade Step — teleport rider on Bardic Inspiration grant
  - Night Music (L14) — reaction frighten trigger after casting, WIS save or Frightened
- **Drunken Master cleanup** — Redirect Attack (L6) rewritten as auto-resolve reaction on melee miss, Drunkard's Luck auto-cancel disadvantage for 2 FP

**Batch 14 subclass features (2026-04-11):**
- **Leap to Your Feet** (Drunken Master L6): prone stand costs 5ft instead of half speed
- **Step of the Wind ally carry** (Monk L10 Heightened Focus): ally-carry targeting prompt when spending FP on Step of the Wind
- **Runic Juggernaut** (Rune Knight L18): Giant's Might upgrades to Huge size, d10 damage die, +5ft reach
- **Greater Divine Intervention** (Cleric L20): full-party buff action with mass heal + condition removal + temp HP
- **Nature Magician** (Druid L20): convert Wild Shape uses to spell slot with player prompt, 1/long rest
- **Distant Strike** (Fey Wanderer/Horizon Walker L11): 10ft teleport before each attack, extra attack on hitting 2+ different creatures
- **Slayer's Counter** (Monster Slayer L15): reaction weapon attack when prey forces save; hit auto-succeeds the save
- **Deft Explorer Expertise** (Ranger L2): Expertise in one skill with player choice prompt
- **Ferocious Charger** (Cavalier L15): STR save or Prone after 10ft+ straight-line move before attack, 1/turn

**Previously implemented:** combat_prowess (+1d6 weapon miss → hit 1/turn), fortitude (+40 HP), irresistible_offense (+2d10 force 1/turn), skill (+1d10 ability check 1/turn), speed (+30ft), the_night_spirit (300ft darkvision + see invisible), truesight (Truesight 60ft)

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

### Short Rest System (Between Waves)

`apply_short_rest()` fires between waves in both endless and wave modes:
- 25% max HP heal
- Fighter: Action Surge + Second Wind resets
- Warlock: Pact Magic slot recovery
- Wizard: Arcane Recovery + Signature Spells
- Druid: Wild Shape resets
- Battle Master: Superiority Dice resets
- Monk: Focus Points resets
- Bard: Bardic Inspiration resets
- Cleric/Paladin: Channel Divinity resets
- Arcane Archer: Arcane Shot resets
- Sorcerer: Sorcerous Restoration (floor(level/2) SP, 1/LR)
- Clear conditions and end concentration
- **Concentration cleanup**: calls `clear_concentration_effects(c)` BEFORE clearing `is_concentrating`, properly removing per-target spell flags (heat_metal_disadv, greater_invisibility, bestow_curse, enlarge, shield_of_faith, beacon_of_hope, etc.)

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

- Level-up flow: players choose new spells, cantrips, subclass (at level 3), fighting style (Fighter L1/Paladin L2/Ranger L2), pact boon (Warlock L3), eldritch invocations (Warlock L1+, multi-pick with level/pact filtering), and metamagic options (Sorcerer L2/L10/L17) interactively. Server detects needs in `send_level_up_choices`, client shows menus in `show_level_up_screen`, server persists in `level_up_response` handler. Metamagic gated both server-side (validation) and client-side (menu filtering via `my_metamagic_choices` synced in broadcast_state).

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


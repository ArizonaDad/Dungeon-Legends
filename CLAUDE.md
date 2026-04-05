# Dungeon Legends - D&D 5e Battle Simulator

## Project Overview
Multiplayer accessible D&D 5e combat arena for blind players built in **NVGT** (NonVisual Gaming Toolkit, AngelScript-like). Players create characters (33 species, 13 classes, 16 backgrounds, 38 weapons, 53 spells) and fight in turn-based combat with full TTS and HRTF spatial audio. Supports PvP Arena, Wave Survival, and Boss Rush modes.

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
| `Server/combat/monster_data.nvgt` | 20 monster definitions (Kobold through Pit Fiend) |
| `Server/combat/wave_system.nvgt` | 3 wave scenarios, `spawn_wave()` |
| `Server/combat/spell_data.nvgt` | 53 spell definitions (34 cantrips + 19 leveled), spell helpers |
| `Server/progression.nvgt` | XP tracking, achievement system, character level progression |
| `Client/client.nvgt` | Main client entry, login, lobby menus, character viewing, first-time login flow |
| `Client/net.nvgt` | Network message dispatcher + connection, character_data restore, daily bonus handler |
| `Client/combat/combat_ui.nvgt` | Combat game loop, action/bonus action menus, scanning, targeting, roll prompts, tab focus, level-up screen |
| `Client/combat/character_creator.nvgt` | Character creation with back-navigation (race->class->level->abilities->weapon->spells) |
| `Client/combat/spell_menu.nvgt` | Spell list building, selection menu, class spell availability check |
| `common/message_types.nvgt` | 70+ network message type constants |
| `common/combat_constants.nvgt` | D&D constants (conditions, damage types, abilities, sizes, roll types) |

## Main Menu
- **Adventure**: Create an adventure lobby with persistent progression (XP, achievements, level-ups)
- **Sandbox**: Create a sandbox lobby for free-build characters (level 1-20, no persistence)
- Adventure characters can be used in sandbox mode as fallback
- First-time login prompts character creation automatically
- Daily login bonuses: streak-based XP (50-200 XP, resets after day 7)

## Combat System

### Turn Structure (D&D 5e 2024)
- Move + Action + Bonus Action + Reaction per turn
- Initiative rolled at battle start (d20 + DEX mod), all rolls announced to all players
- All rolls require the specific prompted player to press R or Enter (other players cannot roll for them)
- All roll results broadcast to ALL players with full context and audio cues (nat 20/1)

### Attack Resolution
- Separate roll to hit (d20 + ability mod + proficiency vs AC), then roll for damage
- Advantage/disadvantage from conditions (prone, paralyzed, dodging, etc.)
- **Extra Attack**: Fighters (level 5+) and other martial classes chain additional attacks
- Out-of-range attacks show distance and range info to the player
- Finesse weapons use higher of STR/DEX
- Ranged disadvantage when hostile within 5ft
- Line of sight required (`can_see` check)

### Spell System
- 53 spells fully resolved server-side via `handle_cast()`
- Spell menu shows range and concentration status for each spell
- Save-based damage (DEX/CON/WIS saves, half on success)
- Attack-roll spells (spell attack bonus vs AC)
- AoE damage (Fireball, Thunderwave, etc.)
- Healing spells with scaling
- Utility spells (Shield, Hold Person, Haste, Banishment, Bless, Misty Step)
- Magic Missile auto-hit
- Cantrip scaling at levels 5/11/17
- Concentration management (drop old when casting new)
- Spell slot consumption (lowest available >= spell level)
- Spell menu shows level (Cantrip/Level N) and Concentration tag for each spell

### Reroll Mechanics
- **Lucky feat**: Characters with the Lucky feat gain Luck Points equal to proficiency bonus per battle. After a failed d20 roll, prompted to spend a Luck Point to reroll with advantage (Press L / Escape). Chains after Bardic Inspiration prompt.
- **Heroic Inspiration**: Earned on any natural 20 d20 roll (players only). After a failed d20 roll, prompted to use Heroic Inspiration for a reroll (Press H / Escape). Chains after Lucky prompt. Consumed on use.
- **Prompt chain order**: Bardic Inspiration (additive) -> Lucky (reroll with advantage) -> Heroic Inspiration (reroll)

### Action Menu (F key)
- Standard actions only: Attack, Cast, Dodge, Dash, Disengage, Help, Hide, Ready, Shove, Grapple, End Turn, Status
- Attack item shows weapon range and current target distance
- Actions that cannot be performed explain why (no target, out of range, no action remaining)

### Bonus Action Menu (B key)
- **Barbarian**: Rage (advantage STR, bonus damage, physical resistance)
- **Fighter**: Action Surge (extra action), Second Wind (1d10+level healing)
- **Rogue**: Cunning Action (bonus Dash/Disengage/Hide)
- **Paladin**: Divine Smite (2d8 radiant on hit), Lay on Hands (level x 5 healing)
- **Monk**: Flurry of Blows (two unarmed strikes)
- **Bard**: Bardic Inspiration (d6 to ally's next roll)
- **Druid** (level 2+): Wild Shape
- **Any class**: Spiritual Weapon (if active)

### Audio System
- **Dual-layer audio**: Synthesized spatial cues (combat_audio.nvgt) + pre-recorded sound files (audio_manager.nvgt)
- **HRTF 3D spatial audio**: All combat sounds positioned at entity locations in 3D space
- **Music manager**: Auto-advances to next random track when one ends. Categories: menu, wait room, battle
- **Weapon sounds**: Mapped by weapon type (sword, dagger, axe, hammer, bow) with flesh impact at target
- **Spell sounds**: Mapped by damage type (fire, lightning, cold/water, shadow/necrotic, wind/thunder, arcane/radiant)
- **Footsteps**: Heavy armor (Fighter/Paladin/Cleric) vs grass steps, alternating variants, spatially positioned
- **Kill streaks**: First Blood, Double Kill (2 in one turn), Triple Kill (3 in one turn), kill_streak1-9 (4+ total)
- **Healing sounds**: Small heals (random from 3 variants), large heals (15+ HP)
- **Buff/debuff sounds**: Different sounds for positive vs negative conditions
- **Announcements**: Low health warning (25% HP), level-up stinger, wave/boss stingers, victory/defeat
- **121 sound files**: Weapon impacts, spell effects, music tracks, footsteps, kill announcements, UI sounds

### Monster AI
- Move toward nearest conscious player
- Attack when in weapon range
- Extra attacks supported for multiattack monsters
- Opportunity attacks on movement
- Auto-resolved rolls (no player input needed)
- 10-second safety timeout forces turn end if AI stalls

### Battle Modes
- **PvP**: Last player standing wins
- **Wave Survival**: Clear waves of monsters (Goblin Ambush, Crypt of Undead, Dragon's Challenge)
- **Boss Rush**: Defeat boss monsters

### Targeting & Scanning
- IJKL to scan directions, Caps Lock or brackets to cycle results
- Scan results show distance, direction, health status, and conditions
- Target lock (Enter) shows HP, AC, distance, direction, and conditions


### Character Persistence
- Characters saved to SQLite via account JSON data blob on creation
- Character data sent to client on login (`character_data` message)
- Client restores `created_char_*` variables from server data
- Adventure progress tracked: XP, level, achievements, kills, healing, waves cleared

### Post-Battle Flow
- Battle end detected (PvP: one standing, Wave: all monsters dead or TPK)
- Adventure mode: XP awarded (monster kills, healing, match completion, achievements)
- Level-up flow: players choose new spells, cantrips, and subclass (at level 3) interactively
- Room `started` flag reset so new games can be launched
- Client shows 5-second countdown then returns to lobby

### Character Creation
- Step-by-step wizard: Name -> Species -> Class -> Level -> Background -> Subclass -> Abilities -> Weapon -> Spells -> Summary
- 16 backgrounds: Acolyte, Artisan, Charlatan, Criminal, Entertainer, Farmer, Guard, Guide, Hermit, Merchant, Noble, Sage, Sailor, Scribe, Soldier, Wayfarer
- Each background grants: 3 ability score bonuses, an Origin feat, 2 skill proficiencies, and a tool proficiency
- **Backspace/Escape goes back** to the previous step at any point
- At the first step, Escape cancels the wizard
- Adventure mode forces level from server progression
- Subclass selection only at level 3+

## Controls (Client)
- **F**: Open action menu (Attack, Cast, Dodge, Dash, Disengage, Help, Hide, Ready, Shove, Grapple, End Turn)
- **B**: Open bonus action menu (class-specific: Rage, Action Surge, Cunning Action, etc.)
- **R/Enter**: Roll dice when prompted (only the prompted player can roll)
- **WASD**: Movement (5ft per tile)
- **IJKL**: Scan directions (north/south/west/east)
- **Caps Lock/Shift+Caps Lock**: Cycle targets from scan results
- **[/]**: Alternative target cycling
- **Enter**: Lock target
- **H**: Status readout
- **O**: Initiative order (reads top to bottom)
- **T**: Whose turn it is
- **Tab**: Switch focus forward (Game -> Chat -> Chat History)
- **Shift+Tab**: Switch focus backward (Game -> Chat History -> Chat)
- **F1**: Combat help
- **Escape x 2**: Forfeit

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

## Development
- Compile: `C:\Users\16239\Documents\games\nvgt\nvgt.exe -c Server/Server.nvgt` and `C:\Users\16239\Documents\games\nvgt\nvgt.exe -c Client/client.nvgt`
- Git repo: https://github.com/ArizonaDad/souls-mmo

# Souls MMO - D&D 5e Battle Simulator

## Project Overview
Multiplayer accessible D&D 5e combat arena for blind players built in **NVGT** (NonVisual Gaming Toolkit, AngelScript-like). Players create characters (33 species, 13 classes, 38 weapons, 53 spells) and fight in turn-based combat with full TTS and HRTF spatial audio. Supports PvP Arena, Wave Survival, and Boss Rush modes.

## Architecture
- **Client-server** model using ENet networking with JSON message passing
- **Server** (`Server/`): Authoritative state, SQLite persistence, room/user management, full combat engine
- **Client** (`Client/`): Input handling, TTS output, menu UI, network dispatcher, thin renderer
- **Common** (`common/`): Shared message type constants, combat constants, utilities

## Key Files
| File | Purpose |
|------|---------|
| `Server/Server.nvgt` | Main server entry, network loop, bot utilities |
| `Server/account.nvgt` | Account persistence (SQLite + JSON data blob) |
| `Server/rooms_Dom.nvgt` | Room/lobby creation and management |
| `Server/users _dom.nvgt` | User class, message handler dispatch, bonus action handlers |
| `Server/combat/battle_manager.nvgt` | Core combat loop: roll system, attack/spell/action resolution, monster AI, initiative, Extra Attack, battle end detection |
| `Server/combat/combat_engine.nvgt` | `combatant` class (HP, AC, abilities, conditions, spell slots), `battle` class (initiative, damage, death saves) |
| `Server/combat/character_data.nvgt` | `character_sheet` class, 13 class defaults, 33 species bonuses, 38 weapons, spell slot tables |
| `Server/combat/monster_data.nvgt` | 20 monster definitions (Kobold through Pit Fiend) |
| `Server/combat/wave_system.nvgt` | 3 wave scenarios, `spawn_wave()` |
| `Server/combat/spell_data.nvgt` | 53 spell definitions (34 cantrips + 19 leveled), spell helpers |
| `Client/client.nvgt` | Main client entry, login, lobby menus, character viewing |
| `Client/net.nvgt` | Network message dispatcher + connection, character_data restore |
| `Client/combat/combat_ui.nvgt` | Combat game loop, action menu, scanning, targeting, roll prompts |
| `Client/combat/character_creator.nvgt` | Character creation (race→class→level→abilities→weapon→spells) |
| `Client/combat/spell_menu.nvgt` | Spell list building and selection menu |
| `common/message_types.nvgt` | 60+ network message type constants |
| `common/combat_constants.nvgt` | D&D constants (conditions, damage types, abilities, sizes, roll types) |

## Combat System

### Turn Structure (D&D 5e 2024)
- Move + Action + Bonus Action + Reaction per turn
- Initiative rolled at battle start (d20 + DEX mod)
- All rolls require player to press "Roll" button (R or Enter)
- All roll results broadcast to ALL players with full context

### Attack Resolution
- Attack roll: d20 + ability mod + proficiency vs AC
- Advantage/disadvantage from conditions (prone, paralyzed, dodging, etc.)
- **Extra Attack**: Fighters (level 5+) and other martial classes chain additional attacks automatically after damage resolves
- Finesse weapons use higher of STR/DEX
- Ranged disadvantage when hostile within 5ft
- Line of sight required (`can_see` check)

### Spell System
- 53 spells fully resolved server-side via `handle_cast()`
- Save-based damage (DEX/CON/WIS saves, half on success)
- Attack-roll spells (spell attack bonus vs AC)
- AoE damage (Fireball, Thunderwave, etc.)
- Healing spells with scaling
- Utility spells (Shield, Hold Person, Haste, Banishment, Bless, Misty Step)
- Magic Missile auto-hit
- Cantrip scaling at levels 5/11/17
- Concentration management (drop old when casting new)
- Spell slot consumption (lowest available >= spell level)

### Class Features (Bonus Actions)
- **Barbarian**: Rage (advantage STR, bonus damage, physical resistance)
- **Fighter**: Action Surge (extra action), Second Wind (1d10+level healing)
- **Rogue**: Cunning Action (bonus Dash/Disengage/Hide)
- **Paladin**: Divine Smite (2d8 radiant on hit), Lay on Hands (level×5 healing)
- **Monk**: Flurry of Blows (two unarmed strikes)
- **Bard**: Bardic Inspiration (d6 to ally's next roll)

### Monster AI
- Move toward nearest conscious player
- Attack when in weapon range
- Extra attacks supported for multiattack monsters
- Opportunity attacks on movement
- Auto-resolved rolls (no player input needed)

### Battle Modes
- **PvP**: Last player standing wins
- **Wave Survival**: Clear waves of monsters (Goblin Ambush, Crypt of Undead, Dragon's Challenge)
- **Boss Rush**: Defeat boss monsters

### Character Persistence
- Characters saved to SQLite via account JSON data blob on creation
- Character data sent to client on login (`character_data` message)
- Client restores `created_char_*` variables from server data

### Post-Battle Flow
- Battle end detected (PvP: one standing, Wave: all monsters dead or TPK)
- Room `started` flag reset so new games can be launched
- Client shows 5-second countdown then returns to lobby

## Controls (Client)
- **F**: Open action menu (Attack, Cast, Dodge, Dash, Disengage, Help, Hide, Ready, Shove, Grapple, class features, End Turn)
- **R/Enter**: Roll dice when prompted
- **WASD**: Movement (5ft per tile)
- **IJKL**: Scan directions (north/south/west/east)
- **[/]**: Cycle targets from scan results
- **Enter**: Lock target
- **H**: Status readout
- **O**: Initiative order
- **Tab**: Switch chat/history
- **F1**: Combat help
- **Escape×2**: Forfeit

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
- All combat actions route through `users_dom.nvgt` → `battle_manager` methods
- Actions: attack, move, dodge, dash, disengage, cast, help, hide, shove, grapple, set_target
- Bonus actions handled inline in `users_dom.nvgt` with combatant validation
- Scan direction handled inline in `users_dom.nvgt`

## Development
- Compile: `c:\nvgt\nvgt.exe -c Server/Server.nvgt` and `c:\nvgt\nvgt.exe -c Client/client.nvgt`
- Git repo: https://github.com/ArizonaDad/souls-mmo

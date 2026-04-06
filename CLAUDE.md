# Dungeon Legends - D&D 5e Battle Simulator

## Project Overview
Multiplayer accessible D&D 5e combat arena for blind players built in **NVGT** (NonVisual Gaming Toolkit, AngelScript-like). Players create characters (33 species, 13 classes, 16 backgrounds, 38 weapons, 86 spells) and fight in turn-based combat with full TTS and HRTF spatial audio. Supports PvP Arena, Wave Survival, Boss Rush, and Endless Survival modes. Features 40+ achievements, glory shop, daily dungeons, leaderboards, loot system, trading, prestige, guilds, and multi-phase boss fights.

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
| `Server/combat/spell_data.nvgt` | 68 spell definitions (34 cantrips + 34 leveled), spell helpers |
| `Server/progression.nvgt` | XP tracking, achievement system, character level progression, prestige system, glory points |
| `common/loot_data.nvgt` | Item catalog (35 items), loot generation, rarity tiers, inventory helpers |
| `common/consumable_data.nvgt` | Consumable catalog (16 items), modifier system, inventory helpers |
| `Client/client.nvgt` | Main client entry, login, lobby menus, character viewing, first-time login flow |
| `Client/net.nvgt` | Network message dispatcher + connection, character_data restore, daily bonus handler |
| `Client/combat/combat_ui.nvgt` | Combat game loop, action/bonus action menus, scanning, targeting, roll prompts, tab focus, level-up screen |
| `Client/combat/character_creator.nvgt` | Character creation with back-navigation (race->class->level->abilities->weapon->spells) |
| `Client/combat/spell_menu.nvgt` | Spell list building, selection menu, class spell availability check |
| `common/message_types.nvgt` | 80+ network message type constants |
| `common/combat_constants.nvgt` | D&D constants (conditions, damage types, abilities, sizes, roll types) |

## Main Menu
- Menu header displays player level, gold, and glory points
- 7 top-level categories: Play, Character, Social, Shop, Challenges, Settings, Quit
- **Play**: Play Adventure (Create Game / Join Game), Play Sandbox Mode (Create Game / Join Game)
- **Character**: Create Character, View Character (with proficiency bonus, saving throws, spell save DC), Inventory, My Stats, Prestige (level 20+)
- **Social**: Friends, Guild (create/join, max 20 members, guild chat, invite, view members/glory), Check Who's Online
- **Shop**: Item Shop (potions, scrolls, throwables with gold), Glory Shop (titles and exclusive items with glory)
- **Challenges**: Daily Dungeon (featured dungeon with bonus rewards), Weekly Challenges, Leaderboards
- **Settings**: Volume Up/Down, TTS Speed Up/Down, About. All settings persisted to disk via `save_settings()`/`load_saved_settings()`
- First-time login prompts adventure character creation automatically (no sandbox prompt)
- Daily login bonuses: streak-based XP (50-200 XP, resets after day 7)
- Settings (volume, TTS speed) saved on change and restored on launch

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
- 68 spells fully resolved server-side via `handle_cast()`
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
- **Barbarian**: Rage + Berserker Frenzy (bonus melee attack while raging)
- **Fighter**: Action Surge, Second Wind + Battle Master Maneuvers (Trip/Precision/Riposte) + Psi Warrior Strike
- **Rogue**: Cunning Action + Soulknife Psychic Blades
- **Paladin**: Divine Smite, Lay on Hands + Channel Divinity (Sacred Weapon, Vow of Enmity, Inspiring Smite, Nature's Wrath)
- **Cleric**: Channel Divinity (Preserve Life, War Priest Attack)
- **Monk**: Flurry of Blows + Shadow Step, Hands of Healing, Elemental Burst
- **Bard**: Bardic Inspiration + Mantle of Inspiration (Glamour)
- **Warlock**: Healing Light (Celestial), Fey Presence (Archfey)
- **Druid** (level 2+): Wild Shape
- **Any class**: Spiritual Weapon (if active)

### Subclass Combat Features (52 subclasses across 13 classes)
- **Fighter**: Champion (crit 19+), Battle Master (superiority dice maneuvers), Eldritch Knight (spellcasting + War Magic), Psi Warrior (force damage strikes)
- **Barbarian**: Berserker (Frenzy bonus attacks), Wild Heart (beast bonuses), World Tree (temp HP on rage), Zealot (radiant fury damage)
- **Rogue**: Assassin (auto-crit first round), Thief (Fast Hands), Arcane Trickster (spellcasting + Magical Ambush), Soulknife (psychic blades)
- **Paladin**: Devotion (Sacred Weapon), Vengeance (Vow of Enmity advantage), Glory (Inspiring Smite temp HP), Ancients (Nature's Wrath restrain)
- **Cleric**: Life (healing bonus + Preserve Life), Light (Warding Flare), Trickery (Invoke Duplicity), War (War Priest attacks)
- **Wizard**: Evoker (Sculpt Spells ally protection), Diviner (Portent forced rolls), Abjurer (Arcane Ward), Illusionist (improved DC)
- **Bard**: Lore (Cutting Words), Valor (Combat Inspiration + Extra Attack), Dance (Dazzling Footwork AC), Glamour (Mantle of Inspiration)
- **Monk**: Open Hand (push/prone/no reactions), Shadow (Shadow Step teleport), Mercy (Hands of Healing), Elements (elemental burst)
- **Ranger**: Hunter (Colossus Slayer + Horde Breaker), Beast Master (Primal Companion), Gloom Stalker (Dread Ambusher), Fey Wanderer (Dreadful Strikes)
- **Sorcerer**: Draconic (AC/HP + Elemental Affinity), Wild Magic (Surge table), Clockwork (Restore Balance), Aberrant (Psychic Defenses)
- **Warlock**: Fiend (temp HP on kill + Dark Luck), Archfey (Fey Presence), Celestial (Healing Light), Great Old One (Entropic Ward)
- **Artificer**: Battle Smith (Steel Defender), Artillerist (Eldritch Cannon), Alchemist (Experimental Elixir), Armorer (Arcane Armor)

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

### Battle Modes
- **PvP**: Last player standing wins
- **Wave Survival**: Clear waves of monsters (Rat Cellar, Goblin Ambush, Bandit Camp, Crypt of Undead, Dragon's Challenge, Haunted Catacombs, Fire Caverns, Shadow Realm, Abyssal Fortress)
- **Boss Rush**: Defeat boss monsters
- **Endless Survival**: Fight infinite escalating waves until the party falls. Waves 1-3: CR 0-1 (rats/kobolds/goblins), 4-6: CR 1-3 (skeletons/wolves/ogres), 7-9: CR 3-5 (owlbear/basilisk/troll), 10-12: CR 5-8 (wight/fire_elemental/frost_giant), 13-15: CR 8-12 (aboleth/remorhaz/archmage), 16+: CR 13+ bosses (pit_fiend/lich/dragon) with HP scaling. Players heal 25% between waves and earn wave_number*15 XP per wave. Best wave tracked per player. Glory earned = 5 + waves_cleared * 3.

### Targeting & Scanning
- IJKL to scan directions, Caps Lock or brackets to cycle results
- Scan results show distance, direction, health status, and conditions
- Target lock (Enter) shows HP, AC, distance, direction, and conditions


### Character Persistence
- Characters saved to SQLite via account JSON data blob on creation
- Character data sent to client on login (`character_data` message) including background, feats, skills, tools, and base ability scores
- Client profile cache stores background and feats alongside core character data
- Client restores `created_char_*` variables from server data (View Character works across sessions)
- Adventure progress tracked: XP, level, achievements, kills, healing, waves cleared

### Post-Battle Flow
- Battle end detected (PvP: one standing, Wave: all monsters dead or TPK)
- Adventure mode: XP awarded (monster kills, healing, match completion, achievements)
- Loot drops generated per defeated monster (rarity based on monster XP tier; boss mode has guaranteed Rare+ drops)
- Glory points awarded: 10 normal, 25 boss; dungeon completions tracked
- Level-up flow: players choose new spells, cantrips, and subclass (at level 3) interactively
- Room `started` flag reset so new games can be launched
- Quick restart option for wave/boss/endless modes: "Play again" re-sends start_game with same scenario/difficulty
- Client shows 5-second countdown then returns to lobby

### Loot & Equipment System
- 35 items across 5 rarity tiers (Common, Uncommon, Rare, Epic, Legendary) and 4 slots (Weapon, Armor, Ring, Amulet)
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
- **[/]**: Alternative target cycling
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
- **Escape x 2**: Forfeit
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

## Development
- Compile: `C:\Users\16239\Documents\games\nvgt\nvgt.exe -c Server/Server.nvgt` and `C:\Users\16239\Documents\games\nvgt\nvgt.exe -c Client/client.nvgt`
- Git repo: https://github.com/ArizonaDad/souls-mmo

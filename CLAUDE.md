# Dungeon Legends - D&D 5e Battle Simulator



## Project Overview

Multiplayer accessible D&D 5e combat arena for blind players built in **NVGT** (NonVisual Gaming Toolkit, AngelScript-like). Players create characters (67 species, 14 classes, 48 backgrounds, 138 subclasses, 77 feats, 38 weapons, 367 spells) and fight in turn-based combat with full TTS and HRTF spatial audio. Supports PvP Arena, Wave Survival, Boss Rush, and Endless Survival modes. Features 40+ achievements, glory shop, daily dungeons, leaderboards, loot system, trading, prestige, guilds, and multi-phase boss fights.



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

| `Server/combat/spell_data.nvgt` | 68 spell definitions (34 cantrips + 34 leveled), spell helpers |

| `Server/progression.nvgt` | XP tracking, achievement system, character level progression, prestige system, glory points |

| `common/loot_data.nvgt` | Item catalog (35 items), loot generation, rarity tiers, inventory helpers |

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

- **Reaction Prompt System**: When a player is about to be hit, they are prompted for available reactions before hit resolves. Options: Shield (+5 AC), Cutting Words (-Id4-d12), Warding Flare (force reroll), Defensive Duelist (+Prof AC), Restore Balance (cancel advantage), Spirit Shield (reduce damage 2d6+), Entropic Ward (force miss), Arcane Deflection (+4 AC)
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
- Grave Cleric Path to the Grave, Forge +1 AC, Peace Emboldening Bond, Twilight Sanctuary, Order Voice of Authority
- Hexblade Curse, Samurai Fighting Spirit, Horizon Walker Planar Warrior
- Storm Herald Storm Aura, Rune Knight Giant Might, Wild Magic Surge table
- Sun Soul Radiant Bolt, Ascendant Dragon Breath, Shadow Sorcerer Strength of the Grave
- Tentacle of the Deeps, Form of Dread, Genie Vessel, Eldritch Cannon, Steel Defender, Experimental Elixir
- College of Eloquence Unsettling Words (subtract Bardic die from save)
- Gunslinger Sharpshooter Stance, Liar's Dice gamble, License to Kill, Ricochet Bullet
- Setting subclass damage bonuses: Frost (cold), Desert (heat), Couatl (radiant), Carrion Raven (necrotic), Misfortune Bringer (jinx), Runetagger (force), Astral Domain (psychic), Inquisition vs casters

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


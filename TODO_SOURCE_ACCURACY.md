# Source Accuracy TODOs

**Mandate:** All spells, class features, subclasses, feats, and items must function EXACTLY as stated in the source material from `C:\Users\16239\Downloads\Sources_clean\Source Books and rules\`. No invented rules. No simplifications of core mechanics.

---

## 1. Skill Check System

**Infrastructure status (RESOLVED 2026-04-08, batch 2A):** `request_skill_check(u, c, skill_name, dc, custom_tag, extra_advantage, extra_disadvantage)` is live in `battle_manager.nvgt`. The pipeline:

1. Computes modifier from `combatant.get_skill_bonus()` (now correctly handles **expertise** = double prof, **Jack of All Trades** = half prof on non-proficient, plus exhaustion)
2. Pulls per-skill advantage/disadvantage from `combatant.skill_check_advantage` / `skill_check_disadvantage`
3. Stacks Pass Without Trace bonus on Stealth automatically
4. Builds a `pending_roll` with `roll_type = ROLL_ABILITY_CHECK` and `resolution_tag = skill_<lowercase>` (e.g., `skill_persuasion`, `skill_sleight_of_hand`)
5. Routes through the standard reroll prompt chain (Bardic, Lucky, Heroic) — `maybe_prompt_bardic_inspiration` now fires on **any** failed `ROLL_ABILITY_CHECK` with a positive DC, not just Hide
6. `handle_roll_result` advantage/disadvantage path now triggers for `ROLL_ABILITY_CHECK` so the d20 is correctly rolled twice

New constants in `common/combat_constants.nvgt`: `DC_VERY_EASY`/`DC_EASY`/`DC_MEDIUM`/`DC_HARD`/`DC_VERY_HARD`/`DC_NEARLY_IMPOSSIBLE`, plus the canonical 18-skill `SKILL_NAMES` array. New helper `skill_to_ability(skill_name)` provides the canonical D&D 5e skill→ability mapping.

**Subclass features wired (RESOLVED 2026-04-08, batch 2B):**

- **Silver Tongue** (College of Eloquence Bard L3, Tasha's para 1696) — clamps natural d20 ≤9 to 10 on `skill_persuasion` and `skill_deception` checks. Always-on, no resource cost. Verified against source: "When you make a Charisma (Persuasion) or Charisma (Deception) check, you can treat a d20 roll of 9 or lower as a 10."
- **Blessing of the Trickster** (Trickery Domain Cleric L3, PHB 2024 para 4697) — Magic action, self or willing creature within 30 feet, target gains advantage on Stealth checks until long rest. Now uses `skill_check_advantage["Stealth"]` flag. **Replaces the pre-existing `+5 hide_dc` bug** which was a wrong-direction approximation (it made the target harder to find rather than rolling Stealth with advantage).
- **Inquisitor's Eye** (Oath of Zeal Paladin L3 Channel Divinity, Grim Hollow Player Pack para 434) — bonus action, costs 1 Channel Divinity, grants advantage on Investigation/Insight/Perception checks for 10 minutes plus immunity to surprise. New `inquisitors_eye_active` combatant flag and `inquisitors_eye` bonus action menu entry. Verified against source.
- **Keeper of History** (College of the Dirge Singer Bard L3, Exploring Eberron para 5263-5264) — at character init, grants History + Performance proficiency, OR Expertise if already proficient. Verified against source: "You gain proficiency in the History and Performance skills. If you already have these proficiencies, you instead gain Expertise."

**Still pending:**

- **Benevolent Presence** (Couatl Herald Fighter) — expend Mercy Dice on Insight/Performance/Persuasion checks. Combat doesn't currently have these social check triggers; the feature is partially blocked on a future Search/Influence action implementation.
- ~50 other subclass / feat features that grant skill proficiency, expertise, or advantage. Most can be wired by adding a few lines to `character_data.nvgt` init or by setting a `skill_check_advantage[]` flag from a feature's bonus action handler.

The Hide action still uses the legacy direct path (`request_hide_check` -> `request_roll`); migrating it to use `request_skill_check` is batch 2C.

---

## 2. Mid-Spell Player Choice System

**Infrastructure status (RESOLVED 2026-04-08):** The `pending_spell_choice` state, `send_spell_choice_prompt`, `handle_spell_choice_response`, and `apply_spell_choice` dispatcher are now in `battle_manager.nvgt`. Client-side `prompt_spell_choice` + `check_spell_choice_prompt_input` + game-loop wiring + `net.nvgt` routing are in place. New `spell_choice_prompt` and `spell_choice_response` message types live in `common/message_types.nvgt`. See CLAUDE.md "Mid-Spell Player Choice System" section for the canonical pattern.

The rule remains: **NEVER choose for the player when a spell has a choice.** Bots and NPC casters auto-pick the first option deterministically so combat keeps moving.

### Spells migrated to the new system:

| Spell | Choice | Status | Source quote |
|-------|--------|--------|--------------|
| **Fire Shield** | Warm (cold resistance, reflects 2d8 fire) OR Chill (fire resistance, reflects 2d8 cold) | DONE 2026-04-08 | Basic Rules para 13322: "warm shield or a chill shield, as you choose" |
| **Spirit Guardians** | Radiant (angelic/fey form) OR Necrotic (fiendish form) | DONE 2026-04-08 | Basic Rules para 15123-15124: alignment-based; game prompts caster since alignment is not tracked |
| **Adjust Density** (Graviturgy L2 feature) | Halve (+10 ft speed, disadvantage STR) OR Double (-10 ft speed, advantage STR) | DONE 2026-04-08 | Wildemount p.5428: "halved or doubled for up to 1 minute or until your concentration ends". Also fixed a pre-existing bug where adjust_density flags lived on the caster instead of the target, with no concentration cleanup path. |
| **Magic Missile** | Distribute N darts among visible enemies (auto-hit, 1d4+1 force per dart) | DONE 2026-04-08 | Basic Rules para 14089: "Each dart strikes a creature of your choice... you can direct them to hit one creature or several." Distribution kind, server rolls per-dart server-side and groups damage per target. |
| **Scorching Ray** | Distribute N rays among visible enemies (separate attack roll per ray, 2d6 fire on hit) | DONE 2026-04-08 | Basic Rules para 14851: "You can hurl them at one target within range or at several. Make a ranged spell attack for each ray." Distribution kind, multi-attack chain consumes `pending_roll.next_target_ids_csv`. |
| **Eldritch Blast** (at caster L5+) | Distribute N beams among visible enemies (separate attack roll per beam, 1d10 force on hit) | DONE 2026-04-08 | Basic Rules para 13047: "You can direct the beams at the same target or at different ones. Make a separate attack roll for each beam." Distribution kind only triggers at L5+ when there are 2+ beams. |

### Spells still needing migration:

| Spell | Choice the player should make | Current behaviour |
|-------|------------------------------|-------------------|
| **Spirit Totem** (Circle of the Shepherd) | Bear OR Hawk OR Unicorn spirit | Working — uses 3 separate bonus action menu entries (acceptable) |
| **Starry Form** (Circle of the Stars) | Archer / Chalice / Dragon form | Working via bonus_action `form` field |
| **Wild Shape / Elemental Wild Shape** | Which creature form | Partial |
| **Elemental Adept feat** | Damage type chosen at feat pickup | Should be at character creation, not combat |
| **Channel Divinity Order's Demand** | Optional "drop held items" rider | Not implemented |
| **Wall of Stone / Wall of Fire** | Shape and orientation | Not implemented (walls not in combat grid) |
| **Polymorph** | Target beast form | Limited — uses a fixed stat block |
| **Telekinesis** | Object vs creature, movement direction | Not implemented |
| **Bigby's Hand** | Hand action each turn (punch/grapple/push/interpose) | Not implemented |
| **Conjure X spells** | Which creature type to summon | Not implemented |
| **Summon Beast/Fey/Construct/etc.** | Aspect chosen at cast | Not implemented |

---

## 3. Per-Subclass Known Approximations (need source re-verification)

### Approximated because no mid-spell prompt yet:
- **Voice of Authority** (Order Domain) — auto-picks nearest enemy for ally's reaction attack. Source says cleric chooses any visible enemy the ally can reach.
- **Awakened Spellbook damage swap** (Order of Scribes) — swap is at-will flag only, no prompt for WHICH damage type.
- **Blessing of the Trickster** (Trickery Domain) — uses +5 hide_dc as approximation for "advantage on Stealth checks" (needs actual skill check system).

### Approximated because the relevant subsystem doesn't exist yet:
- **Manifest Echo** (Echo Knight) — echo placement is auto (5ft north). Source says "unoccupied space you can see within 15 feet". Needs position-picker UI.
- **Wall of Force / Wall of Stone / Wall of Fire** — walls aren't tracked on the combat grid.
- **Darkness / Fog Cloud** — LoS mechanics not implemented, just flags.

### Known rule divergences flagged for the user:
- **Shield Master (2024)** — Implemented as automatic rider after Attack action hit. Source allows choice of Push 5ft OR Prone — currently always Prone.
- **Polearm Master** — Bonus action butt-strike implemented, but **Reactive Strike (reaction on enter reach) is NOT implemented**. Needs a new reaction trigger system for opportunity attacks on entering reach (the existing system only handles leaving reach).
- **Order's Demand** — Drop-held-items rider on failed save is not implemented.
- **Mage Slayer 2024 Guarded Mind** — 1/rest auto-succeed on failed INT/WIS/CHA save not implemented.

---

## 4. Subclass Implementation Status (147 total)

### Source extracted, ready to implement (14):
**Book of Ebon Tides (10):**
- Circle of Shadows (Druid) — Umbral Form wild shape, Dark Servant, Shadow Mass, Darkness Falls
- College of Shadow (Bard) — Dancing Shadows sphere, Fear of the Dark aura, Shade Step, Night Music
- Keeper Domain (Cleric) — Blessed Chosen reaction, Divine Initiative CD, Fighting Fit, Hobbling Strike, Duty Over Death
- Light Weaver (Sorcerer) — Trick of the Light, Flickering Aura, Refraction Shield, Aura Magnification, Spell Blind
- Mother of Sorrows (Warlock) — Poison Soul, Venomous Mark, Sickening Revenge, Dark Inoculation, Touch of Sorrow
- Shadow Arcane Tradition (Wizard) — Shadow Symbiote, Dark Transfusion, Orb of Night, From the Shadows, Second Skin
- Shadow Domain (Cleric) — Cover of Night, Lengthen Shadow, Shadow Grasp CD, Fade to Black, Potent Spellcasting, Army of Shadow
- Shadow Gnawer (Barbarian) — Shadow Smoke, Creeping Fog teleport, Consume Darkness, Corrosive Haze
- Umbral Binder (Rogue) — Eyes In the Dark, Shadow Bind ritual, Cloaked Dagger, Black Magic, Shadow Grasp
- Way of the Prophet (Monk) — Wise Words, Ki spellcasting, Prophecy

### Source missing entirely (2):
- **College of Spirits** (Ravenloft Bard) — zero matches in Van Richten's cleaned or uncleaned docx
- **Undead Patron** (Ravenloft Warlock) — zero matches. Form of Dread was implemented from memory in an earlier session and should be reviewed against the source once the user can provide the page.

### Already extensively implemented (needs full feature audit pass):
Every Xanathar's, Tasha's, Fizban's, Wildemount, Eberron, Griffon's Saddlebag, Grim Hollow, Gunslinger, and Sword Coast subclass has at least init logic and combat effect logic but may be missing L6/L10/L14/L17 features.

### PHB gaps (from Phase 1 breakdown):
PHB docx file is missing full subclass detail pages for Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard. Basic Rules file has 1 subclass per class (Oath of Devotion, Thief, Draconic, Fiend Patron, etc). Need to extract from Basic Rules Ch 3 paragraphs 2063+ for proper feature text.

---

## 5. Spell System TODOs

### Spell descriptions in Basic Rules (not PHB):
Phase 1 notes that the PHB file is missing spell descriptions. Basic Rules file paragraphs 11869-15661 contain 300+ spell descriptions. **All new spell implementations must pull from Basic Rules, not PHB.**

### Generic spell resolver gaps:
- AoE healing spells work (Mass Cure Wounds fixed in batch 20)
- AoE damage spells work via the generic save loop
- Wall spells have no grid implementation
- Summon spells have no creature-spawn flow (some use `create_monster_combatant` but most don't)
- Conjure X spells (Animals, Elementals, Fey, Minor Elementals, Woodland Beings) not implemented
- Concentration drop needs to properly clear ALL of the spell's effects, not just a flag

### Spell list completeness:
- 367 spells in `spell_data.nvgt`
- Source has ~500+ spells in Basic Rules + Xanathar's + Tasha's + Fizban's + Wildemount + Griffon's + Grim Hollow + Ebon Tides (has extensive shadow spell list)
- Need to run a diff pass to confirm no gaps

---

## 6. Class Feature TODOs (non-subclass)

Every base class has features that need the same level of rigor as subclasses:
- **Barbarian:** Reckless Attack, Danger Sense, Brutal Strike (2024), Relentless Rage
- **Bard:** Jack of All Trades, Expertise, Magical Inspiration, Countercharm, Superior Inspiration
- **Cleric:** Channel Divinity (generic Turn Undead + Divine Intervention), Destroy Undead
- **Druid:** Wild Companion, Elemental Fury, Archdruid
- **Fighter:** Tactical Mind/Shift/Master, Second Wind (correct dice), Studied Attacks
- **Monk:** Martial Arts die scaling, Deflect Attacks (was Deflect Missiles), Stunning Strike, Empowered Strikes, Perfect Focus
- **Paladin:** Lay on Hands (pool size), Divine Smite (slot-based in 2024), Aura of Courage, Cleansing Touch
- **Ranger:** Favored Enemy (2024 uses Hunter's Mark), Natural Explorer, Primeval Awareness
- **Rogue:** Sneak Attack dice scaling, Cunning Strike (2024), Reliable Talent
- **Sorcerer:** Font of Magic, Metamagic options (need full list), Sorcerous Restoration
- **Warlock:** Pact Boon selection, Mystic Arcanum, Eldritch Master
- **Wizard:** Arcane Recovery, Spell Mastery, Signature Spells
- **Artificer:** Infusions, Flash of Genius, Spell Storing Item

---

## 7. Feat TODOs

**Current status (verified 2026-04-08):** 77 feats defined in `common/feat_data.nvgt`. Only 24 have `has_feat()` checks in combat code. **53 feats have no combat logic at all** — they're selectable at character creation but do nothing in combat.

### Feats WITH combat logic (24 — need audit pass for 2024 accuracy):
alert, archery, boon_of_combat_prowess, boon_of_irresistible_offense, boon_of_truesight, crossbow_expert, crusher, defensive_duelist, dueling, grappler, great_weapon_fighting, great_weapon_master, healer, heavy_armor_master, mage_slayer, piercer, polearm_master, savage_attacker, sentinel, shield_master, slasher, tavern_brawler, thrown_weapon_fighting, war_caster

### Feats WITHOUT combat logic (53 — need full implementation):

**Origin feats (6 missing):**
- crafter, magic_initiate_cleric, magic_initiate_druid, magic_initiate_wizard, musician, skilled, tough, lucky

**General feats (29 missing — level 4+, the biggest group):**
- ability_score_improvement, actor, athlete, charger, chef, defense, dual_wielder, durable, elemental_adept, fey_touched, heavily_armored, inspiring_leader, keen_mind, lightly_armored, martial_weapon_training, medium_armor_master, moderately_armored, mounted_combatant, observant, poisoner, resilient, ritual_caster, shadow_touched, sharpshooter, skill_expert, skulker, speedy, spell_sniper, telekinetic, telepathic, weapon_master

**Fighting Style feats (4 missing):**
- blind_fighting, interception, protection, two_weapon_fighting, unarmed_fighting

**Epic Boon feats (8 missing):**
- boon_of_dimensional_travel, boon_of_energy_resistance, boon_of_fate, boon_of_fortitude, boon_of_recovery, boon_of_skill, boon_of_speed, boon_of_spell_recall, boon_of_the_night_spirit

### Key complex feat effects still needing work:
- **Polearm Master Reactive Strike** — opportunity attack when a creature enters reach (not just when leaving). Current game only supports leave-reach OAs.
- **Shield Master Interpose Shield** — reaction to take 0 damage instead of half on a successful DEX save against a half-damage effect.
- **Shield Master push option** — player choice of Push 5ft OR Prone (currently always Prone).
- **Mage Slayer Guarded Mind** — 1/rest reaction auto-succeed on failed INT/WIS/CHA save.
- **Charger** — When you Dash, bonus action melee attack or shove with +1d8 damage.
- **Inspiring Leader** — After short/long rest, grant 6 creatures temp HP = level + CHA mod.
- **Elemental Adept** — ignore resistance to chosen damage type, treat 1s as 2s on damage dice.
- **Fey Touched** — free Misty Step + one 1st-level Div/Enchant spell once per long rest each.
- **Shadow Touched** — free Invisibility + one 1st-level Illusion/Necromancy spell once per long rest each.
- **Telekinetic** — bonus action Mage Hand / push-pull 5ft.
- **Telepathic** — telepathic communication + Detect Thoughts spell.
- **Sharpshooter** — ignore cover, no long range penalty, -5/+10 trade.
- **Spell Sniper** — double spell attack range, ignore cover, learn an attack cantrip.
- **Poisoner** — apply poison for +2d8 poison damage + poisoned condition.
- **Resilient** — gain proficiency in one saving throw.
- **Ability Score Improvement** — +2 or +1/+1 (data only, no combat effect beyond stats).

**Total new feat implementations needed: ~40** (53 feats missing, but ability_score_improvement is purely stat-based and doesn't need combat code; several are simply +skill/+tool proficiency and will partly land in the skill check system).

---

## 7B. Custom Spell Handlers (SEPARATE from generic resolver)

The generic spell resolver in `battle_manager.nvgt` handles most damage/healing/save spells via the `pending_roll` → save loop flow. But many spells have unique mechanics that need custom handlers. Status as of 2026-04-08:

### Spells with custom handlers implemented:
true_strike, spiritual_weapon, revivify, heal, ice_storm, finger_of_death, power_word_stun, magic_missile, shield, longstrider, misty_step, bless, lesser_restoration, pass_without_trace, haste, heroism, hex, hunters_mark, mage_armor, web, blindness_deafness, animate_dead, fear, hypnotic_pattern, polymorph, wall_of_force, hold_person, banishment, charm_person, sleep, color_spray, tashas_hideous_laughter, ensnaring_strike, sanctuary, aid, stoneskin, greater_invisibility, fly, fire_shield, spirit_guardians, fog_cloud, darkness

### Spells from the catalog (367+) that lack custom handlers and need them for correct source behavior:

**Wall spells** — entire category has no grid implementation:
- Wall of Fire, Wall of Stone, Wall of Thorns, Wall of Ice, Wall of Water, Wall of Sand, Wall of Light, Blade Barrier

**Summon/Conjure spells** — no creature-spawn flow for most:
- Summon Beast, Summon Celestial, Summon Construct, Summon Draconic Spirit, Summon Elemental, Summon Fey, Summon Fiend, Summon Shadowspawn, Summon Undead, Summon Dragon
- Conjure Animals, Conjure Celestial, Conjure Elemental, Conjure Fey, Conjure Minor Elementals, Conjure Woodland Beings
- Animate Objects, Create Undead, Danse Macabre, Find Familiar, Find Steed, Find Greater Steed

**Control / manipulation spells** — need new movement / target-grab flow:
- Telekinesis (move creature/object by thought each turn)
- Bigby's Hand (5 action modes: clenched fist / forceful hand / grasping hand / interposing hand)
- Control Water, Control Winds, Control Weather, Control Flames
- Investiture of Flame/Ice/Stone/Wind
- Reverse Gravity
- Maelstrom

**Shape-shift / transformation spells**:
- Alter Self, Disguise Self, Enlarge/Reduce, Gaseous Form, Giant Insect, Shapechange, True Polymorph
- Druid Wild Shape already has partial flow — needs verification against 2024 rules

**Concentration-ongoing damage/control fields**:
- Evard's Black Tentacles, Sickening Radiance, Maelstrom, Storm Sphere, Tidal Wave, Cloudkill, Stinking Cloud, Incendiary Cloud, Insect Plague
- Antimagic Field, Globe of Invulnerability, Resilient Sphere
- Guardian of Faith, Forbiddance

**Utility / save-or-suck**:
- Banishment (partial), Blink, Contingency, Crown of Madness, Dominate Person/Monster/Beast, Eyebite, Feeblemind, Flesh to Stone, Geas, Hold Monster, Imprisonment, Plane Shift, Planar Binding, Suggestion, Temporal Stasis, Tongues, Weird

**Divination** — no exploration flow so skipped for combat:
- Augury, Clairvoyance, Commune, Contact Other Plane, Detect Evil and Good, Detect Magic, Detect Poison and Disease, Detect Thoughts, Divination, Find the Path, Foresight, Legend Lore, Locate Animals/Object/Creature, Scrying, See Invisibility, True Seeing, Vision

**Healing / buff spells needing proper resource tracking**:
- Aura of Life, Aura of Purity, Aura of Vitality, Beacon of Hope, Death Ward, Gift of Alacrity, Holy Weapon, Regenerate, Resurrection, True Resurrection, Reincarnate, Life Transference

**Eldritch Blast / Scorching Ray / Magic Missile distribution** — auto-split dart/beam counts evenly. Source lets the caster distribute them freely. Needs a target-distribution prompt (same mid-spell choice system).

**True Strike** (2024) — new version is a melee weapon attack with a spellcasting ability modifier. Source text has been implemented but needs re-verification.

**Estimated custom-handler gap: ~60-80 spells** out of 367+ currently in `spell_data.nvgt`, plus probably ~150+ more spells not yet added to the catalog (Basic Rules has 300+ descriptions, Griffon's Saddlebag + Book of Ebon Tides + Valda's add hundreds more).

---

## 7C. Companion / Summon System

Currently a single-minded stub exists (Beast Master `beast_companion_active` flag, Drakewarden `drake_hp`, Battle Smith `steel_defender_active`), but there's no proper companion system. A real implementation needs:

### System requirements:
1. **Companion entity** — a combatant tracked in the battle with its own HP, AC, initiative, actions, reactions, and stat block.
2. **Ownership** — each companion is owned by a player combatant; if owner dies, companion may remain / flee / die depending on subclass.
3. **Command action** — owner spends action (or bonus action) to command companion; some subclasses grant free commands.
4. **Companion AI** — for moments when the companion acts without a direct command (Beast Master L7+ Exceptional Training, Battle Smith passive attack).
5. **Stat block scaling** — companion stats scale with the owner's level / proficiency bonus per subclass rules.
6. **Death and resurrection** — each subclass has different rules for bringing back a slain companion.

### Subclasses currently flagged but NOT functioning correctly:
- **Beast Master (Ranger)** — Primal Companion has Land/Sea/Sky variants each with full stat blocks in Tasha's. None are implemented. Current code has a flag but no entity spawns.
- **Battle Smith (Artificer)** — Steel Defender has a full stat block in Tasha's. Current code has a flag and a placeholder "Steel Defender Attack" bonus action, but no actual entity.
- **Drakewarden (Ranger)** — Drake Companion has a full stat block in Fizban's (Small → Medium → Large scaling). Partially tracked via `drake_hp` but no entity.
- **Circle of the Shepherd (Druid)** — Spirit Totem is an aura, not a companion, but Guardian Spirit (L10) heals summoned creatures. Needs the generic summon tracker first.
- **Circle of Wildfire (Druid)** — Wildfire Spirit is a full companion with Teleport + Fiery Teleportation mechanics. Currently just a flag.
- **Circle of the Land (Druid)** — no companion, skip
- **Artillerist (Artificer)** — Eldritch Cannon is a companion-like entity (Flamethrower / Force Ballista / Protector modes). Partially implemented with `eldritch_cannon_hp`, but the 3 modes and their specific attacks aren't.
- **Alchemist (Artificer)** — no companion, skip
- **Armorer (Artificer)** — not a companion, but the suit is basically a form change with different attack options. Needs similar state-swap logic.
- **Echo Knight (Fighter)** — Echo is a pseudo-companion (1 HP shadow). Partially implemented in batch 22, but needs proper entity tracking for Unleash Incarnation + Reclaim Potential + Shadow Martyr + Legion of One (two echoes at L18).
- **Ancestral Guardian (Barbarian)** — Ancestral Protectors is an aura effect, not a companion, but tracked as `ancestral_protector_target`.
- **The Fathomless (Warlock)** — Tentacle of the Deeps is a companion-like 1d8 cold damage reach weapon. Partial.
- **Circle of the Stars (Druid)** — Starry Form is a self-buff, not a companion.

### Full spells that are companion-adjacent:
- **Find Familiar** — owl / hawk / cat / etc. with its own stat block
- **Find Steed** — mount with its own stat block
- **Find Greater Steed** — same, larger
- **Animate Dead** — zombie/skeleton minions under command
- **Create Undead** — ghoul minions
- **Danse Macabre** — temporary zombie/skeleton minions
- **Conjure X spells** (Animals/Celestial/Elemental/Fey/Minor Elementals/Woodland Beings) — summon creatures
- **Summon X spells** (Beast/Celestial/Construct/Draconic/Elemental/Fey/Fiend/Shadowspawn/Undead/Dragon) — summon creature with a scaling stat block

### Minimum viable companion implementation:
1. Extend `combatant` class with `owner_id`, `is_companion`, `companion_subclass`
2. Add `create_companion(owner, stat_block_name)` in combat_engine
3. Add `companion_act(companion)` in battle_manager (uses owner's turn or bonus action)
4. Add companion stat blocks to `monster_data.nvgt` or a new `companion_data.nvgt`
5. Hook subclass bonus actions (Primal Companion Attack, Steel Defender Attack, Drake Breath, Summon Wildfire Spirit, Manifest Echo) into the companion spawn/command flow
6. Handle companion death separately from player death (no death saves, just removal)
7. Apply ownership rules: companion uses owner's proficiency bonus, companion's stats scale with owner level per source tables

**This is a major refactor** — estimated 500+ lines of new code across combat_engine, battle_manager, monster_data, users _dom, and combat_ui. Should be its own milestone.

---

## 8. Items and Shop TODOs

Phase 1 identifies massive item catalogs:
- DMG 2024: paragraphs 6632-10570 (~4000 paras of magic items alphabetically)
- Griffon's Saddlebag Book One + Two: hundreds of items
- Tasha's Ch 3, Fizban's, Book of Many Things, Wildemount, Theros, Ravnica, Ravenloft — all have setting-specific items
- Grim Hollow Player Pack: 10+ items
- Valda's Gunslinger: 15 firearms across 3 eras

Current catalog size in game: TBD. Needs a pass against each source file.

**Pricing rule:** Use source price. If missing, use rarity defaults: Common 100gp, Uncommon 500gp, Rare 5000gp, Very Rare 20000gp, Legendary 50000gp, Above Legendary 100000gp.

---

## 9. Other Systems From Phase 1 Not Yet Implemented

- **Dragonmarks** (Eberron Rising, Wayfinder's, Forge of Artificer) — 12-13 marks with subrace-style benefits
- **Piety system** (Theros) — 15 gods with devotion tracks
- **Supernatural Gifts** (Theros) — 10 gifts (Anvilwrought, Heroic Destiny, Iconoclast, Inscrutable, Lucky, Mythic Companion, Nyxborn, Oracle, Pious, Unscarred)
- **Dark Gifts** (Ravenloft) — source missing
- **Vestiges of Divergence** (Wildemount) — 3-tier evolving legendary items
- **Heroic Chronicle** (Wildemount) — backstory tables
- **Transformations** (Grim Hollow) — 7 types × 4 levels = 28 progression tracks (Aberrant/Celestial/Fiendish/Fey/Lich/Lycanthrope/Vampire)
- **Shadow Roads** (Book of Ebon Tides) — planar travel
- **Fey Courts** (Book of Ebon Tides) — Golden Oak / Midnight Teeth / Fallen Courts
- **Guild Membership** (Ravnica) — renown and rank advancement
- **Faction Tracks** (Grim Hollow) — faction reward progression
- **Bastions** (DMG 2024 + Forge of Artificer) — player-owned strongholds with facilities
- **Group Patrons** (Tasha's, Eberron Rising) — party-level patron benefits

These are large systems. None should be built from memory — each needs a full source extraction pass before coding.

---

## Working Rule Going Forward

**Before implementing any feature:**
1. Open the actual docx file and extract the exact source text
2. Quote it in the commit message
3. Never invent a mechanic, damage die, DC formula, or duration
4. If a choice exists in the source, the player MUST be prompted — never auto-pick
5. If a rule is ambiguous in the source, flag it and ask the user

**Before releasing any subclass as "done":**
1. All features at levels 1/2/3/6/10/14/17/18/20 (as applicable) must be implemented
2. Every resource pool (ki/focus/rage/inspiration/channel divinity/etc.) must use the correct scaling table
3. Features that reference other features (e.g., "When you use X, also do Y") must actually chain
4. Short-rest vs long-rest recharge must match the source

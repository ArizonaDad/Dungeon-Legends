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

### Source extracted, in progress / shipped:
**Book of Ebon Tides (10 — ALL 10 SHIPPED in batches 3A-3D):**
- **Light Weaver (Sorcerer)** — SHIPPED batch 3A. Trick of the Light, Flickering Aura toggle, Refraction Shield melee retort. Spell Blind capstone (L18) deferred (needs aura concentration system). Aura Magnification (L14) is a passive flag — implemented as light-shifted vs dark-shifted variant on the existing aura.
- **Shadow Domain (Cleric)** — SHIPPED batch 3A. Cover of Night Stealth proficiency, Shadow Grasp Channel Divinity action (with L17 Army of Shadow PB-target expansion), Fade to Black bonus action invisibility. Lengthen Shadow (touch spell delivery via shadow), Potent Spellcasting (cantrip damage WIS bonus), and Army of Shadow's full effect deferred — Lengthen Shadow needs spell delivery tracking, Potent Spellcasting needs to touch every cantrip damage path.
- **Way of the Prophet (Monk)** — SHIPPED batch 3A. Wise Words skill proficiency + WIS-on-CHA-skills flag, Righteous Strike on-hit ki rider (1/turn proficiency-bonus radiant damage). Charming Aura (ki spellcasting), Blessed Chosen revival (L11), and Force of Personality reaction deferred — they need spell-from-class infrastructure and a death save intercept.
- **College of Shadow (Bard)** — SHIPPED batch 3B. Dancing Shadows BI bonus action with 10-round duration tick-down, Fear of the Dark passive flag. Shade Step (BI rider teleport) and Night Music (L14 reaction frighten) deferred — Shade Step needs the BI grant flow extended with a teleport rider, Night Music needs a post-cast reaction hook.
- **Mother of Sorrows (Warlock)** — SHIPPED batch 3B. Poison Soul wired into apply_damage so the warlock's poison damage bypasses both target poison_resistance AND poison_immunity (source check). Venomous Mark bonus action curse with 1d6 poison rider on first spell attack hit per spell. Dark Inoculation L10 grants poison immunity. Sickening Revenge (L6 reaction CON save) and Touch of Sorrow (L14 paralysis rider) deferred — both need new reaction triggers.
- **Circle of Shadows (Druid)** — SHIPPED batch 3C. Umbral Form bonus action (expends Wild Shape, 10 min duration tracked) with L10 Shadow Mass auto-applying B/P/S resistance + flying speed equal to base speed. Darkness Falls L14 action with 1/SR cooldown. Dark Servant L6 init grants WIS-mod uses (the actual minion summon needs the companion/summon system from §7C and is deferred).
- **Shadow Arcane Tradition (Wizard)** — SHIPPED batch 3C. Shadow Symbiote at L2 grants the darkvision bonus + sunlight sensitivity. Dark Transfusion bonus action handler picks the two lowest spell slots and recovers a slot equal to or less than their combined value. From the Shadows L10 + Second Skin L14 set as init flags (passive — auto-hide on initiative and +2 AC + B/P/S resistance in dim/dark). Orb of Night L6 reaction is the only major piece deferred (needs the existing reaction prompt chain extended to include attack-target wizards).
- **Keeper Domain (Cleric)** — SHIPPED batch 3D. L1 init grants WIS-mod Blessed Chosen reaction uses + Persuasion proficiency + Fighting Fit uses at L6. L2 Divine Initiative Channel Divinity action handler grants temp HP (5/8/11/14 by level scaling) to up to WIS-mod allies within 60 ft. L8 Hobbling Strike auto-applies first weapon hit per turn (STR save vs WIS spell save DC; on fail, target prone; L14 also halves speed). Blessed Chosen reaction trigger and Duty Over Death revive deferred — both need new reaction triggers and a death save intercept respectively.
- **Shadow Gnawer (Barbarian)** — SHIPPED batch 3D. L3 init flag (passive Shadow Smoke aura). L6 Creeping Fog action: 60 ft teleport to a target's adjacent square + free melee attack. L10 Consume Darkness bonus action while raging: 1d12+CON heal + 1 HP/turn for the rest of rage (1/SR). Shadow Smoke active disadvantage hookup and L14 Corrosive Haze CON-save blind deferred — both need a "creature starts turn within X feet of source" check loop.
- **Umbral Binder (Rogue)** — SHIPPED batch 3D. L3 init flag with Shadow Bind defaulting to the cold-damage rider option (the rider is wired in apply_subclass_on_hit_damage as proficiency-bonus cold damage on first weapon hit per turn). The two other Shadow Bind options (teleport, half cover) require a long rest ritual flow that doesn't currently exist. L13 Black Magic 3 free darkness casts/LR set as a counter. L9 Cloaked Dagger and L17 Shadow Grasp on sneak attack hit deferred — both need extending the sneak attack flow.

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

### Spell description text rigor — RESOLVED 2026-04-09 (batch source-pull pass):
- **334 of 367 catalog spells** had truncated (cut at 150 chars) or paraphrased two-sentence descriptions before this pass. They now use **full source-quoted Basic Rules 2024 text** including upcast riders ("Using a Higher-Level Spell Slot.") and "Cantrip Upgrade." notes, capped at ~600 chars and ending on a sentence boundary.
- Method: `py` extraction script reads `basic_rules_full.txt`, detects spell headers via `Level N <school>` / `<school> Cantrip` patterns, collects body lines until next header, normalizes, set-matches to catalog `s.id` entries, and writes back into `Server/combat/spell_data.nvgt`.
- 33 catalog spells were already full-length and end-punctuated, so they were skipped untouched. 29 catalog spells (Wildemount, Eberron, Tasha's, Fizban's extras) are not in Basic Rules and remain on their existing descriptions until extracted from those source docx files.

### Spell save type rigor — RESOLVED 2026-04-09 (6 bug fixes against source):
- Color Spray: -1 → CON (was missing the save entirely, source: "Constitution save or Blinded")
- Ensnaring Strike: -1 → STR + 1d6 piercing rider (was missing save AND damage)
- Sleep: -1 → WIS + concentration true + range 90→60 (2024 update — Incapacitated→Unconscious chain)
- Slow: DEX → WIS + max_targets 1→6 (source: "Up to six creatures must succeed on a WIS save")
- Otto's Irresistible Dance: DEX → WIS + concentration true (description text always said WIS)
- Storm of Vengeance: DEX → CON + AoE radius 300 (source: "must make a CON save... 2d6 Thunder + Deafened")
- See commit `3e3f5ab` for full source quotes.

### Generic spell resolver gaps:
- AoE healing spells work (Mass Cure Wounds fixed in batch 20)
- AoE damage spells work via the generic save loop
- Wall spells have no grid implementation
- Summon spells have no creature-spawn flow (some use `create_monster_combatant` but most don't)
- Conjure X spells (Animals, Elementals, Fey, Minor Elementals, Woodland Beings) not implemented
- Concentration drop needs to properly clear ALL of the spell's effects, not just a flag

### Spell list completeness — RESOLVED 2026-04-09 (verified diff pass):
- **365 spells in `spell_data.nvgt`**, **339 spell descriptions in Basic Rules** (paras 11935-15661+, "Spell Descriptions" through "Spells (Z)").
- After normalization (apostrophes, dashes, underscores), **0 Basic Rules spells are missing** from the catalog. The catalog is a SUPERSET — it has 26 extras from Xanathar's/Tasha's/Fizban's/Wildemount/etc.
- All wizard-named spells (Bigby's Hand, Mordenkainen's Sword, Tasha's Hideous Laughter, Otiluke's Resilient Sphere, Drawmij's Instant Summons, Leomund's Tiny Hut, Melf's Acid Arrow, Nystul's Magic Aura, Otto's Irresistible Dance, Rary's Telepathic Bond, Tenser's Floating Disk, Heroes' Feast, Dragon's Breath, Hunter's Mark, Evard's Black Tentacles) are present.
- Diff method: extract Basic Rules spell headers (lines preceded by `Level N <school> (...)` or `<school> Cantrip (...)`), normalize to lowercase + strip apostrophes/dashes/underscores, set-diff against `s.name=...` matches in catalog. Confirmed via `py` script run 2026-04-09.

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

### Feats WITH combat logic (37 after batches 4A+4B; 16 still missing):
alert, archery, athlete (BATCH 4A), blind_fighting (BATCH 4B), boon_of_combat_prowess, boon_of_irresistible_offense, boon_of_truesight, charger (BATCH 4B), crossbow_expert, crusher, defensive_duelist, dueling, fey_touched (BATCH 4B), grappler, great_weapon_fighting, great_weapon_master, healer, heavy_armor_master, inspiring_leader (BATCH 4A), mage_slayer, observant (BATCH 4A), piercer, poisoner (BATCH 4A), polearm_master, resilient (BATCH 4A), savage_attacker, sentinel, shadow_touched (BATCH 4B), sharpshooter (BATCH 4A), shield_master, skill_expert (BATCH 4A), skulker (BATCH 4A), slasher, spell_sniper (BATCH 4A), tavern_brawler, telekinetic (BATCH 4A), thrown_weapon_fighting, unarmed_fighting (BATCH 4B), war_caster

**Batch 4B wired (5 new feats):**
- **Blind Fighting** (PHB para 7846) - sets `combatant.blindsight_range = 10` (used by future LoS / hidden checks)
- **Unarmed Fighting** (PHB para 7880) - 1d6 (with shield) or 1d8 (no shield) bludgeoning unarmed strike, picks the higher of weapon die / monk MA die / Tavern Brawler die
- **Charger** (PHB para 7557) - Improved Dash adds +10 ft to Dash speed. The d8 Charge Attack rider after a 10-ft straight-line move is deferred (needs movement-direction tracking).
- **Fey Touched** (PHB para 7614) - auto-prepares Misty Step + Bless (default L1 Enchantment) at character init. Free-cast tracking deferred.
- **Shadow Touched** (PHB para 7753) - auto-prepares Invisibility + Blindness/Deafness (default L2 Necromancy) at character init. Free-cast tracking deferred.

**Batch 4A wired (10 new feats):**
- **Athlete** (PHB para 7549) - climb_speed = base speed
- **Observant** (PHB para 7701) - skill proficiency in Perception (or Investigation/Insight if already proficient)
- **Resilient** (PHB para 7731) - saving throw proficiency in CON (default; falls through to other abilities if already proficient)
- **Skill Expert** (PHB paras 7774-7775) - one skill proficiency (Perception default) + one expertise (Stealth default)
- **Inspiring Leader** (PHB para 7649) - on battle start, grants level + CHA mod temp HP to up to 6 allies within 30 ft
- **Skulker** (PHB para 7782) - skill_check_advantage["Stealth"] (was already wired for darkvision)
- **Sharpshooter** (PHB para 7760) - skips ranged-attack-in-melee disadvantage. Bypass cover and Long Shots are no-ops because cover and long range disadvantage aren't currently tracked.
- **Spell Sniper** (PHB para 7805) - skips ranged-spell-in-melee disadvantage. Same caveats as Sharpshooter.
- **Poisoner** (PHB para 7715) - poison damage from this character bypasses Resistance (but NOT Immunity, unlike Mother of Sorrows Poison Soul)
- **Telekinetic** (PHB para 7813) - bonus action shove: target within 30 ft, STR save vs DC 8 + PB + best of INT/WIS/CHA mod, push 5 ft on fail. New telekinetic_shove menu entry visible only to characters with the feat.

### Feats WITHOUT combat logic (43 still missing after batch 4A):

**Origin feats (6 missing):**
- crafter, magic_initiate_cleric, magic_initiate_druid, magic_initiate_wizard, musician, skilled
- (tough and lucky already wired in earlier batches.)

**General feats (still missing — level 4+, the biggest group):**
- ability_score_improvement (data only — not really a "feat" in the combat sense), actor, charger, chef, defense (already wired as +1 AC), dual_wielder (already wired as +1 AC), durable, elemental_adept, fey_touched, heavily_armored, keen_mind, lightly_armored, martial_weapon_training, medium_armor_master, moderately_armored, mounted_combatant, ritual_caster, shadow_touched, speedy (already wired as +10 speed), telepathic, weapon_master

**Fighting Style feats (5 missing):**
- blind_fighting, interception, protection, two_weapon_fighting, unarmed_fighting

**Epic Boon feats (8 missing):**
- boon_of_dimensional_travel, boon_of_energy_resistance, boon_of_fate, boon_of_fortitude (already wired as +40 HP), boon_of_recovery, boon_of_skill, boon_of_speed (already wired as +30 speed), boon_of_spell_recall, boon_of_the_night_spirit (already wired as 300 ft darkvision)

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

### Spells with custom handlers implemented (~87 as of 2026-04-08):
true_strike, spiritual_weapon, revivify, heal, ice_storm, finger_of_death, power_word_stun, magic_missile, shield, longstrider, misty_step, bless, lesser_restoration, pass_without_trace, haste, heroism, hex, hunters_mark, mage_armor, web, blindness_deafness, animate_dead, fear, hypnotic_pattern, polymorph, wall_of_force, hold_person, banishment, charm_person, sleep, color_spray, tashas_hideous_laughter, ensnaring_strike, sanctuary, aid, stoneskin, greater_invisibility, fly, fire_shield, spirit_guardians, fog_cloud, darkness, fire_shield (with prompt), spirit_guardians (with prompt), adjust_density, magic_missile (distribution), scorching_ray (distribution), eldritch_blast (distribution), hold_monster, cloudkill, wall_of_fire, stinking_cloud, dominate_person, wall_of_stone, beacon_of_hope, insect_plague, sleet_storm, death_ward, spike_growth, wind_wall, wall_of_thorns, sunbeam, reverse_gravity, holy_weapon, sickening_radiance, storm_sphere, bigbys_hand, tsunami, mass_heal, slow, power_word_kill, earthquake, guardian_of_faith, bane, healing_word, mass_healing_word, feeblemind, eyebite, power_word_heal, sunburst, greater_restoration, command, suggestion, disintegrate, cone_of_cold, chain_lightning, meteor_swarm, maze, mass_suggestion, bestow_curse, vampiric_touch, plant_growth, turn_undead (cleric channel divinity)

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

**Estimated custom-handler gap: ~30-40 spells** out of 367+ currently in `spell_data.nvgt`, plus probably ~150+ more spells not yet added to the catalog (Basic Rules has 300+ descriptions, Griffon's Saddlebag + Book of Ebon Tides + Valda's add hundreds more). Custom handler count was ~42 at session start (2026-04-08), now ~129 after batches 1A-34.

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
- DMG 2024: paragraphs 6632-10570 (~4000 paras of magic items alphabetically) — IN PROGRESS, ~84 items extracted across batches 17B-24B
- Griffon's Saddlebag Book One + Two: hundreds of items. PENDING.
- Tasha's Ch 3, Fizban's, Book of Many Things, Wildemount, Theros, Ravnica, Ravenloft — all have setting-specific items. PENDING.
- Grim Hollow Player Pack: 10+ items. PENDING.
- Valda's Gunslinger: 15 firearms across 3 eras. PENDING.

Current catalog size in game: 128 items (was 35 at session start 2026-04-08).

**Pricing rule:** Use source price. If missing, use rarity defaults: Common 100gp, Uncommon 500gp, Rare 5000gp, Very Rare 20000gp, Legendary 50000gp, Above Legendary 100000gp.

---

## 9. Other Systems From Phase 1 — ALL SHIPPED 2026-04-08

- **Dragonmarks** (Eberron Rising, Wayfinder's, Forge of Artificer) — SHIPPED batch 22. 12 marks live as race options.
- **Supernatural Gifts** (Theros) — SHIPPED batch 23. 8 of 10 gifts live (Lucky and Mythic Companion deferred).
- **Piety system** (Theros) — SHIPPED. 15 gods with source-quoted Devotee/Votary/Disciple/Champion tier text in `Server/combat/piety_data.nvgt`. Tier thresholds 3/10/25/50 per source para 1242. Combatant fields: `piety_god`, `piety_score`, `piety_devotee_uses`.
- **Vestiges of Divergence** (Wildemount) — SHIPPED data + auto-advancement + loot catalog. 8 source-quoted legendary items with Dormant/Awakened (L9-15)/Exalted (L16+) states in `Server/combat/vestiges_data.nvgt` per source paras 9058-9219. State auto-advances by character level via `apply_equipment_bonuses()` (`character_data.nvgt`); L9/L16 crossings trigger an announcement in `send_level_up_choices()` (`battle_manager.nvgt`). **All 8 vestiges now in `loot_data.nvgt`** as droppable Legendary items (`wildemount_<vestige_id>`). **Auto-applied state effects:** Hide of the Feral Guardian (AC +1/+2/+3 by state), Stormgirdle (lightning resist + STR override 19/21/25), Verminshroud (CHA +2 + poison resist + necrotic resist at L9+), Wreath of the Prism (all 5 chromatic resistances at L9+ Awakened). **Still deferred:** Stormgirdle melee lightning rider, Verminshroud cloudkill / unarmed necrotic rider, Danoth's Visor see-invisible vision system, Grimoire Infinitus prepared-spells +N (needs spell prep system), Infiltrator's Key dimension door / pass walls, Spell Bottle spell storage, Wreath of the Prism single-type-at-attunement choice prompt.
- **Heroic Chronicle** (Wildemount) — SHIPPED. 5 homelands, 20 backgrounds (PH + EGW), 20 prophecies in `Server/combat/heroic_chronicle_data.nvgt` per source paras 5617-5900+.
- **Transformations** (Grim Hollow) — SHIPPED. 6 paths × 5 stages in `Server/combat/transformations_data.nvgt` per source paras 2294-2306. Paths: Vampirism, Lycanthropy, Lichdom, Aberrant Horror, Demonic Pact, Seraphic Ascension.
- **Shadow Roads + Fey Courts** (Book of Ebon Tides) — SHIPPED. 14 fey courts + 7 named shadow roads in `Server/combat/ebon_tides_data.nvgt` per source paras 209-2700+.
- **Guild Membership** (Ravnica) — SHIPPED. All 10 guilds with color philosophy, contact perks, equipment perks, and source-themed free spells in `Server/combat/ravnica_guilds_data.nvgt`.
- **Faction Tracks** (Grim Hollow) — SHIPPED. 11 factions of Etharis with Hated→Champion reputation tracks in `Server/combat/factions_data.nvgt` per source paras 4374-4500+.
- **Bastions** (DMG 2024) — SHIPPED. 29 source-quoted special facilities across L5/9/13/17, 7 order types, prerequisites enforced, in `Server/combat/bastions_data.nvgt` per DMG 2024 paras 11759-12420+.
- **Group Patrons** (Tasha's) — SHIPPED. 8 archetypes in `Server/combat/group_patrons_data.nvgt` per source paras 4892-5300+. Group Assistance d4 mechanic per source para 4910. Combatant fields: `group_patron`, `group_assistance_used_this_rest`.
- **Dark Gifts** (Ravenloft) — source missing per earlier extraction confirmation. CANNOT IMPLEMENT.

**Wiring status:** Data modules built, compiled, committed, and pushed to master. Per-character UI integration (creation prompts, level-up unlocks, action menu entries) deferred — these are scaffolding for the upcoming character creation rewrite. Combatant fields exist for Piety + Group Patrons; Vestige/Bastion/Transformation tracking will be per-account JSON.

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

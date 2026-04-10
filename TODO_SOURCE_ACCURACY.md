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
- **Polearm Master** — RESOLVED (commit 2813154). Bonus action butt-strike implemented, and Reactive Strike now wired: entering-reach OA trigger in `check_opportunity_attacks`, gated on `has_feat("polearm_master")` + non-ranged.
- **Order's Demand** — Drop-held-items rider on failed save is not implemented.
- **Mage Slayer 2024 Guarded Mind** — RESOLVED (commit 7a47504). 1/SR auto-succeed on failed INT/WIS/CHA save wired into 22 save failure sites via `try_mage_slayer_guarded_mind`. 1/SR reset in `apply_short_rest`.

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

### Barbarian — RESOLVED 2026-04-09 (most features)
Audited against Basic Rules 2024 paras 2301-2359 (full Barbarian class entry).

| Feature | Level | Source para | Status |
|---|---|---|---|
| Rage (BPS resist, +damage, STR adv, no concentration, 10-rd duration) | 1 | 2301-2313 | ✓ Done |
| Unarmored Defense (10 + DEX + CON) | 1 | 2314-2315 | ✓ Done |
| Weapon Mastery | 1 | 2316-2318 | ✓ Done (system-wide) |
| Danger Sense (advantage on DEX saves) | 2 | 2319-2320 | ✓ Done |
| Reckless Attack | 2 | 2321-2322 | ✓ Done |
| Primal Knowledge (extra skill + STR substitution while raging on 5 skills) | 3 | 2325-2327 | ✓ Done 2026-04-09 — `request_skill_check` swaps the ability to STR for Acrobatics/Intimidation/Perception/Stealth/Survival when class is Barbarian L3+ and raging |
| Extra Attack | 5 | 2330-2331 | ✓ Done |
| **Fast Movement** (+10 ft speed when not in heavy armor) | 5 | 2332-2333 | ✓ Done 2026-04-09 — `apply_class_defaults` Barbarian block adds `cs.speed += 10` at L5+ |
| **Feral Instinct** (advantage on Initiative rolls) | 7 | 2334-2335 | ✓ Done 2026-04-09 — `request_next_initiative` sets `pr.has_advantage = true`; `handle_roll_result` and the bot/auto-roll path both honor advantage on `ROLL_INITIATIVE` |
| **Instinctive Pounce** (move half speed as part of rage entry) | 7 | 2336-2337 | ✓ Done 2026-04-09 — rage handler in `users _dom.nvgt` adds `c.movement_remaining += c.speed / 2` at L7+ |
| **Brutal Strike** (forgo advantage for +1d10 + Forceful/Hamstring effect) | 9 | 2338-2341 | ✓ Done 2026-04-10 — Bonus action toggle + damage + effects wired. Forceful Blow (push 15ft + half speed move), Hamstring (-15ft speed). |
| Relentless Rage (DC 10 CON save when dropped to 0 HP, +5 each use) | 11 | 2342-2344 | ✓ Done |
| **Improved Brutal Strike** (Staggering/Sundering effects) | 13 | 2345-2348 | ✓ Done 2026-04-10 — Staggering Blow (disadvantage on next save, wired into 6 save sites) + Sundering Blow (+5 to next ally attack). |
| **Persistent Rage** (rage lasts 10 minutes / 100 rounds without needing to extend) | 15 | 2349-2351 | ✓ Done 2026-04-09 — rage handler sets `rage_turns_remaining = 100` and `persistent_rage_active = true` at L15+ |
| **Improved Brutal Strike** (2d10 + 2 effects) | 17 | 2352-2353 | ✓ Done 2026-04-10 — 2d10 damage + two different effects from full menu. |
| **Indomitable Might** (STR check/save total ≥ STR score) | 18 | 2354-2355 | ✓ Done 2026-04-09 — new `combatant.apply_indomitable_might(total, ability_id)` helper. Wired into `finalize_roll_result` for STR ability checks via the new `pr.ability_id` field, plus inline at the trip attack / hobbling strike / shield master / shove / grapple sites. Not yet wired into all spell-handler STR saves (Storm Sphere, etc.) — those are rare and queued for a later pass. |
| **Primal Champion** (+4 STR/CON, max 25) | 20 | 2358-2359 | ✓ Done 2026-04-09 — `apply_class_defaults` adds the bonus with the cap |

**Brutal Strike infrastructure plan (deferred):** Add `brutal_strike_pending` flag on combatant + a `brutal_strike` bonus action menu entry. When set, the next Strength-based weapon attack drops Reckless Attack advantage (must not have disadvantage). On hit, deal +1d10 (or +2d10 at L17) of the weapon's damage type and queue a `pending_brutal_strike_choice` prompt with the available effects (Forceful/Hamstring at L9, +Staggering/Sundering at L13). Player picks via numeric key. At L17, repeat the prompt for a second different effect.

Other base class features that still need the same audit:
- **Barbarian (Brutal Strike line above is the only remaining gap)**

### Bard — FULLY RESOLVED 2026-04-09
Audited against Basic Rules 2024 paras 2722-2765 (full Bard class entry).

| Feature | Level | Source para | Status |
|---|---|---|---|
| Bardic Inspiration (BA, 60 ft, d6→d12) | 1 | 2722-2727 | ✓ Done |
| Spellcasting (full caster, CHA) | 1 | 2728-2739 | ✓ Done |
| Expertise (2 skills L2, +2 more L9) | 2/9 | 2740-2742 | ✓ Done (system-wide expertise field) |
| Jack of All Trades (half-prof on non-prof skill checks) | 2 | 2743-2745 | ✓ Done — `combatant.jack_of_all_trades` flag set in `character_data.nvgt` and consumed by `get_skill_bonus` |
| Bard Subclass | 3 | 2749-2750 | ✓ Done |
| **Font of Inspiration** (regen BI on Short Rest, spend slot to regain one) | 5 | 2753-2755 | ✓ Done 2026-04-09 — `font_of_inspiration_active` flag set on Bard init at L5+. New `font_of_inspiration` handler in `users _dom.nvgt` is a no-action menu entry that finds the lowest-level available spell slot, expends it, and increments `bardic_inspiration_uses` (capped at CHA mod). Short-rest regen is naturally handled because in-session we only have long rests, which already restore all BI. |
| **Countercharm** (Reaction reroll on Charmed/Frightened save fail) | 7 | 2756-2757 | ✓ Done 2026-04-09 — `countercharm_active` flag set on Bard init at L7+. New `try_countercharm_reroll` helper in `battle_manager.nvgt` scans for any L7+ Bard ally with `countercharm_active` and reaction available within 30 ft of the failing save target (self allowed per RAW), consumes the reaction, rerolls the save with advantage. Wired into 15 Charm/Frighten failed-save sites: cause_fear AoE/single, hypnotic_pattern, phantasmal_killer, mass_suggestion, command, suggestion, eyebite, dominate_person, charm_person, dominate_monster, enthrall, charm_monster, dominate_beast, weird. Polymorph's COND_CHARMED is an implementation marker (not a real charm) so it is intentionally skipped. |
| Magical Secrets (broader spell list at L10) | 10 | 2758 | ✓ Done — `magical_secrets_active` flag now set on Bard init at L10+ for client UI awareness. Out-of-combat spell list expansion handled by existing spell menu. |
| **Superior Inspiration** (top up BI to 2 on Initiative) | 18 | 2760-2761 | ✓ Done 2026-04-09 — `superior_inspiration_active` flag set on Bard init at L18+; `request_next_initiative` restores BI uses to 2 if fewer for Bards with the flag. |
| **Words of Creation** (Power Word Heal/Kill always prepared, target second creature within 10 ft) | 20 | 2764 | ✓ Done 2026-04-09 — `words_of_creation_active` flag set on Bard init at L20+. Power Word Heal and Power Word Kill are auto-added to `c.prepared_spells` for L20 Bards; spell catalog `class_list` updated to "wizard,bard" so they appear in the bard's spell menu. Both `power_word_heal` and `power_word_kill` cast handlers in `battle_manager.nvgt` check `c.words_of_creation_active` and apply the spell to a second creature within 10 ft of the first target — Power Word Heal auto-picks the most-injured ally, Power Word Kill auto-picks the lowest-HP enemy (highest kill chance). |

### Cleric — RESOLVED 2026-04-09 (almost all features)
Audited against Basic Rules 2024 paras 3589-3630 (full Cleric class entry).

| Feature | Level | Source para | Status |
|---|---|---|---|
| Spellcasting (full caster, WIS, prepared) | 1 | 3593-3599 | ✓ Done |
| **Divine Order** (Protector or Thaumaturge — once-per-character choice) | 1 | 3600-3603 | ✓ Done 2026-04-09 — `divine_order` field on character_sheet + combatant. Configured via Shift+P → "Set Cleric Divine Order". Thaumaturge bonus to Arcana/Religion checks (WIS mod, min +1) wired in `finalize_roll_result`. Protector heavy-armor + martial weapon proficiency at character creation deferred to a future `apply_class_defaults` pass. |
| Channel Divinity (Turn Undead) | 2 | 3604-3607 | ✓ Done |
| **Channel Divinity: Divine Spark** (heal OR radiant/necrotic damage, scales L7/13/18) | 2 | 3608-3610 | ✓ Done 2026-04-09 — three bonus action handlers (`divine_spark_heal`, `divine_spark_radiant`, `divine_spark_necrotic`) in `users _dom.nvgt`. WIS-mod scaling, 1d8→4d8 dice progression, half-on-save for damage variants, all source-quoted. Client menu entries appear at Cleric L2+. |
| Sear Undead (Channel Divinity replaces Turn Undead at L5+) | 5 | 3615-3616 | ✓ Done (folded into existing `turn_undead` handler) |
| **Blessed Strikes** (Divine Strike OR Potent Spellcasting — choose at L7) | 7 | 3617-3620 | ✓ Done 2026-04-09 — `blessed_strikes_choice` field. Divine Strike: `roll_divine_strike` helper applies +1d8 necrotic/radiant once per turn on weapon hits, hooked into the attack damage path in `battle_manager.nvgt`. Potent Spellcasting: `potent_spellcasting_bonus` adds WIS mod to Cleric cantrip damage (sacred_flame inline path + generic spell save damage path both updated). Choice configured via Shift+P. |
| **Divine Intervention** (cast any Cleric spell L5- without a slot, 1/long rest) | 10 | 3621-3622 | ✓ Done 2026-04-09 — bonus action sets `divine_intervention_ready` flag; next cast of any Cleric spell ≤L5 in `handle_cast` consumes the flag instead of a slot. Player picks the spell normally via the cast menu (no auto-pick per source-only mandate). |
| **Improved Blessed Strikes** (Divine Strike +2d8 / Potent Spellcasting WIS*2 temp HP) | 14 | 3623-3626 | ✓ Done 2026-04-09 — `roll_divine_strike` doubles dice at L14+; `apply_improved_potent_temp_hp` grants WIS*2 temp HP after sacred_flame and the generic Cleric cantrip save path. |
| **Greater Divine Intervention** (Wish) | 20 | 3629-3630 | ✗ DEFERRED — requires Wish spell infrastructure which is not yet implemented. Listed in spell catalog but not handled. |

**Player choice infrastructure:** Three new Phase 1 config commands (`set_divine_order`, `set_blessed_strikes`, `set_divine_strike_damage_type`) added to the Shift+P menu. They persist to `account.data` so Cleric choices survive across sessions. Source-only rule respected — players configure their own choices, no auto-pick.

### Druid — RESOLVED 2026-04-09 (most features)
Audited against Basic Rules 2024 paras 4052-4445 (full Druid class entry).

| Feature | Level | Source para | Status |
|---|---|---|---|
| Spellcasting (full caster, WIS, prepared) | 1 | 4372-4383 | ✓ Done |
| Druidic (Speak with Animals always prepared) | 1 | 4384-4386 | ✓ Done — auto-prepared in `character_data.nvgt` Druid init block (line 2359). |
| **Primal Order** (Magician or Warden — once-per-character choice) | 1 | 4387-4390 | ✓ Done 2026-04-09 — `primal_order` field on character_sheet + combatant. Configured via Shift+P → "Set Druid Primal Order". Magician bonus to Arcana/Nature checks (WIS mod, min +1) wired in `finalize_roll_result`. Warden martial-weapon + medium-armor proficiency at character creation deferred to a future `apply_class_defaults` pass. |
| Wild Shape (BA, scale 2/3/4 uses at L2/6/14, temp HP) | 2 | 4391-4419 | ✓ Done — and 2026-04-09 added the use-count scaling to `apply_class_defaults` (was hard-coded to 2). |
| **Wild Companion** (Magic action, expend slot or WS use, cast Find Familiar) | 2 | 4420-4422 | ✓ Done 2026-04-09 — bonus action handler in `users _dom.nvgt` consumes WS use first, falls back to lowest spell slot. Find Familiar narrative-only (no grid familiar pet, matches no-pet-grid policy). Client menu entry visible at Druid L2+. |
| Druid Subclass | 3 | 4423-4424 | ✓ Done |
| **Wild Resurgence** (slot → WS use 1/turn; WS use → L1 slot 1/long rest) | 5 | 4427-4429 | ✓ Done 2026-04-09 — two no-action bonus action handlers (`wild_resurgence_slot_to_use` and `wild_resurgence_use_to_slot`). Per-turn and per-rest tracking flags reset at turn start (slot → use) and on long rest (use → slot). |
| **Elemental Fury** (Potent Spellcasting OR Primal Strike — choose at L7) | 7 | 4430-4433 | ✓ Done 2026-04-09 — `elemental_fury_choice` field. Primal Strike: `roll_primal_strike` helper applies +1d8 cold/fire/lightning/thunder once per turn on weapon and Wild Shape attacks (mirrors Cleric Divine Strike). Potent Spellcasting: `druid_potent_spellcasting_bonus` adds WIS mod to Druid cantrip damage (produce_flame inline + generic spell save damage path both updated). Damage type sub-choice persisted. Configured via Shift+P. |
| **Improved Elemental Fury** (Primal Strike +2d8 / Potent Spellcasting cantrip range +300 ft) | 15 | 4434-4437 | ✓ Done 2026-04-09 — Primal Strike doubles dice at L15+ via `roll_primal_strike`. Potent Spellcasting cantrip range extension is descriptive only (range checks pass at +300 ft regardless since combat grid is small). |
| **Beast Spells** (cast spells in Wild Shape form, except costed material components) | 18 | 4438-4439 | ✓ Done 2026-04-10 — `beast_spells_active` flag set on Druid L18+ init; `handle_cast` bypasses Wild Shape spellcasting block when flag is set. |
| **Archdruid: Evergreen Wild Shape** (regen WS on Initiative if 0 uses) | 20 | 4444 | ✓ Done 2026-04-10 — wired in `request_next_initiative` after Dire Gambit block. Restores 1 WS use when rolling initiative with 0 uses remaining. |
| **Archdruid: Nature Magician** (convert WS uses to a single spell slot, 1/long rest) | 20 | 4445 | ✗ DEFERRED — needs a player-prompt "how many uses to convert" UI. Per-rest flag is in place. |

**Player choice infrastructure:** Three new Phase 1 config commands (`set_primal_order`, `set_elemental_fury`, `set_primal_strike_damage_type`) added to the Shift+P menu. They persist to `account.data` so Druid choices survive across sessions.


### Fighter Audit (PHB 2024 Basic Rules paras 4967-5135) — completed 2026-04-09

| Feature | Lvl | Source para | Status |
|---|---|---|---|
| Fighting Style (feat selection from list) | 1 | 5100-5102 | ✓ Done — chooses a Fighting Style feat at creation; feat data has the styles. |
| **Second Wind** (BA, heal 1d10+lvl, scaling uses) | 1 | 5103-5106 | ✓ Done 2026-04-09 — was a single bool; now `second_wind_uses_remaining` / `second_wind_uses_max` int pair. 2 uses L1-3, 3 uses L4-9, 4 uses L10+. Bonus action handler decrements properly and announces remaining. |
| **Weapon Mastery** (3/4/5/6 weapons by level) | 1 | 5107-5109 | ✓ Done 2026-04-10 — All 7 mastery properties (Push/Sap/Slow/Topple/Vex/Cleave/Graze) wired into attack resolution. `main_hand_mastery` field plumbed from `character_data.nvgt` weapon table through `character_sheet` to `combatant`. Nick deferred (requires Light property TWF system). |
| **Action Surge** (1 use L2, 2 uses L17) | 2 | 5110-5112 | ✓ Done — properly tracked and handled. |
| **Tactical Mind** (spend Second Wind on failed ability check, refund on still-fail) | 2 | 5113-5114 | ✓ Done 2026-04-09 — new prompt chain entry after Lucky/Heroic. `pending_tactical_mind_prompt` struct + `maybe_prompt_tactical_mind` + `handle_tactical_mind_response` server-side. New `tactical_mind_prompt`/`tactical_mind_response` message types. Client `prompt_tactical_mind_choice` + `check_tactical_mind_prompt_input` (T to use, Escape to skip). Use is refunded if the +1d10 still fails to clear the DC, per source. Bots auto-use when `failure_margin <= 5` (1d10 average). |
| Fighter Subclass | 3 | 5115-5116 | ✓ Done — Champion + many extra subclasses. |
| Ability Score Improvement | 4/6/8/12/14/16 | 5117-5118 | ✓ Done. |
| Extra Attack | 5 | 5119-5120 | ✓ Done. |
| **Tactical Shift** (Second Wind also grants half-Speed OA-free move) | 5 | 5121-5122 | ✓ Done 2026-04-09 — `tactical_shift_feet_remaining` field on combatant. When Second Wind is activated at L5+, that pool is set to half speed and `movement_remaining` is bumped. `check_opportunity_attacks` consumes pool greedily and suppresses OA while feet remain. Cleared at start of turn. |
| **Indomitable** (failed save reroll, +Fighter level) | 9 | 5123-5125 | ✓ Done — 1/2/3 uses at L9/13/17, properly hooked in `handle_save_result`. |
| **Tactical Master** (replace weapon mastery with Push/Sap/Slow) | 9 | 5126-5127 | ✓ Done 2026-04-10 — Bonus action toggle in users_dom.nvgt with Push/Sap/Slow sub-choice. Mastery override fires in weapon mastery block, clears after one attack. Client menu entry with sub-menu for L9+ Fighters. |
| Two Extra Attacks | 11 | 5128-5129 | ✓ Done. |
| **Studied Attacks** (advantage on next attack vs creature you missed) | 13 | 5130-5131 | ✓ Done — `studied_attacks_active` flag + `studied_attacks_target_id`. Set on miss, granted as advantage and consumed on next attack against the same target. |
| Action Surge (two uses) | 17 | 5082 | ✓ Done — `action_surge_uses` upgrades at L17. |
| Indomitable (three uses) | 17 | 5082 | ✓ Done. |
| Epic Boon | 19 | 5132-5133 | ✓ Done — Epic Boon feat catalog ships boon_of_combat_prowess et al. |
| **Three Extra Attacks** (4 attacks per Attack action) | 20 | 5134-5135 | ✓ FIXED 2026-04-09 — was triggering at L17 (wrong), now triggers at L20 per source. |

### Monk Audit (PHB 2024 Basic Rules paras 5156-5395) — completed 2026-04-09 (batch 1)

| Feature | Lvl | Source para | Status |
|---|---|---|---|
| **Martial Arts: Bonus Unarmed Strike** (BA, free) | 1 | 5319 | ✓ Done 2026-04-09 — new `martial_arts_unarmed_strike` bonus action handler that calls `start_flurry_strike(c, target, 0)` to make a single bonus unarmed strike with no Focus cost. |
| **Martial Arts Die scaling** (1d6→1d8→1d10→1d12) | 1/5/11/17 | 5320 | ✓ Done — `monk_martial_arts_die()` already correct in `battle_manager.nvgt`. |
| **Dexterous Attacks** (DEX for unarmed/Monk weapon attack/dmg) | 1 | 5321 | ✓ Done — `get_weapon_attack_ability_mod` already returns DEX for unarmed Monks. |
| **Unarmored Defense** (10 + DEX + WIS unarmored AC) | 1 | 5322-5323 | ✓ Done — `has_unarmored_defense` flag and AC calc in `character_data.nvgt`. |
| **Monk's Focus** (Focus Points = Monk level, Flurry/Patient/Step) | 2 | 5324-5331 | ✓ Done 2026-04-09 — `focus_points` already initialized; new `focus_points_max` cap field. Patient Defense and Step of the Wind handlers added (were entirely missing). |
| **Patient Defense** (BA Disengage; spend 1 FP for Disengage+Dodge) | 2 | 5330 | ✓ Done 2026-04-09 — new `patient_defense` bonus action handler. Free Disengage by default; `spend_focus` flag adds Dodge. Heightened Focus L10 grants `2 × MA die` temp HP automatically. |
| **Step of the Wind** (BA Dash; spend 1 FP for Disengage+Dash, jump x2) | 2 | 5331 | ✓ Done 2026-04-09 — new `step_of_the_wind` bonus action handler. Free Dash by default; `spend_focus` flag adds Disengage. (Heightened Focus ally-move deferred — needs targeting prompt.) |
| **Unarmored Movement** (+10/15/20/25/30 ft at L2/6/10/14/18) | 2/6/10/14/18 | 5332-5333 | ✓ Done 2026-04-09 — was entirely missing for Monk class. Added speed bonus block in `character_data.nvgt` Monk init that respects unarmored + no shield gating. |
| **Uncanny Metabolism** (regain all FP + heal lvl + MA die at initiative) | 2 | 5334-5336 | ✓ Done 2026-04-09 — new `uncanny_metabolism_available` flag (1/long rest). Exposed as a free bonus action so the player chooses when to spend it during the first round (source ties to initiative roll which the simulator pre-rolls). New `uncanny_metabolism` bonus action menu entry. |
| **Deflect Attacks** (reaction, reduce 1d10+DEX+lvl B/P/S; redirect at 0) | 3 | 5337-5339 | PARTIAL 2026-04-09 — base reaction wired into existing reaction prompt system; reduces incoming damage in `apply_damage` via new `deflect_attacks_reduction` field; gated to B/P/S unless L13+. Redirect target picker (Focus Point spend on damage reduced to 0) deferred — needs new prompt path. |
| **Monk Subclass** | 3 | 5340-5341 | ✓ Done — Warrior of the Open Hand and 10+ extra subclasses. |
| **Slow Fall** (reaction reduces fall damage by 5x lvl) | 4 | 5344-5345 | DEFERRED — combat doesn't currently model falling damage. |
| **Extra Attack** (2 attacks per Attack action) | 5 | 5346-5347 | ✓ Done — `cs.extra_attacks = 1` set at L5. |
| **Stunning Strike** (1/turn, 1 FP, CON save or Stunned until start of monk's next turn; speed halved + adv on next attack on success) | 5 | 5348-5349 | ✓ FIXED 2026-04-09 — was using stale 2014 wording ("end of next turn" + repeating saves). Now: stuns until start of monk's next turn (cleared in `start_turn` block when source monk's turn comes around). Success rider added: `stunning_strike_speed_orig` halves the target's speed and `stunning_strike_advantage_pending` grants advantage on the next attack roll against them. |
| **Empowered Strikes** (Force damage option on unarmed) | 6 | 5350-5351 | ✓ Done — `empowered_strikes_active` flag set at L6+. (Damage type currently auto-defaults to original; player choice prompt deferred.) |
| **Evasion** (DEX save: 0 dmg on success, half on failure) | 7 | 5352-5354 | ✓ Done — `evasion_active` flag set at L7+ and applied in `apply_save_damage`. |
| **Acrobatic Movement** (climb walls + run on liquids unarmored) | 9 | 5355-5356 | DEFERRED — combat doesn't currently model vertical surfaces or liquid terrain. |
| **Heightened Focus** (Flurry +1 strike, Patient Def temp HP, Step ally) | 10 | 5357-5361 | PARTIAL 2026-04-09 — Patient Defense temp HP rider implemented (batch 1). Flurry of Blows third strike implemented (batch 3) by passing chain count of 2 instead of 1 to `start_flurry_strike`. Step of the Wind ally-carry still deferred — needs targeting prompt. |
| **Self-Restoration** (auto remove Charmed/Frightened/Poisoned at end of turn) | 10 | 5362-5364 | ✓ Done 2026-04-09 — `self_restoration_active` flag and end-of-turn cleanup in `advance_turn` (highest-priority condition removed first). |
| **Subclass feature** | 11 | 5256 | ✓ Done. |
| **Deflect Energy** (Deflect Attacks works on any damage type) | 13 | 5365-5366 | ✓ Done 2026-04-09 — Deflect Attacks reaction option is offered for any damage type when defender is L13+ (the L3 gating only enforces B/P/S below L13). |
| **Disciplined Survivor** (all save profs + reroll failed save with FP) | 14 | 5367-5369 | ✓ Done 2026-04-10 — all save proficiencies set at L14+. `try_disciplined_survivor_reroll` helper wired into 22+ save failure sites. Spends 1 FP, smart-spend only if nat 20 + bonus >= DC. |
| **Perfect Focus** (regain to 4 FP on initiative if 3 or fewer) | 15 | 5370-5371 | ✓ Done 2026-04-09 — applied in `finish_initiative()` immediately after initiative rolls. Tops up to 4 if current < 4. Announced to players. Uncanny Metabolism path unaffected (UM fully refills anyway). |
| **Subclass feature** | 17 | 5292 | ✓ Done. |
| **Superior Defense** (3 FP, 1 minute Resistance to all but Force) | 18 | 5372-5373 | ✓ Done 2026-04-09 — new `superior_defense_active` + `superior_defense_rounds_remaining` fields, bonus action handler, damage halving in `apply_damage` for any non-Force damage type, round-tick in `start_turn`, ends if Incapacitated. |
| **Epic Boon** | 19 | 5374-5375 | ✓ Done — Epic Boon feat catalog. |
| **Body and Mind** (+4 DEX/WIS, max 25) | 20 | 5376-5377 | ✓ Done 2026-04-09 — `body_and_mind_applied` one-time guard in Monk init block. Boost capped at 25. |

**Pending follow-up Monk batches:**
- Deflect Attacks redirect target picker (Focus Point spend, 5ft melee / 60ft ranged, DEX save, 2× MA die + DEX mod same damage type)
- ~~Disciplined Survivor failed-save reroll prompt chain (L14)~~ RESOLVED 2026-04-10 — `try_disciplined_survivor_reroll` wired into 22+ save failure sites.
- Heightened Focus Step of the Wind ally-carry (needs targeting prompt)
- Empowered Strikes Force/normal damage type prompt (L6) — could be a persistent toggle bonus action

### Paladin Audit (2026-04-09) — Basic Rules 2024 paras 5396-5691

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Lay On Hands** (5×level pool, Bonus Action heal, 5 HP cure Poisoned) | 1 | 5637-5640 | ✓ Done — pool sized correctly in `character_data.nvgt`, bonus action handler in `users _dom.nvgt` accepts `cleanse_conditions` for Poisoned (always) plus L14 Restoring Touch list. |
| **Spellcasting** (CHA, Holy Symbol focus) | 1 | 5641-5649 | ✓ Done — `cs.is_caster=true`, `spellcasting_ability=ABILITY_CHA`, half-caster slot table. |
| **Weapon Mastery** (2 weapons) | 1 | 5650-5652 | ✓ Done 2026-04-10 — mastery properties wired to attack resolution. |
| **Fighting Style** (incl. Blessed Warrior cleric cantrips) | 2 | 5653-5655 | DEFERRED — Fighting Style feat selection at character creation not yet implemented for Paladin. Blessed Warrior cantrip choice deferred. |
| **Paladin's Smite** (Divine Smite always prepared, 1 free cast/LR) | 2 | 5656-5657 | ✓ Done 2026-04-09 — new `paladins_smite_free_cast_used` flag, divine_smite bonus action handler tries the free cast first (L1 base = 2d8 radiant) before consuming a slot. |
| **Channel Divinity** (2 uses, regain 1 SR, +1 at L11) + Divine Sense | 3 | 5658-5662 | ✓ Done — channel divinity uses present, Divine Sense flavor announce; subclass-specific CD effects (Sacred Weapon, Vow of Enmity, Inspiring Smite, Nature's Wrath) implemented. |
| **Paladin Subclass** | 3 | 5663-5664 | ✓ Done — 9+ subclasses (Devotion, Vengeance, Ancients, Glory, Conquest, Watchers, Redemption, Hearth, Zeal). |
| **Ability Score Improvement** | 4/8/12/16 | 5669-5670 | ✓ Done — global feat-grant system. |
| **Extra Attack** (2 attacks) | 5 | 5671-5672 | ✓ Done — `cs.extra_attacks=1` set in init. |
| **Faithful Steed** (Find Steed always prepared, 1 free cast/LR) | 5 | 5673-5675 | PARTIAL 2026-04-09 — new `faithful_steed_free_cast_used` flag added; Find Steed companion summon (mount entity with stats) deferred per existing Beast Master/Steel Defender pattern. |
| **Aura of Protection** (10ft Emanation, +CHA mod to saves) | 6 | 5676-5679 | ✓ Done 2026-04-10 — refresh_paladin_auras() scans all friendly Paladins by position. Ally coverage for Aura of Protection (CHA mod to saves within 10ft/30ft at L18) and Aura of Courage (Frightened immunity within range). Called at turn start and after movement. |
| **Abjure Foes** (CD action, 60ft, CHA mod targets, WIS save Frightened) | 9 | 5680-5681 | ✓ Done 2026-04-10 — Auto-targets nearest CHA mod (min 1) hostiles within 60ft. Full WIS save failure chain. Client menu entry for all Paladins L9+. |
| **Aura of Courage** (Frightened immunity in aura) | 10 | 5682-5683 | ✓ Done 2026-04-10 — Ally coverage wired via refresh_paladin_auras(). Frightened immunity applied to allies within 10ft (30ft at L18) of any L10+ Paladin. |
| **Radiant Strikes** (+1d8 radiant on melee weapon/unarmed hit) | 11 | 5684-5685 | ✓ Done 2026-04-09 — block added in `battle_manager.nvgt` after Druid Primal Strike: every qualifying hit adds 1d8 radiant. Excludes ranged weapons per source ("Melee weapon or Unarmed Strike"). |
| **Restoring Touch** (LoH heals + remove condition list, 5 HP each) | 14 | 5686-5687 | ✓ Done — `lay_on_hands` handler already accepts L14 conditions (Blinded/Charmed/Deafened/Frightened/Paralyzed/Stunned) at 5 HP each. |
| **Aura Expansion** (10ft → 30ft) | 18 | 5688-5689 | ✓ Done 2026-04-10 — refresh_paladin_auras() uses 30ft range for L18+ Paladins. |
| **Epic Boon** | 19 | 5690-5691 | ✓ Done — Epic Boon feat catalog. |

**Pending follow-up Paladin batches:**
- ~~Abjure Foes L9 Channel Divinity action~~ RESOLVED 2026-04-10 — auto-targets nearest CHA mod hostiles within 60ft, WIS save with full failure chain, Frightened on fail.
- ~~Aura range loop for ally coverage of Aura of Protection (saves), Aura of Courage (Frightened immunity), and L18 Aura Expansion (10ft → 30ft).~~ RESOLVED 2026-04-10 — refresh_paladin_auras() scans all friendly Paladins by position. Ally coverage for Aura of Protection + Aura of Courage within 10ft/30ft at L18. Called at turn start and after movement.
- Faithful Steed L5 mount summon (full companion entity) — deferred along with the rest of the mount system.
- Fighting Style at character creation flow + Blessed Warrior cleric cantrip selection prompt.
- ~~Weapon Mastery property application~~ RESOLVED 2026-04-10 — 7 properties wired. ~~Fighter Tactical Master swap still pending.~~ RESOLVED 2026-04-10 — Tactical Master bonus action toggle with Push/Sap/Slow sub-choice wired.

### Ranger Audit (2026-04-09) — Basic Rules 2024 paras 5906-6194

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Favored Enemy** (Hunter's Mark always prepared, free casts scale 2/3/4/5/6) | 1 | 6155-6157 | ✓ Done 2026-04-09 — `grant_free_cast()` helper sets explicit count; scaling 2 (L1-4), 3 (L5-8), 4 (L9-12), 5 (L13-16), 6 (L17+). |
| **Spellcasting** (WIS, half-caster, Druidic Focus) | 1 | 6158-6164 | ✓ Done — `cs.is_caster=true`, `spellcasting_ability=ABILITY_WIS`, half-caster slot table. |
| **Weapon Mastery** (2 weapons) | 1 | 6165-6166 | ✓ Done 2026-04-10 — mastery properties wired to attack resolution. |
| **Deft Explorer** (Expertise in 1 of your skills) | 2 | 6167-6168 | DEFERRED — needs player choice prompt at L2 (and again with the 2 added skills at L9 in same feature line). |
| **Fighting Style** (incl. Druidic Warrior druid cantrips) | 2 | 6169-6170 | DEFERRED — Fighting Style feat selection at character creation not yet implemented for Ranger. Druidic Warrior cantrip choice deferred. |
| **Ranger Subclass** | 3 | 6171-6172 | ✓ Done — 6+ subclasses (Hunter, Gloom Stalker, Beast Master, Fey Wanderer, Drakewarden, Horizon Walker). |
| **Ability Score Improvement** | 4/8/12/16/19 | 6173 | ✓ Done — global feat-grant system. |
| **Roving** (+10 ft speed, climb/swim speed = speed) | 5 | 6174-6175 | ✓ Done 2026-04-09 — applied at init; +10 ft speed with matching climb/swim. |
| **Extra Attack** (2 attacks) | 5 | 6176-6177 | ✓ Done — `cs.extra_attacks=1` set in init. |
| **Expertise** (2 more skills) | 9 | 6177 | DEFERRED — needs player choice prompt at L9. |
| **Tireless** (Magic action 1d8+WIS temp HP, WIS-mod uses/LR; halve exhaustion on SR) | 10 | 6178-6180 | PARTIAL 2026-04-09 — temp HP grant via bonus action menu, WIS mod uses tracked, server enforces action consumption. Exhaustion halving on SR deferred (no exhaustion subsystem yet). |
| **Nature's Veil** (Bonus Action self-Invisible until end of next turn, WIS-mod uses/LR) | 14 | 6184-6186 | ✓ Done 2026-04-09 — full implementation: bonus action handler, condition application, 2-tick rounds_remaining, end-of-turn cleanup in `advance_turn`. |
| **Relentless Hunter** (Hunter's Mark concentration cannot be broken by damage) | 13 | 6182-6183 | ✓ Done 2026-04-09 — short-circuit at top of `check_concentration` when target is L13+ Ranger and concentration spell is "Hunter's Mark". |
| **Precise Hunter** (advantage on attack rolls vs your Hunter's Mark target) | 17 | 6187-6188 | ✓ Done 2026-04-09 — advantage flag set in `apply_attack_advantage_state` after Vow of Enmity check. |
| **Feral Senses** (Blindsight 30 ft) | 18 | 6189-6190 | ✓ Done 2026-04-09 — sets `blindsight_range = 30` if higher than current at init. |
| **Foe Slayer** (Hunter's Mark damage die d6 → d10) | 20 | 6193-6194 | ✓ Done 2026-04-09 — Hunter's Mark damage line now picks d10 when caster is L20+ Ranger. |
| **Epic Boon** | 19 | 6191-6192 | ✓ Done — Epic Boon feat catalog. |

**Pending follow-up Ranger batches:**
- Deft Explorer L2 Expertise player choice (Skill Expertise selection prompt at character creation/level-up).
- Expertise L9 (2 more skills player choice).
- Fighting Style L2 (Archery / Defense / Druidic Warrior / Two-Weapon Fighting / Thrown Weapon Fighting / Blind Fighting). Druidic Warrior also requires a druid-cantrip selection prompt.
- Tireless L10 exhaustion-halving on Short Rest (deferred until exhaustion subsystem exists).
- ~~Weapon Mastery property application~~ RESOLVED 2026-04-10.

### Rogue Audit (2026-04-09) — Basic Rules 2024 paras 6443-6605

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Expertise** (2 skill proficiencies → expertise) | 1 | 6529-6531 | ✓ Done — Rogue init grants expertise on 2 skills (default Stealth + Perception). Player choice at character creation deferred. |
| **Sneak Attack** (1d6 → 10d6, once per turn, finesse/ranged + advantage OR ally within 5ft no disadvantage) | 1 | 6537-6540 | ✓ Done 2026-04-09 — `apply_subclass_on_hit_damage` now has the base case. Tracks `sneak_attack_used_this_turn` (reset in `advance_turn`). Scaling: `(level+1)/2` dice. Conditions: weapon attack + finesse/ranged + (advantage OR ally-within-5ft-of-target with no disadvantage on roll). |
| **Thieves' Cant** (lore — speak/write Thieves' Cant) | 1 | 6541-6542 | DEFERRED — narrative-only, no combat impact. |
| **Weapon Mastery** (2 weapons) | 1 | 6543-6544 | ✓ Done 2026-04-10 — mastery properties wired to attack resolution. |
| **Cunning Action** (Bonus Action: Dash, Disengage, Hide) | 2 | 6545-6546 | ✓ Done — bonus action handler routes Dash/Disengage/Hide. |
| **Rogue Subclass** | 3 | 6547 | ✓ Done — 12 subclasses implemented. |
| **Steady Aim** (Bonus Action: Advantage on next attack this turn, Speed = 0 until end of turn) | 3 | 6550-6551 | ✓ Done 2026-04-09 — bonus action handler in `users _dom.nvgt`, `steady_aim_pending` flag, advantage flag set in `apply_attack_advantage_state`, `movement_remaining = 0` enforces speed=0 clause. Requires unmoved Speed (`movement_remaining >= speed`) per source. Client menu entry gated. |
| **Cunning Strike** (Poison/Trip/Withdraw effects, swap SA dice for riders) | 5 | 6552-6560 | ✓ Done 2026-04-10 — Toggle via bonus action menu, dice cost subtracted from SA before rolling. |
| **Ability Score Improvement** | 4/8/12/16/19 | 6549 | ✓ Done — global feat-grant system. |
| **Uncanny Dodge** (Reaction halves attack damage round down) | 5 | 6561-6562 | ✓ Done 2026-04-09 — reaction option added to `reaction_options` array. `uncanny_dodge_pending` flag set in `handle_reaction_response`, consumed in `apply_damage` to halve final damage post-reductions. Gated on `!Incapacitated`. Client text label added. |
| **Evasion** (DEX save vs half damage → no damage on success, half on fail) | 7 | 6563-6564 | ✓ Done — `evasion_active` flag was missing init at L7 (only Monk got it); fixed in batch 0 (commit 5e78f1c). |
| **Reliable Talent** (treat d20 ≤9 as 10 on proficient checks) | 7 | 6565-6566 | ✓ Done 2026-04-09 — was incorrectly gated at L11; corrected to L7 in `character_data.nvgt` init. Comment in `finalize_roll_result` updated to L7 + para 6565-6566. |
| **Improved Cunning Strike** (use 2 effects) | 11 | 6567-6568 | ✓ Done 2026-04-10 — Two effects allowed at L11+ via second picker. |
| **Devious Strikes** (Daze/Knock Out/Obscure effects added to Cunning Strike) | 14 | 6569-6573 | ✓ Done 2026-04-10 — Daze (2d6), Knock Out (6d6), Obscure (3d6) added to CS menu. Daze enforced at turn start. |
| **Slippery Mind** (proficiency in WIS and CHA saves) | 15 | 6574-6575 | ✓ Done 2026-04-09 — init grants both save proficiencies. |
| **Elusive** (no attack roll has Advantage against you unless Incapacitated) | 18 | 6576-6577 | ✓ Done 2026-04-09 — `elusive_active` flag set at L18 init; override at end of `apply_attack_advantage_state` clears advantage when defender is L18+ Rogue and not Incapacitated. |
| **Epic Boon** | 19 | 6578-6579 | ✓ Done — Epic Boon feat catalog. |
| **Stroke of Luck** (1/short rest: turn a failed D20 Test into a 20) | 20 | 6580-6582 | ✓ Done — Turns miss into nat 20 crit, consumes flag (1/LR). |

**Pending follow-up Rogue batches:**
- ~~Cunning Strike L5~~ RESOLVED 2026-04-10 — Toggle via bonus action menu, dice cost subtracted from SA before rolling.
- ~~Improved Cunning Strike L11~~ RESOLVED 2026-04-10 — Two effects allowed at L11+.
- ~~Devious Strikes L14~~ RESOLVED 2026-04-10 — Daze (2d6), Knock Out (6d6), Obscure (3d6) wired.
- ~~Stroke of Luck L20 auto-prompt~~ RESOLVED 2026-04-10 — `try_stroke_of_luck_save` wired into 40+ save failure sites.
- Sneak Attack interactions: verify it triggers correctly for Soulknife Psychic Blades and Inquisitive Insightful Fighting (existing subclass riders).

### Sorcerer Audit (2026-04-09) — Basic Rules 2024 paras 6632-7044

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Spellcasting** (CHA, Arcane Focus) | 1 | 6952-6962 | ✓ Done — `cs.is_caster=true`, `spellcasting_ability=ABILITY_CHA`. |
| **Innate Sorcery** (Bonus Action: +1 spell save DC + Advantage on Sorcerer spell attacks for 1 minute, 2/LR) | 1 | 6963-6967 | ✓ Done 2026-04-09 — bonus action handler in `users _dom.nvgt`, `innate_sorcery_active` flag, +1 DC in `spell_save_dc()`, advantage in `apply_attack_advantage_state()` (new `is_spell_attack` parameter), 10-round tickdown in `advance_turn`, broadcast to client. |
| **Font of Magic** (SP pool, convert slot↔SP) | 2 | 6968-6993 | ✓ Done 2026-04-09 — Sorcery Points = level. Bonus action handlers: `font_of_magic_to_slot` (cost table 1=2/2=3/3=5/4=6/5=7 SP with min-level gating) and `font_of_magic_to_sp` (free action, gain SP = slot level, capped at max). Client menu entries with sub-menu for slot level. |
| **Metamagic** (2 options at L2, +2 at L10, +2 at L17) | 2 | 6994-6997 | ✓ Done 2026-04-10 — All 10 options wired as toggle bonus actions with SP costs. Careful/Distant/Empowered/Extended/Heightened/Quickened/Seeking/Subtle/Transmuted all functional. Twinned deferred (needs dual-target cast flow). Extended Spell grants advantage on concentration saves. |
| **Sorcerer Subclass** | 3 | 6998-6999 | ✓ Done — Draconic, Wild Magic, Aberrant, Storm, Clockwork, Divine Soul, Frost, Desert Soul, Light Weaver, Shadow. |
| **Ability Score Improvement** | 4/8/12/16 | 7000-7001 | ✓ Done — global feat-grant system. |
| **Sorcerous Restoration** (regain SP up to half level on short rest, 1/LR) | 5 | 7002-7003 | ✓ Done 2026-04-10 — Wired into apply_short_rest: L5+ Sorcerers regain floor(level/2) SP on short rest, once per long rest via sorcerous_restoration_available flag. |
| **Sorcery Incarnate** (spend 2 SP for Innate Sorcery use; 2 metamagic per spell while active) | 7 | 7004-7006 | PARTIAL 2026-04-09 — bonus action handler accepts the 2 SP fallback for Innate Sorcery activation. Multi-metamagic-per-spell while active deferred to metamagic pipeline rewrite. |
| **Metamagic** (2 more options) | 10 | 7011 | DEFERRED — depends on the metamagic option choice prompt at level-up (we currently grant Quickened/Twinned/Subtle by default to all Sorcerers). |
| **Metamagic** (2 more options) | 17 | 7011 | DEFERRED — same as L10. |
| **Epic Boon** | 19 | 7007-7008 | ✓ Done — Epic Boon feat catalog. |
| **Arcane Apotheosis** | 20 | 7009 | SOURCE GAP — Basic Rules 2024 para 7009 has no body text for L20 capstone (jumps directly to "Metamagic Options" header). Likely a docx-extraction artifact. Flagged for re-extraction from PHB 2024 PDF or escalation to user. |

**Pending follow-up Sorcerer batches:**
- Metamagic option selection at L2/L10/L17 (player choice prompt). Currently we grant Quickened/Twinned/Subtle by default to all Sorcerers. Source allows the player to pick from 10.
- ~~Metamagic options not yet wired to spell pipeline~~ RESOLVED 2026-04-10 — All 7 non-trivial metamagic effects are wired: Careful (allies auto-succeed AoE save), Distant (double range), Empowered (reroll CHA mod damage dice), Extended (concentration advantage), Heightened (target save disadvantage), Seeking (reroll missed spell attack), Transmuted (swap damage type). Flags snapshot onto pending_roll at cast time.
- Sorcery Incarnate L7 multi-metamagic-per-spell — needs metamagic pipeline rewrite to allow 2 simultaneous flags during a single cast.
- ~~Sorcerous Restoration L5 — needs short rest subsystem (currently we only have long rest reset).~~ RESOLVED 2026-04-10 — Wired into apply_short_rest.
- Arcane Apotheosis L20 — escalate to user; basic_rules_full.txt para 7009 has no body text.

### Storm Sorcery Subclass Audit (2026-04-09) — Xanathar's paras 2515-2577

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Wind Speaker** (learn Primordial + 4 dialects) | 1 | 2515-2520 | SKIPPED — language only, no combat effect. |
| **Tempestuous Magic** (fly 10 ft without OA before/after casting L1+ spell) | 1 | 2521-2526 | SKIPPED — `tempestuous_magic` flag existed prior; no behavioral change needed in this audit. |
| **Heart of the Storm** (lightning/thunder resistance + eruption damage to enemies within 10 ft when casting L1+ lightning/thunder spell) | 6 | 2527-2545 | ✓ Done 2026-04-09 — eruption damage (half Sorcerer level round down) to enemies within 10 ft on qualifying spell cast. Lightning and thunder resistance granted on init. |
| **Storm Guide** (stop rain in 20 ft sphere or direct winds in 100 ft) | 6 | 2546-2555 | SKIPPED — out-of-combat weather control, no combat effect. |
| **Storm's Fury** (reaction when hit by melee: sorcerer-level lightning damage + STR save or pushed 20 ft) | 14 | 2556-2567 | ✓ Done 2026-04-09 — reaction prompt on melee hit, deals Sorcerer-level lightning damage, STR save DC = spell save DC or pushed 20 ft in straight line. |
| **Wind Soul** (immunity to lightning + thunder damage, fly 60 ft, action to grant 6 allies fly 30 for 1 hour) | 18 | 2568-2577 | ✓ Done 2026-04-09 — lightning + thunder immunity and fly 60 ft on init. Deferred: ally-fly action (grant 6 allies fly 30 for 1 hour, lose own fly until LR). |

### Divine Soul Subclass Audit (2026-04-09) — Xanathar's paras 2578-2639

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Divine Magic** (access to Cleric spell list + affinity spell) | 1 | 2578-2600 | ✓ Done 2026-04-09 — affinity choice via Shift+P, auto-prepared spell based on chosen affinity (Good/Evil/Law/Chaos/Neutrality). |
| **Favored by the Gods** (add 2d4 to failed attack or save, 1/SR) | 1 | 2601-2610 | ✓ Done 2026-04-09 — auto 2d4 additive in reroll chain, 1/SR via `favored_by_the_gods_available` flag. |
| **Empowered Healing** (reroll healing dice for self or ally within 5 ft, 1 SP per reroll) | 6 | 2611-2620 | PARTIAL — `empowered_healing_active` flag set on init. Heal-dice reroll mechanic deferred (needs hook into healing spell resolution pipeline). |
| **Otherworldly Wings** (bonus action toggle spectral wings, fly 30 ft) | 14 | 2621-2630 | ✓ Done 2026-04-09 — toggle bonus action, fly 30 ft while active. |
| **Unearthly Recovery** (bonus action heal half max HP when below half HP, 1/LR) | 18 | 2631-2639 | ✓ Done 2026-04-09 — bonus action handler, heals half max HP, gated on current HP < half max HP, `unearthly_recovery_available` flag 1/LR. |

### Shadow Magic Subclass Audit (2026-04-09) — Xanathar's paras 2557-2607

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Eyes of the Dark** (darkvision 120 ft; L3: learn darkness, can cast with 2 SP and see through it) | 1/3 | 2590-2592 | PARTIAL — darkness auto-prepared at L3. See-through-darkness with SP casting deferred (needs SP-casting hook in spell pipeline). |
| **Strength of the Grave** (CHA save DC 5+damage when reduced to 0 HP, drop to 1 instead; not if radiant or crit; 1/LR) | 1 | 2593-2595 | ✓ Done — wired in `apply_damage`. Source para ref added. Radiant exclusion works. Crit exclusion done 2026-04-10 via was_crit parameter on apply_damage. |
| **Hound of Ill Omen** (BA 3 SP, summon dire wolf variant targeting one creature within 120 ft) | 6 | 2596-2602 | ✓ Done 2026-04-10 — BA handler in `users _dom.nvgt`, spawns companion with dire wolf stats (HP 37 + half level, AC 14, Speed 50, 2d6+3 piercing). Save disadvantage FULLY WIRED: `apply_hound_save_disadvantage` helper in battle_manager checks hound alive + within 5ft + caster matches, wired into central `resolve_spell_save_damage_roll`, 5 end-of-turn saves, and all ~105 individual spell handler saves in `handle_cast`. Start-of-turn psychic damage (half sorcerer level) wired in `advance_turn`. Hound death cleanup clears `hound_caster_id` on target via `dismiss_companion`. |
| **Shadow Walk** (BA teleport 120 ft when in dim light/darkness) | 14 | 2603-2604 | ✓ Done 2026-04-09 — BA handler teleports toward locked target up to 120 ft. Dim/dark gating not enforced (no lighting system). |
| **Umbral Form** (BA 6 SP, resistance to all except force/radiant, move through objects, 1 min) | 18 | 2605-2607 | ✓ Done 2026-04-09 — BA handler, 6 SP cost, `shadow_umbral_active` flag, 10-round tickdown in `advance_turn`, dismiss as BA. Resistance wired in `apply_damage`. |

### Aberrant Mind Subclass Audit (2026-04-09) — Tasha's paras 3894-3952

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Psionic Spells** (auto-learn spells per level: arms of Hadar, dissonant whispers, mind sliver, calm emotions, detect thoughts, hunger of Hadar, sending, Evard's black tentacles, telekinesis) | 1-9 | 3914-3930 | ✓ Done 2026-04-09 — auto-prepared in character_data init. Summon aberration (L7) and Rary's telepathic bond (L9) skipped (not in spell catalog). |
| **Telepathic Speech** (BA 30 ft telepathic connection, sorcerer-level minutes) | 1 | 3932-3935 | SKIPPED — non-combat feature (telepathy flavor). |
| **Psionic Sorcery** (cast psionic spells with SP = spell level instead of slot, no components) | 6 | 3936-3938 | DEFERRED — needs spell choice prompt "Cast with slot or SP?" in spell pipeline. Flag `psionic_sorcery_active` not yet set. |
| **Psychic Defenses** (psychic resistance + advantage on charm/frighten saves) | 6 | 3939-3941 | ✓ Done 2026-04-10 — psychic resistance via `psychic_resistance` flag. `charm_frighten_save_advantage` wired into 12 charm/frighten save sites: Fear (AoE + EOT), Hypnotic Pattern, Cause Fear, Phantasmal Killer, Eyebite, Dominate Person/Monster/Beast, Charm Person/Monster, Weird. |
| **Revelation in Flesh** (BA 1+ SP, 10 min: see invisible 60 ft / fly speed / swim / squeeze) | 14 | 3942-3948 | ✓ Done 2026-04-09 — BA handler with sub-menu (see invisible / fly / both), 100-round tickdown in `advance_turn`. Swim and squeeze options skipped (non-combat). |
| **Warping Implosion** (action teleport 120 ft + 30 ft AoE 3d10 force STR save, 1/LR or 5 SP) | 18 | 3949-3952 | ✓ Done 2026-04-09 — action handler, teleport toward target, AoE loop with STR save vs spell DC, half on success, 1/LR or 5 SP recharge. |

### Warlock Audit (2026-04-09) — Basic Rules 2024 paras 7589-7799

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Eldritch Invocations** (1 known at L1; scales to 10 at L18) | 1+ | 7607-7762 (Warlock Features table), 7764-7769 | PARTIAL 2026-04-10 — 7 combat-relevant invocations wired: Agonizing Blast (+CHA to EB damage), Repelling Blast (10ft push on EB hit), Thirsting Blade (Extra Attack at L5), Devouring Blade (3 attacks at L12), Eldritch Smite (expend slot for force+prone), Lifedrinker (+1d6 necrotic + HP recovery 1/turn), Devil's Sight (flag set, zone-based bypass deferred). Invocations defaulted by level+pact until selection prompt built. `eldritch_invocations_known` count corrected 2026-04-09 to match source table (1/3/3/3/5/5/6/6/7/7/7/8/8/8/8/9/9/10/10/10). |
| **Pact Magic** (CHA, all slots same level, recover on Short Rest) | 1 | 7770-7781 | ✓ Done — `apply_warlock_slots()` matches source table (1 slot at L1, 2 at L2-10, 3 at L11-16, 4 at L17-20; slot levels 1/1/2/2/3/3/4/4/5/5...). Spellcasting=CHA. |
| **Magical Cunning** (1-min rite to recover half max Pact slots round up, 1/LR) | 2 | 7782-7783 | ✓ Done 2026-04-09 — Magic action handler in `users _dom.nvgt`, `magical_cunning_available` flag, recovers `(max+1)/2` slots at the Pact slot level (or all at L20 via Eldritch Master). Init in `character_data.nvgt`. |
| **Warlock Subclass** | 3 | 7784-7785 | ✓ Done — Fiend, Archfey, Great Old One, Hexblade, Celestial, Genie, Fathomless, Undead, Undying, Pact of the Astral Griffon, Pact of the Many, Mother of Sorrows, etc. |
| **Ability Score Improvement** | 4/8/12/16 | 7786-7787 | ✓ Done — global feat-grant system. |
| **Contact Patron** (free Contact Other Plane, auto-success on save, 1/LR) | 9 | 7788-7790 | ✓ Done 2026-04-09 — bonus_action handler `contact_patron`, sets `contact_patron_available=false`, broadcast announcement. Spell narrative (revelations) deferred — combat sim doesn't need scryer flavor. |
| **Mystic Arcanum (level 6 spell)** | 11 | 7791-7795 | ✓ Done 2026-04-09 — bonus_action handler `mystic_arcanum` with `arc_level=6`, grants phantom L6 slot for next cast. Spell choice = player. |
| **Mystic Arcanum (level 7 spell)** | 13 | 7791-7795 | ✓ Done 2026-04-09 — same handler, `arc_level=7`. |
| **Mystic Arcanum (level 8 spell)** | 15 | 7791-7795 | ✓ Done 2026-04-09 — same handler, `arc_level=8`. |
| **Mystic Arcanum (level 9 spell)** | 17 | 7791-7795 | ✓ Done 2026-04-09 — same handler, `arc_level=9`. |
| **Epic Boon** | 19 | 7796-7797 | ✓ Done — Epic Boon feat catalog. |
| **Eldritch Master** (Magical Cunning regains all slots) | 20 | 7798-7799 | ✓ Done 2026-04-09 — `eldritch_master_active` flag set on init at L20; Magical Cunning handler reads `c.level >= 20` and grants full pact slot recovery. |

**Pending follow-up Warlock batches:**
- Eldritch Invocation effects: PARTIAL 2026-04-10 — 7 combat-relevant invocations wired (Agonizing Blast, Repelling Blast, Thirsting Blade, Devouring Blade, Eldritch Smite, Lifedrinker, Devil's Sight flag). Remaining invocations still need logic: Pact of the Blade weapon conjure, Pact of the Chain familiar attack, Pact of the Tome cantrip/ritual prep, Misty Visions/Mask of Many Faces/etc. as free at-will casts. Invocations defaulted by level+pact until selection prompt built. Source: paras 7800-7927.
- Mystic Arcanum spell choice prompt at level-up — currently any chosen Warlock spell at the appropriate level can be cast. Source allows the player to designate one specific spell per arcanum level.
- Magical Cunning duration — currently collapses the 1-minute rite to a single Magic action because 10 rounds of standing still is unusable in combat. Source-accurate behavior would require a "rite in progress" state that ticks down per round and breaks on offensive actions.
- Pact Boon (Blade/Chain/Tome/Talisman) selection prompt at L3 — currently defaults to Pact of the Tome since the source mandates a player choice.

### Wizard Audit (2026-04-09) — Basic Rules 2024 paras 8298-8635

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Spellcasting** (INT, Arcane Focus or spellbook) | 1 | 8597-8610 | ✓ Done — `cs.is_caster=true`, `spellcasting_ability=ABILITY_INT`, full caster slot table. |
| **Ritual Adept** (cast any Ritual-tagged spellbook spell as ritual without prep) | 1 | 8616-8617 | PARTIAL 2026-04-09 — `ritual_adept_active` flag set on Wizard init. Actual ritual casting hook (no-slot, no-prep, +10 minutes) not yet wired into spell pipeline. Would need Ritual tag on `spell_data` entries first. |
| **Arcane Recovery** (recover slots half level round up, none L6+, 1/LR via short rest) | 1 | 8618-8620 | ✓ Done — `arcane_recovery_charges = 1`, bonus action handler in `users _dom.nvgt`, greedy slot recovery loop. |
| **Scholar** (Expertise in chosen knowledge skill) | 2 | 8621-8622 | DEFERRED — needs player choice prompt at level-up to designate Arcana/History/Investigation/Medicine/Nature/Religion. Skill expertise system exists but no wizard-specific selector. |
| **Wizard Subclass** | 3 | 8623-8624 | ✓ Done — Evoker, Diviner, Abjurer, Illusionist, War Magic, Bladesinging, Order of Scribes, Chronurgy Magic, Graviturgy Magic, Materializer, Wand Lore, Shadow Arcane Tradition, etc. |
| **Ability Score Improvement** | 4/8/12/16 | 8625-8626 | ✓ Done — global feat-grant system. |
| **Memorize Spell** (swap one prepared spell on short rest) | 5 | 8627-8628 | DEFERRED — needs short rest subsystem and prepared-spell-list mutator UI. |
| **Spell Mastery** (chosen L1+L2 spells castable at base level without slot) | 18 | 8629-8631 | PARTIAL 2026-04-09 — `spell_mastery_active` flag set on init. Slot bypass wired into `cast_spell` pipeline in battle_manager.nvgt: if `spell.id == c.spell_mastery_l1_spell_id` (or l2), the cast skips slot consumption with announcement "casts X through Spell Mastery — no spell slot consumed!". `spell_mastery_l1_spell_id` and `spell_mastery_l2_spell_id` strings default to empty; the player must designate (level-up choice prompt deferred). |
| **Epic Boon** | 19 | 8632-8633 | ✓ Done — Epic Boon feat catalog. |
| **Signature Spells** (two L3 spells castable at L3 without slot, 1/short rest each) | 20 | 8634-8635 | PARTIAL 2026-04-09 — `signature_spells_charges_max = 2` and `signature_spells_charges_remaining = 2` set on L20 init. Slot bypass wired in cast pipeline for `signature_spell_a_id` and `signature_spell_b_id` (separate `_used_this_rest` flags per spell). The two designation strings default to empty; the player must designate. Short rest reset deferred (currently only long rest). |

**Pending follow-up Wizard batches:**
- Spell Mastery designation prompt at L18 — player picks 1 L1 + 1 L2 spell from spellbook (the spell IDs are fields in `combatant`, just need a level-up UI flow to set them).
- Signature Spells designation prompt at L20 — same as above for two L3 spells.
- Scholar L2 expertise prompt at L2 — knowledge skill picker.
- Memorize Spell L5 — short rest subsystem dependency.
- Ritual Adept L1 spell pipeline integration — needs `Ritual` tag on spell data entries and a separate ritual cast path that consumes 10 minutes (or 11 minutes per source) and skips slot/prep requirements for spellbook ritual spells.

### War Magic Wizard Subclass Audit (2026-04-10) — Xanathar's paras 2915-2944

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Arcane Deflection** (reaction: +2 AC vs attack OR +4 to failed save; can't cast non-cantrip until end of next turn) | 2 | 2932-2934 | ✓ Done — AC reaction in prompt system (+2 AC). Save variant `try_arcane_deflection_save` (+4 save) wired into 28+ save failure sites (smart-spend). Non-cantrip restriction enforced via `arcane_deflection_no_spell_turns = 2` checked in `handle_cast`. L14 Deflecting Shroud fires on both AC and save uses. |
| **Tactical Wit** (+INT mod to initiative rolls) | 2 | 2935-2936 | ✓ Done — `tactical_wit_active` flag set on init; `request_next_initiative` adds `c.get_ability_mod(ABILITY_INT)` to initiative modifier. |
| **Power Surge** (store surges max=INT mod, gain from dispel_magic/counterspell success, spend 1/turn for half-level force damage on wizard spell hit) | 6 | 2937-2940 | PARTIAL — Charges init'd at INT mod, auto-spend on spell attack hit for `level/2` force damage (1/turn), gain from `dispel_magic` success. Save-based spell damage rider wired to central AoE path 2026-04-10. Deferred: gain from `counterspell` (interception not fully resolved), short-rest "if 0 surges, gain 1" recovery. |
| **Durable Magic** (+2 AC and +2 all saving throws while concentrating) | 10 | 2941-2942 | ✓ Done — `durable_magic_active` flag; AC dynamically added/removed at concentration start/`clear_concentration_effects`; +2 saves in `get_save_bonus` when `durable_magic_active and is_concentrating`. |
| **Deflecting Shroud** (when Arcane Deflection used, up to 3 enemies within 60ft take half-wizard-level force damage) | 14 | 2943-2944 | ✓ Done — `deflecting_shroud_active` flag; damage loop in Arcane Deflection reaction handler, iterates combatants, skips allies/dead, distance check ≤60ft, caps at 3 targets. |

**Pending War Magic follow-ups:**
- ~~Arcane Deflection +4 save variant~~ RESOLVED 2026-04-10 — `try_arcane_deflection_save` wired into 28+ save failure sites.
- ~~Arcane Deflection non-cantrip casting restriction~~ RESOLVED 2026-04-10 — `arcane_deflection_no_spell_turns` enforced in `handle_cast`.
- Power Surge: counterspell gain (depends on counterspell interception being fully resolved), short-rest 0→1 recovery. Save-based spell damage rider wired to central AoE path 2026-04-10.

### Grave Domain Cleric Subclass Audit (2026-04-10) — Xanathar's paras 794-832

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Circle of Mortality** (max healing dice when healing a 0hp creature) | 1 | 795 | ✓ Done — `circle_of_mortality_active` flag set on init. |
| **Eyes of the Grave** (detect undead within 60ft) | 1 | 796 | DEFERRED — no undead-detection system exists. |
| **Path to the Grave** (Channel Divinity: next attack against cursed creature deals double damage via vulnerability) | 2 | 794-796 | ✓ Done — FIXED from wrong 1d8 bonus to correct vulnerability doubling on TARGET. Flag `path_to_grave_vulnerable` set on target; consumed before `apply_damage` to double `total_damage` for ANY attacker. |
| **Sentinel at Death's Door** (reaction: negate crit within 30ft) | 6 | 808-812 | ✓ Done — auto-resolved: scans for Grave Cleric within 30ft with reaction + WIS mod uses. |
| **Blessed Strikes** (Potent Spellcasting — +WIS mod to cantrip damage) | 8 | — | ✓ Done — `blessed_strikes_choice = "potent_spellcasting"` set on init. |
| **Domain Spells** (bane, false_life, ray_of_enfeeblement, vampiric_touch, blight, antilife_shell) | 1-9 | 794 | ✓ Done — auto-prepared via init. |
| **Keeper of Souls** (on enemy death within 60ft, heal most-injured ally for target-level HP, 1/turn) | 17 | 826-832 | ✓ Done — wired into `maybe_apply_on_kill_features`. |

### Hexblade Warlock Subclass Audit (2026-04-10) — Xanathar's paras 2271-2306

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Hexblade's Curse** (bonus action: +prof damage, crit 19-20, heal on kill = warlock level + CHA mod, 1/SR) | 1 | 2278-2288 | ✓ Done — `hexblade_curse_used` flag, `hexblade_curse_target` tracking. Crit threshold wired in `get_critical_threshold`. Heal + damage in `maybe_apply_on_kill_features` + `apply_subclass_on_hit_damage`. |
| **Hex Warrior** (CHA for melee weapon attacks) | 1 | 2275-2277 | ✓ Done 2026-04-10 — `get_weapon_attack_ability_mod` uses highest of STR/DEX/CHA for Hexblade non-two-handed melee attacks. |
| **Expanded Spell List** (shield, wrathful_smite, blur, branding_smite, blink, elemental_weapon, phantasmal_killer, staggering_smite, banishing_smite, cone_of_cold) | 1-9 | 2271-2274 | ✓ Done — auto-prepared via init. |
| **Accursed Specter** (raise spectre from humanoid killed with curse) | 6 | 2289-2291 | DEFERRED — needs summon/companion system extension. |
| **Armor of Hexes** (reaction: d6, 4+ forces cursed attacker to miss) | 10 | 2295-2298 | ✓ Done — reaction prompt option when cursed target attacks warlock. Resolution: `random(1,6) >= 4` → `rp.attack_total = 0`. |
| **Master of Hexes** (auto-transfer curse to nearest enemy within 30ft on cursed target death) | 14 | 2302-2306 | ✓ Done — wired into `maybe_apply_on_kill_features`. Scans for nearest living enemy within 30ft and transfers `hexblade_curse_target`. |

### Samurai Fighter Subclass Audit (2026-04-10) — Xanathar's paras 1685-1714

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Bonus Proficiency** (History/Insight/Performance/Persuasion or language) | 3 | 1700-1701 | Done 2026-04-10 -- auto-grants first unproficient of History/Insight/Performance/Persuasion at init. |
| **Fighting Spirit** (BA: advantage on weapon attacks this turn + 5/10/15 temp HP; 3 uses/LR) | 3 | 1702-1704 | ✓ Done — FIXED uses from proficiency_bonus to correct 3/LR. Temp HP scaling 5/10/15 at L3/10/15 already correct. |
| **Elegant Courtier** (+WIS mod to Persuasion checks; WIS save proficiency) | 7 | 1705-1707 | Done 2026-04-10 -- WIS save proficiency at init + WIS mod added to Persuasion in get_skill_bonus. |
| **Tireless Spirit** (regain 1 Fighting Spirit on initiative if at 0 uses) | 10 | 1708-1709 | ✓ Done — wired in `request_next_initiative`. |
| **Rapid Strike** (forgo advantage on one attack to gain an extra attack; 1/turn) | 15 | 1710-1711 | DEFERRED — needs an attack-time prompt to choose between advantage and extra attack. Complex interaction with Extra Attack system. |
| **Strength before Death** (reaction on dropping to 0 HP: take extra turn immediately; 1/LR) | 18 | 1712-1714 | DEFERRED — needs turn interruption / insertion system. Very complex interaction with initiative order. |

### Arcane Archer Fighter Subclass Audit (2026-04-10) — Xanathar's paras 1599-1646

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Arcane Archer Lore** (Arcana or Nature proficiency + prestidigitation or druidcraft cantrip) | 3 | 1616-1617 | Done 2026-04-10 -- auto-grants Arcana (or Nature fallback) proficiency + prestidigitation cantrip at init. |
| **Arcane Shot** (2 uses/SR, apply shot effect on ranged hit, 1/turn; 8 shot options) | 3 | 1618-1621 | SKELETON — uses tracked (2/rest), pending flag set via BA menu. Shot effects NOT applied in battle_manager (flag never read). Shot type selection menu hardcoded to one type. Full 8-shot implementation pending. |
| **Magic Arrow** (nonmagical arrows become magical to overcome resistance/immunity) | 7 | 1622-1623 | DEFERRED — no weapon-magic-damage system exists. |
| **Curving Shot** (BA: reroll missed arrow attack vs different target within 60ft) | 7 | 1624-1625 | DEFERRED — needs miss-redirect mechanic. |
| **Ever-Ready Shot** (regain 1 Arcane Shot use on initiative if at 0 uses) | 15 | 1626-1627 | ✓ Done — wired in `request_next_initiative`. |
| **Arcane Shot Options** (Banishing, Beguiling, Bursting, Enfeebling, Grasping, Piercing, Seeking, Shadow) | 3-18 | 1628-1646 | NOT IMPLEMENTED — 8 shot types with unique effects, saves, and L18 damage upgrades. Requires dedicated implementation batch. |

### Ancestral Guardian Barbarian Subclass Audit (2026-04-10) — Xanathar's paras 371-398

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Ancestral Protectors** (first creature hit per turn while raging: disadvantage on attacks not targeting you; allies hit by marked creature have resistance) | 3 | 389-390 | ✓ Done — auto-mark on first hit per turn while raging. `ancestral_protector_marked_by` on target, disadvantage in `apply_attack_advantage_state`, resistance halving in ROLL_DAMAGE path. Mark cleared at start of barbarian's next turn. |
| **Spirit Shield** (reaction: reduce damage to creature within 30ft by 2d6/3d6/4d6) | 6 | 391-393 | ✓ Done — reaction prompt option, `spirit_shield_reduction` consumed in `apply_damage`. Source-quoted dice scaling at L6/10/14. |
| **Consult the Spirits** (cast augury or clairvoyance without slot, 1/SR) | 10 | 394-396 | DEFERRED — augury/clairvoyance not implemented as spells. Utility, not combat. |
| **Vengeful Ancestors** (Spirit Shield deals equal force damage to attacker) | 14 | 397-398 | ✓ Done — wired in Spirit Shield reaction handler. `apply_damage` to attacker for the reduction amount as force damage. |

### Cavalier Fighter Subclass Audit (2026-04-10) — Xanathar's paras 1649-1682

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Born to the Saddle** (advantage on saves vs falling off mount, quick mount/dismount) | 3 | 1666-1668 | DEFERRED — no mount system exists. |
| **Unwavering Mark** (auto-mark on melee hit; marked creature has disadvantage on attacks not targeting you within 5ft; if marked creature damages ally, BA retaliation attack with advantage + half level damage; STR mod uses/LR) | 3 | 1669-1673 | ✓ Done — MAJOR REWORK from wrong +prof bonus damage. Now: auto-mark on melee hit, disadvantage in `apply_attack_advantage_state`, BA retaliation in `users _dom.nvgt`, mark expiry in `advance_turn`. |
| **Warding Maneuver** (reaction: +1d8 AC to self or ally within 5ft; if still hit, resistance to damage; CON mod uses/LR) | 7 | 1674-1676 | ✓ Done — self-defense as reaction prompt option, ally defense auto-resolved. `warding_maneuver_resistance` consumed in `apply_damage` to halve damage. |
| **Hold the Line** (OA triggers on 5ft movement within reach; hit reduces speed to 0) | 10 | 1677-1678 | DEFERRED — `hold_the_line_active` flag set. Needs OA trigger on per-tile movement (current OA system only fires on leaving 5ft reach entirely). |
| **Ferocious Charger** (10ft+ straight-line move before attack → STR save or prone; 1/turn) | 15 | 1679-1680 | DEFERRED — `ferocious_charger_active` flag set. Needs straight-line movement path tracking before attack resolution. |
| **Vigilant Defender** (special reaction on every other creature's turn for OA only) | 18 | 1681-1682 | DEFERRED — `vigilant_defender_active` flag set. Needs multi-reaction-per-round system (current system has single `has_reaction` bool reset once per turn). |

### Artificer Audit (2026-04-09) — Forgotten Realms PHB Forge of the Artificer paras 455-675

| Feature | Level | Source para | Status |
|---|---|---|---|
| **Spellcasting** (INT, half-caster, Artisan's/Thieves'/Tinker's Tools as focus) | 1 | 455-466 | ✓ Done — `cs.is_caster=true`, `spellcasting_ability=ABILITY_INT`, `apply_half_caster_slots`. |
| **Tinker's Magic** (Mending cantrip + Magic action create mundane item, INT mod uses/LR) | 1 | 467-502 | PARTIAL 2026-04-09 — `tinkers_magic_uses_max` and `tinkers_magic_uses_current` fields set on init at INT-mod-min-1 uses. The Magic action mundane-item creation handler is deferred — needs a hazards system for ball bearings/caltrops to have combat effect, and a player-side item picker for the 30-item list. Use tracking is wired so future batches can add the action handler. |
| **Replicate Magic Item** (4 plans, craft during LR, items vanish 1d4 days post-death) | 2 | 503-513 | DEFERRED — `replicate_magic_item_known` flag set on init for client awareness. Full implementation requires the DMG magic item plan tables, a long-rest crafting subsystem, item-attunement-from-this-feature tracking, and per-item vanish timers. None of those subsystems exist. |
| **Artificer Subclass** | 3 | 646-647 | ✓ Done — Alchemist, Armorer, Artillerist, Battle Smith, Cartographer (Eberron). |
| **Ability Score Improvement** | 4/8/12/16 | 648-649 | ✓ Done — global feat-grant system. |
| **Magic Item Tinker** (Charge BA / Drain BA / Transmute Action options on Replicate items) | 6 | 650-654 | DEFERRED — depends on Replicate Magic Item infrastructure. Without the plan + crafted-item registry there is no item to charge/drain/transmute. Documented for the same future batch as Replicate Magic Item. |
| **Flash of Genius** (Reaction +INT mod to failed ability check or save w/in 30 ft, INT mod uses/LR) | 7 | 655-657 | ✓ Done 2026-04-09 — `flash_of_genius_uses_max` and `flash_of_genius_uses_current` set on init at INT-mod-min-1 uses. New `try_flash_of_genius` helper in `battle_manager.nvgt` scans for any L7+ Artificer with the feature available and reaction free within 30 ft of the failing target (self allowed per RAW), smart-spends only when the bonus would actually turn the failure into a success, decrements the use, consumes the reaction, and returns the new total. Wired into 20 save sites: 5 end-of-turn condition saves (Hold Person, Web, Blindness/Deafness, Fear, Tasha's Hideous Laughter) and 15 charm/frighten failed-save sites (mirrors Bard Countercharm coverage). Also wired into `finalize_roll_result` for failed `ROLL_ABILITY_CHECK` paths so any skill check or hide check routed through the pending_roll system gets Flash of Genius coverage automatically. Damage saves (Fireball/Lightning Bolt/Cone of Cold/etc.) coverage left for a future Flash of Genius coverage extension batch — there are 80+ inline save sites and the pattern repeats; to be wired in a focused follow-up. |
| **Magic Item Adept** (4 attunements) | 10 | 658-659 | ✓ Done 2026-04-09 — `magic_item_attunement_max = 4` set on init at L10+. |
| **Spell-Storing Item** (LR-store 1 L1-3 Artificer spell in object, 2×INT mod uses) | 11 | 660-663 | DEFERRED — `spell_storing_item_known` flag set for client awareness. Full implementation requires per-item spell-storage state on the inventory item objects, plus a Magic action handler that anyone holding the item can trigger. Item infrastructure not present. |
| **Advanced Artifice — Magic Item Savant** (5 attunements) | 14 | 664-666 | ✓ Done 2026-04-09 — `magic_item_attunement_max = 5` overrides the L10 cap. |
| **Advanced Artifice — Refreshed Genius** (regain 1 Flash of Genius use on Short Rest) | 14 | 664-667 | PARTIAL 2026-04-09 — `refreshed_genius_active` flag set on init at L14+. Actual SR regen requires the short rest subsystem. Currently combat sessions only have long rests, which already restore all uses. The flag is in place so when SR is added it will hook in correctly. |
| **Magic Item Master** (6 attunements) | 18 | 668-669 | ✓ Done 2026-04-09 — `magic_item_attunement_max = 6` overrides L14 cap. |
| **Epic Boon** | 19 | 670-671 | ✓ Done — Epic Boon feat catalog. |
| **Soul of Artifice — Cheat Death** (disintegrate Uncommon/Rare items for 20 HP each when reduced to 0 HP) | 20 | 672-674 | DEFERRED — depends on Replicate Magic Item infrastructure. Without a per-character registry of items created via Replicate Magic Item there is nothing to disintegrate. |
| **Soul of Artifice — Magical Guidance** (Flash of Genius full regen on Short Rest if attuned to ≥1 magic item) | 20 | 672-675 | PARTIAL 2026-04-09 — `magical_guidance_active` flag set on init at L20+. Same SR-subsystem dependency as Refreshed Genius. Flag is in place for the eventual SR hook. |

**Pending follow-up Artificer batches:**
- Replicate Magic Item L2 — needs DMG magic item plan tables (Levels 2/6/10/14 from source paras 517-645), a long-rest crafting subsystem, attunement-from-this-feature tracking, and per-item vanish timers. Bag of Holding, Cap of Water Breathing, Sending Stones, Wand of the War Mage are recommended starting plans.
- Magic Item Tinker L6 — Charge/Drain/Transmute Bonus/Magic actions on Replicate Magic Items. Requires the Replicate registry above.
- Spell-Storing Item L11 — store an Artificer L1-3 spell in an object during Long Rest, anyone holding can use Magic action to cast (`2*INT mod` uses).
- Refreshed Genius L14 + Magical Guidance L20 — Short Rest subsystem dependency.
- Cheat Death L20 — depends on Replicate Magic Item infrastructure.
- ~~Flash of Genius coverage extension~~ RESOLVED 2026-04-10: `try_flash_of_genius` now wired into central AoE save path + 46+ individual spell handler save sites (all spell save sites covered, including cantrips and damage-only saves).
- Tinker's Magic L1 Magic action — needs a hazards system for ball bearings/caltrops in adjacent tiles.

### Gunslinger Audit (2026-04-09) — Valda's Spire of Secrets paras 159-203

| Feature | Level | Source para | Status |
|---|---|---|---|
| **Fighting Style** (one Fighting Style feat; can apply melee styles to ranged weapons) | 1 | 160-161 | ✓ Done — global Fighting Style infra. |
| **Quick Draw** (Advantage on Initiative + Double Draw) | 1 | 162-165 | ✓ Done 2026-04-09 — `quick_draw_active` flag set on init at L1+. Hooked at initiative request in `request_initiative_roll` (`battle_manager.nvgt`) and adds `pr.has_advantage = true`. **Bug fix:** previous implementation added a flat `+2` initiative bonus, which is RAW-incorrect. Double Draw is enforced by free draw/stow infra (no per-attack token gating). |
| **Weapon Mastery** (2/3/4 Simple or Martial Ranged weapons; LR swap) | 1 | 166-168 | PARTIAL — global weapon mastery infra applies the kinds count, but the per-property application during attack rolls is part of the deferred Weapon Mastery integration backlog (shared across all martial classes). |
| **Critical Shot** (passive crit-range expansion 19/18/17 with Ranged weapons) | 2 | 170-171 | ✓ Done 2026-04-09 — `gunslinger_crit_threshold = 19/18/17` set on init at L2/9/17. Hooked in `get_critical_threshold` (`battle_manager.nvgt`) gated on `attacker.main_hand_is_ranged` so it only applies to Ranged weapon attacks. **Bug fix:** previous implementation treated Critical Shot as a use-based bonus-damage maneuver, which is RAW-incorrect — it's a passive crit-range expansion. Removed broken `critical_shot_uses/_pending` user-action handler from `users _dom.nvgt` and the menu entries from `combat_ui.nvgt`. |
| **Risk + Risk Dice** (4d8 / 5d8 / 5d10 / 6d10 / 6d12 by tier; SR/LR refresh) | 2 | 172-176 | ✓ Done 2026-04-09 — `risk_dice_max` and `risk_die_size` scale by level: L2=4d8, L6=5d8, L10=5d10, L14=6d10, L18=6d12. **Bug fix:** previous implementation had 2d8 → 3d10 → 4d12, which is RAW-incorrect on both count and tier-thresholds. |
| **Gunslinger Subclass** | 3 | 178-179 | ✓ Done — Deadeye, High Roller, Secret Agent, Spellslinger, Trick Shot, White Hat selectable. (Spellslinger spellcasting subsystem is a separate batch.) |
| **Ability Score Improvement** | 4/8/12/16 | 180-181 | ✓ Done — global feat-grant system. |
| **Extra Attack** (one extra) | 5 | 182-183 | ✓ Done 2026-04-09 — `c.extra_attacks = 1` set on init at L5+. |
| **Gut Shot** (on crit vs Large or smaller, 1 minute speed-half + Disadvantage on attacks until dislodged) | 5 | 184-185 | ✓ Done 2026-04-09 — `gut_shot_active` flag set on init at L5+ (gates the on-crit trigger). New Gut Shot block in `finalize_roll_result` checks `pr.is_crit and c.main_hand_is_ranged and target.size <= SIZE_LARGE` and on success: sets `target.gut_shot_rounds_remaining = 10` (1 minute), halves `target.speed`. Disadvantage on the gut-shot creature's outgoing attacks is hooked in `apply_attack_advantage_state` (sets `disadv = true` when `attacker.gut_shot_rounds_remaining > 0`). Tickdown in `advance_turn` decrements per round and restores speed on expiry. **Bug fix:** previous implementation was a manual bonus-action maneuver that added Risk Die bonus damage, which is RAW-incorrect — Gut Shot is an automatic on-crit debuff. Removed broken handler from `users _dom.nvgt` and menu entry from `combat_ui.nvgt`. |
| **Evasion** (DEX save: success → no damage, fail → half) | 7 | 187-188 | ✓ Done 2026-04-09 — sets the existing shared `evasion_active` field on init at L7+. Already handled by the existing Monk/Rogue Evasion path in damage save logic. |
| **Overkill** (ranged weapon: add ability mod if not present, else +1d8) | 11 | 189-191 | ✓ Done 2026-04-09 — `overkill_active` flag set on init at L11+. Wired in `finalize_roll_result` damage path: when attacker is Gunslinger with `overkill_active` and the attack is a ranged weapon attack, adds `1d8` bonus damage. Note: the ability mod adder for firearms is the source intent for weapons that don't already add mod to damage; until the Firearm property is exposed on the weapon registry the implementation conservatively applies the +1d8 branch (player upside). |
| **Cheat Death** (drop to 1 HP instead of 0, regain Gunslinger level HP, 1/SR) | 13 | 193-194 | ✓ Done 2026-04-09 — `cheat_death_used` resets on init at L13+. Wired in `apply_damage` (`combat_engine.nvgt`) right after Sorcerer Strength of the Grave: when a L13+ Gunslinger is reduced to 0 HP and is not killed outright (overflow < max HP) and `!cheat_death_used`, sets `cheat_death_used = true` and restores `current_hp = 1 + level` (capped at max HP). **Bug fix:** previous implementation had a `cheat_death_available` flag with no actual hook into the damage pipeline. SR refresh is deferred to the SR subsystem batch. |
| **Dire Gambit** (regain 1 Risk Die on initiative or crit) | 15 | 196 | ✓ Done 2026-04-09 — `dire_gambit_active` flag set on init at L15+. Wired at two sites: (1) `request_initiative_roll` (`battle_manager.nvgt`) increments `risk_dice_current` (capped at max) right after the Bard Superior Inspiration block, with announce; (2) `finalize_roll_result` crit-detection block increments on each crit. |
| **Deft Maneuver** (extra Bonus Action that can only be a maneuver) | 18 | 197-198 | PARTIAL — `deft_maneuver_active` flag set on init at L18+. The extra-bonus-action grant is wired via the flag for client awareness; the per-turn refresh of an additional bonus-action token specific to maneuvers is deferred until maneuver-action infrastructure is added (to differentiate "any bonus action" from "maneuver-only bonus action"). |
| **Epic Boon** | 19 | 199-200 | ✓ Done — Epic Boon feat catalog. |
| **Headshot** (on crit with Ranged weapon: target with <100 HP dies, else +10d10 damage; 1/SR or 3 Risk Dice) | 20 | 201-203 | ✓ Done 2026-04-09 — `headshot_active` flag set on init at L20+, `headshot_used` reset on init. Wired in `finalize_roll_result` crit-detection block: when L20 Gunslinger crits with a ranged weapon and `!headshot_used` and target is alive, sets `headshot_used = true` and either (a) if `target.current_hp < 100`: adds `target.current_hp` to total_damage to ensure kill, with HEADSHOT! announcement, or (b) else: rolls 10d10 extra damage. The 3-Risk-Dice refund alternate refresh path is deferred until the SR subsystem; LR resets `headshot_used` via the existing init reset. |

**Pending follow-up Gunslinger batches:**
- Maneuvers (paras 207-218) — ✓ Done 2026-04-09 batch 2: **Bite the Bullet** (BA, Risk Die + level temp HP) wired in `users _dom.nvgt`. **Blindfire** (BA, Blindsight 30 ft until end of turn) corrected to RAW from the broken "ignore disadvantage" stub; `blindfire_active` flag set on activation, cleared at start of next turn in `advance_turn`. **Dodge Roll** (BA, +15 ft movement) corrected to RAW from the broken `add_condition(COND_DODGING)` stub; grants `c.movement_remaining += 15`. OA-immunity and difficult-terrain-immunity for that movement segment are deferred until per-segment movement tracking exists. **Grazing Shot** (no action, on miss with ranged weapon: Risk Die + DEX mod weapon-type damage, 1/turn) — new `try_grazing_shot` helper in `battle_manager.nvgt` mirroring `try_flash_of_genius`, wired right after the attack `broadcast_roll` on miss path; per-turn flag `grazing_shot_used_this_turn` reset in `advance_turn`. **Maverick Spirit** (no action, failed INT/WIS/CHA check or save: add Risk Die, 1/turn) — new `try_maverick_spirit` helper in `battle_manager.nvgt` with smart-spend (only commits if the Risk Die roll would actually turn the failure into a success). Wired into the generic ability check path (gated on INT/WIS/CHA `ability_id`) and 16 WIS save sites paired with `try_flash_of_genius` (Hold Person EOT, Fear EOT, Tasha's Hideous Laughter EOT, Fear AoE, Hypnotic Pattern, Cause Fear, Phantasmal Killer, Mass Suggestion, Command, Suggestion, Eyebite, Dominate Person, Charm Person, Dominate Monster, Enthrall, Charm Monster, Dominate Beast, Weird). Per-turn flag `maverick_spirit_used_this_turn` reset in `advance_turn`. **Skin of Your Teeth** (Reaction: on hit, add Risk Die to AC) is deferred — depends on the existing reaction prompt infrastructure being extended with a new reaction option.
- Subclass features — Spellslinger spellcasting (separate L3 INT half-caster table at paras 296-415) is a substantial batch on its own. Other subclasses have placeholder L3 init only; full feature implementations (Eagle Eye, Liar's Dice, Risky Business, Risk Taker, Concealed Position, Reposition, Focused Shot, etc.) are deferred.
- Headshot 3-Risk-Dice refresh — depends on the Risk-Dice spend infrastructure for non-action effects.
- Deft Maneuver L18 — requires a separate maneuver-only bonus action token to differentiate from the regular bonus action.
- Skin of Your Teeth maneuver — requires extending the reaction prompt infrastructure with a new opt-in reaction option visible only to L2+ Gunslingers with at least one Risk Die.
- ~~Weapon Mastery property application~~ RESOLVED 2026-04-10 — 7 properties wired to attack resolution.

- **Paladin:** Lay on Hands (pool size), Divine Smite (slot-based in 2024), Aura of Courage, Cleansing Touch — all addressed in 2026-04-09 audit; remaining items in pending list above.
- **Ranger:** Favored Enemy / Roving / Tireless / Relentless Hunter / Nature's Veil / Precise Hunter / Feral Senses / Foe Slayer all addressed 2026-04-09; deferred items in Ranger pending list above.
- **Rogue:** Sneak Attack base case / Steady Aim / Uncanny Dodge / Reliable Talent L7 fix / Slippery Mind / Elusive / Stroke of Luck flag all addressed 2026-04-09; deferred Cunning Strike family in Rogue pending list above.
- **Sorcerer:** Innate Sorcery, Font of Magic, Sorcery Incarnate fallback, Eldritch Master prep all addressed 2026-04-09; metamagic pipeline wired 2026-04-10. Sorcerous Restoration wired into apply_short_rest 2026-04-10.
- **Warlock:** Magical Cunning, Contact Patron, Mystic Arcanum L11/13/15/17, Eldritch Master, invocation count fix all addressed 2026-04-09; 7 combat-relevant invocation effects wired 2026-04-10 (Agonizing/Repelling Blast, Thirsting/Devouring Blade, Eldritch Smite, Lifedrinker, Devil's Sight). Remaining invocations deferred.
- **Wizard:** Arcane Recovery, Spell Mastery, Signature Spells
- **Artificer:** Tinker's Magic uses, Flash of Genius (20 sites + finalize_roll_result), Magic Item Adept/Savant/Master attunement caps, Magical Guidance flag
- **Gunslinger:** Risk Dice progression fix (4/5/5/6/6 not 2/3/4), Critical Shot passive crit-range (19/18/17), Quick Draw initiative advantage, Extra Attack L5, Gut Shot crit debuff (speed half + disadv 10 rounds), Evasion L7, Overkill L11, Cheat Death L13 drop-to-1, Dire Gambit L15 Risk Die regen, Headshot L20 kill/+10d10

---

## 7. Feat TODOs

**Current status (verified 2026-04-08):** 77 feats defined in `common/feat_data.nvgt`. Only 24 have `has_feat()` checks in combat code. **53 feats have no combat logic at all** — they're selectable at character creation but do nothing in combat.

### Feats WITH combat logic (50+ after all batches through 2026-04-10):
alert, archery, athlete (BATCH 4A), blind_fighting (BATCH 4B), boon_of_combat_prowess, boon_of_irresistible_offense, boon_of_truesight, charger (BATCH 4B), crossbow_expert, crusher, defensive_duelist, dueling, fey_touched (BATCH 4B), grappler, great_weapon_fighting, great_weapon_master, healer, heavy_armor_master, inspiring_leader (BATCH 4A), mage_slayer, mobile (2026-04-10), observant (BATCH 4A), piercer, poisoner (BATCH 4A), polearm_master, resilient (BATCH 4A), savage_attacker, sentinel, shadow_touched (BATCH 4B), sharpshooter (BATCH 4A), shield_master, skill_expert (BATCH 4A), skulker (BATCH 4A), slasher, spell_sniper (BATCH 4A), tavern_brawler, telekinetic (BATCH 4A), thrown_weapon_fighting, unarmed_fighting (BATCH 4B), war_caster

**Batch 4B wired (5 new feats):**
- **Blind Fighting** (PHB para 7846) - sets `combatant.blindsight_range = 10` (used by future LoS / hidden checks)
- **Unarmed Fighting** (PHB para 7880) - 1d6 (with shield) or 1d8 (no shield) bludgeoning unarmed strike, picks the higher of weapon die / monk MA die / Tavern Brawler die
- **Charger** (PHB para 7557) - Improved Dash adds +10 ft to Dash speed. Charger +1d8 charge damage wired (2026-04-10). Straight-line movement detection is approximated.
- **Fey Touched** (PHB para 7614) - auto-prepares Misty Step + Bless (default L1 Enchantment) at character init. Free-cast tracking wired via grant_free_cast pipeline (2026-04-10).
- **Shadow Touched** (PHB para 7753) - auto-prepares Invisibility + Blindness/Deafness (default L2 Necromancy) at character init. Free-cast tracking wired via grant_free_cast pipeline (2026-04-10).

**2026-04-10 additions:**
- **Mobile** (PHB para 7697) - ✓ Done 2026-04-10 — Blanket OA immunity approximation in check_opportunity_attacks. Strict RAW is only vs creatures attacked this turn.

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

**Fighting Style feats (ALL RESOLVED):**
- ~~blind_fighting~~ Done (blindsight 10ft). ~~interception~~ Done (auto-resolved -1d10-prof reaction). ~~protection~~ Done (auto-resolved disadvantage reaction). ~~two_weapon_fighting~~ Done (TWF system). ~~unarmed_fighting~~ Done (d6/d8 die).

**Epic Boon feats (ALL RESOLVED):**
- ~~boon_of_dimensional_travel~~ Done (Blink Steps teleport). ~~boon_of_energy_resistance~~ Removed (not in source). ~~boon_of_fate~~ Done (2d4 ally save bonus). ~~boon_of_fortitude~~ Done (+40 HP). ~~boon_of_recovery~~ Done (BA heal half max HP). ~~boon_of_skill~~ Done (+1d10 ability check). ~~boon_of_speed~~ Done (+30 speed). ~~boon_of_spell_recall~~ Done (free spell cast). ~~boon_of_the_night_spirit~~ Done (300ft darkvision).

### Key complex feat effects — status:
- ~~**Polearm Master Reactive Strike**~~ RESOLVED (commit 2813154) — entering-reach OA trigger wired.
- ~~**Shield Master Interpose Shield**~~ RESOLVED 2026-04-10 — Reaction on successful DEX save → 0 damage.
- ~~**Shield Master push option**~~ RESOLVED 2026-04-10 — player choice of Push 5ft OR Prone via B-menu toggle.
- ~~**Mage Slayer Guarded Mind**~~ RESOLVED (commit 7a47504) — 1/SR auto-succeed on failed INT/WIS/CHA save, wired into 40+ save sites.
- ~~**Charger**~~ RESOLVED 2026-04-10 — +1d8 charge damage wired.
- ~~**Inspiring Leader**~~ RESOLVED 2026-04-10 — temp HP at battle start + short rest.
- ~~**Elemental Adept**~~ RESOLVED — resistance bypass + dice floor of 2 wired.
- ~~**Fey Touched / Shadow Touched**~~ RESOLVED 2026-04-10 — Free-cast tracking wired.
- ~~**Telekinetic**~~ RESOLVED 2026-04-10 — bonus action shove wired.
- ~~**Telepathic**~~ RESOLVED 2026-04-10 — Detect Thoughts free cast 1/LR via grant_free_cast. Telepathic communication is non-combat flavor.
- ~~**Sharpshooter**~~ RESOLVED — skips ranged-in-melee disadvantage. PHB 2024 removed the -5/+10 trade (2014 only).
- ~~**Spell Sniper**~~ RESOLVED — skips ranged-spell-in-melee disadvantage.
- ~~**Poisoner**~~ RESOLVED — poison damage bypasses Resistance.
- ~~**Resilient**~~ RESOLVED — saving throw proficiency wired.
- **Ability Score Improvement** — data only, no combat logic needed.

**Remaining feats without combat logic:** ~15, mostly non-combat (actor, crafter, keen_mind, skilled, magic_initiate variants, armor/weapon proficiency feats). All combat-relevant feat gaps are now RESOLVED (Shield Master choice, Telepathic free cast, medium_armor_master +3 DEX cap already implemented).

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

### Forge Domain Cleric Subclass Audit (2026-04-10) — Xanathar's paras 701-755

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Bonus Proficiencies** (heavy armor, smith's tools) | 1 | 719-720 | DEFERRED — proficiency system handles at character creation. |
| **Blessing of the Forge** (+1 weapon or armor per LR) | 1 | 738-740 | DEFERRED — needs item enchantment infrastructure. +1 AC approximation in `calculate_ac` noted. |
| **Domain Spells** (searing_smite, heat_metal, magic_weapon, elemental_weapon, protection_from_energy, wall_of_fire) | 1-9 | 721-735 | ✓ Done — all 6 auto-prepared in `character_data.nvgt` init block. |
| **Soul of the Forge** (fire resistance + +1 AC in heavy armor) | 6 | 746-749 | ✓ Done — `fire_resistance = true`, +1 AC, extra +1 AC gated on heavy armor type check. |
| **Divine Strike → Blessed Strikes** (1d8 fire at L8, 2d8 at L14) | 8/14 | 750-751 | ✓ Done — wired through existing Blessed Strikes/divine_strike system. |
| **Saint of Forge and Fire** (fire immunity approximated as resistance, B/P/S resistance in heavy armor) | 17 | 752-755 | ✓ Done — `fire_resistance = true` (immunity approximation), `bludgeoning/piercing/slashing_resistance = true` gated on heavy armor. |

### Oath of Conquest Paladin Subclass Audit (2026-04-10) — Xanathar's paras 1949-2003

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Oath Spells** (armor_of_agathys, command, hold_person, spiritual_weapon, bestow_curse, fear, dominate_beast, stoneskin, cloudkill, dominate_person) | 3-17 | 1973-1987 | ✓ Done — all 10 auto-prepared in `character_data.nvgt` init block. |
| **Conquering Presence** (Channel Divinity: frighten each creature of choice within 30ft, WIS save) | 3 | 1988-1991 | Done 2026-04-10 -- Action + CD use. Loops enemies within 30ft, WIS save vs spell DC or Frightened. Client menu entry wired. |
| **Guided Strike** (Channel Divinity: +10 to attack roll) | 3 | 1988-1991 | Done -- field + activation handler + consumption all wired (BA + CD use + +10 attack bonus). Was incorrectly marked PARTIAL. |
| **Aura of Conquest** (frightened creatures in 10ft/30ft aura: speed 0, half-paladin-level psychic damage at turn start) | 7/18 | 1992-1995 | ✓ Done — `aura_of_conquest_active` + `aura_of_conquest_range` (10→30 at L18). Wired in `advance_turn`: scans for frightened enemies within range, sets speed 0, applies psychic damage. |
| **Scornful Rebuke** (when hit, attacker takes CHA mod psychic damage, min 1) | 15 | 1996-1997 | ✓ Done — `scornful_rebuke_active` flag. Wired in ROLL_DAMAGE path after Fire Shield / Refraction Shield. |
| **Invincible Conqueror** (Action: 1 min resistance to all damage + extra attack + crit 19-20, 1/LR) | 20 | 1998-2003 | Done 2026-04-10 -- Action, 1/LR, 10-round timer. Resistance to all damage in apply_damage. +1 extra_attack. Crit 19-20 on melee in get_critical_threshold. Tickdown in advance_turn. Client menu entry at L20+. |

### Gloom Stalker Ranger Subclass Audit (2026-04-10) — Xanathar's paras 2130-2163

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Gloom Stalker Magic** (disguise_self, rope_trick, fear, greater_invisibility, seeming) | 3-17 | 2137-2151 | ✓ Done — all 5 auto-prepared at appropriate Ranger levels. |
| **Dread Ambusher** (+WIS to initiative, +10ft first turn, extra attack on first turn dealing +1d8) | 3 | 2152-2154 | ✓ Done 2026-04-10 — WIS initiative bonus, +10ft speed round 1, extra attack via `dread_ambusher_extra_attack_used` flag (+1 to `attacks_remaining_this_turn` on round 1), +1d8 damage rider on first hit via `dread_ambusher_used`. |
| **Umbral Sight** (darkvision 60ft, invisible in darkness to darkvision-reliant creatures) | 3 | 2155-2157 | DEFERRED — no darkvision/lighting system exists. Flavor/exploration feature, not combat. |
| **Iron Mind** (WIS save proficiency, or INT/CHA if already proficient) | 7 | 2158-2159 | ✓ Done — `save_proficiencies[ABILITY_WIS] = 1` with INT/CHA fallback in `character_data.nvgt`. |
| **Stalker's Flurry** (on miss with weapon attack, make another weapon attack, 1/turn) | 11 | 2160-2161 | ✓ Done — `stalkers_flurry_active` flag, `stalkers_flurry_used_this_turn` per-turn tracking. Full attack + damage roll chain in ROLL_ATTACK miss path. |
| **Shadowy Dodge** (reaction: impose disadvantage if attacker has no advantage) | 15 | 2162-2163 | ✓ Done — `shadowy_dodge_active` flag. Reaction option gated on `!has_effective_advantage`. Handler rolls second d20, takes lower, recalculates attack total. |

### Way of the Drunken Master Monk Subclass Audit (2026-04-10) — Xanathar's paras 1780-1805

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Bonus Proficiencies** (Performance, brewer's supplies) | 3 | 1785-1786 | Done 2026-04-10 -- auto-grants Performance proficiency at init. |
| **Drunken Technique** (on Flurry of Blows: free Disengage + 10ft speed) | 3 | 1787-1790 | ✓ Done — `drunken_technique_active` flag. Wired in Flurry handler: `took_disengage = true` + `movement_remaining += 10`. |
| **Tipsy Sway: Leap to Your Feet** (stand from prone for 5ft instead of half speed) | 6 | 1791-1793 | DEFERRED — prone stand cost not tracked granularly. |
| **Tipsy Sway: Redirect Attack** (reaction when missed: redirect attack to another creature within 5ft) | 6 | 1794-1797 | PARTIAL — `drunken_master_redirect` reaction handler exists (consumes 1 ki + reaction), but full redirect-to-new-target resolution is stub. |
| **Drunkard's Luck** (when making STR/DEX/CON save with disadvantage, spend 1 ki to cancel disadvantage) | 11 | 1798-1800 | DEFERRED — save disadvantage cancellation requires hooking into save resolution pipeline. |
| **Intoxicated Frenzy** (on Flurry of Blows: make up to 3 additional unarmed strikes, each against different target) | 17 | 1801-1805 | DEFERRED — multi-target Flurry expansion requires target selection prompt. |

### Way of the Kensei Monk Subclass Audit (2026-04-10) — Xanathar's paras 1806-1835

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Path of the Kensei: Kensei Weapons** (choose 2 weapon types as kensei weapons) | 3 | 1808-1813 | PARTIAL — `kensei_weapon_active` flag exists. Weapon selection prompt deferred. |
| **Path of the Kensei: Agile Parry** (+2 AC when making unarmed strike while holding melee kensei weapon) | 3 | 1814-1817 | ✓ Done — +2 AC on unarmed strike while holding kensei weapon, AC restored at turn start. |
| **Path of the Kensei: Kensei's Shot** (BA: ranged kensei attacks deal +1d4 this turn) | 3 | 1814-1817 | ✓ Done — `kenseis_shot_active` flag set by BA handler. +1d4 applied in `apply_subclass_on_hit_damage` for ranged weapon attacks. Client menu entry wired. |
| **One with the Blade: Deft Strike** (on kensei weapon hit, spend 1 ki for +MA die damage, 1/turn) | 6 | 1828-1831 | ✓ Done — `deft_strike_active` + `deft_strike_used_this_turn` flags. Wired in `apply_subclass_on_hit_damage`. |
| **One with the Blade: Magic Kensei Weapons** (kensei weapons count as magical) | 6 | 1826-1827 | N/A — damage type bypass not tracked; all weapon attacks resolve normally. |
| **Sharpen the Blade** (BA: spend 1-3 ki for +1/+2/+3 attack and damage, 1 minute, no magic weapon stack) | 11 | 1832-1835 | ✓ Done — `sharpen_the_blade_bonus`/`_rounds` fields. BA handler with ki_amount picker (1-3). Attack bonus in `get_attack_bonus_for_roll`, damage bonus in `get_damage_modifier_for_attack`, both gated on `magic_weapon_bonus == 0`. Duration tickdown in `advance_turn`. Client menu entries for 3 tiers. |
| **Unerring Accuracy** (reroll one weapon miss per turn) | 17 | 1836-1838 | ✓ Done — `unerring_accuracy_active` + `unerring_accuracy_used_this_turn` flags. Wired in ROLL_ATTACK miss path after Stalker's Flurry. |

### Way of the Sun Soul Monk Subclass Audit (2026-04-10) — Xanathar's paras 1836-1865

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Radiant Sun Bolt** (ranged spell attack 30ft, 1d4+DEX radiant, replaces unarmed strike) | 3 | 1840-1845 | PARTIAL — `sun_bolt_ready` flag. Bonus action handler fires radiant bolt. Full unarmed-strike replacement in Attack action deferred. |
| **Searing Arc Strike** (after Attack action: spend 2+ ki to cast Burning Hands as BA, scaling damage) | 6 | 1846-1850 | DEFERRED — requires post-Attack-action trigger + ki-gated spell cast. |
| **Searing Sunburst** (action: 20ft-radius 150ft, 2d6 radiant CON save, +2d6 per ki up to 3) | 11 | 1851-1858 | DEFERRED — AoE ki-scaled spell not yet implemented. |
| **Sun Shield** (bright light 30ft, when hit by melee: 5+WIS radiant, reaction) | 17 | 1859-1865 | ✓ Done — `sun_shield_active` flag. Wired in ROLL_DAMAGE path after apply_damage: `5 + target.get_ability_mod(ABILITY_WIS)` radiant to melee attacker, consumes reaction. |

### Horizon Walker Ranger Subclass Audit (2026-04-10) — Xanathar's paras 2195-2209

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Horizon Walker Magic** (protection from evil, misty step, haste, banishment, teleportation circle) | 3-17 | 2180-2181 | Done 2026-04-10 -- 5 spells auto-prepared at init by Ranger level (protection_from_evil_and_good, misty_step, haste, banishment, teleportation_circle). |
| **Detect Portal** (action: sense nearest planar portal within 1 mile, 1/SR) | 3 | 2195-2198 | DEFERRED — exploration/utility, no combat effect. |
| **Planar Warrior** (BA: mark target, next weapon hit = +1d8/2d8 force, all damage becomes force) | 3 | 2199-2201 | ✓ Done — `planar_warrior_active` flag. BA handler in `users _dom.nvgt`. Damage rider in `apply_subclass_on_hit_damage`. Scales to 2d8 at L11. |
| **Ethereal Step** (BA: cast etherealness, ends at end of turn, 1/SR) | 7 | 2202-2204 | DEFERRED — etherealness mechanics (phase through objects, invisible) require movement/visibility system changes. |
| **Distant Strike** (teleport 10ft before each attack; if hitting 2+ different creatures, make 1 extra attack) | 11 | 2205-2207 | DEFERRED — per-attack teleport + multi-target tracking complex. |
| **Spectral Defense** (reaction: resistance to all damage from one attack) | 15 | 2208-2209 | ✓ Done — `spectral_defense_active` flag. Reaction option in prompt section. Handler sets `warding_maneuver_resistance` for damage halving. |

### Monster Slayer Ranger Subclass Audit (2026-04-10) — Xanathar's paras 2238-2250

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Monster Slayer Magic** (protection from evil, zone of truth, magic circle, banishment, hold monster) | 3-17 | 2210-2237 | Done 2026-04-10 -- 5 spells auto-prepared at init by Ranger level (protection_from_evil_and_good, zone_of_truth, magic_circle, banishment, hold_monster). |
| **Hunter's Sense** (action: learn creature immunities/resistances/vulnerabilities, WIS mod uses/LR) | 3 | 2238-2240 | DEFERRED — creature trait inspection not exposed to player UI. |
| **Slayer's Prey** (BA: mark target, +1d6 first weapon hit per turn, lasts until SR/LR or new target) | 3 | 2241-2243 | ✓ Done — `monster_slayer_prey`, `monster_slayer_target`, `slayer_prey_used_this_turn` flags. BA handler stores target. +1d6 in `apply_subclass_on_hit_damage`. |
| **Supernatural Defense** (+1d6 to saves when Slayer's Prey target forces a save) | 7 | 2244-2245 | PARTIAL — `supernatural_defense_active` flag set on init. Save bonus logic deferred (requires hooking into save resolution for specific attacker gating). |
| **Magic-User's Nemesis** (reaction: counter spell/teleport within 60ft, WIS save vs DC, 1/SR) | 11 | 2246-2248 | DEFERRED — `magic_users_nemesis_used` flag set on init. Counterspell-like reaction requires spell-cast interception system. |
| **Slayer's Counter** (reaction: when prey forces save, make weapon attack first, hit = auto-succeed save) | 15 | 2249-2250 | DEFERRED — `slayers_counter_active` flag set on init. Complex save-interruption mechanics. |

### Oath of Redemption Paladin Subclass Audit (2026-04-10) — Xanathar's paras 2004-2056

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Oath Spells** (sanctuary, sleep, calm emotions, hold person, counterspell, hypnotic pattern, resilient sphere, stoneskin, hold monster, wall of force) | 3-17 | 2028-2042 | Done 2026-04-10 -- 10 spells auto-prepared at init (sanctuary, sleep, calm_emotions, hold_person, counterspell, hypnotic_pattern, resilient_sphere, stoneskin, hold_monster, wall_of_force). |
| **CD: Emissary of Peace** (+5 Persuasion for 10 minutes) | 3 | 2045 | DEFERRED — non-combat social feature. |
| **CD: Rebuke the Violent** (reaction when attacker damages ally within 30ft: WIS save, radiant damage = damage dealt, half on save) | 3 | 2046 | ✓ Done — `rebuke_violent_ready` flag. CD handler in `users _dom.nvgt`. Trigger auto-resolves in ROLL_DAMAGE path: scans for Redemption Paladin within 30ft, WIS save vs DC. |
| **Aura of the Guardian** (reaction: take ally's damage within 10/30ft, unreducible) | 7 | 2047-2048 | PARTIAL — `aura_of_guardian_active` + `aura_of_guardian_range` set on init (10 at L7, 30 at L18). Damage-transfer reaction logic deferred. |
| **Protective Spirit** (end of turn: regain 1d6+half level HP if below half HP and not incapacitated) | 15 | 2050-2051 | ✓ Done — `protective_spirit_active` flag. Passive heal wired in `advance_turn` after Sharpen the Blade tickdown. |
| **Emissary of Redemption** (resistance to all creature damage + radiant retaliation = half damage taken; lost vs creatures you attack) | 20 | 2052-2056 | PARTIAL 2026-04-10 -- resistance to all damage from other creatures + radiant retaliation (half damage dealt) wired in apply_damage. Per-creature exclusion tracking deferred. |

### Path of the Storm Herald Barbarian Subclass Audit (2026-04-10) — Xanathar's paras 416-434

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Storm Aura** (10ft aura on rage: desert=fire dmg, sea=lightning DEX save, tundra=temp HP) | 3 | 416-422 | ✓ Done — `apply_storm_aura_effect()` helper with 3-environment support. Auto-fires on rage entry + BA handler for per-turn reactivation. Flat dmg 2/3/4/5/6 scaling (desert/tundra), d6 dice 1/2/3/4 (sea). Environment stored in `storm_aura_damage_type` (DMG_FIRE/LIGHTNING/COLD). |
| **Storm Soul** (passive resistance: desert=fire, sea=lightning+swim, tundra=cold) | 6 | 423-427 | ✓ Done — resistance auto-granted at init based on `storm_aura_damage_type` (desert→fire, sea→lightning, tundra→cold). Swim speed deferred (no swim combat). |
| **Shielding Storm** (aura grants Storm Soul resistance to allies) | 10 | 428-429 | DEFERRED — extending resistance to other combatants in AoE requires per-turn resistance tracking. |
| **Raging Storm** (desert=reaction fire on melee hit, sea=reaction prone on hit, tundra=STR save speed 0) | 14 | 430-434 | DEFERRED — 3 reaction/trigger variants. Desert variant similar to Scornful Rebuke pattern. |

### College of Glamour Bard Subclass Audit (2026-04-10) — Xanathar's paras 549-565

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Mantle of Inspiration** (BA, 1 BI: flat 5/8/11/14 temp HP to CHA mod allies within 60ft) | 3 | 549-552 | ✓ Done — BA handler in `users _dom.nvgt`. Fixed: was BI die+CHA, now flat 5/8/11/14 per source. Movement reaction deferred (allies can move up to speed without OA). |
| **Enthralling Performance** (1-minute performance, WIS save or charmed for 1 hour) | 3 | 553-557 | DEFERRED — non-combat social feature. |
| **Mantle of Majesty** (BA: free Command each turn for 1 minute, concentration, 1/LR) | 6 | 558-561 | DEFERRED — requires casting pipeline integration for free Command each turn. |
| **Unbreakable Majesty** (BA 1 min: attackers must CHA save or can't attack you this turn) | 14 | 562-565 | DEFERRED — requires per-attacker save check before attack resolution. |

### College of Swords Bard Subclass Audit (2026-04-10) — Xanathar's paras 579-595

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Bonus Proficiencies** (medium armor, scimitar) | 3 | 579-581 | N/A — proficiency tracking exists but not auto-granted by subclass. |
| **Fighting Style** (Dueling or Two-Weapon Fighting) | 3 | 582-585 | PARTIAL — Dueling/TWF feat system exists; not auto-prompted at subclass selection for Swords Bard. |
| **Blade Flourish** (on Attack action +10ft speed; on weapon hit spend 1 BI for extra damage + variant) | 3 | 586-591 | PARTIAL — `blade_flourish_active` BA handler spends BI for bonus BI-die damage. +10ft speed on Attack action wired 2026-04-10 via `blade_flourish_speed_applied`. Missing: 3 Flourish variants (Defensive=+AC, Slashing=AoE, Mobile=push+move) — needs player choice prompt. |
| **Extra Attack** (attack twice per Attack action) | 6 | 592-593 | ✓ Done — `c.extra_attacks = 1` at L6 in character_data.nvgt. |
| **Master's Flourish** (Blade Flourish can roll d6 instead of spending BI) | 14 | 594-595 | Done 2026-04-10 -- At L14+, Blade Flourish rolls d6 instead of expending BI die. Handler bypasses BI spend; damage rider uses d6 at L14+. |

### College of Whispers Bard Subclass Audit (2026-04-10) — Xanathar's paras 610-631

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Psychic Blades** (on weapon hit, spend 1 BI: 2d6/3d6/5d6/8d6 psychic, 1/round on turn) | 3 | 610-613 | ✓ Done — `psychic_blades_pending` flag. Fixed: was wrong scaling formula. Now correctly 2d6/3d6/5d6/8d6 at L3/5/10/15 per source. |
| **Words of Terror** (1-min speech, WIS save or frightened, 1/SR) | 3 | 614-618 | DEFERRED — non-combat social feature. |
| **Mantle of Whispers** (reaction: capture dead humanoid's shadow, use as disguise) | 6 | 619-624 | DEFERRED — non-combat espionage feature. |
| **Shadow Lore** (action: WIS save or charmed 8 hours, obeys commands) | 14 | 625-631 | DEFERRED — non-combat social feature. |

### Circle of Dreams Druid Subclass Audit (2026-04-10) — Xanathar's paras 883-898

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Balm of the Summer Court** (BA: spend up to half-level d6s, heal total + 1 temp HP per die) | 2 | 883-886 | ✓ Done — `balm_of_summer_pool = cs.level`. BA handler rolls `dice_count` d6s (clamped to 1..level/2 and pool), heals total, grants temp HP = dice spent. `dice_count` param supported (default 1). |
| **Hearth of Moonlight and Shadow** (rest in 30ft sphere: invisible to creatures outside, +5 Stealth/Perception) | 6 | 889-892 | DEFERRED — rest/camp system not yet implemented. No combat effect. |
| **Hidden Paths** (BA: teleport self 60ft or willing creature within 30ft 30ft, WIS mod uses/LR) | 10 | 891-893 | ✓ Done — `hidden_paths_uses`/`_max` fields (WIS mod, min 1). BA handler teleports self 60ft toward target (12 tiles). Client menu entry wired at L10+. Touch-teleport-ally variant deferred. |
| **Walker in Dreams** (after SR: cast Dream, Scrying, or Teleportation Circle for free) | 14 | 896-898 | DEFERRED — non-combat/exploration feature. |

### Circle of the Shepherd Druid Subclass Audit (2026-04-10) — Xanathar's paras 913-932

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Speech of the Woods** (Sylvan language + communicate with beasts) | 2 | 913-915 | N/A — language/roleplay feature, no combat effect. |
| **Spirit Totem** (BA: summon 60ft spirit aura for 1 min — Bear: temp HP 5+level + STR advantage; Hawk: reaction grant attack advantage; Unicorn: healing spells heal allies in aura) | 2 | 916-923 | PARTIAL — Bear: temp HP (5+level) + STR Athletics advantage now wired. Unicorn: `try_unicorn_totem_heal()` fires after Cure Wounds, Healing Word, Mass Healing Word, Heal — heals allies within 30ft for druid level HP. Hawk: reaction-to-grant-advantage deferred (needs reaction prompt extension). |
| **Mighty Summoner** (summoned beasts/fey: +2 HP per HD + attacks count as magical) | 6 | 925-927 | DEFERRED — requires companion/summon HP scaling hooks. |
| **Guardian Spirit** (beast/fey in Spirit Totem aura regain HP = half druid level at end of their turn) | 10 | 928-929 | DEFERRED — requires per-turn heal on summons within aura. |
| **Faithful Summons** (when reduced to 0 HP: auto-cast Conjure Animals 8 beasts, no concentration, 1/LR) | 14 | 930-932 | DEFERRED — auto-cast trigger on death + mass summon. |

### Inquisitive Rogue Subclass Audit (2026-04-10) — Xanathar's paras 2332-2345

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Ear for Deceit** (minimum roll on Insight to detect lies = 8 + WIS mod) | 3 | 2332-2333 | DEFERRED — non-combat social feature. |
| **Eye for Detail** (BA: Perception check to find hidden creature or Investigation check to find clues) | 3 | 2334-2335 | DEFERRED — BA skill check not wired. |
| **Insightful Fighting** (BA: Insight vs target's Deception; success = SA without advantage for 1 min) | 3 | 2336-2339 | ✓ Done — `inquisitive_target` field. BA handler sets target. SA qualification integrated into standard SA condition block (no longer a separate double-dip block). |
| **Steady Eye** (advantage on Perception and Investigation if move ≤ half speed) | 9 | 2340-2341 | DEFERRED — non-combat, requires movement tracking per turn for conditional advantage. |
| **Unerring Eye** (action: sense illusion/shapechanger/deception within 30ft, WIS mod uses/LR) | 13 | 2342-2343 | DEFERRED — detection/utility feature, no direct combat effect. |
| **Eye for Weakness** (+3d6 SA against Insightful Fighting target) | 17 | 2344-2345 | ✓ Done — +3d6 bonus fires inside SA block when `inquisitive_target` matches and level >= 17. |

### Mastermind Rogue Subclass Audit (2026-04-10) — Xanathar's paras 2361-2377

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Master of Intrigue** (disguise kit, forgery kit, 2 languages, mimic speech/writing) | 3 | 2361-2365 | N/A — proficiency/roleplay feature, no combat effect. |
| **Master of Tactics** (Help as BA at 30ft range instead of action at 5ft) | 3 | 2366-2369 | ✓ Done — `mastermind_help` flag. BA handler sets help target with 30ft range validation. |
| **Insightful Manipulator** (study creature for 1 min: learn 2 stats relative to self) | 9 | 2370-2372 | DEFERRED — non-combat information-gathering feature. |
| **Misdirection** (reaction: redirect attack targeting you to another creature within 5ft providing cover) | 13 | 2373-2375 | DEFERRED — requires cover system + attack-redirect reaction. |
| **Soul of Deceit** (immune to telepathy, always appear truthful to lies-detection magic, CHA vs WIS on zone of truth) | 17 | 2376-2377 | DEFERRED — non-combat / anti-magic detection feature. |

### Scout Rogue Subclass Audit (2026-04-10) — Xanathar's paras 2391-2401

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Skirmisher** (reaction: move half speed when enemy ends turn within 5ft, no OA) | 3 | 2391-2393 | PARTIAL — `scout_skirmisher` flag set on init. Manual BA activation exists but automatic end-of-enemy-turn trigger not implemented (needs per-movement event hooks). |
| **Survivalist** (proficiency + expertise in Nature and Survival) | 3 | 2394-2395 | ✓ Done — auto-grants Nature + Survival proficiency and expertise at init. |
| **Superior Mobility** (+10ft speed to walk/climb/swim) | 9 | 2396-2397 | ✓ Done — `c.speed += 10` at init. Climb/swim deferred (no climbing/swimming combat). |
| **Ambush Master** (advantage on initiative; first creature hit in first turn grants all allies advantage vs it until start of next turn) | 13 | 2398-2399 | ✓ Done 2026-04-10 — initiative advantage wired. `ambush_master_marked_by` field set on first hit in round 1; all attacks vs marked target get advantage via `apply_attack_advantage_state`. Mark cleared at start of Scout's next turn. |
| **Sudden Strike** (if take Attack action, can make extra attack as BA against different creature with SA) | 17 | 2400-2401 | DEFERRED — extra attack via BA with SA on different target. |

### Swashbuckler Rogue Subclass Audit (2026-04-10) — Xanathar's paras 2418-2430

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Fancy Footwork** (after melee attack vs creature, it can't make OA against you for rest of turn) | 3 | 2418-2420 | ✓ Done — `swashbuckler_attacked_this_turn` flag. Set on attack in battle_manager. OA suppression logic checks flag. Reset in `advance_turn`. |
| **Rakish Audacity** (+CHA to initiative; SA without advantage if no creature other than target within 5ft of you) | 3 | 2421-2423 | ✓ Done — +CHA initiative bonus in `request_next_initiative`. Solo-engagement SA condition integrated into standard SA qualification block in `apply_subclass_on_hit_damage`. |
| **Panache** (action: Persuasion vs Insight; hostile = disadvantage on attacks vs others and no OA for 1 min; friendly = charmed for 1 min) | 9 | 2424-2426 | DEFERRED — non-combat social feature (hostile version has combat use but needs contested check system). |
| **Elegant Maneuver** (BA: advantage on next Acrobatics or Athletics check this turn) | 13 | 2427-2428 | DEFERRED — BA skill check advantage grant. |
| **Master Duelist** (1/SR: miss → reroll with advantage) | 17 | 2429-2430 | ✓ Done — `master_duelist_active` + `master_duelist_used` flags. Reroll with advantage in miss path after Unerring Accuracy. |

### Celestial Warlock Subclass Audit (2026-04-10) — Xanathar's paras 2720-2747

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Expanded Spell List** (Cure Wounds, Flaming Sphere, Lesser Restoration, Daylight, Revivify, Guardian of Faith, Wall of Fire, Flame Strike, Greater Restoration) | 1-9 | 2720-2726 | Done 2026-04-10 -- 9 spells auto-prepared at init by Warlock level (cure_wounds, flaming_sphere, lesser_restoration, daylight, revivify, guardian_of_faith, wall_of_fire, flame_strike, greater_restoration). |
| **Bonus Cantrips** (Light, Sacred Flame) | 1 | 2727-2728 | ✓ Done — auto-added to `prepared_spells` at init. |
| **Healing Light** (BA: pool of 1+level d6s, spend 1-CHA mod dice to heal creature within 60ft) | 1 | 2729-2735 | ✓ Done — `healing_light_dice` field initialized to `1 + cs.level`. BA handler with dice spending. Client menu entry wired. |
| **Radiant Soul** (resistance to radiant damage; when casting fire/radiant spell, add CHA to one damage roll) | 6 | 2736-2739 | ✓ Done 2026-04-10 — radiant resistance at init + CHA mod added to fire/radiant spell damage in both save-based (`resolve_spell_save_damage_roll`) and attack-roll (`ROLL_DAMAGE`) paths. Per-turn flag `radiant_soul_used_this_turn`. |
| **Celestial Resilience** (temp HP = Warlock level + CHA at end of SR/LR; 5 allies get half Warlock level + CHA) | 10 | 2740-2743 | PARTIAL — self temp HP (level + CHA) applied at combat init. Ally temp HP distribution deferred (no rest system yet). |
| **Searing Vengeance** (at start of turn while dying: regain half max HP + stand + 2d8+CHA radiant to chosen creatures within 30ft, blinding on fail, 1/LR) | 14 | 2744-2747 | ✓ Done 2026-04-10 — replaces death save at start of turn. Regains half max HP, removes UNCONSCIOUS, deals 2d8+CHA radiant to enemies within 30ft, blinds them. 1/LR via `searing_vengeance_used`. |

### Path of the Zealot Barbarian Subclass Audit (2026-04-10) — Xanathar's paras 435-450

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Divine Fury** (first melee weapon hit per turn while raging: +1d6 + half level radiant/necrotic) | 3 | 439-440 | ✓ Fixed 2026-04-10 — was missing `+ half level` scaling and `is_weapon_attack` gate. Now `random(1, 6) + attacker.level / 2` gated on `is_weapon_attack`. |
| **Warrior of the Gods** (resurrection spells cost no material components) | 3 | 441-442 | DEFERRED — non-combat / resurrection system not yet implemented. |
| **Fanatical Focus** (while raging, reroll failed save 1/rage) | 6 | 443-444 | ✓ Done 2026-04-10 — `try_fanatical_focus` helper, wired into 5 EOT saves + concentration save, before Flash of Genius in reroll chain. `fanatical_focus_used_this_rage` flag reset on rage start. |
| **Zealous Presence** (BA 1/LR: up to 10 allies within 60ft gain advantage on attacks and saves until start of your next turn) | 10 | 445-447 | ✓ Done 2026-04-10 — BA handler in users_dom.nvgt, attack advantage via `apply_attack_advantage_state`, buff cleanup at start of Zealot's turn. Save advantage for inline spell saves deferred (only EOT/pending_roll saves benefit). |
| **Rage Beyond Death** (while raging at 0 HP: don't fall unconscious, death saves still accumulate, die when rage ends if at 0 HP) | 14 | 448-450 | ✓ Done 2026-04-10 — 3-site implementation: apply_damage (stay conscious), process_death_save (defer death), advance_turn rage expiry (death on rage end if 0 HP). |

### Clockwork Soul Sorcerer Subclass Audit (2026-04-10) — Tasha's paras 3953-4011

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Clockwork Magic** (auto-prepared abjuration/transmutation spells by level) | 1 | 3958-3974 | ✓ Done — protection_from_evil_and_good, aid, lesser_restoration, dispel_magic, protection_from_energy, greater_restoration, wall_of_force. L7 freedom_of_movement + summon_construct skipped (not in spell catalog). Alarm skipped (non-combat). |
| **Restore Balance** (reaction: cancel advantage/disadvantage on d20 test within 60ft, PB uses/LR) | 1 | 3993-3996 | PARTIAL — reaction fires only on attacks against self with advantage (source allows any creature within 60ft on any d20 test). Fixed 2026-04-10: now gated on `has_effective_advantage` and rerolls a flat d20 instead of the old -5 flat penalty. |
| **Bastion of Law** (action: 1-5 SP, create Nd8 ward dice on self/ally within 30ft) | 6 | 3997-4000 | ✓ Done — ward dice absorb damage in `apply_damage` (auto-optimal one-at-a-time spend). Source says creature chooses how many dice to spend; auto-optimization is acceptable. |
| **Trance of Order** (BA 1 min: attacks against you can't benefit from advantage, d20 ≤9→10 on attack/check/save, 1/LR or 5 SP) | 14 | 4001-4004 | ✓ Fixed 2026-04-10 — was missing 1/LR tracking entirely (unlimited free uses). Added `trance_of_order_used` field. Handler now properly gates: first use free, subsequent uses cost 5 SP. Anti-advantage in `apply_attack_advantage_state`, d20 clamp in `finalize_roll_result`, duration tickdown in `advance_turn` all verified. |
| **Clockwork Cavalcade** (action: 30ft cube, 100 HP heal split among chosen + dispel ≤6th level spells, 1/LR or 7 SP) | 18 | 4005-4011 | PARTIAL — 100 HP healing correctly distributed among allies within 30ft, 1/LR with 7 SP reuse. Dispel effect ("every spell of 6th level or lower ends") is NOT implemented (requires spell tracking on creatures). |

### College of Eloquence Bard Subclass Audit (2026-04-10) — Tasha's paras 1703-1719

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Silver Tongue** (Persuasion/Deception check: treat d20 ≤9 as 10) | 3 | 1703-1705 | ✓ Done — `silver_tongue_active` flag, clamp in `finalize_roll_result` on `skill_persuasion`/`skill_deception`. |
| **Unsettling Words** (BA: expend Bardic Inspiration, target subtracts die from next save before start of your next turn) | 3 | 1706-1708 | ✓ Done — `unsettling_words_pending` flag with `unsettling_words_target`. Applied in end-of-turn save resolution. Consumed on next save. Turn-start expiry not implemented (persists until consumed). |
| **Unfailing Inspiration** (when creature uses your Bardic Inspiration die and the roll fails, they keep the die) | 6 | 1709-1711 | ✓ Done 2026-04-10 — `check_eloquence_inspiration` helper tracks `bardic_source_id`/`bardic_die_used` on pending_roll. On failed roll with bardic die from Eloquence L6+ Bard, die is restored to the creature. Wired into all 5 resolution points (attack, death save, concentration, hide, ability check). |
| **Universal Speech** (action: CHA mod creatures within 60ft understand you for 1 hour, 1/LR or spell slot) | 6 | 1712-1715 | DEFERRED — non-combat flavor/social feature. |
| **Infectious Inspiration** (reaction: when creature succeeds with your Bardic die, grant a free die to another ally within 60ft, CHA mod uses/LR) | 14 | 1716-1719 | ✓ Done 2026-04-10 — `infectious_inspiration_uses` field (CHA mod, min 1). Auto-resolved: on successful bardic-aided roll, nearest eligible ally within 60ft without a die gets one free. Consumes source Bard's reaction. |

### Psi Warrior Fighter Subclass Audit (2026-04-10) — Tasha's paras 6-50

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Psionic Power** (Psionic Energy dice pool = 2×proficiency bonus, die scaling d6 L3 / d8 L5 / d10 L11 / d12 L17) | 3 | 6-13 | ✓ Fixed 2026-04-10 — was `prof` (half), corrected to `prof * 2`. Die size scaling via `psionic_die_size` field set on init. |
| **Psionic Strike** (on hit: spend 1 die, deal die + INT mod force damage) | 3 | 14-17 | ✓ Fixed 2026-04-10 — now uses `psionic_die_size` instead of hardcoded d6. |
| **Protective Field** (reaction: when you or ally within 30ft takes damage, reduce by die + INT mod) | 3 | 18-21 | DEFERRED — needs reaction prompt extension for damage-reduction reactions. |
| **Telekinetic Movement** (action: move Large or smaller object/creature 30ft) | 3 | 22-25 | DEFERRED — non-combat utility; needs position-picker UI for combat use. |
| **Telekinetic Thrust** (on Psionic Strike hit: STR save or pushed 10ft + prone) | 7 | 26-29 | DEFERRED — Psionic Strike is wired but Thrust rider not yet added. |
| **Guarded Mind** (psychic resistance; spend die to end charmed/frightened) | 10 | 30-33 | PARTIAL — `psychic_resistance = true` set on init at L10. Condition-clearing spend not implemented. |
| **Bulwark of Force** (BA: grant half cover to INT mod allies within 30ft, concentration 1 min) | 15 | 34-40 | DEFERRED — cover system not in combat grid. |
| **Telekinetic Master** (cast Telekinesis free 1/LR or spend 7 Psionic Energy dice) | 18 | 41-50 | DEFERRED — Telekinesis spell not fully implemented. |

### Phantom Rogue Subclass Audit (2026-04-10) — Tasha's paras 3438-3474

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Whispers of the Dead** (after rest: gain proficiency in 1 skill or tool until next rest) | 3 | 3438-3442 | DEFERRED — needs rest subsystem + proficiency swap UI. |
| **Wails from the Grave** (after Sneak Attack: half SA dice d6 necrotic to second creature within 30ft of target, Prof uses/LR) | 3 | 3443-3451 | ✓ Fixed 2026-04-10 — was gated at L9 with `prof/2` uses. Corrected to L3 with full `prof` uses. Auto-selects nearest enemy within 30ft of target. |
| **Tokens of the Departed** (reaction on death within 30ft: create soul trinket, max Prof trinkets; while trinket held, death saves have advantage; destroy trinket for SA without normal requirements or Wails free use) | 9 | 3452-3462 | DEFERRED — needs trinket item infrastructure + death save advantage hook. |
| **Ghost Walk** (BA: spectral form — fly 10ft hover, attacks against you have disadvantage unless attacker can see invisible, 10 min, Prof uses/LR) | 13 | 3463-3469 | DEFERRED — fly/hover movement not in combat grid. |
| **Death's Friend** (Wails from the Grave necrotic also hits the Sneak Attack target; if no soul trinkets, one appears) | 17 | 3470-3474 | PARTIAL — L17 dual-target Wails damage done. Trinket auto-creation not implemented (blocked on Tokens of the Departed). |

### Rune Knight Fighter Subclass Audit (2026-04-10) — Tasha's paras 3200-3280

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Giant's Might** (BA: become Large for 1 min, +1d6 weapon damage once/turn, ADV on STR checks/saves, Prof uses/LR) | 3 | 3200-3210 | ✓ Fixed 2026-04-10 — damage die now scales (d6 L3 / d8 L10 / d10 L18). Added `is_first_hit_this_turn` gate for once-per-turn. STR check/save advantage not yet wired. |
| **Rune Carver** (learn 2 runes at L3, +1 at L7/10/15; invoke each 1/LR) | 3 | 3211-3240 | DEFERRED — 6 runes (Cloud, Fire, Frost, Stone, Hill, Storm) each with passive + invoked effect. Needs rune selection UI + invocation handlers. |
| **Runic Shield** (reaction: when ally within 60ft is hit, force attacker to reroll and use lower) | 7 | 3241-3245 | DEFERRED — needs reaction prompt extension. |
| **Great Stature** (height +3d4 inches; Giant's Might extra damage die → d8) | 10 | 3246-3250 | ✓ Implicit — die scaling already in `gm_die` logic (`d8` at L10+). Height is flavor only. |
| **Master of Runes** (invoke each rune twice instead of once per LR) | 15 | 3251-3255 | DEFERRED — blocked on Rune Carver implementation. |
| **Runic Juggernaut** (Large → Huge on Giant's Might; Giant's Might die → d10; +5ft reach) | 18 | 3256-3260 | PARTIAL — die scales to d10. Size change to Huge and +5ft reach not implemented. |

### Circle of Stars Druid Subclass Audit (2026-04-10) — Tasha's paras 2130-2181

| Feature | Level | Source para | Status |
|---------|-------|-------------|--------|
| **Star Map** (learn Guidance cantrip + Guiding Bolt free; Guiding Bolt free casts = Prof/LR) | 2 | 2130-2140 | PARTIAL — auto-adds Guidance + Guiding Bolt to prepared spells. Free cast tracking not implemented (uses spell slots). |
| **Starry Form: Archer** (BA ranged spell attack 60ft, 1d8+WIS radiant; scales to 2d8 at L10) | 2 | 2141-2150 | DEFERRED — needs a BA combat handler for the ranged spell attack each turn. |
| **Starry Form: Chalice** (when you cast a heal spell with spell slot, bonus 1d8+WIS heal to another creature within 30ft; 2d8 at L10) | 2 | 2151-2155 | DEFERRED — needs hook into heal spell resolution path. |
| **Starry Form: Dragon** (INT/WIS checks and concentration saves: treat d20 ≤9 as 10) | 2 | 2156-2160 | ✓ Done 2026-04-10 — clamp in `finalize_roll_result` for `ROLL_ABILITY_CHECK` (INT/WIS) and `ROLL_CONCENTRATION`. |
| **Cosmic Omen** (after LR: roll die → Woe or Weal; reaction to subtract/add d6 from creature's attack/save/check within 30ft, Prof uses/LR) | 6 | 2161-2168 | DEFERRED — needs reaction prompt for triggered buff/debuff on ally/enemy rolls. |
| **Twinkling Constellations** (change Starry Form at start of each turn; Archer/Chalice heal dice → 2d8) | 10 | 2169-2173 | DEFERRED — blocked on Archer/Chalice implementation + advance_turn hook. |
| **Full of Stars** (while in Starry Form: resistance to B/P/S damage) | 14 | 2179-2181 | ✓ Done 2026-04-10 — `apply_damage` halves B/P/S when `starry_form_active and level >= 14`. |

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

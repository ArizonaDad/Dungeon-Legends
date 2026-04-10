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
| **Brutal Strike** (forgo advantage for +1d10 + Forceful/Hamstring effect) | 9 | 2338-2341 | ✗ DEFERRED — needs a player-choice prompt similar to `pending_smite_prompt` (declared via bonus action, drops Reckless Attack advantage, prompts for effect on hit). Not yet wired. |
| Relentless Rage (DC 10 CON save when dropped to 0 HP, +5 each use) | 11 | 2342-2344 | ✓ Done |
| **Improved Brutal Strike** (Staggering/Sundering effects) | 13 | 2345-2348 | ✗ DEFERRED — depends on Brutal Strike infrastructure |
| **Persistent Rage** (rage lasts 10 minutes / 100 rounds without needing to extend) | 15 | 2349-2351 | ✓ Done 2026-04-09 — rage handler sets `rage_turns_remaining = 100` and `persistent_rage_active = true` at L15+ |
| **Improved Brutal Strike** (2d10 + 2 effects) | 17 | 2352-2353 | ✗ DEFERRED — depends on Brutal Strike infrastructure |
| **Indomitable Might** (STR check/save total ≥ STR score) | 18 | 2354-2355 | ✓ Done 2026-04-09 — new `combatant.apply_indomitable_might(total, ability_id)` helper. Wired into `finalize_roll_result` for STR ability checks via the new `pr.ability_id` field, plus inline at the trip attack / hobbling strike / shield master / shove / grapple sites. Not yet wired into all spell-handler STR saves (Storm Sphere, etc.) — those are rare and queued for a later pass. |
| **Primal Champion** (+4 STR/CON, max 25) | 20 | 2358-2359 | ✓ Done 2026-04-09 — `apply_class_defaults` adds the bonus with the cap |

**Brutal Strike infrastructure plan (deferred):** Add `brutal_strike_pending` flag on combatant + a `brutal_strike` bonus action menu entry. When set, the next Strength-based weapon attack drops Reckless Attack advantage (must not have disadvantage). On hit, deal +1d10 (or +2d10 at L17) of the weapon's damage type and queue a `pending_brutal_strike_choice` prompt with the available effects (Forceful/Hamstring at L9, +Staggering/Sundering at L13). Player picks via numeric key. At L17, repeat the prompt for a second different effect.

Other base class features that still need the same audit:
- **Barbarian (Brutal Strike line above is the only remaining gap)**

### Bard — RESOLVED 2026-04-09 (mostly)
Audited against Basic Rules 2024 paras 2722-2765 (full Bard class entry).

| Feature | Level | Source para | Status |
|---|---|---|---|
| Bardic Inspiration (BA, 60 ft, d6→d12) | 1 | 2722-2727 | ✓ Done |
| Spellcasting (full caster, CHA) | 1 | 2728-2739 | ✓ Done |
| Expertise (2 skills L2, +2 more L9) | 2/9 | 2740-2742 | ✓ Done (system-wide expertise field) |
| Jack of All Trades (half-prof on non-prof skill checks) | 2 | 2743-2745 | ✓ Done — `combatant.jack_of_all_trades` flag set in `character_data.nvgt` and consumed by `get_skill_bonus` |
| Bard Subclass | 3 | 2749-2750 | ✓ Done |
| Font of Inspiration (regen BI on Short Rest, spend slot to regain one) | 5 | 2753-2755 | PARTIAL — regen-on-rest works because in-combat there are no short rests and a long rest (between sessions) restores all uses; the spell-slot-to-BI swap is not yet wired. Defer until a `convert_slot_to_bardic_inspiration` bonus action menu entry exists. |
| **Countercharm** (Reaction reroll on Charmed/Frightened save fail) | 7 | 2756-2757 | ✗ DEFERRED — requires intercepting save failures at many call sites and offering a Reaction prompt to nearby Bard L7+. Pattern is similar to Cutting Words / Warding Flare. |
| Magical Secrets (broader spell list at L10) | 10 | 2758 | ✓ Done (out-of-combat spell list expansion, handled by spell menu) |
| **Superior Inspiration** (top up BI to 2 on Initiative) | 18 | 2760-2761 | ✓ Done 2026-04-09 — `request_next_initiative` restores BI uses to 2 if fewer for Bard L18+ |
| **Words of Creation** (Power Word Heal/Kill always prepared, target second creature within 10 ft) | 20 | 2764 | ✗ DEFERRED — auto-prepared can be added to `apply_class_defaults`, but the multi-target rider on Power Word Heal/Kill needs custom handler edits |

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
| Druidic (Speak with Animals always prepared) | 1 | 4384-4386 | PARTIAL — language flavor only; auto-prepare of Speak with Animals deferred |
| **Primal Order** (Magician or Warden — once-per-character choice) | 1 | 4387-4390 | ✓ Done 2026-04-09 — `primal_order` field on character_sheet + combatant. Configured via Shift+P → "Set Druid Primal Order". Magician bonus to Arcana/Nature checks (WIS mod, min +1) wired in `finalize_roll_result`. Warden martial-weapon + medium-armor proficiency at character creation deferred to a future `apply_class_defaults` pass. |
| Wild Shape (BA, scale 2/3/4 uses at L2/6/14, temp HP) | 2 | 4391-4419 | ✓ Done — and 2026-04-09 added the use-count scaling to `apply_class_defaults` (was hard-coded to 2). |
| **Wild Companion** (Magic action, expend slot or WS use, cast Find Familiar) | 2 | 4420-4422 | ✓ Done 2026-04-09 — bonus action handler in `users _dom.nvgt` consumes WS use first, falls back to lowest spell slot. Find Familiar narrative-only (no grid familiar pet, matches no-pet-grid policy). Client menu entry visible at Druid L2+. |
| Druid Subclass | 3 | 4423-4424 | ✓ Done |
| **Wild Resurgence** (slot → WS use 1/turn; WS use → L1 slot 1/long rest) | 5 | 4427-4429 | ✓ Done 2026-04-09 — two no-action bonus action handlers (`wild_resurgence_slot_to_use` and `wild_resurgence_use_to_slot`). Per-turn and per-rest tracking flags reset at turn start (slot → use) and on long rest (use → slot). |
| **Elemental Fury** (Potent Spellcasting OR Primal Strike — choose at L7) | 7 | 4430-4433 | ✓ Done 2026-04-09 — `elemental_fury_choice` field. Primal Strike: `roll_primal_strike` helper applies +1d8 cold/fire/lightning/thunder once per turn on weapon and Wild Shape attacks (mirrors Cleric Divine Strike). Potent Spellcasting: `druid_potent_spellcasting_bonus` adds WIS mod to Druid cantrip damage (produce_flame inline + generic spell save damage path both updated). Damage type sub-choice persisted. Configured via Shift+P. |
| **Improved Elemental Fury** (Primal Strike +2d8 / Potent Spellcasting cantrip range +300 ft) | 15 | 4434-4437 | ✓ Done 2026-04-09 — Primal Strike doubles dice at L15+ via `roll_primal_strike`. Potent Spellcasting cantrip range extension is descriptive only (range checks pass at +300 ft regardless since combat grid is small). |
| **Beast Spells** (cast spells in Wild Shape form, except costed material components) | 18 | 4438-4439 | ✗ DEFERRED — requires Wild Shape spellcasting refactor (current code blocks spellcasting in beast form). |
| **Archdruid: Evergreen Wild Shape** (regen WS on Initiative if 0 uses) | 20 | 4444 | ✗ DEFERRED — easy add, slated for L20 polish pass. |
| **Archdruid: Nature Magician** (convert WS uses to a single spell slot, 1/long rest) | 20 | 4445 | ✗ DEFERRED — needs a player-prompt "how many uses to convert" UI. Per-rest flag is in place. |

**Player choice infrastructure:** Three new Phase 1 config commands (`set_primal_order`, `set_elemental_fury`, `set_primal_strike_damage_type`) added to the Shift+P menu. They persist to `account.data` so Druid choices survive across sessions.


### Fighter Audit (PHB 2024 Basic Rules paras 4967-5135) — completed 2026-04-09

| Feature | Lvl | Source para | Status |
|---|---|---|---|
| Fighting Style (feat selection from list) | 1 | 5100-5102 | ✓ Done — chooses a Fighting Style feat at creation; feat data has the styles. |
| **Second Wind** (BA, heal 1d10+lvl, scaling uses) | 1 | 5103-5106 | ✓ Done 2026-04-09 — was a single bool; now `second_wind_uses_remaining` / `second_wind_uses_max` int pair. 2 uses L1-3, 3 uses L4-9, 4 uses L10+. Bonus action handler decrements properly and announces remaining. |
| **Weapon Mastery** (3/4/5/6 weapons by level) | 1 | 5107-5109 | PARTIAL — character creation tracks the choice; the property effects themselves (Push/Sap/Slow/Vex/etc.) are NOT yet wired into attack resolution. The local `mastery` variable in `apply_weapon` is set then discarded — needs a follow-up to plumb mastery IDs through to the combatant and the attack pipeline. |
| **Action Surge** (1 use L2, 2 uses L17) | 2 | 5110-5112 | ✓ Done — properly tracked and handled. |
| **Tactical Mind** (spend Second Wind on failed ability check, refund on still-fail) | 2 | 5113-5114 | ✓ Done 2026-04-09 — new prompt chain entry after Lucky/Heroic. `pending_tactical_mind_prompt` struct + `maybe_prompt_tactical_mind` + `handle_tactical_mind_response` server-side. New `tactical_mind_prompt`/`tactical_mind_response` message types. Client `prompt_tactical_mind_choice` + `check_tactical_mind_prompt_input` (T to use, Escape to skip). Use is refunded if the +1d10 still fails to clear the DC, per source. Bots auto-use when `failure_margin <= 5` (1d10 average). |
| Fighter Subclass | 3 | 5115-5116 | ✓ Done — Champion + many extra subclasses. |
| Ability Score Improvement | 4/6/8/12/14/16 | 5117-5118 | ✓ Done. |
| Extra Attack | 5 | 5119-5120 | ✓ Done. |
| **Tactical Shift** (Second Wind also grants half-Speed OA-free move) | 5 | 5121-5122 | ✓ Done 2026-04-09 — `tactical_shift_feet_remaining` field on combatant. When Second Wind is activated at L5+, that pool is set to half speed and `movement_remaining` is bumped. `check_opportunity_attacks` consumes pool greedily and suppresses OA while feet remain. Cleared at start of turn. |
| **Indomitable** (failed save reroll, +Fighter level) | 9 | 5123-5125 | ✓ Done — 1/2/3 uses at L9/13/17, properly hooked in `handle_save_result`. |
| **Tactical Master** (replace weapon mastery with Push/Sap/Slow) | 9 | 5126-5127 | ✗ DEFERRED — depends on Weapon Mastery property application system being wired first. Stubbed in audit notes. |
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
| **Heightened Focus** (Flurry +1 strike, Patient Def temp HP, Step ally) | 10 | 5357-5361 | PARTIAL 2026-04-09 — Patient Defense temp HP rider implemented. Flurry of Blows third strike and Step of the Wind ally-carry deferred (Flurry needs `start_flurry_strike` count parameter, ally-carry needs targeting prompt). |
| **Self-Restoration** (auto remove Charmed/Frightened/Poisoned at end of turn) | 10 | 5362-5364 | ✓ Done 2026-04-09 — `self_restoration_active` flag and end-of-turn cleanup in `advance_turn` (highest-priority condition removed first). |
| **Subclass feature** | 11 | 5256 | ✓ Done. |
| **Deflect Energy** (Deflect Attacks works on any damage type) | 13 | 5365-5366 | ✓ Done 2026-04-09 — Deflect Attacks reaction option is offered for any damage type when defender is L13+ (the L3 gating only enforces B/P/S below L13). |
| **Disciplined Survivor** (all save profs + reroll failed save with FP) | 14 | 5367-5369 | PARTIAL 2026-04-09 — all save proficiencies set in `character_data.nvgt` Monk L14+ block. Save reroll prompt deferred (needs failed-save prompt chain integration). |
| **Perfect Focus** (regain to 4 FP on initiative if 3 or fewer) | 15 | 5370-5371 | DEFERRED — needs initiative-time hook similar to Uncanny Metabolism. |
| **Subclass feature** | 17 | 5292 | ✓ Done. |
| **Superior Defense** (3 FP, 1 minute Resistance to all but Force) | 18 | 5372-5373 | ✓ Done 2026-04-09 — new `superior_defense_active` + `superior_defense_rounds_remaining` fields, bonus action handler, damage halving in `apply_damage` for any non-Force damage type, round-tick in `start_turn`, ends if Incapacitated. |
| **Epic Boon** | 19 | 5374-5375 | ✓ Done — Epic Boon feat catalog. |
| **Body and Mind** (+4 DEX/WIS, max 25) | 20 | 5376-5377 | ✓ Done 2026-04-09 — `body_and_mind_applied` one-time guard in Monk init block. Boost capped at 25. |

**Pending follow-up Monk batches:**
- Deflect Attacks redirect target picker (Focus Point spend, 5ft melee / 60ft ranged, DEX save, 2× MA die + DEX mod same damage type)
- Disciplined Survivor failed-save reroll prompt chain
- Perfect Focus initiative-time floor
- Heightened Focus Flurry-of-Blows third strike (needs `start_flurry_strike` count parameter)
- Heightened Focus Step of the Wind ally-carry (needs targeting prompt)
- Empowered Strikes Force/normal damage type prompt

- **Paladin:** Lay on Hands (pool size), Divine Smite (slot-based in 2024), Aura of Courage, Cleansing Touch
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

# Source Accuracy TODOs

**Mandate:** All spells, class features, subclasses, feats, and items must function EXACTLY as stated in the source material from `C:\Users\16239\Downloads\Sources_clean\Source Books and rules\`. No invented rules. No simplifications of core mechanics.

---

## 1. Skill Check System (blocks several features)

Combat currently has no skill check resolution. Some features need this to function correctly:

- **Silver Tongue (College of Eloquence Bard L3)** — "treat a d20 roll of 9 or lower as a 10" on Persuasion and Deception checks
- **Blessing of the Trickster (Trickery Domain Cleric)** — "Advantage on Dexterity (Stealth) checks" (currently approximated with +5 hide_dc)
- **Inquisitor's Eye (Oath of Zeal Paladin)** — "advantage on Intelligence (Investigation), Wisdom (Insight), and Wisdom (Perception)"
- **Keeper of History (Dirge Singer Bard)** — Expertise in History and Performance
- **Benevolent Presence (Couatl Herald Fighter)** — expend Mercy Dice on Insight/Performance/Persuasion checks
- Many other subclass features that grant skill proficiency or advantage

**Required work:** Add a `roll_skill_check` handler to battle_manager, hook it into actions that need skill checks (social encounters, searches, stealth), and respect subclass/feat modifiers.

---

## 2. Mid-Spell Player Choice System

When a spell lets the player choose an option during resolution, the current code auto-picks. The rule the user gave is: **NEVER choose for the player when a spell has a choice.**

Required plumbing: a `pending_spell_choice` state on the battle_manager that pauses spell resolution, sends a choice prompt to the client, and waits for a response message. Pattern exists for `bardic_response`, `lucky_response`, `smite_response`, `reaction_response` — extend the same pattern for spell choices.

### Known spells that auto-choose and need proper prompts:

| Spell | Choice the player should make | Current auto-pick |
|-------|------------------------------|-------------------|
| **Fire Shield** | Warm (cold resistance, reflects fire) OR Chill (fire resistance, reflects cold) | Hardcoded warm |
| **Adjust Density** (Graviturgy L2) | Halve OR double the target's density | Auto-halves allies, auto-doubles enemies |
| **Spirit Guardians** | Radiant (good/neutral) OR Necrotic (evil) damage type | Hardcoded radiant |
| **Spirit Totem** (Circle of the Shepherd) | Bear OR Hawk OR Unicorn spirit | Currently has 3 separate menu entries — this one IS working |
| **Starry Form** (Circle of the Stars) | Archer / Chalice / Dragon form | This one IS working via sub-menu |
| **Wild Shape / Elemental Wild Shape** | Which creature form | Partial |
| **Elemental Adept feat** | Damage type chosen at feat pickup | Should be prompted at character creation, not combat |
| **Channel Divinity Order's Demand** | Optional "drop held items" rider | Not implemented |
| **Wall of Stone / Wall of Fire** | Shape and orientation | Not implemented (walls not in combat grid)|
| **Polymorph** | Target beast form | Limited — uses a fixed stat block |
| **Scorching Ray** | Ray distribution across targets | Auto-distributes |
| **Magic Missile** | Dart distribution | Auto-distributes evenly |
| **Eldritch Blast** | Beam distribution | Auto-distributes |
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

Roughly 80 feats have at least a flag in the code. The ones with correct 2024 mechanics (verified against source):
- Mage Slayer (Concentration Breaker implemented, Guarded Mind TODO)
- Shield Master (automatic rider implemented, Interpose Shield reaction TODO)
- Polearm Master (bonus action implemented, Reactive Strike TODO)

Every other feat needs a 2024 PHB source pass to verify it matches the current text.

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

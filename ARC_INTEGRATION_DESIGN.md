# ARC Integration Design Document

## Executive Summary

The Adaptive Resolution Core (ARC) is the central resolution engine for the Persistent Narrative Engine, handling all uncertain outcomes in the narrative. This document outlines the architecture, integration strategy, database requirements, and long-term roadmap for ARC within PNE.

**Key Principles:**
- **No core modification** to ARC resolution logic during integration
- **Decoupled systems** - each PNE subsystem interacts independently with ARC
- **Mode agnostic** - same resolution engine supports three narrative modes
- **Narrative first** - outcomes drive story, not mechanics

---

## 1. ARC Architecture Overview

### 1.1 Core Resolution Loop

ARC operates as a pure resolution engine, isolated from PNE systems:

```
┌─────────────────────────────────────────────────────┐
│  PLAYER/CHARACTER ACTION                            │
│  (e.g., "Pick the ancient lock")                    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  CONTEXT EXTRACTION (Optional)                      │
│  - Derive skill_bonus from character stats          │
│  - Derive attribute_bonus from modifiers            │
│  - Collect environmental factors                    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  ARC RESOLUTION                                     │
│  - Roll D20 (+ bonuses) → Success Level             │
│  - Roll D6 (no bonuses) → Consequence Level         │
│  - Generate Narrative Text                          │
│  Returns: ARCResult                                 │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  SYSTEM DISPATCH (Adapter Pattern)                  │
│  - Record Event                                     │
│  - Generate Memory Candidates                       │
│  - Trigger Quest Hooks                              │
│  - Update Relationships                             │
│  - Mark Story Flags                                 │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  NARRATIVE OUTPUT                                   │
│  - Display result (mode-dependent)                  │
│  - Advance story                                    │
│  - Update context for next action                   │
└─────────────────────────────────────────────────────┘
```

### 1.2 Components

#### **arc_models.py** (Phase 1)
- `SuccessLevel` enum (6 outcomes)
- `ConsequenceLevel` enum (6 outcomes)
- `ARCResult` dataclass with helper methods

#### **arc_engine.py** (Phase 1)
- Dice rolling mechanics
- Outcome interpretation
- Bonus application
- Narrative text generation

#### **arc_resolution.py** (Phase 1)
- Public API: `resolve_action()`
- Entry point for all resolution requests

#### **arc_adapter.py** (Phase 2)
- Event recording bridge
- Memory candidate generation
- Quest hook registry
- Mode-specific filtering

#### **arc_integration_layer.py** (Phase 3 - Future)
- Character stat integration
- Story flag application
- Relationship impact calculation
- Context enrichment

---

## 2. System Interaction Diagram

### 2.1 Complete Integration Map

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          PERSISTENT NARRATIVE ENGINE                       │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Character   │  │  Memory      │  │  Story       │  │  Quests      │  │
│  │  System      │  │  System      │  │  Flags       │  │              │  │
│  │              │  │              │  │              │  │              │  │
│  │ - stats      │  │ - memories   │  │ - flags      │  │ - goals      │  │
│  │ - skills     │  │ - candidates │  │ - timeline   │  │ - objectives │  │
│  │ - equipment  │  │ - categories │  │ - checks     │  │ - progress   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │                 │         │
│         │                 │                 │                 │         │
│         └─────────────────┼─────────────────┼─────────────────┘         │
│                           │                 │                           │
│                  ┌────────▼─────────┐       │                           │
│                  │  Context Builder │       │                           │
│                  │  - Derives bonus │       │                           │
│                  │  - Injects facts │       │                           │
│                  └────────┬─────────┘       │                           │
│                           │                 │                           │
│         ┌─────────────────▼─────────────────▼───────────┐               │
│         │                                               │               │
│         │   ▲                                           │               │
│         │   │  [Player Action]                        │               │
│         │   │                                          │               │
│         │   └──────────────────────────────────────►   │               │
│         │                                              │               │
│         │          ARC (Phase 1 + 2)                  │               │
│         │   ┌──────────────────────────────────────┐  │               │
│         │   │ D20 + D6 Resolution                 │  │               │
│         │   │ Success/Failure/Critical             │  │               │
│         │   │ Advantage/Threat                     │  │               │
│         │   │ Returns: ARCResult                   │  │               │
│         │   └──────────────────────────────────────┘  │               │
│         │                  │                          │               │
│         │       ┌──────────┴──────────┐               │               │
│         │       │                     │               │               │
│         │       ▼                     ▼               │               │
│         │  ┌─────────────┐   ┌──────────────┐        │               │
│         │  │   Events    │   │   Relationships   │   │               │
│         │  │   Adapter   │   │   Adapter     │   │               │
│         │  │             │   │               │   │               │
│         │  │ - Records   │   │ - Updates     │   │               │
│         │  │   outcomes  │   │   bond score  │   │               │
│         │  │ - Tracks    │   │ - Checks      │   │               │
│         │  │   history   │   │   thresholds  │   │               │
│         │  └─────────────┘   └──────────────┘   │               │
│         │       │                     │           │               │
│         │       └─────────┬───────────┘           │               │
│         │                 │                       │               │
│         │       ┌─────────▼────────────────────┐  │               │
│         │       │  Memory Adapter              │  │               │
│         │       │                              │  │               │
│         │       │ - Generates memory           │  │               │
│         │       │   candidates                 │  │               │
│         │       │ - Prioritizes by importance  │  │               │
│         │       │ - Stores arc_resolution tag  │  │               │
│         │       └─────────┬────────────────────┘  │               │
│         │                 │                       │               │
│         │       ┌─────────▼────────────────────┐  │               │
│         │       │  Quest Adapter               │  │               │
│         │       │                              │  │               │
│         │       │ - Triggers callbacks         │  │               │
│         │       │ - success/failure            │  │               │
│         │       │ - advantage/threat           │  │               │
│         │       │ - Logs to events             │  │               │
│         │       └─────────┬────────────────────┘  │               │
│         │                 │                       │               │
│         │       ┌─────────▼────────────────────┐  │               │
│         │       │  Story Flag Adapter          │  │               │
│         │       │  (Phase 3 Future)            │  │               │
│         │       │                              │  │               │
│         │       │ - Sets flags by outcome      │  │               │
│         │       │ - Checks conditionals        │  │               │
│         │       │ - Branches narrative         │  │               │
│         │       └─────────┬────────────────────┘  │               │
│         │                 │                       │               │
│         └─────────────────┼───────────────────────┘               │
│                           │                                       │
│                           ▼                                       │
│                  [Narrative Output / Next State]                  │
│                                                                   │
└────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow Patterns

#### Pattern A: Success with Advantage
```
Action: Attempt to pick lock
D20: 17 (Success) + D6: 5 (Advantage)
    ↓
Event: arc_resolution, importance=8
Memory: Achievement - "Successfully picked the ancient lock"
Quest: Progress - Advance "Heist" objective +1
Relationship: +2 bond with quest-giver
Story Flag: SET heist_lock_opened = true
Context: Add "has_ancient_key" to context
    ↓
Narrative: "You deftly manipulate the pins... the lock gives way.
           The ancient key is within reach!"
```

#### Pattern B: Partial Success with Cost
```
Action: Attempt to negotiate with merchant
D20: 13 (Partial Success) + D6: 3 (Cost)
    ↓
Event: arc_resolution, importance=6
Memory: Discovery - "Negotiated but at a cost"
Quest: Partial - Reduce gold by negotiation_cost
Relationship: +1 bond (partial success) -1 trust (cost)
Story Flag: SET merchant_wary = true
Context: Add "merchant_suspicious" as ongoing complication
    ↓
Narrative: "Your persuasion nearly works... but the merchant
           demands a premium price for your boldness."
```

#### Pattern C: Critical Failure with Threat
```
Action: Attempt to charm the guard
D20: 1 (Critical Failure) + D6: 1 (Severe Threat)
    ↓
Event: arc_resolution, importance=10, critical=true
Memory: Challenge - "Spectacularly failed to charm the guard"
Quest: Failure - Trigger "Guard Alert" sequence
Relationship: -3 bond (catastrophic failure), -5 trust
Story Flag: SET guard_alerted = true, SET area_lockdown = true
Context: Add "guards_searching", "time_pressure_2_hours" to context
    ↓
Narrative: "Your attempt at charm backfires spectacularly.
           The guard's hand moves to their weapon as alarms sound..."
```

---

## 3. Database Requirements

### 3.1 New Tables Required

#### **arc_resolutions** (Primary audit trail)
```sql
CREATE TABLE arc_resolutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Action Context
    character_name TEXT,
    action_description TEXT NOT NULL,
    action_type TEXT,  -- 'skill', 'social', 'combat', 'exploration'
    
    -- Dice Rolls
    d20_roll INTEGER NOT NULL CHECK(d20_roll BETWEEN 1 AND 20),
    d6_roll INTEGER NOT NULL CHECK(d6_roll BETWEEN 1 AND 6),
    
    -- Bonuses Applied
    skill_bonus INTEGER DEFAULT 0,
    attribute_bonus INTEGER DEFAULT 0,
    environmental_bonus INTEGER DEFAULT 0,
    total_bonus INTEGER DEFAULT 0,
    
    -- Results
    success_level TEXT NOT NULL,  -- 'critical_failure', 'failure', etc.
    consequence_level TEXT NOT NULL,  -- 'severe_threat', 'threat', etc.
    
    -- Narrative
    narrative_text TEXT,
    
    -- Metadata
    mode TEXT DEFAULT 'rpg',  -- 'companion', 'fanfiction', 'rpg'
    importance INTEGER CHECK(importance BETWEEN 1 AND 10),
    is_critical BOOLEAN DEFAULT FALSE,
    
    -- Foreign Keys
    quest_id INTEGER,
    
    FOREIGN KEY (quest_id) REFERENCES character_quests(id)
);

CREATE INDEX idx_arc_character ON arc_resolutions(character_name, day);
CREATE INDEX idx_arc_mode ON arc_resolutions(mode);
CREATE INDEX idx_arc_critical ON arc_resolutions(is_critical);
```

#### **arc_consequences** (Outcome tracking)
```sql
CREATE TABLE arc_consequences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    arc_resolution_id INTEGER NOT NULL,
    
    -- Consequence Type
    consequence_type TEXT NOT NULL,  -- 'quest_progress', 'flag_set', 'memory_generated', etc.
    target_entity TEXT,  -- quest_id, flag_name, memory_id, etc.
    
    -- Change Details
    old_value TEXT,
    new_value TEXT,
    change_description TEXT,
    
    -- Processing Status
    applied BOOLEAN DEFAULT FALSE,
    applied_at DATETIME,
    
    FOREIGN KEY (arc_resolution_id) REFERENCES arc_resolutions(id)
);

CREATE INDEX idx_consequences_arc ON arc_consequences(arc_resolution_id);
```

### 3.2 New Columns Required in Existing Tables

#### **events** (Existing - add columns)
```sql
ALTER TABLE events ADD COLUMN arc_resolution_id INTEGER;
ALTER TABLE events ADD COLUMN d20_roll INTEGER;
ALTER TABLE events ADD COLUMN d6_roll INTEGER;
ALTER TABLE events ADD COLUMN success_level TEXT;
ALTER TABLE events ADD COLUMN consequence_level TEXT;

FOREIGN KEY (arc_resolution_id) REFERENCES arc_resolutions(id)
```

#### **memory_candidates** (Existing - add column)
```sql
ALTER TABLE memory_candidates ADD COLUMN arc_resolution_id INTEGER;
ALTER TABLE memory_candidates ADD COLUMN arc_outcome_importance INTEGER;

-- Helps distinguish memories from ARC outcomes vs other sources
```

#### **character_quests** (Existing - add columns)
```sql
ALTER TABLE character_quests ADD COLUMN last_arc_resolution_id INTEGER;
ALTER TABLE character_quests ADD COLUMN total_resolutions INTEGER DEFAULT 0;
ALTER TABLE character_quests ADD COLUMN critical_successes INTEGER DEFAULT 0;
ALTER TABLE character_quests ADD COLUMN critical_failures INTEGER DEFAULT 0;

-- Track quest progression through ARC outcomes
```

#### **story_flags** (Existing - add columns)
```sql
ALTER TABLE story_flags ADD COLUMN arc_triggered BOOLEAN DEFAULT FALSE;
ALTER TABLE story_flags ADD COLUMN arc_resolution_id INTEGER;
ALTER TABLE story_flags ADD COLUMN trigger_condition TEXT;

-- Track which ARC outcomes set which flags
```

#### **relationships** (Existing - add columns)
```sql
ALTER TABLE relationships ADD COLUMN last_arc_resolution_id INTEGER;
ALTER TABLE relationships ADD COLUMN total_arc_interactions INTEGER DEFAULT 0;
ALTER TABLE relationships ADD COLUMN last_arc_outcome TEXT;

-- Track relationship history with ARC outcomes
```

### 3.3 Optional Enhancement: Mode-Specific Tracking

```sql
CREATE TABLE arc_mode_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day INTEGER NOT NULL,
    mode TEXT NOT NULL,  -- 'companion', 'fanfiction', 'rpg'
    
    -- Statistics
    total_resolutions INTEGER DEFAULT 0,
    critical_successes INTEGER DEFAULT 0,
    critical_failures INTEGER DEFAULT 0,
    average_importance REAL,
    
    -- Mode-Specific Metrics
    visible_rolls INTEGER DEFAULT 0,  -- companion shows fewer
    narrative_branches_triggered INTEGER DEFAULT 0,
    
    UNIQUE(day, mode)
);
```

### 3.4 Migration Strategy

**Phase 1:** Core ARC tables (`arc_resolutions`)
- Minimal impact, standalone tracking
- Can be added at any time

**Phase 2:** Integration columns
- Add to existing tables gradually
- Backward compatible (NULLable columns)
- Can populate retroactively

**Phase 3:** Mode-specific tables
- Only when implementing mode-specific features
- Not required for basic functionality

---

## 4. Narrative Flow Design

### 4.1 Complete Resolution Sequence

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: ACTION DECLARATION                                      │
│ Player/NPC: "I attempt to pick the ancient lock"                │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ STEP 2: CONTEXT EXTRACTION                                      │
│ - Query character sheet: "Rue's Lockpicking skill = 5"           │
│ - Query character bonuses: "Night elves get +1 perception"      │
│ - Query location modifiers: "Ancient locks grant -1 difficulty" │
│ - Query equipment: "Has master's lockpick set +2"               │
│ Result: skill_bonus=6, attribute_bonus=2, special_bonus=1      │
│ Total bonus = 9                                                  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ STEP 3: ARC RESOLUTION                                          │
│ Call: resolve_action(                                            │
│   "Pick the ancient lock",                                       │
│   skill_bonus=6,                                                │
│   attribute_bonus=3                                             │
│ )                                                               │
│                                                                │
│ Roll D20: 14 (result) + 9 (bonuses) = 23 → Clamped to 20     │
│           D20: 17 (rolled) (with bonuses applied)              │
│           → SUCCESS (16-19 range)                             │
│                                                                │
│ Roll D6: 5                                                      │
│         → ADVANTAGE                                            │
│                                                                │
│ Generate narrative: "Your years of experience show as you      │
│ deftly work the mechanism. The lock yields with a satisfying   │
│ click, and more quickly than expected."                        │
│                                                                │
│ Return: ARCResult                                              │
│   - d20_roll = 17                                              │
│   - d6_roll = 5                                                │
│   - success_level = SUCCESS                                    │
│   - consequence_level = ADVANTAGE                              │
│   - final_text = [narrative]                                   │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ STEP 4: EVENT RECORDING                                         │
│ create_arc_event(                                               │
│   cursor,                                                       │
│   action="Pick the ancient lock",                              │
│   result=ARCResult,                                            │
│   character_name="Rue",                                        │
│   day=5                                                        │
│ )                                                              │
│                                                                │
│ Calculates importance: 8 (success + advantage)                 │
│ Stores in arc_resolutions and events tables                    │
│ Creates entry with all metadata                                │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ STEP 5: MEMORY CANDIDATE GENERATION                             │
│ arc_memory_candidates(result, action, "Rue")                   │
│                                                                │
│ Since result.is_success() AND result.has_advantage():          │
│ Generate: {                                                    │
│   "text": "Successfully picked the ancient lock with ease",    │
│   "importance": 8,                                            │
│   "category": "Achievement",                                  │
│   "source": "arc_outcome"                                     │
│ }                                                              │
│                                                                │
│ Pass to memory_extraction system for:                          │
│ - Deduplication check                                         │
│ - Canonicalization                                            │
│ - Auto-canonization evaluation                                │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ STEP 6: QUEST IMPACT CALCULATION                                │
│ global_quest_registry.execute_hooks(                            │
│   result,                                                       │
│   context={'quest_id': 42, 'character': 'Rue'},               │
│   mode='rpg'                                                   │
│ )                                                              │
│                                                                │
│ Registered callbacks for quest_42 execute:                     │
│ - on_arc_success: "Progress 'Open the Vault' objective +1"    │
│ - on_arc_advantage: "Gain 'Swiftness' token for this session" │
│                                                                │
│ Quest system independently decides:                            │
│ - Check if objective complete (yes → trigger quest_complete)   │
│ - Award reputation with quest-giver (+2)                      │
│ - Update quest progress display                               │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ STEP 7: RELATIONSHIP IMPACT                                     │
│ arc_relationship_adapter (Phase 3 future):                      │
│                                                                │
│ - Quest-giver sees SUCCESS + ADVANTAGE                         │
│ - Updates bond score: +3 (success) +2 (advantage)              │
│ - Checks threshold: bond >= 50? Set "trusted_advisor" flag    │
│ - Records arc_resolution_id for history                        │
│ - Adds to relationship memories                               │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ STEP 8: STORY FLAG UPDATES                                      │
│ arc_story_flag_adapter (Phase 3 future):                        │
│                                                                │
│ Check arc_resolutions for outcome patterns:                    │
│ IF (quest_42 → SUCCESS AND location='vault' AND day >= 5):    │
│    SET flag 'vault_accessible' = true                         │
│    TRIGGER 'vault_themes' context injection                   │
│                                                                │
│ Check conditional flags:                                       │
│ IF (flag 'security_alert' = true AND recent_failure):         │
│    SET flag 'guards_increased' = true                         │
│    MODIFY context → "guards_doubled"                          │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ STEP 9: CONTEXT INJECTION FOR NEXT TURN                         │
│ context_builder.inject_arc_context(                             │
│   last_result=ARCResult,                                       │
│   new_facts=['has_ancient_key', 'vault_unlocked'],             │
│   removing_facts=['unknown_lock_combination']                  │
│ )                                                              │
│                                                                │
│ Updates context for next LLM prompt:                           │
│ - Adds facts from successful outcome                           │
│ - Removes invalidated assumptions                              │
│ - Injects relationship state                                   │
│ - Adds story flags as narrative anchors                        │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ STEP 10: NARRATIVE OUTPUT (Mode-Dependent)                      │
│                                                                │
│ COMPANION MODE:                                                 │
│   "The lock clicks open. You have the ancient key!"            │
│   [No dice shown]                                              │
│                                                                │
│ FANFICTION MODE:                                                │
│   "With careful precision, you unlock the mechanism.           │
│   The ancient key is finally within reach."                    │
│   [Subtle narrative weaving of ARC outcome]                    │
│                                                                │
│ RPG MODE:                                                       │
│   "D20: 17 + 9 bonus = SUCCESS | D6: 5 = ADVANTAGE             │
│   With your expertise and a touch of luck, the lock            │
│   yields quickly. You gain the ancient key!"                   │
│   [Full mechanical detail + narrative]                         │
│                                                                │
│ ALL MODES:                                                     │
│   [Story continues based on new context state]                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Parallel Processing Considerations

These steps execute sequentially in terms of narrative flow, but can be processed in parallel for performance:

- **Immediate:** Steps 1-3 (must complete before ARC resolution)
- **Parallel (after Step 3):**
  - Step 4 (Event recording)
  - Step 5 (Memory candidates)
  - Step 6 (Quest hooks)
  - Step 7 (Relationships)
  - Step 8 (Story flags)
- **Sequential (after parallel):** Step 9 (Context injection depends on results)
- **Last:** Step 10 (Output generation)

---

## 5. RPG Dial Design

### 5.1 Mode Overview

The "RPG Dial" determines how much mechanical detail is visible and how much influence ARC has on narrative outcomes.

```
┌────────────────────────────────────────────────────────────────┐
│  COMPANION MODE          FANFICTION MODE         RPG MODE      │
│  (Narrative First)       (Story Balanced)        (Mechanics)    │
└────────────────────────────────────────────────────────────────┘

Mechanical Visibility
└─ 10%                    └─ 40%                   └─ 100%

Dice Shown
└─ NO                     └─ SOMETIMES             └─ YES

Bonus Visibility
└─ NO                     └─ CONTEXT CLUES         └─ EXPLICIT

Failure Tolerance
└─ LOW (reroll/reframe)   └─ MEDIUM (consequences) └─ HIGH (accept)

Story Branching
└─ TIGHT (main path)      └─ FLEXIBLE (variations) └─ OPEN (full choices)

Character Stats Impact
└─ FLAVOR                 └─ MODERATE              └─ HIGH

Quest Progression
└─ GUIDED                 └─ ORGANIC               └─ EMERGENT
```

### 5.2 Companion Mode (Narrative First)

**Philosophy:** Player experience should never feel mechanical. Hide the dice, show the story.

**Dice Visibility:**
- D20 and D6 rolls happen, but results are translated
- Example: "Your expertise shows" instead of "D20: 19 = Success"
- Critical rolls might be subtly indicated through prose

**Bonus Application:**
- Skill bonuses are expressed as narrative: "With your training..."
- Environmental bonuses: "The old lock is worn, making it easier..."
- No explicit numbers

**Failure Handling:**
- Failed actions are reframed as complications: "You slip... but catch yourself"
- Critical failures become dramatic moments: "The guard turns just as you reach for the lock"
- Rarely ends quest objectives (branching instead)

**Memory Candidate Storage:**
- Only significant outcomes create memories (importance ≥ 7)
- Memories are narrative-focused: "Saved the merchant's life"
- No mechanical tags

**Quest Impact:**
- Quests progress through narrative choices, not just rolls
- Failed rolls create complications, not dead ends
- Players never feel "blocked" by bad luck

**Example Resolution:**
```
Action: "I try to convince the merchant to help us"
ARC Roll: D20=5 (Failure) + D6=3 (Cost)

Companion Mode Output:
  "The merchant seems skeptical of your proposal. 
   To truly convince him, you might need to sweeten the deal 
   or find another approach."

[No dice shown. Player offered story alternatives.]

RPG Mode Output:
  "D20: 5 + 2 bonus = 7 (FAILURE) | D6: 3 (COST)
   The merchant's expression hardens. He'll require payment 
   upfront if you want his cooperation—5000 gold."
```

**Mode Flag:** `narrative_mode = 'companion'`

### 5.3 Fanfiction Mode (Story Balanced)

**Philosophy:** Outcomes matter, but story flow is preserved. ARC results influence narrative direction without dominating it.

**Dice Visibility:**
- Rolls are hidden during resolution
- Results are shown through narrative consequences
- Example: "Despite your best efforts" (implies failure), "Unexpectedly well" (implies advantage)

**Bonus Application:**
- Bonuses provide narrative context clues
- Character knowledge is evident: "Drawing on your experience..."
- Environment is described: "The ancient mechanism resists, as if protecting a secret"

**Failure Handling:**
- Failures create complications that branch the story
- Critical failures become plot twists
- Story continues, but with new challenges

**Memory Candidate Storage:**
- Significant moments create memories (importance ≥ 5)
- Memories emphasize story impact: "The merchant's reaction hardened your resolve"
- Track emotional consequences

**Quest Impact:**
- Quest objectives remain achievable through multiple paths
- Failed rolls suggest alternative approaches
- Quest-giver reactions evolve based on player performance

**Example Resolution:**
```
Action: "I try to convince the merchant to help us"
ARC Roll: D20=5 (Failure) + D6=3 (Cost)

Fanfiction Mode Output:
  "Despite your persuasive words, something in your tone 
   makes the merchant wary. You sense his doubt. He suggests 
   a demonstration of good faith—a significant payment—before 
   he'd consider helping."

[Outcome visible through narrative, not dice.
 Story continues with new complications.]

Impact: 
  - Quest flag: 'merchant_demanding' = true
  - Memory: "The merchant demanded proof of commitment"
  - Options: Pay, find alternative supplier, or persuade differently
```

**Mode Flag:** `narrative_mode = 'fanfiction'`

### 5.4 RPG Mode (Full Mechanics)

**Philosophy:** Mechanics and narrative are equal. Outcomes are earned or suffered. Full transparency.

**Dice Visibility:**
- All rolls shown: "D20: 14 + 3 bonus = 17 = SUCCESS"
- D6 result: "D6: 4 = NEUTRAL"
- Critical rolls celebrated: "D20: 20 = CRITICAL SUCCESS!"

**Bonus Application:**
- Explicit bonus breakdown: "Lockpicking skill +4 + Night Elf bonus +1 + Masterwork Tools +2"
- Character optimization visible and rewarded
- Mechanical failures hurt more because players understand why

**Failure Handling:**
- Failures have lasting consequences
- Critical failures can permanently lock out objectives
- Players learn from mechanical failures

**Memory Candidate Storage:**
- All significant outcomes create memories (importance ≥ 5)
- Memories include mechanical details: "Successfully picked ancient locks (3 times)"
- Track achievement statistics

**Quest Impact:**
- Quests fail if objectives aren't met (no reframe)
- Multiple attempts with escalating difficulty
- Reputation with NPCs based on mechanical performance

**Example Resolution:**
```
Action: "I try to convince the merchant to help us"
ARC Roll: D20=5 (Failure) + D6=3 (Cost)

RPG Mode Output:
  "SKILL CHECK FAILED
   D20: 5 + Charisma Modifier (+2) = 7 vs DC 10
   D6: 3 = COST
   
   The merchant sees through your flattery. His eyes narrow.
   'That tactic will cost you,' he says coldly. 
   '500 gold for my trouble, or we're done here.'"

Impact:
  - Quest Progress: "Convince Merchant" → FAILED
  - Reputation: Merchant disposition → UNFRIENDLY
  - Cost: -500 gold
  - Options: 
    * Pay (continue with disadvantage later)
    * Refuse (merchant becomes hostile)
    * Retry in different session (DC increases to 12)
```

**Mode Flag:** `narrative_mode = 'rpg'`

### 5.5 Mode Switching Architecture

```
┌─────────────────────────────────────────────────────────┐
│  DETERMINE MODE FOR THIS ACTION                         │
│  (Priority order)                                       │
└─────────────────────────────────────────────────────────┘
         │
         ├─ Action-specific override? → Use it
         │  (some actions forced to RPG for balance)
         │
         ├─ Quest-specific mode? → Use it
         │  (critical quest moments use RPG mode)
         │
         ├─ Character preference? → Use it
         │  (player sets default mode in settings)
         │
         └─ World state? → Use it
            (story_flags might force mode change)


EXAMPLE: Time pressure forces RPG mode
┌─────────────────────────────────────────────────────────┐
│ story_flags['time_pressure'] = true                     │
│ → Resolution mode = 'rpg' (forced)                       │
│ → All rolls shown                                        │
│ → Failures have immediate consequences                  │
│ → Story tension increases mechanically                  │
└─────────────────────────────────────────────────────────┘
```

### 5.6 Mode-Specific Probability Tuning

The core ARC engine doesn't change between modes, but narrative treatment does:

```
SUCCESS: D20 16-19
FAILURE: D20 2-5
PARTIAL: D20 6-15
CRITICAL: D20 1, 20

Same probabilities for all modes:
- ~9% Critical Success (20)
- ~40% Success/Partial Success
- ~40% Partial Failure
- ~20% Failure
- ~5% Critical Failure (1)

But treatment differs:

COMPANION MODE:
  - Critical Failures reframed as complications
  - Partial Failures become "interesting challenges"
  - Story continues regardless

FANFICTION MODE:
  - Failures create plot twists
  - Bonuses provide narrative flourish
  - Consequences are story-relevant

RPG MODE:
  - Failures have mechanical cost
  - Bonuses are explicitly calculated
  - Critical failures can end goals
```

---

## 6. Long-Term Roadmap

### Phase 1: Core Resolution Engine ✅ **COMPLETE**

**Deliverables:**
- Standalone D20/D6 resolution system
- SuccessLevel and ConsequenceLevel enums
- ARCResult dataclass with helper methods
- Full test coverage
- Zero dependencies on existing PNE systems

**Status:** Validated, all tests passing

### Phase 2: System Integration ✅ **IN PROGRESS/COMPLETE**

**Deliverables:**
- Event recording adapter
- Memory candidate generation
- Quest hook registry
- Relationship adapter skeleton
- Story flag adapter skeleton
- Mode-aware output formatting
- Comprehensive integration tests

**Status:** Core adapters complete, integration tests passing

**Database:** No migrations needed (all backward compatible)

**Integration Points:**
- Chat system can call `resolve_action()`
- Quest system can register callbacks
- Memory system can evaluate candidates
- Events table can track outcomes

### Phase 3: Character & World State Integration

**Deliverables:**
- Character stat derivation
- Environmental modifier calculation
- Relationship impact system
- Story flag conditional evaluation
- Consequence auto-application

**Database Changes:**
- Add `arc_resolutions` table (full audit trail)
- Add columns to existing tables (relationships, quests, flags)
- Add `arc_consequences` table (outcome tracking)

**Scope:**
- Extract skill_bonus from character.skills
- Extract attribute_bonus from character.attributes
- Calculate environmental_bonus from location/story state
- Apply relationship changes automatically
- Set story flags based on outcomes
- Queue consequences for processing

**Success Criteria:**
- Action → ARC → Automatic world state updates
- Character stats visibly affect roll outcomes (RPG mode)
- Story flags branch narrative correctly
- All updates logged in arc_resolutions table

### Phase 4: Combat & Complex Encounters

**Deliverables:**
- Combat round resolution
- Multi-actor encounter handling
- Initiative system integration
- Cumulative effect tracking
- Opposed rolls (attacker vs defender)

**Scope:**
- Extend ARC for combat rolls
- Track HP/condition changes
- Handle advantage/disadvantage from conditions
- Record combat history in events
- Update character_initiatives based on performance

**New Components:**
- Combat turn sequencing
- Damage calculation from ARC results
- Status effect application
- Combat outcome narratives

**Success Criteria:**
- Full combat encounters resolvable via ARC
- Combat results properly cascade (armor + damage = HP)
- Initiative system respects ARC outcomes
- Combat is engaging in all three modes

### Phase 5: Advanced Narrative Features

**Deliverables:**
- Consequence chains (one outcome triggers next ARC roll)
- Branching narrative paths based on ARC history
- Dynamic difficulty adjustment
- Cumulative advantage/disadvantage tracking
- Emotional consequence system

**Scope:**
- Critical successes grant bonuses for next related action
- Repeated failures increase difficulty
- Relationship outcomes create narrative forks
- Environmental feedback loops

**New Components:**
- Consequence queue system
- Dynamic DC calculation
- Narrative branch selection
- Emotional state tracking

### Phase 6: AI/LLM Integration

**Deliverables:**
- ARC outcomes directly inform LLM prompts
- Outcome-based context injection
- NPC behavior modified by ARC history
- Dynamic narrative generation from rolls

**Scope:**
- Pass ARCResult to prompt builder
- Update context with outcome consequences
- Include relevant memory candidates in NPC context
- Generate situation-specific narrative

**New Components:**
- Prompt template modifications
- Context injection system
- NPC state updates from outcomes

---

## 7. Integration Considerations

### 7.1 Backward Compatibility

**Current State (Pre-Integration):**
- PNE operates without ARC
- Actions have immediate narrative outcomes
- No dice resolution layer

**Integration Strategy:**
- ARC runs in parallel, not replacement
- Existing systems continue unchanged
- New `arc_resolutions` table is additive
- All new columns are NULLable

**Migration Path:**
- Phase 1-2: ARC optional (parallel results)
- Phase 2-3: Gradual adoption (some actions use ARC)
- Phase 3+: Full integration (all uncertain outcomes via ARC)

### 7.2 Performance Considerations

**Current Bottlenecks:**
- LLM calls for action generation (most expensive)
- Database queries for context gathering
- Memory search operations

**ARC Overhead:**
- Resolution: ~1ms (dice + lookup)
- Adapter calls: ~10-50ms (database writes)
- Hook execution: ~5-20ms (callback overhead)

**Total:** ~50-100ms per action (negligible vs LLM)

**Optimization Opportunities:**
- Cache character stats (update only on level-up)
- Batch arc_consequences writes
- Async adapter calls
- Parallel consequence processing

### 7.3 Testing Strategy

**Unit Tests:**
- ARC engine tests (dice, interpretation)
- Adapter tests (event creation, hook execution)
- Mode-specific output tests

**Integration Tests:**
- End-to-end resolution with all adapters
- Database transaction tests
- Relationship impact calculations
- Flag conditional evaluation

**System Tests:**
- Full character journey through ARC
- Multi-NPC interactions
- Complex quest progressions
- Mode switching scenarios

**Load Tests:**
- 1000s of ARC resolutions per day
- Consequence queue processing
- Relationship recalculation
- Flag evaluation at scale

### 7.4 Error Handling

**Resolution Failures:**
- Invalid dice values → reroll
- Bonus overflow → clamp to max
- Missing character data → use defaults

**Adapter Failures:**
- Database write fails → log, retry
- Hook callback crashes → isolate, log, continue
- Missing context data → skip gracefully

**Degradation Modes:**
- If adapters fail → ARC still resolves (core logic)
- If events fail → outcome still applies
- If memory fails → no candidates generated
- If hooks fail → quests still progress

### 7.5 Extensibility

**Future Addition Points:**
- New adapter types (combat, social, exploration)
- Custom consequence processors
- Mode-specific rules engines
- Advanced narrative generators

**Plugin Architecture:**
```python
class ARCAdapterPlugin:
    def on_resolution(result: ARCResult, context: Dict) -> List[str]
    def on_consequence(consequence: Consequence) -> bool
    def on_narrative_generation(result: ARCResult) -> str

# Example: Custom "Romance" adapter
class RomanceAdapter(ARCAdapterPlugin):
    def on_resolution(result, context):
        if result.has_advantage() and context.get('romance_target'):
            return bond_increase(2)
```

---

## 8. Success Metrics

### 8.1 Functional Metrics

- ✅ All ARC resolutions recorded in database
- ✅ 100% of adapter callbacks execute without error
- ✅ Mode-specific output correctly filtered
- ✅ Memory candidates generated for ≥90% of significant outcomes
- ✅ Quest hooks properly trigger on outcomes
- ✅ Relationship updates cascade correctly

### 8.2 User Experience Metrics

- **Companion Mode:** Players don't notice dice mechanics
- **Fanfiction Mode:** Story flows naturally with ARC consequences
- **RPG Mode:** Mechanics feel fair and transparent

### 8.3 Performance Metrics

- ARC resolution: <100ms including all adapters
- Event writing: <50ms for batch operations
- Context injection: <200ms for complex scenarios
- Memory candidates: <30ms generation

### 8.4 Quality Metrics

- 95%+ test coverage of adapters
- <1% adapter callback failure rate
- Zero data corruption in arc_resolutions
- Audit trail integrity verified

---

## 9. Open Questions & Future Design Topics

1. **How should consequence chains work?** (ARC roll triggers another ARC roll)
2. **Can NPCs have ARC stats?** (NPC skill_bonus derived from archetype)
3. **Should equipment modify D20 or just bonuses?** (Mechanical vs narrative)
4. **How to handle simultaneous character actions?** (Turn order, conflict resolution)
5. **Should critical outcomes grant rerolls?** (Once per session? Cost?)
6. **How to implement "advantage/disadvantage"?** (RAW: roll 2d20, take higher/lower)
7. **Should companions have shared stats?** (Party bonuses vs individual)
8. **How to tune difficulty across modes?** (DC scaling per mode?)

---

## 10. Appendix: Example Integration Scenarios

### Scenario A: Lock Picking in Companion Mode
```
Action: "I try to pick the lock"
ARC: D20=17 (Success) + D6=5 (Advantage)
Output: "The lock gives way under your careful touch."
Memory: Generated
Quest: +1 progress
Relationship: +1 (NPC watching admires skill)
Flags: vault_accessible = true
```

### Scenario B: Social Challenge in RPG Mode
```
Action: "I persuade the guard to let us pass"
Context: Charisma 14, +2 modifier
ARC: D20=8 + 2 = 10 vs DC 12 (Failure) + D6=2 (Minor Threat)
Output: "D20: 8 + 2 = 10 (FAILURE) | D6: 2 (THREAT)
         The guard's suspicion grows. His hand moves toward his weapon."
Memory: "Failed to convince the guard; guard became hostile"
Quest: Guard Alert triggered
Relationship: -2 (guard now hostile)
Flags: guard_alert = true
```

### Scenario C: Environmental Challenge in Fanfiction Mode
```
Action: "I traverse the treacherous mountain pass"
ARC: D20=11 (Partial Success) + D6=4 (Neutral)
Output: "You navigate the narrow path with difficulty. 
         A few close calls, but you make it through."
Memory: "Crossed the mountain pass with difficulty"
Quest: +1 progress (path traversed)
Context: stamina_depleted = true (minor complication)
Flags: mountain_crossed = true
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-06-23  
**Status:** Design Phase (Pre-Implementation)

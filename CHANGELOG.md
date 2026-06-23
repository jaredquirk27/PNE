Changelog

v1.3 - Memory Extraction Fixes

Fixed

* Fixed sentence splitting issue where user messages and character replies were being merged into a single sentence.
* Fixed memory extraction failing on preference statements during live chat.
* Fixed duplicate detection being global across all characters.
* Updated duplicate detection to be character-specific.

Added

* Automatic canonization during live chat persistence.
* Improved memory relevance scoring.
* Preference extraction for:
    * Favorite movie
    * Favorite color
    * Favorite sports team
    * Favorite dinosaur

Validated

* Rue successfully stores:
    * Jared’s favorite movie is The Fifth Element.
    * Jared’s favorite NHL team is the Tampa Bay Lightning.
    * Jared’s favorite color is purple.
    * Jared’s favorite dinosaur is raptor.
* Duplicate protection prevents repeated insertion of identical memories.

Notes

* Investigate whether memory_already_canonized() should be character-specific instead of global.
* Continue testing relationship memories and initiative generation using extracted preferences.

## ARC Phase 1 Started

Date: 2026-06-23

Goal:
Build the first implementation of Adaptive Resolution Core (ARC).

Phase 1 Scope:
- D20 success resolution
- D6 threat/advantage resolution
- ARCResult dataclass
- resolve_action() API
- Test harness

Excluded:
- Combat
- UI
- Character stats
- Quest integration
- Memory integration

Status:
In Development

NEXT SESSION GOAL

Project: Persistent Narrative Engine (PNE)

Current State:

* Memory extraction system validated
* Character-specific duplicate detection fixed
* ARC Phase 1 complete
* ARC Integration Design Document complete

Next Objective:
Begin ARC Phase 2 Integration

Phase 2 Tasks:

1. Review ARC Phase 1 code
    * Verify architecture matches design document
    * Confirm no unwanted coupling
2. Create arc_adapter.py
    * Bridge ARC to PNE systems
    * No direct database modifications yet
3. Create ARC Event Pipeline
    * ARC result → Event
    * Event stored in events table
4. Create ARC Memory Candidate Pipeline
    * ARC result → Memory Candidate
    * No direct memory creation
5. Create RPG Dial Prototype
    * Companion Mode
    * Fanfiction Mode
    * RPG Mode
6. Test with Rue
    Example:
    “Convince Kavik to reveal information.”
    ARC resolves action.
    Event generated.
    Context updated.
    Narrative reflects outcome.

Success Condition:
ARC influences narrative without breaking existing memory, quest, or relationship systems.
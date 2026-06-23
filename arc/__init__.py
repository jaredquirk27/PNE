"""
ARC (Adaptive Resolution Core) Module

A standalone narrative resolution engine for the Persistent Narrative Engine.
Provides D20/D6-based outcome determination for uncertain actions.

Phase 1 Components:
- arc_models: Data structures (SuccessLevel, ConsequenceLevel, ARCResult)
- arc_engine: Core mechanics (dice rolling, interpretation)
- arc_resolution: Public API (resolve_action)
- arc_test: Test harness and usage examples

Usage:
    from arc_resolution import resolve_action
    
    result = resolve_action(
        "Attempt to pick the lock",
        skill_bonus=2,
        attribute_bonus=1,
    )
    print(result)

Future Integration:
- Chat/quest handlers for action outcomes
- Event system for recording consequences
- Character memory for narrative consistency
- Story state updates based on results
"""

__version__ = "1.0.0-phase1"
__author__ = "PNE Development Team"

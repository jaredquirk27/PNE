"""
ARC (Adaptive Resolution Core) Integration Test Harness

Tests Phase 2 integration points:
- Event recording to database
- Helper methods on ARCResult (is_success, is_failure, etc.)
- Memory candidate generation
- Quest hook registry and execution
- Mode-specific callbacks
- Event importance scoring

Run with:
    cd /Users/jared/Projects/PNE
    python -m arc.arc_integration_test
"""

import sqlite3
import tempfile
import os
from typing import Dict, List, Any

from arc.arc_resolution import resolve_action
from arc.arc_models import SuccessLevel, ConsequenceLevel, ARCResult
from arc.arc_adapter import (
    create_arc_event,
    arc_outcome_importance,
    arc_memory_candidates,
    QuestHookRegistry,
    NarrativeMode,
    global_quest_registry,
)


# ============================================================================
# Test Database Setup
# ============================================================================

def setup_test_database():
    """Create a temporary SQLite database with events table."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    cursor = sqlite3.connect(db_path).cursor()
    cursor.execute(
        """
        CREATE TABLE events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day INTEGER,
            event_type TEXT,
            character_name TEXT,
            description TEXT,
            importance INTEGER
        )
        """
    )
    cursor.connection.commit()
    return db_path, sqlite3.connect(db_path)


def teardown_test_database(db_path: str, connection):
    """Clean up test database."""
    connection.close()
    if os.path.exists(db_path):
        os.remove(db_path)


# ============================================================================
# Helper Methods Tests
# ============================================================================

def test_arcresult_helper_methods():
    """Test ARCResult helper methods: is_success, is_failure, has_advantage, etc."""
    print("\n" + "=" * 60)
    print("ARCRESULT HELPER METHODS TESTS")
    print("=" * 60)

    # Test is_success()
    result_success = resolve_action(
        "Test action",
        forced_d20=18,  # Success
        forced_d6=4,    # Neutral
    )
    assert result_success.is_success() == True, "is_success() should be True for SUCCESS"
    assert result_success.is_failure() == False, "is_failure() should be False for SUCCESS"
    print("✓ is_success() and is_failure() work for SUCCESS")

    # Test is_failure()
    result_failure = resolve_action(
        "Test action",
        forced_d20=4,   # Failure
        forced_d6=4,    # Neutral
    )
    assert result_failure.is_failure() == True, "is_failure() should be True for FAILURE"
    assert result_failure.is_success() == False, "is_success() should be False for FAILURE"
    print("✓ is_success() and is_failure() work for FAILURE")

    # Test has_advantage()
    result_advantage = resolve_action(
        "Test action",
        forced_d20=12,  # Partial Success
        forced_d6=5,    # Advantage
    )
    assert result_advantage.has_advantage() == True, "has_advantage() should be True for ADVANTAGE"
    assert result_advantage.has_threat() == False, "has_threat() should be False for ADVANTAGE"
    print("✓ has_advantage() and has_threat() work for ADVANTAGE")

    # Test has_threat()
    result_threat = resolve_action(
        "Test action",
        forced_d20=8,   # Partial Failure
        forced_d6=2,    # Minor Threat
    )
    assert result_threat.has_threat() == True, "has_threat() should be True for MINOR_THREAT"
    assert result_threat.has_advantage() == False, "has_advantage() should be False for MINOR_THREAT"
    print("✓ has_threat() works for MINOR_THREAT")

    # Test is_critical()
    result_critical_success = resolve_action(
        "Test action",
        forced_d20=20,  # Critical Success
        forced_d6=4,    # Neutral
    )
    assert result_critical_success.is_critical() == True, "is_critical() should be True for CRITICAL_SUCCESS"
    print("✓ is_critical() works for CRITICAL_SUCCESS")

    result_critical_failure = resolve_action(
        "Test action",
        forced_d20=1,   # Critical Failure
        forced_d6=4,    # Neutral
    )
    assert result_critical_failure.is_critical() == True, "is_critical() should be True for CRITICAL_FAILURE"
    print("✓ is_critical() works for CRITICAL_FAILURE")

    result_non_critical = resolve_action(
        "Test action",
        forced_d20=10,  # Partial Failure
        forced_d6=4,    # Neutral
    )
    assert result_non_critical.is_critical() == False, "is_critical() should be False for non-critical"
    print("✓ is_critical() returns False for non-critical results")

    print("\nAll helper methods tests passed! ✓")


# ============================================================================
# Event Recording Tests
# ============================================================================

def test_event_recording():
    """Test creating ARC events in database."""
    print("\n" + "=" * 60)
    print("EVENT RECORDING TESTS")
    print("=" * 60)

    db_path, connection = setup_test_database()
    cursor = connection.cursor()

    try:
        # Create an event from a successful action
        result = resolve_action(
            "Attempt to pick lock",
            forced_d20=18,
            forced_d6=5,
        )

        event_id = create_arc_event(
            cursor,
            "Attempt to pick lock",
            result,
            character_name="Rue",
            day=5,
        )

        assert event_id is not None, "Event ID should be returned"
        print(f"✓ Event created with ID: {event_id}")

        # Verify event in database
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        event = cursor.fetchone()

        assert event is not None, "Event should exist in database"
        assert event[1] == 5, "Day should be 5"
        assert event[2] == "arc_resolution", "Event type should be 'arc_resolution'"
        assert event[3] == "Rue", "Character name should be 'Rue'"
        assert "Success" in event[4], "Description should contain 'Success'"
        assert "Advantage" in event[4], "Description should contain 'Advantage'"
        print("✓ Event stored correctly in database")

        # Test critical failure event
        result_critical = resolve_action(
            "Negotiate with warlord",
            forced_d20=1,
            forced_d6=1,
        )

        event_id_2 = create_arc_event(
            cursor,
            "Negotiate with warlord",
            result_critical,
            character_name="Baras",
            day=3,
        )

        cursor.execute("SELECT importance FROM events WHERE id = ?", (event_id_2,))
        importance = cursor.fetchone()[0]

        assert importance > 8, "Critical failure should have high importance"
        print(f"✓ Critical failure event has high importance: {importance}")

        # Test partial success event
        result_partial = resolve_action(
            "Sneak past guards",
            forced_d20=12,
            forced_d6=4,
        )

        event_id_3 = create_arc_event(
            cursor,
            "Sneak past guards",
            result_partial,
            character_name="Jared",
            day=1,
        )

        cursor.execute("SELECT importance FROM events WHERE id = ?", (event_id_3,))
        importance_partial = cursor.fetchone()[0]

        assert importance_partial < importance, "Partial success should have lower importance than critical"
        print(f"✓ Partial success event has appropriate importance: {importance_partial}")

        connection.commit()
        print("\nAll event recording tests passed! ✓")

    finally:
        teardown_test_database(db_path, connection)


# ============================================================================
# Outcome Importance Tests
# ============================================================================

def test_outcome_importance():
    """Test importance scoring for different outcomes."""
    print("\n" + "=" * 60)
    print("OUTCOME IMPORTANCE TESTS")
    print("=" * 60)

    # Critical success + major advantage = highest importance
    result_best = resolve_action(
        "Epic action",
        forced_d20=20,
        forced_d6=6,
    )
    importance_best = arc_outcome_importance(result_best)
    assert importance_best == 10, "Critical success + major advantage should be importance 10"
    print(f"✓ Critical Success + Major Advantage = {importance_best}/10 (highest)")

    # Critical failure + severe threat = very high importance
    result_worst = resolve_action(
        "Terrible action",
        forced_d20=1,
        forced_d6=1,
    )
    importance_worst = arc_outcome_importance(result_worst)
    assert importance_worst >= 9, "Critical failure + severe threat should be high importance"
    print(f"✓ Critical Failure + Severe Threat = {importance_worst}/10 (very high)")

    # Success + neutral = moderate importance
    result_moderate = resolve_action(
        "Normal action",
        forced_d20=17,
        forced_d6=4,
    )
    importance_moderate = arc_outcome_importance(result_moderate)
    assert 5 <= importance_moderate <= 8, "Success + neutral should be moderate importance"
    print(f"✓ Success + Neutral = {importance_moderate}/10 (moderate)")

    # Partial failure + cost = lower importance
    result_lower = resolve_action(
        "Weak action",
        forced_d20=8,
        forced_d6=3,
    )
    importance_lower = arc_outcome_importance(result_lower)
    assert importance_lower <= 7, "Partial failure + cost should be lower importance"
    print(f"✓ Partial Failure + Cost = {importance_lower}/10 (lower)")

    print("\nAll importance tests passed! ✓")


# ============================================================================
# Memory Candidate Tests
# ============================================================================

def test_memory_candidates():
    """Test memory candidate generation for different outcomes."""
    print("\n" + "=" * 60)
    print("MEMORY CANDIDATE TESTS")
    print("=" * 60)

    # Critical success with advantage should generate achievement memory
    result_achievement = resolve_action(
        "Defeat the dragon",
        forced_d20=20,
        forced_d6=6,
    )

    candidates = arc_memory_candidates(
        result_achievement,
        "Defeat the dragon",
        character_name="Rue",
    )

    assert len(candidates) > 0, "Critical success should generate memories"
    assert candidates[0]["category"] == "Achievement", "Should be Achievement category"
    assert candidates[0]["importance"] == 10, "Achievement should be high importance"
    assert "Successfully accomplished" in candidates[0]["text"]
    print(f"✓ Critical Success generates Achievement memory: {candidates[0]['text']}")

    # Critical failure with threat should generate challenge memory
    result_challenge = resolve_action(
        "Escape the guards",
        forced_d20=1,
        forced_d6=1,
    )

    candidates = arc_memory_candidates(
        result_challenge,
        "Escape the guards",
        character_name="Baras",
    )

    assert len(candidates) > 0, "Critical failure should generate memories"
    assert candidates[0]["category"] == "Challenge", "Should be Challenge category"
    assert "Failed critically" in candidates[0]["text"]
    print(f"✓ Critical Failure generates Challenge memory: {candidates[0]['text']}")

    # Success with cost should generate mixed outcome memory
    result_mixed = resolve_action(
        "Negotiate trade deal",
        forced_d20=17,
        forced_d6=3,
    )

    candidates = arc_memory_candidates(
        result_mixed,
        "Negotiate trade deal",
        character_name="Jared",
    )

    assert len(candidates) > 0, "Success with cost should generate memories"
    assert candidates[0]["category"] == "Discovery", "Should be Discovery category"
    assert "cost" in candidates[0]["text"].lower()
    print(f"✓ Success + Cost generates Discovery memory: {candidates[0]['text']}")

    # Failure should generate setback memory
    result_failure = resolve_action(
        "Climb the cliff",
        forced_d20=3,
        forced_d6=4,
    )

    candidates = arc_memory_candidates(
        result_failure,
        "Climb the cliff",
        character_name="Rue",
    )

    assert len(candidates) > 0, "Failure should generate memories"
    assert candidates[0]["category"] == "Setback", "Should be Setback category"
    assert "Failed to" in candidates[0]["text"]
    print(f"✓ Failure generates Setback memory: {candidates[0]['text']}")

    print("\nAll memory candidate tests passed! ✓")


# ============================================================================
# Quest Hook Registry Tests
# ============================================================================

def test_quest_hook_registry():
    """Test quest hook registration and execution."""
    print("\n" + "=" * 60)
    print("QUEST HOOK REGISTRY TESTS")
    print("=" * 60)

    registry = QuestHookRegistry()
    callback_log = []

    # Register callbacks
    def on_success(result, context):
        callback_log.append(f"success:{context.get('quest_id', 'unknown')}")
        return f"Quest progress for {context.get('quest_id', 'unknown')}"

    def on_failure(result, context):
        callback_log.append(f"failure:{context.get('quest_id', 'unknown')}")
        return f"Quest failed for {context.get('quest_id', 'unknown')}"

    def on_advantage(result, context):
        callback_log.append(f"advantage:{context.get('quest_id', 'unknown')}")
        return f"Extra reward for quest {context.get('quest_id', 'unknown')}"

    def on_threat(result, context):
        callback_log.append(f"threat:{context.get('quest_id', 'unknown')}")
        return f"Complication in quest {context.get('quest_id', 'unknown')}"

    registry.register_on_arc_success(on_success)
    registry.register_on_arc_failure(on_failure)
    registry.register_on_arc_advantage(on_advantage)
    registry.register_on_arc_threat(on_threat)

    print("✓ Callbacks registered")

    # Test success outcome triggers success callback
    result_success = resolve_action(
        "Test",
        forced_d20=18,
        forced_d6=4,
    )
    context = {"quest_id": 42, "character_name": "Rue"}
    messages = registry.execute_hooks(result_success, context)

    assert "success:42" in callback_log, "Success callback should be triggered"
    assert len(messages) > 0, "Should return messages"
    print(f"✓ Success outcome triggers success callback: {messages[0]}")

    callback_log.clear()

    # Test failure outcome triggers failure callback
    result_failure = resolve_action(
        "Test",
        forced_d20=4,
        forced_d6=4,
    )
    messages = registry.execute_hooks(result_failure, context)

    assert "failure:42" in callback_log, "Failure callback should be triggered"
    print(f"✓ Failure outcome triggers failure callback: {messages[0]}")

    callback_log.clear()

    # Test advantage outcome
    result_advantage = resolve_action(
        "Test",
        forced_d20=18,
        forced_d6=5,
    )
    messages = registry.execute_hooks(result_advantage, context)

    assert "success:42" in callback_log, "Success callback should be triggered"
    assert "advantage:42" in callback_log, "Advantage callback should be triggered"
    assert len(messages) == 2, "Should return 2 messages (success + advantage)"
    print(f"✓ Advantage outcome triggers both success and advantage callbacks")

    callback_log.clear()

    # Test threat outcome
    result_threat = resolve_action(
        "Test",
        forced_d20=4,
        forced_d6=2,
    )
    messages = registry.execute_hooks(result_threat, context)

    assert "failure:42" in callback_log, "Failure callback should be triggered"
    assert "threat:42" in callback_log, "Threat callback should be triggered"
    assert len(messages) == 2, "Should return 2 messages (failure + threat)"
    print(f"✓ Threat outcome triggers both failure and threat callbacks")

    print("\nAll quest hook tests passed! ✓")


# ============================================================================
# Mode-Specific Hook Tests
# ============================================================================

def test_mode_specific_hooks():
    """Test mode-specific callback registration and filtering."""
    print("\n" + "=" * 60)
    print("MODE-SPECIFIC HOOK TESTS")
    print("=" * 60)

    registry = QuestHookRegistry()
    callback_log = []

    # Register mode-specific callbacks
    def companion_callback(result, context):
        callback_log.append("companion_mode")
        return "Companion mode response"

    def rpg_callback(result, context):
        callback_log.append("rpg_mode")
        return "RPG mode response"

    registry.register_on_arc_success(companion_callback, mode=NarrativeMode.COMPANION)
    registry.register_on_arc_success(rpg_callback, mode=NarrativeMode.RPG)

    print("✓ Mode-specific callbacks registered")

    # Test that callbacks only execute for matching mode
    result = resolve_action("Test", forced_d20=18, forced_d6=4)

    callback_log.clear()
    messages = registry.execute_hooks(result, mode=NarrativeMode.COMPANION)
    assert "companion_mode" in callback_log, "Companion callback should execute in companion mode"
    assert "rpg_mode" not in callback_log, "RPG callback should not execute in companion mode"
    print(f"✓ Companion mode callbacks execute correctly")

    callback_log.clear()
    messages = registry.execute_hooks(result, mode=NarrativeMode.RPG)
    assert "rpg_mode" in callback_log, "RPG callback should execute in RPG mode"
    assert "companion_mode" not in callback_log, "Companion callback should not execute in RPG mode"
    print(f"✓ RPG mode callbacks execute correctly")

    callback_log.clear()
    messages = registry.execute_hooks(result, mode=NarrativeMode.FANFICTION)
    assert len(callback_log) == 0, "No callbacks should execute for fanfiction mode (none registered)"
    print(f"✓ Fanfiction mode correctly has no specific callbacks")

    print("\nAll mode-specific hook tests passed! ✓")


# ============================================================================
# Integration Scenario Test
# ============================================================================

def test_full_integration_scenario():
    """Test a complete integration scenario: resolve -> event -> memory -> quest hooks."""
    print("\n" + "=" * 60)
    print("FULL INTEGRATION SCENARIO TEST")
    print("=" * 60)

    db_path, connection = setup_test_database()
    cursor = connection.cursor()

    try:
        # Setup
        registry = QuestHookRegistry()
        action_log = []

        def on_success(result, context):
            action_log.append("quest_updated")
            return "Quest progress updated"

        def on_advantage(result, context):
            action_log.append("bonus_reward_granted")
            return "Bonus reward granted"

        registry.register_on_arc_success(on_success)
        registry.register_on_arc_advantage(on_advantage)

        # Scenario: Character attempts to pick a lock
        print("\n--- Scenario: Rue attempts to pick an ancient lock ---")

        result = resolve_action(
            "Pick the ancient lock",
            skill_bonus=3,
            attribute_bonus=1,
            forced_d20=17,  # Success (with bonuses)
            forced_d6=5,    # Advantage
        )

        print(f"  Action Result: {result.success_level.value} + {result.consequence_level.value}")

        # 1. Record event
        event_id = create_arc_event(
            cursor,
            "Pick the ancient lock",
            result,
            character_name="Rue",
            day=5,
        )
        print(f"  Event recorded (ID: {event_id})")

        # 2. Generate memory candidates
        memory_candidates = arc_memory_candidates(
            result,
            "Pick the ancient lock",
            character_name="Rue",
        )
        print(f"  Memory candidates generated: {len(memory_candidates)}")
        for i, candidate in enumerate(memory_candidates, 1):
            print(f"    {i}. [{candidate['category']}] {candidate['text']} (importance: {candidate['importance']})")

        # 3. Trigger quest hooks
        context = {
            "character_name": "Rue",
            "quest_id": 7,
            "location": "Ancient tomb",
        }
        messages = registry.execute_hooks(result, context, mode=NarrativeMode.RPG)
        print(f"  Quest hooks executed:")
        for msg in messages:
            print(f"    - {msg}")

        # 4. Verify database state
        connection.commit()
        cursor.execute("SELECT COUNT(*) FROM events WHERE event_type = 'arc_resolution'")
        event_count = cursor.fetchone()[0]
        assert event_count == 1, "One ARC event should be in database"

        cursor.execute("SELECT importance FROM events WHERE id = ?", (event_id,))
        importance = cursor.fetchone()[0]
        assert importance >= 7, "Success with advantage should have high importance"

        # 5. Verify callbacks were triggered
        assert "quest_updated" in action_log, "Quest update callback should have been triggered"
        assert "bonus_reward_granted" in action_log, "Bonus reward callback should have been triggered"

        print(f"\n✓ Full integration scenario completed successfully!")

    finally:
        teardown_test_database(db_path, connection)


# ============================================================================
# Main Test Runner
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ARC PHASE 2 INTEGRATION TEST HARNESS")
    print("=" * 60)

    try:
        test_arcresult_helper_methods()
        test_event_recording()
        test_outcome_importance()
        test_memory_candidates()
        test_quest_hook_registry()
        test_mode_specific_hooks()
        test_full_integration_scenario()

        print("\n" + "=" * 60)
        print("ALL INTEGRATION TESTS PASSED ✓")
        print("=" * 60)
        print("\nARC Phase 2 integration points validated:")
        print("  ✓ ARCResult helper methods (is_success, is_failure, etc.)")
        print("  ✓ Event recording to database")
        print("  ✓ Outcome importance scoring")
        print("  ✓ Memory candidate generation")
        print("  ✓ Quest hook registration and execution")
        print("  ✓ Mode-specific hook filtering")
        print("  ✓ Full integration scenario")
        print("\nReady for Phase 2 implementation:")
        print("  - Chat system can now use arc_resolution and store events")
        print("  - Quest system can register callbacks without coupling to ARC")
        print("  - Memory system can evaluate candidates independently")
        print("  - All modes (companion/fanfiction/rpg) supported by design")

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

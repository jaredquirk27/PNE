"""
ARC (Adaptive Resolution Core) Test Harness

Demonstrates ARC Phase 1 functionality with example actions.
This harness tests deterministic and random outcomes.

Run with:
    cd /Users/jared/Projects/PNE
    python -m arc.arc_test
"""

from arc.arc_resolution import resolve_action


def print_result(result, title: str = ""):
    """Pretty-print an ARCResult."""
    if title:
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}")
    print(result)
    print()


def test_deterministic_outcomes():
    """
    Test deterministic outcomes using forced dice values.
    These results are repeatable and useful for validation.
    """
    print("\n" + "=" * 60)
    print("DETERMINISTIC OUTCOME TESTS")
    print("=" * 60)

    # Critical Success + Major Advantage
    result1 = resolve_action(
        "Leap across a chasm",
        forced_d20=20,
        forced_d6=6,
    )
    print_result(result1, "Critical Success + Major Advantage")
    assert result1.d20_roll == 20
    assert result1.d6_roll == 6
    assert result1.success_level.value == "Critical Success"
    assert result1.consequence_level.value == "Major Advantage"

    # Critical Failure + Severe Threat
    result2 = resolve_action(
        "Negotiate with the hostile warlord",
        forced_d20=1,
        forced_d6=1,
    )
    print_result(result2, "Critical Failure + Severe Threat")
    assert result2.d20_roll == 1
    assert result2.d6_roll == 1
    assert result2.success_level.value == "Critical Failure"
    assert result2.consequence_level.value == "Severe Threat"

    # Success + Neutral
    result3 = resolve_action(
        "Pick a locked door",
        forced_d20=18,
        forced_d6=4,
    )
    print_result(result3, "Success + Neutral")
    assert result3.d20_roll == 18
    assert result3.d6_roll == 4
    assert result3.success_level.value == "Success"
    assert result3.consequence_level.value == "Neutral"

    # Partial Success + Advantage
    result4 = resolve_action(
        "Sneak past the guards",
        forced_d20=12,
        forced_d6=5,
    )
    print_result(result4, "Partial Success + Advantage")
    assert result4.d20_roll == 12
    assert result4.d6_roll == 5
    assert result4.success_level.value == "Partial Success"
    assert result4.consequence_level.value == "Advantage"

    # Partial Failure + Cost
    result5 = resolve_action(
        "Hack the security terminal",
        forced_d20=8,
        forced_d6=3,
    )
    print_result(result5, "Partial Failure + Cost")
    assert result5.d20_roll == 8
    assert result5.d6_roll == 3
    assert result5.success_level.value == "Partial Failure"
    assert result5.consequence_level.value == "Cost"

    print("✓ All deterministic outcome tests passed!")


def test_bonus_application():
    """
    Test that bonuses correctly modify the success threshold without
    affecting critical results.
    """
    print("\n" + "=" * 60)
    print("BONUS APPLICATION TESTS")
    print("=" * 60)

    # D20=15 (threshold for Partial Success) without bonus = Partial Success
    result1 = resolve_action(
        "Climb the wall (no bonus)",
        skill_bonus=0,
        forced_d20=15,
        forced_d6=4,
    )
    print_result(result1, "D20=15, no bonus → Partial Success")
    assert result1.success_level.value == "Partial Success"

    # D20=13 + bonus=2 = 15 (threshold for Partial Success) = Partial Success
    result2 = resolve_action(
        "Climb the wall (with bonus)",
        skill_bonus=2,
        forced_d20=13,
        forced_d6=4,
    )
    print_result(result2, "D20=13, bonus=2 (total 15) → Partial Success")
    assert result2.success_level.value == "Partial Success"

    # D20=13 + bonus=3 = 16 (threshold for Success) = Success
    result3 = resolve_action(
        "Climb the wall (higher bonus)",
        skill_bonus=3,
        forced_d20=13,
        forced_d6=4,
    )
    print_result(result3, "D20=13, bonus=3 (total 16) → Success")
    assert result3.success_level.value == "Success"

    # D20=1 is always Critical Failure, even with bonus
    result4 = resolve_action(
        "Climb the wall (unlucky)",
        skill_bonus=10,
        forced_d20=1,
        forced_d6=4,
    )
    print_result(result4, "D20=1 with bonus=10 → Still Critical Failure")
    assert result4.success_level.value == "Critical Failure"

    # D20=20 is always Critical Success, even without bonus
    result5 = resolve_action(
        "Climb the wall (lucky)",
        skill_bonus=0,
        forced_d20=20,
        forced_d6=4,
    )
    print_result(result5, "D20=20, no bonus → Still Critical Success")
    assert result5.success_level.value == "Critical Success"

    print("✓ All bonus application tests passed!")


def test_random_outcomes():
    """
    Test random outcomes (without forced dice).
    These demonstrate the engine in normal operation.
    """
    print("\n" + "=" * 60)
    print("RANDOM OUTCOME TESTS (sample execution)")
    print("=" * 60)

    actions = [
        ("Persuade the merchant to lower prices", 2, 1),
        ("Disarm the trap", 3, 0),
        ("Dodge the incoming fireball", 1, 2),
        ("Decipher the ancient runes", 4, 0),
        ("Intimidate the bouncer", 0, 3),
    ]

    for action, skill, attribute in actions:
        result = resolve_action(
            action,
            skill_bonus=skill,
            attribute_bonus=attribute,
        )
        print_result(result, f"{action} (skill+{skill} attr+{attribute})")


def test_edge_cases():
    """
    Test edge cases and boundary conditions.
    """
    print("\n" + "=" * 60)
    print("EDGE CASE TESTS")
    print("=" * 60)

    # Minimum D20, maximum D6
    result1 = resolve_action(
        "Action with minimum success, maximum advantage",
        forced_d20=1,
        forced_d6=6,
    )
    print_result(result1, "D20=1 (min), D6=6 (max)")
    assert result1.success_level.value == "Critical Failure"
    assert result1.consequence_level.value == "Major Advantage"

    # Maximum D20, minimum D6
    result2 = resolve_action(
        "Action with maximum success, maximum threat",
        forced_d20=20,
        forced_d6=1,
    )
    print_result(result2, "D20=20 (max), D6=1 (min)")
    assert result2.success_level.value == "Critical Success"
    assert result2.consequence_level.value == "Severe Threat"

    # Large bonus values
    result3 = resolve_action(
        "Expert action with massive bonus",
        skill_bonus=20,
        attribute_bonus=15,
        forced_d20=2,
        forced_d6=3,
    )
    print_result(result3, "D20=2 with bonus=35")
    assert result3.success_level.value == "Critical Success"

    print("✓ All edge case tests passed!")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ARC (Adaptive Resolution Core) - Phase 1 Test Harness")
    print("=" * 60)

    try:
        test_deterministic_outcomes()
        test_bonus_application()
        test_edge_cases()
        test_random_outcomes()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nARC Phase 1 is ready for integration with:")
        print("  - Quest systems")
        print("  - Combat mechanics")
        print("  - Event recording")
        print("  - Character memory systems")
        print("  - Chat/dialogue flows")

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        exit(1)

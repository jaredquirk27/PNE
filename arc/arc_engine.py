"""
ARC (Adaptive Resolution Core) Engine

Core resolution mechanics: dice rolling, bonus application, and outcome interpretation.
This module handles the low-level rules engine without assuming integration context.

Future integration: Will be called by quest systems, combat mechanics, and event processors.
"""

import random
from typing import Optional

from arc.arc_models import SuccessLevel, ConsequenceLevel, ARCResult


def roll_d20(forced_value: Optional[int] = None) -> int:
    """
    Roll a d20 (1-20).
    
    Args:
        forced_value: If provided, use this value instead of random roll.
                     Enables deterministic testing.
    
    Returns:
        Integer between 1 and 20.
    
    Raises:
        ValueError: If forced_value is outside 1-20 range.
    """
    if forced_value is not None:
        if not (1 <= forced_value <= 20):
            raise ValueError(f"D20 forced_value must be 1-20, got {forced_value}")
        return forced_value
    return random.randint(1, 20)


def roll_d6(forced_value: Optional[int] = None) -> int:
    """
    Roll a d6 (1-6).
    
    Args:
        forced_value: If provided, use this value instead of random roll.
                     Enables deterministic testing.
    
    Returns:
        Integer between 1 and 6.
    
    Raises:
        ValueError: If forced_value is outside 1-6 range.
    """
    if forced_value is not None:
        if not (1 <= forced_value <= 6):
            raise ValueError(f"D6 forced_value must be 1-6, got {forced_value}")
        return forced_value
    return random.randint(1, 6)


def interpret_d20(roll: int, bonus: int = 0) -> SuccessLevel:
    """
    Interpret a D20 roll (plus optional bonus) into a SuccessLevel.
    
    Mapping:
    - 1 = Critical Failure (always, regardless of bonus)
    - 2-5 + bonus < 6 = Failure
    - 6-10 + bonus < 11 = Partial Failure
    - 11-15 + bonus < 16 = Partial Success
    - 16-19 + bonus < 20 = Success
    - 20 + bonus = Critical Success (always, regardless of bonus)
    
    Args:
        roll: Raw D20 result (1-20)
        bonus: Optional skill/attribute bonus applied to the roll (≥ 0)
    
    Returns:
        SuccessLevel enum value.
    
    Note:
        Bonus is applied by raising the threshold, not the roll itself.
        This prevents bonuses from lowering a critical failure or elevating
        a critical success beyond their narrative significance.
    
    Future integration: Bonus will be derived from character skills, attributes,
    equipment, and active narrative modifiers.
    """
    if roll == 1:
        return SuccessLevel.CRITICAL_FAILURE
    if roll == 20:
        return SuccessLevel.CRITICAL_SUCCESS

    adjusted_roll = roll + bonus

    if adjusted_roll < 6:
        return SuccessLevel.FAILURE
    elif adjusted_roll < 11:
        return SuccessLevel.PARTIAL_FAILURE
    elif adjusted_roll < 16:
        return SuccessLevel.PARTIAL_SUCCESS
    elif adjusted_roll < 20:
        return SuccessLevel.SUCCESS
    else:
        return SuccessLevel.CRITICAL_SUCCESS


def interpret_d6(roll: int) -> ConsequenceLevel:
    """
    Interpret a D6 roll into a ConsequenceLevel.
    
    Mapping:
    - 1 = Severe Threat
    - 2 = Minor Threat
    - 3 = Cost
    - 4 = Neutral
    - 5 = Advantage
    - 6 = Major Advantage
    
    Args:
        roll: Raw D6 result (1-6)
    
    Returns:
        ConsequenceLevel enum value.
    
    Future integration: Consequences will trigger event creation, memory recording,
    and quest objective updates.
    """
    consequence_map = {
        1: ConsequenceLevel.SEVERE_THREAT,
        2: ConsequenceLevel.MINOR_THREAT,
        3: ConsequenceLevel.COST,
        4: ConsequenceLevel.NEUTRAL,
        5: ConsequenceLevel.ADVANTAGE,
        6: ConsequenceLevel.MAJOR_ADVANTAGE,
    }
    return consequence_map[roll]


def generate_narrative_text(
    success_level: SuccessLevel,
    consequence_level: ConsequenceLevel,
    action_description: str
) -> str:
    """
    Generate a human-readable narrative summary of the resolution.
    
    Args:
        success_level: Interpreted outcome from D20
        consequence_level: Interpreted complication/advantage from D6
        action_description: User-provided action description
    
    Returns:
        Formatted string describing the resolution.
    
    Future integration: Will be replaced with dynamic narrative generation
    using character context, location, and memory systems.
    """
    summary = f"{success_level.value} with {consequence_level.value}"
    if action_description:
        return f"Action: {action_description}\nResult: {summary}"
    return summary

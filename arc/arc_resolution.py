"""
ARC (Adaptive Resolution Core) Resolution

Public API for narrative action resolution.
This is the primary entry point for resolving uncertain actions in the narrative.

Future integration:
- Called from chat/quest handlers for action outcomes
- Results logged to events table and character memories
- Consequences trigger world state updates
"""

from typing import Optional

from arc.arc_models import ARCResult
from arc.arc_engine import (
    roll_d20,
    roll_d6,
    interpret_d20,
    interpret_d6,
    generate_narrative_text,
)


def resolve_action(
    action_description: str,
    skill_bonus: int = 0,
    attribute_bonus: int = 0,
    forced_d20: Optional[int] = None,
    forced_d6: Optional[int] = None,
) -> ARCResult:
    """
    Resolve an uncertain narrative action and return a structured result.
    
    This is the primary entry point for the ARC system. It rolls dice,
    applies bonuses, interprets outcomes, and returns a narrative result.
    
    Args:
        action_description: Description of the action being attempted.
                           (e.g., "Hack the security terminal")
        skill_bonus: Bonus from character skills (≥ 0). Default: 0.
        attribute_bonus: Bonus from character attributes (≥ 0). Default: 0.
        forced_d20: For testing only. Force a specific D20 result (1-20).
                   Omit for random roll.
        forced_d6: For testing only. Force a specific D6 result (1-6).
                  Omit for random roll.
    
    Returns:
        ARCResult containing:
        - d20_roll: Raw dice value
        - d6_roll: Raw dice value
        - success_level: Interpreted success outcome
        - consequence_level: Interpreted complication/advantage
        - final_text: Human-readable narrative summary
    
    Raises:
        ValueError: If forced_d20 or forced_d6 are out of valid range.
    
    Example:
        >>> result = resolve_action("Attempt to escape the guards")
        >>> print(result)
        
        >>> result = resolve_action(
        ...     "Hack security terminal",
        ...     skill_bonus=3,
        ...     forced_d20=18,
        ...     forced_d6=5
        ... )
        >>> assert result.success_level.value == "Success"
        >>> assert result.consequence_level.value == "Advantage"
    
    Bonus Application:
        The total bonus (skill_bonus + attribute_bonus) is applied to the
        D20 result when interpreting success level. This raises the threshold
        for higher success, without modifying critical results (1 or 20).
        
        The D6 is rolled independently and unaffected by bonuses.
    
    Future Integration Points:
        - Character stats will derive skill_bonus and attribute_bonus
        - Character state (wounds, conditions) will modify bonuses
        - Environmental modifiers will add to bonuses
        - Results will trigger quest objective updates
        - Consequences will create events in the events table
        - Success/failure will affect character memories
        - Narrative text will be enriched with character/location context
    """
    # Roll dice
    d20_roll = roll_d20(forced_d20)
    d6_roll = roll_d6(forced_d6)

    # Apply bonuses
    total_bonus = skill_bonus + attribute_bonus

    # Interpret rolls
    success_level = interpret_d20(d20_roll, total_bonus)
    consequence_level = interpret_d6(d6_roll)

    # Generate narrative
    final_text = generate_narrative_text(
        success_level,
        consequence_level,
        action_description,
    )

    # Return structured result
    return ARCResult(
        d20_roll=d20_roll,
        d6_roll=d6_roll,
        success_level=success_level,
        consequence_level=consequence_level,
        final_text=final_text,
    )

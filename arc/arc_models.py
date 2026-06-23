"""
ARC (Adaptive Resolution Core) Data Models

Defines enums, constants, and dataclasses used throughout the ARC module.
Future integration: These models will be extended with metadata for logging,
event creation, and memory system interactions.
"""

from dataclasses import dataclass
from enum import Enum


class SuccessLevel(Enum):
    """
    Outcome levels based on D20 roll.
    
    Mapping:
    - 1 = Critical Failure
    - 2-5 = Failure
    - 6-10 = Partial Failure
    - 11-15 = Partial Success
    - 16-19 = Success
    - 20 = Critical Success
    """
    CRITICAL_FAILURE = "Critical Failure"
    FAILURE = "Failure"
    PARTIAL_FAILURE = "Partial Failure"
    PARTIAL_SUCCESS = "Partial Success"
    SUCCESS = "Success"
    CRITICAL_SUCCESS = "Critical Success"


class ConsequenceLevel(Enum):
    """
    Complication or advantage level based on D6 roll.
    
    Mapping:
    - 1 = Severe Threat
    - 2 = Minor Threat
    - 3 = Cost
    - 4 = Neutral
    - 5 = Advantage
    - 6 = Major Advantage
    """
    SEVERE_THREAT = "Severe Threat"
    MINOR_THREAT = "Minor Threat"
    COST = "Cost"
    NEUTRAL = "Neutral"
    ADVANTAGE = "Advantage"
    MAJOR_ADVANTAGE = "Major Advantage"


@dataclass
class ARCResult:
    """
    Structured result of a narrative action resolution.
    
    Fields:
    - d20_roll: Raw D20 result (1-20)
    - d6_roll: Raw D6 result (1-6)
    - success_level: Interpreted outcome level from D20
    - consequence_level: Interpreted complication/advantage level from D6
    - final_text: Human-readable summary of the resolution
    
    Future integration points:
    - timestamp: When the action was resolved
    - action_id: For linking to quest/event systems
    - character_name: For memory/event recording
    - d20_bonus_applied: For tracking derived success
    - narrative_tags: For filtering outcomes by category
    """
    d20_roll: int
    d6_roll: int
    success_level: SuccessLevel
    consequence_level: ConsequenceLevel
    final_text: str

    def is_success(self) -> bool:
        """
        Check if action was successful.
        Returns True for SUCCESS or CRITICAL_SUCCESS.
        """
        return self.success_level in (
            SuccessLevel.SUCCESS,
            SuccessLevel.CRITICAL_SUCCESS,
        )

    def is_failure(self) -> bool:
        """
        Check if action failed.
        Returns True for FAILURE or CRITICAL_FAILURE.
        """
        return self.success_level in (
            SuccessLevel.FAILURE,
            SuccessLevel.CRITICAL_FAILURE,
        )

    def has_advantage(self) -> bool:
        """
        Check if action has advantageous consequences.
        Returns True for ADVANTAGE or MAJOR_ADVANTAGE.
        """
        return self.consequence_level in (
            ConsequenceLevel.ADVANTAGE,
            ConsequenceLevel.MAJOR_ADVANTAGE,
        )

    def has_threat(self) -> bool:
        """
        Check if action has threatening consequences.
        Returns True for SEVERE_THREAT or MINOR_THREAT.
        """
        return self.consequence_level in (
            ConsequenceLevel.SEVERE_THREAT,
            ConsequenceLevel.MINOR_THREAT,
        )

    def is_critical(self) -> bool:
        """
        Check if action was a critical result (1 or 20).
        Returns True for CRITICAL_SUCCESS or CRITICAL_FAILURE.
        """
        return self.success_level in (
            SuccessLevel.CRITICAL_SUCCESS,
            SuccessLevel.CRITICAL_FAILURE,
        )

    def __str__(self) -> str:
        """Human-readable representation."""
        return (
            f"ARC Result: {self.success_level.value} + {self.consequence_level.value}\n"
            f"  D20: {self.d20_roll}, D6: {self.d6_roll}\n"
            f"  {self.final_text}"
        )

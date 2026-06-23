"""
ARC (Adaptive Resolution Core) Adapter

Bridges ARC results into existing PNE systems (events, memories, quests)
without modifying the core ARC resolution logic.

This adapter provides:
1. Event recording - Stores ARC outcomes in the events table
2. Memory hooks - Determines if outcomes should become memory candidates
3. Quest integration - Callbacks for quest systems to react to outcomes
4. Mode support - Agnostic to Companion/Fanfiction/RPG modes

Design principle: Integration points only. No direct PNE system modification.
"""

from typing import Callable, Dict, List, Optional
from arc.arc_models import ARCResult, SuccessLevel, ConsequenceLevel


# ============================================================================
# Future Mode Support (no core changes needed)
# ============================================================================

class NarrativeMode:
    """
    Supported narrative modes in PNE.
    Each mode can interpret ARC outcomes differently without changing
    the resolution engine itself.
    """
    COMPANION = "companion"      # Interactive companion mode
    FANFICTION = "fanfiction"    # Story generation mode
    RPG = "rpg"                  # Role-playing game mode

    @staticmethod
    def all_modes() -> List[str]:
        """Return all supported narrative modes."""
        return [NarrativeMode.COMPANION, NarrativeMode.FANFICTION, NarrativeMode.RPG]


# ============================================================================
# Event Recording
# ============================================================================

def create_arc_event(
    cursor,
    action_description: str,
    result: ARCResult,
    character_name: Optional[str] = None,
    day: int = 1,
) -> Optional[int]:
    """
    Record an ARC outcome as an event in the database.

    Creates an 'arc_resolution' event with complete outcome details.
    This integration point allows external systems to log and query
    ARC outcomes without modifying the ARC engine.

    Args:
        cursor: Database cursor for event insertion
        action_description: The action that was attempted
        result: ARCResult from resolve_action()
        character_name: Optional character performing the action
        day: Game day for the event (default: current day)

    Returns:
        Event ID if insertion succeeds, None if database unavailable

    Database Contract:
        Expects events table with columns:
        - id, day, event_type, character_name, description, importance

        Event record created will have:
        - event_type: 'arc_resolution'
        - description: JSON-like string with all outcome details
        - importance: Derived from success_level and consequence_level

    Future Integration:
        External systems should query this table to:
        - Track character action history
        - Trigger consequences in quests
        - Update character reputation/stats
        - Generate narrative logs
    """
    try:
        # Determine narrative importance
        importance = arc_outcome_importance(result)

        # Build comprehensive description
        description = (
            f"Action: {action_description} | "
            f"Success: {result.success_level.value} | "
            f"Consequence: {result.consequence_level.value} | "
            f"D20: {result.d20_roll} | D6: {result.d6_roll} | "
            f"Narrative: {result.final_text}"
        )

        # Insert event
        cursor.execute(
            """
            INSERT INTO events
            (day, event_type, character_name, description, importance)
            VALUES (?, ?, ?, ?, ?)
            """,
            (day, "arc_resolution", character_name, description, importance),
        )

        return cursor.lastrowid

    except Exception as e:
        # Integration point: External systems should handle gracefully
        print(f"Warning: Failed to create ARC event: {e}")
        return None


def arc_outcome_importance(result: ARCResult) -> int:
    """
    Score the narrative importance of an ARC outcome (1-10).

    Used to determine event importance and memory candidate weighting.
    Base scoring:
    - Critical results (1 or 20): +3
    - Success/Failure vs Partial: +1
    - Advantage/Threat vs Neutral/Cost: +1
    - Severe Threat or Major Advantage: +2

    Returns:
        Integer between 1 and 10 representing narrative significance

    Future Enhancement:
        Could be extended to consider:
        - Character emotional state
        - Quest context
        - Story beats
        - Character relationship history
    """
    importance = 5  # Base importance

    # Critical results are always significant
    if result.is_critical():
        importance += 3

    # Full success/failure more significant than partial
    if result.success_level in (SuccessLevel.SUCCESS, SuccessLevel.FAILURE):
        importance += 1
    elif result.success_level in (
        SuccessLevel.CRITICAL_SUCCESS,
        SuccessLevel.CRITICAL_FAILURE,
    ):
        importance += 2

    # Extreme consequences are significant
    if result.consequence_level in (
        ConsequenceLevel.SEVERE_THREAT,
        ConsequenceLevel.MAJOR_ADVANTAGE,
    ):
        importance += 2
    elif result.consequence_level in (
        ConsequenceLevel.MINOR_THREAT,
        ConsequenceLevel.ADVANTAGE,
    ):
        importance += 1

    return min(importance, 10)


# ============================================================================
# Memory Integration
# ============================================================================

def arc_memory_candidates(
    result: ARCResult,
    action_description: str,
    character_name: Optional[str] = None,
) -> List[Dict[str, any]]:
    """
    Determine if an ARC outcome should generate memory candidates.

    Does NOT create memories directly. Instead returns a list of potential
    memory candidates that external memory systems can evaluate and store.

    Args:
        result: ARCResult from resolve_action()
        action_description: The action that was attempted
        character_name: Optional character performing the action

    Returns:
        List of candidate memory dictionaries with:
        - text: Memory candidate text
        - importance: Calculated importance (1-10)
        - category: Type of memory (e.g., 'Outcome', 'Achievement', 'Failure')
        - source: "arc_outcome" to identify origin

    Integration Pattern:
        External memory system should:
        1. Call this function with ARC result
        2. Evaluate each candidate against character's existing memories
        3. Apply duplicate detection and canonicalization
        4. Insert accepted candidates into memory_candidates table

    Memory Categories:
        - Achievement: Critical success with advantage
        - Challenge: Critical failure or threat
        - Discovery: Success with interesting consequence
        - Setback: Failure regardless of consequence
        - Turning Point: Critical results with major consequence shifts
    """
    candidates = []

    # Critical success with advantage - Major achievement
    if result.is_critical() and result.success_level == SuccessLevel.CRITICAL_SUCCESS:
        if result.has_advantage():
            candidates.append(
                {
                    "text": f"Successfully accomplished: {action_description}",
                    "importance": 10,
                    "category": "Achievement",
                    "source": "arc_outcome",
                }
            )
        else:
            candidates.append(
                {
                    "text": f"Successfully accomplished: {action_description}",
                    "importance": 9,
                    "category": "Achievement",
                    "source": "arc_outcome",
                }
            )

    # Critical failure with threat - Major challenge/setback
    if result.is_critical() and result.success_level == SuccessLevel.CRITICAL_FAILURE:
        if result.has_threat():
            candidates.append(
                {
                    "text": f"Failed critically at: {action_description}",
                    "importance": 9,
                    "category": "Challenge",
                    "source": "arc_outcome",
                }
            )
        else:
            candidates.append(
                {
                    "text": f"Failed at: {action_description}",
                    "importance": 7,
                    "category": "Setback",
                    "source": "arc_outcome",
                }
            )

    # Success with advantage - Notable achievement
    elif result.is_success() and result.has_advantage():
        candidates.append(
            {
                "text": f"Successfully completed: {action_description}",
                "importance": 8,
                "category": "Achievement",
                "source": "arc_outcome",
            }
        )

    # Success but with cost/threat - Mixed outcome worth noting
    elif result.is_success() and result.consequence_level in (
        ConsequenceLevel.COST,
        ConsequenceLevel.MINOR_THREAT,
    ):
        candidates.append(
            {
                "text": f"Succeeded at: {action_description} but incurred a cost",
                "importance": 7,
                "category": "Discovery",
                "source": "arc_outcome",
            }
        )

    # Failure with consequence - Worth remembering
    elif result.is_failure():
        candidates.append(
            {
                "text": f"Failed to: {action_description}",
                "importance": 6,
                "category": "Setback",
                "source": "arc_outcome",
            }
        )

    # Partial success with interesting consequence
    elif result.success_level == SuccessLevel.PARTIAL_SUCCESS and not result.consequence_level == ConsequenceLevel.NEUTRAL:
        candidates.append(
            {
                "text": f"Partially succeeded at: {action_description}",
                "importance": 6,
                "category": "Discovery",
                "source": "arc_outcome",
            }
        )

    return candidates


# ============================================================================
# Quest Integration
# ============================================================================

class QuestHookRegistry:
    """
    Registry for quest system callbacks triggered by ARC outcomes.

    Allows quest systems to register interest in specific outcome types
    without coupling the ARC engine to quest logic.

    Design: Quest systems register callbacks that are invoked when ARC
    resolves actions. The callbacks receive the result and context but
    cannot modify the core resolution.

    Future Integration Points:
    - Quest progress tracking
    - Objective completion checking
    - Consequence chains
    - Narrative branching
    """

    def __init__(self):
        """Initialize callback registries."""
        self._success_callbacks: List[Callable] = []
        self._failure_callbacks: List[Callable] = []
        self._advantage_callbacks: List[Callable] = []
        self._threat_callbacks: List[Callable] = []
        self._mode_specific_callbacks: Dict[str, List[Callable]] = {
            mode: [] for mode in NarrativeMode.all_modes()
        }

    def register_on_arc_success(
        self,
        callback: Callable[[ARCResult, Dict[str, any]], None],
        mode: Optional[str] = None,
    ) -> None:
        """
        Register a callback for successful ARC outcomes.

        Args:
            callback: Function(result, context) -> None
                     Called when result.is_success() == True
            mode: Optional narrative mode filter (companion/fanfiction/rpg)
                  If None, callback triggers for all modes
        """
        if mode and mode in self._mode_specific_callbacks:
            self._mode_specific_callbacks[mode].append(("success", callback))
        else:
            self._success_callbacks.append(callback)

    def register_on_arc_failure(
        self,
        callback: Callable[[ARCResult, Dict[str, any]], None],
        mode: Optional[str] = None,
    ) -> None:
        """
        Register a callback for failed ARC outcomes.

        Args:
            callback: Function(result, context) -> None
                     Called when result.is_failure() == True
            mode: Optional narrative mode filter
        """
        if mode and mode in self._mode_specific_callbacks:
            self._mode_specific_callbacks[mode].append(("failure", callback))
        else:
            self._failure_callbacks.append(callback)

    def register_on_arc_advantage(
        self,
        callback: Callable[[ARCResult, Dict[str, any]], None],
        mode: Optional[str] = None,
    ) -> None:
        """
        Register a callback for advantageous consequences.

        Args:
            callback: Function(result, context) -> None
                     Called when result.has_advantage() == True
            mode: Optional narrative mode filter
        """
        if mode and mode in self._mode_specific_callbacks:
            self._mode_specific_callbacks[mode].append(("advantage", callback))
        else:
            self._advantage_callbacks.append(callback)

    def register_on_arc_threat(
        self,
        callback: Callable[[ARCResult, Dict[str, any]], None],
        mode: Optional[str] = None,
    ) -> None:
        """
        Register a callback for threatening consequences.

        Args:
            callback: Function(result, context) -> None
                     Called when result.has_threat() == True
            mode: Optional narrative mode filter
        """
        if mode and mode in self._mode_specific_callbacks:
            self._mode_specific_callbacks[mode].append(("threat", callback))
        else:
            self._threat_callbacks.append(callback)

    def execute_hooks(
        self,
        result: ARCResult,
        context: Optional[Dict[str, any]] = None,
        mode: Optional[str] = None,
    ) -> List[str]:
        """
        Execute all registered callbacks for an ARC outcome.

        Args:
            result: ARCResult to evaluate
            context: Optional context dict with keys like:
                    - 'character_name': Who performed the action
                    - 'action_description': What was attempted
                    - 'quest_id': Associated quest if any
                    - 'location': Where action occurred
            mode: Optional narrative mode (companion/fanfiction/rpg)
                 If specified, mode-specific callbacks also execute

        Returns:
            List of messages from executed callbacks for logging/UI

        Hook Execution Order:
            1. Success/Failure hooks (if applicable)
            2. Advantage/Threat hooks (if applicable)
            3. Mode-specific hooks (if mode specified)

        Callback Contract:
            - Callbacks receive (result, context)
            - They should NOT modify the result
            - They should return a message string for logging
            - They should handle all exceptions internally
            - They should be idempotent (safe to call multiple times)
        """
        if context is None:
            context = {}

        messages = []

        # Execute outcome callbacks
        if result.is_success():
            for callback in self._success_callbacks:
                try:
                    msg = callback(result, context)
                    if msg:
                        messages.append(msg)
                except Exception as e:
                    messages.append(f"Error in success hook: {e}")

        if result.is_failure():
            for callback in self._failure_callbacks:
                try:
                    msg = callback(result, context)
                    if msg:
                        messages.append(msg)
                except Exception as e:
                    messages.append(f"Error in failure hook: {e}")

        # Execute consequence callbacks
        if result.has_advantage():
            for callback in self._advantage_callbacks:
                try:
                    msg = callback(result, context)
                    if msg:
                        messages.append(msg)
                except Exception as e:
                    messages.append(f"Error in advantage hook: {e}")

        if result.has_threat():
            for callback in self._threat_callbacks:
                try:
                    msg = callback(result, context)
                    if msg:
                        messages.append(msg)
                except Exception as e:
                    messages.append(f"Error in threat hook: {e}")

        # Execute mode-specific hooks
        if mode and mode in self._mode_specific_callbacks:
            for hook_type, callback in self._mode_specific_callbacks[mode]:
                try:
                    # Check if this hook applies to this result
                    should_execute = False
                    if hook_type == "success" and result.is_success():
                        should_execute = True
                    elif hook_type == "failure" and result.is_failure():
                        should_execute = True
                    elif hook_type == "advantage" and result.has_advantage():
                        should_execute = True
                    elif hook_type == "threat" and result.has_threat():
                        should_execute = True

                    if should_execute:
                        msg = callback(result, context)
                        if msg:
                            messages.append(msg)
                except Exception as e:
                    messages.append(f"Error in mode-specific hook: {e}")

        return messages

    def clear_all(self) -> None:
        """Clear all registered callbacks. Useful for testing."""
        self._success_callbacks.clear()
        self._failure_callbacks.clear()
        self._advantage_callbacks.clear()
        self._threat_callbacks.clear()
        for callbacks_list in self._mode_specific_callbacks.values():
            callbacks_list.clear()


# Global registry instance for convenience
# External systems can use: from arc_adapter import global_quest_registry
global_quest_registry = QuestHookRegistry()


# ============================================================================
# Integration Pattern Summary
# ============================================================================

"""
INTEGRATION PATTERN FOR PNE SYSTEMS

When using ARC in Phase 2+, the typical flow is:

1. RESOLVE ACTION
   from arc.arc_resolution import resolve_action
   result = resolve_action("Attempt lock pick", skill_bonus=2)

2. RECORD EVENT
   event_id = create_arc_event(cursor, "Attempt lock pick", result, 
                               character_name="Rue", day=5)

3. CHECK FOR MEMORIES
   memory_candidates = arc_memory_candidates(result, "Attempt lock pick", 
                                             character_name="Rue")
   # Pass to memory system for evaluation and deduplication

4. TRIGGER QUESTS
   context = {
       'character_name': 'Rue',
       'action_description': 'Attempt lock pick',
       'quest_id': 42,
       'location': 'Underground bunker'
   }
   messages = global_quest_registry.execute_hooks(result, context, 
                                                   mode='rpg')

5. SYSTEM-SPECIFIC HANDLING
   Each system (chat, quests, memory) independently processes the result
   without coupling to ARC engine or each other.

FUTURE MODES
The same code works for all modes without modification:
- Companion: Quest hooks adapt tone, memory system adds relationship context
- Fanfiction: Memory system prioritizes narrative beats, quests auto-complete
- RPG: Full mechanical resolution with stat updates and persistent consequences
"""

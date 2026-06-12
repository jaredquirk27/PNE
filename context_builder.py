from characters import get_character
from memories import get_top_memories
from goals import get_active_goals
from story_state import get_story_state
from quests import get_active_quests
from flags import get_all_flags
from initiatives import get_active_initiatives


# ==========================
# CHARACTER FLAGS
# ==========================

def get_character_flags(
    cursor,
    character
):

    cursor.execute("""
    SELECT *
    FROM story_flags
    WHERE flag_name LIKE ?
    """,
    (f"{character}_%",))

    return cursor.fetchall()


# ==========================
# RECENT IMPORTANT EVENTS
# ==========================

def get_recent_events(
    cursor,
    character,
    limit=5
):

    cursor.execute("""
    SELECT *
    FROM events
    WHERE character_name = ?
    ORDER BY day DESC
    LIMIT ?
    """,
    (
        character,
        limit
    ))

    return cursor.fetchall()


# ==========================
# CONTEXT BUILDER
# ==========================

def build_character_context(
    cursor,
    character
):

    character_data = get_character(
        cursor,
        character
    )

    if not character_data:

        return "Character not found."

    memories = get_top_memories(
        cursor,
        character,
        5
    )

    goals = get_active_goals(
        cursor,
        character
    )

    flags = get_character_flags(
        cursor,
        character
    )

    recent_events = get_recent_events(
        cursor,
        character
    )

    story_state = get_story_state(
        cursor,
        character
    )

    active_quests = get_active_quests(
        cursor
    )
    active_initiatives = (
        get_active_initiatives(
            cursor
        )
    )

    context = []

    # ==================
    # CHARACTER
    # ==================

    context.append(
        f"Character: {character_data[1]}"
    )

    context.append(
        f"Trust: {character_data[2]}"
    )

    context.append(
        f"Relationship: {character_data[3]}"
    )

    if character_data[5]:

        context.append(
            f"Persona: {character_data[5]}"
        )

    if character_data[6]:

        context.append(
            f"Speaking Style: {character_data[6]}"
        )

    # ==================
    # STORY STATE
    # ==================

    context.append(
        "\nCurrent Story State:"
    )

    if story_state:

        context.append(
            f"- Location: {story_state[0]}"
        )

        context.append(
            f"- Scene: {story_state[1]}"
        )

        context.append(
            f"- Story Arc: {story_state[2]}"
        )

        context.append(
            f"- Quest: {story_state[3]}"
        )

    else:

        context.append(
            "- No story state found"
        )
    # ==================
    # CURRENT DAY
    # ==================

    cursor.execute("""
    SELECT current_day
    FROM world_state
    WHERE id = 1
    """)

    current_day = cursor.fetchone()

    if current_day:

        context.append(
            f"\nCurrent Day: {current_day[0]}"
        )
    # ==================
    # TOP MEMORIES
    # ==================

    context.append(
        "\nTop Memories:"
    )

    if memories:

        for memory in memories:

            context.append(
                f"- {memory[4]}"
            )

    else:

        context.append(
            "- No significant memories"
        )

    # ==================
    # ACTIVE GOALS
    # ==================

    context.append(
        "\nActive Goals:"
    )

    if goals:

        for goal in goals:

            context.append(
                f"- {goal[2]}"
            )

    else:

        context.append(
            "- No active goals"
        )

    # ==================
    # ACTIVE QUESTS
    # ==================

    context.append(
        "\nActive Quests:"
    )

    if active_quests:

        for quest in active_quests:

            context.append(
                f"- {quest[1]}"
            )

    else:

        context.append(
            "- No active quests"
        )
    # ==================
    # ACTIVE INITIATIVES
    # ==================

    context.append(
        "\nActive Initiatives:"
    )

    character_initiatives = []

    for initiative in active_initiatives:

        if initiative[1] == character:

            character_initiatives.append(
                initiative
            )

    if character_initiatives:

        for initiative in character_initiatives:

            context.append(
                f"- {initiative[2]}"
            )

            context.append(
                f"  Location: {initiative[4]}"
            )

            context.append(
                f"  Scene: {initiative[5]}"
            )

    else:

        context.append(
            "- No active initiatives"
        )
    # ==================
    # RECENT EVENTS
    # ==================

    context.append(
        "\nRecent Events:"
    )

    if recent_events:

        for event in recent_events:

            context.append(
                f"- Day {event[1]}: {event[4]}"
            )

    else:

        context.append(
            "- No recent events"
        )

    # ==================
    # FLAGS
    # ==================

    context.append(
        "\nKnown Flags:"
    )

    if flags:

        for flag in flags:

            context.append(
                f"- {flag[0]}"
            )

    else:

        context.append(
            "- No flags"
        )

    return "\n".join(context)
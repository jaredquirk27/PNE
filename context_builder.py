from characters import get_character
from memories import get_top_memories
from goals import get_active_goals


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

    flags = get_character_flags(
        cursor,
        character
    )

    goals = get_active_goals(
        cursor,
        character
    )

    context = []

    # ==================
    # CORE INFO
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

    if len(character_data) > 5 and character_data[5]:

        context.append(
            f"Persona: {character_data[5]}"
        )

    if len(character_data) > 6 and character_data[6]:

        context.append(
            f"Speaking Style: {character_data[6]}"
        )

    # ==================
    # TOP MEMORIES
    # ==================

    context.append("\nTop Memories:")

    if not memories:

        context.append(
            "- No significant memories"
        )

    else:

        for memory in memories:

            event_name = (
                memory[2]
                .replace("_", " ")
                .title()
            )

            context.append(
                f"- {event_name}: {memory[4]}"
            )

    # ==================
    # RELATIONSHIP FLAGS
    # ==================

    context.append(
        "\nRelationship Status:"
    )

    relationship_found = False

    for flag in flags:

        flag_name = flag[0]

        if flag_name.endswith("_dating"):

            context.append(
                "- Dating"
            )

            relationship_found = True

        elif flag_name.endswith("_romantic_moment"):

            context.append(
                "- Romantic Relationship"
            )

            relationship_found = True

    if not relationship_found:

        context.append(
            "- No special relationship flags"
        )

    # ==================
    # HISTORY
    # ==================

    context.append(
        "\nHistory:"
    )

    history_found = False

    for flag in flags:

        flag_name = flag[0]

        if flag_name.endswith("_dating"):
            continue

        if flag_name.endswith("_romantic_moment"):
            continue

        history_name = (
            flag_name
            .replace(
                f"{character}_",
                ""
            )
            .replace("_", " ")
            .title()
        )

        context.append(
            f"- {history_name}"
        )

        history_found = True

    if not history_found:

        context.append(
            "- No historical flags"
        )

    # ==================
    # ACTIVE GOALS
    # ==================

    context.append(
        "\nActive Goals:"
    )

    if not goals:

        context.append(
            "- No active goals"
        )

    else:

        for goal in goals:

            context.append(
                f"- {goal[2]}"
            )

    return "\n".join(context)

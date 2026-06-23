from characters import get_character
from memories import get_top_memories, get_relevant_memories
from goals import get_active_goals
from story_state import get_story_state
from quests import get_active_quests
from initiatives import get_active_initiatives

def get_character_flags(cursor, character):

    cursor.execute("""
    SELECT *
    FROM story_flags
    WHERE flag_name LIKE ?
    """, (f"{character}_%",))

    return cursor.fetchall()

def get_recent_events(cursor, character, limit=5):

    cursor.execute("""
    SELECT *
    FROM events
    WHERE character_name = ?
    ORDER BY day DESC
    LIMIT ?
    """, (character, limit))

    return cursor.fetchall()

def build_character_context(cursor, character, user_message=""):

    character_data = get_character(cursor, character)

    if user_message:
        memories = get_relevant_memories(
            cursor, character, user_message, 10
        )
    else:
        memories = get_top_memories(
            cursor, character, 15
        )

    goals = get_active_goals(cursor, character)
    flags = get_character_flags(cursor, character)
    recent_events = get_recent_events(cursor, character)
    story_state = get_story_state(cursor, character)
    active_quests = get_active_quests(cursor)
    active_initiatives = get_active_initiatives(cursor)

    context = []

    context.append(f"Character: {character_data[1]}")
    context.append(f"Trust: {character_data[2]}")
    context.append(f"Relationship: {character_data[3]}")

    context.append("\\nRelevant Memories:")

    definitions = []
    entities = []
    other = []

    for memory in memories:

        text = memory[4]

        if "stands for" in text.lower():
            definitions.append(text)
        elif any(x in text.lower() for x in
                 ["kavik", "nix", "melbourne dragons", "rue meridian"]):
            entities.append(text)
        else:
            other.append(text)

    if definitions:
        context.append("\\nDefinitions:")
        for x in definitions:
            context.append(f"- {x}")

    if entities:
        context.append("\\nNamed Entities:")
        for x in entities:
            context.append(f"- {x}")

    if other:
        context.append("\\nOther Memories:")
        for x in other:
            context.append(f"- {x}")

    context.append("\\nCurrent Story State:")

    if story_state:
        context.append(f"- Location: {story_state[0]}")
        context.append(f"- Scene: {story_state[1]}")

    return "\\n".join(context)

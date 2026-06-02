# ==========================
# MEMORY FUNCTIONS
# ==========================

def get_character_memories(
    cursor,
    character,
    min_importance
):

    cursor.execute("""
    SELECT *
    FROM events
    WHERE character_name = ?
    AND importance >= ?
    ORDER BY day DESC
    """,
    (
        character,
        min_importance
    ))

    return cursor.fetchall()


def show_character_memories(
    memories
):

    if not memories:
        print("No memories found.")
        return

    print("\n=== Character Memories ===\n")

    for memory in memories:

        print(f"Day {memory[1]}")
        print(
            f"Event: "
            f"{memory[2].replace('_', ' ').title()}"
        )
        print(f"Description: {memory[4]}")
        print(f"Importance: {memory[5]}")
        print("-------------------")


def get_top_memories(
    cursor,
    character,
    limit=5
):

    cursor.execute("""
    SELECT *
    FROM events
    WHERE character_name = ?
    ORDER BY importance DESC,
             day DESC
    LIMIT ?
    """,
    (
        character,
        limit
    ))

    memories = cursor.fetchall()

    unique_memories = []
    seen = set()

    for memory in memories:

        key = (
            memory[2],
            memory[4]
        )

        if key in seen:
            continue

        seen.add(key)

        unique_memories.append(
            memory
        )

    return unique_memories
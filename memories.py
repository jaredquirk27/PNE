def get_character_memories(
    cursor,
    character,
    min_importance=1
):

    cursor.execute("""
    SELECT *
    FROM events
    WHERE character_name = ?
    AND event_type = 'memory_extracted'
    AND importance >= ?
    ORDER BY importance DESC, day DESC
    """, (character, min_importance))

    return cursor.fetchall()


def get_top_memories(
    cursor,
    character,
    limit=25
):

    cursor.execute("""
    SELECT *
    FROM events
    WHERE character_name = ?
    AND event_type = 'memory_extracted'
    ORDER BY importance DESC, day DESC
    LIMIT ?
    """, (character, limit))

    return cursor.fetchall()


def get_relevant_memories(
    cursor,
    character,
    query,
    limit=10
):

    cursor.execute("""
    SELECT *
    FROM events
    WHERE character_name = ?
    AND event_type = 'memory_extracted'
    """, (character,))

    memories = cursor.fetchall()

    keywords = [
        x.lower().strip(".,!?")
        for x in query.split()
        if len(x) > 2
    ]

    scored = []

    for memory in memories:

        text = str(memory[4]).lower()
        score = memory[5]

        for keyword in keywords:
            if keyword in text:
                score += 15

        if query.lower() in text:
            score += 25

        if "stands for" in text:
            score += 5

        scored.append((score, memory))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [memory for score, memory in scored[:limit]]


def show_character_memories(memories):

    if not memories:
        print("No memories found.")
        return

    print("\n=== Memories ===\n")

    for memory in memories:

        print(f"Day: {memory[1]}")
        print(f"Importance: {memory[5]}")
        print(f"Memory: {memory[4]}")
        print("-------------------")

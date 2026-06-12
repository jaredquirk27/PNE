from constants import MEMORY_PATTERNS


# ==========================
# MEMORY CANDIDATES
# ==========================

def add_memory_candidate(
    cursor,
    character_name,
    memory_text,
    importance
):

    cursor.execute("""
    SELECT id
    FROM memory_candidates
    WHERE character_name = ?
    AND memory_text = ?
    AND accepted = 0
    """,
    (
        character_name,
        memory_text
    ))

    if cursor.fetchone():
        return False

    cursor.execute("""
    INSERT INTO memory_candidates
    (
        character_name,
        memory_text,
        importance
    )
    VALUES (?, ?, ?)
    """,
    (
        character_name,
        memory_text,
        importance
    ))

    return True


def get_memory_candidates(cursor):

    cursor.execute("""
    SELECT *
    FROM memory_candidates
    WHERE accepted = 0
    ORDER BY importance DESC
    """)

    return cursor.fetchall()


def show_memory_candidates(candidates):

    if not candidates:
        print("No memory candidates.")
        return

    print("\n=== Memory Candidates ===\n")

    for memory in candidates:

        print(f"ID: {memory[0]}")
        print(f"Character: {memory[1]}")
        print(f"Memory: {memory[2]}")
        print(f"Importance: {memory[3]}")
        print("-------------------")


# ==========================
# MEMORY ACCEPTANCE
# ==========================

def accept_memory_candidate(
    cursor,
    memory_id,
    get_current_day,
    add_event
):

    cursor.execute("""
    SELECT *
    FROM memory_candidates
    WHERE id = ?
    """,
    (memory_id,))

    memory = cursor.fetchone()

    if not memory:
        print("Memory not found.")
        return

    day = get_current_day(cursor)

    character_name = memory[1]
    memory_text = memory[2]
    importance = memory[3]

    add_event(
        cursor,
        day,
        "memory_extracted",
        character_name,
        memory_text,
        importance
    )

    cursor.execute("""
    UPDATE memory_candidates
    SET accepted = 1
    WHERE id = ?
    """,
    (memory_id,))


# ==========================
# EXTRACTION ENGINE
# ==========================

def extract_memory_from_text(
    cursor,
    character,
    conversation_text
):

    conversation_lower = (
        conversation_text.lower()
    )

    found_memories = []

    for keyword, data in MEMORY_PATTERNS.items():

        if keyword in conversation_lower:

            added = add_memory_candidate(
                cursor,
                character,
                data["template"],
                data["importance"]
            )

            if added:

                found_memories.append(
                    data["template"]
                )

    return found_memories

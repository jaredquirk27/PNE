from constants import MEMORY_PATTERNS
import re
import hashlib


def generate_memory_hash(text):
    return hashlib.md5(text.lower().strip().encode()).hexdigest()


def add_memory_candidate(
    cursor,
    character_name,
    memory_text,
    importance,
    category="story_event",
    entity=""
):

    memory_hash = generate_memory_hash(memory_text)

    try:
        cursor.execute("""
        SELECT id
        FROM memory_candidates
        WHERE memory_hash = ?
        """, (memory_hash,))

        if cursor.fetchone():
            return False
    except:
        pass

    try:
        cursor.execute("""
        INSERT INTO memory_candidates
        (
            character_name,
            memory_text,
            importance,
            accepted,
            category,
            entity,
            memory_hash
        )
        VALUES (?, ?, ?, 0, ?, ?, ?)
        """,
        (
            character_name,
            memory_text,
            importance,
            category,
            entity,
            memory_hash
        ))
    except:
        cursor.execute("""
        INSERT INTO memory_candidates
        (
            character_name,
            memory_text,
            importance,
            accepted
        )
        VALUES (?, ?, ?, 0)
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

    print("\\n=== Memory Candidates ===\\n")

    for memory in candidates:
        print(f"ID: {memory[0]}")
        print(f"Character: {memory[1]}")
        print(f"Memory: {memory[2]}")
        print(f"Importance: {memory[3]}")
        print("-------------------")


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
    """, (memory_id,))

    memory = cursor.fetchone()

    if not memory:
        return

    day = get_current_day(cursor)

    add_event(
        cursor,
        day,
        "memory_extracted",
        memory[1],
        memory[2],
        memory[3]
    )

    cursor.execute("""
    UPDATE memory_candidates
    SET accepted = 1
    WHERE id = ?
    """, (memory_id,))


def extract_fact_memories(conversation_text):

    memories = []

    for line in conversation_text.splitlines():

        clean = line.strip()

        if not clean:
            continue

        lower = clean.lower()

        if "stands for" in lower:
            memories.append((clean[:150], 10))

        elif any(
            entity in lower
            for entity in [
                "arc",
                "pne",
                "kavik",
                "nix",
                "rue meridian",
                "melbourne dragons"
            ]
        ) and " is " in lower:

            memories.append((clean[:150], 8))

    return memories


def extract_memory_from_text(
    cursor,
    character,
    conversation_text
):

    found_memories = []

    conversation_lower = conversation_text.lower()

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

    fact_memories = extract_fact_memories(
        conversation_text
    )

    for memory_text, importance in fact_memories:

        added = add_memory_candidate(
            cursor,
            character,
            memory_text,
            importance
        )

        if added:
            found_memories.append(
                memory_text
            )

    return found_memories

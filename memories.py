import re

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
    LIMIT ?
    """, (character, limit))

    return cursor.fetchall()


def normalize_text(text):
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower()).strip()


def extract_entities_from_message(message):
    raw_tokens = [
        token.strip(".,!?\"'()[]")
        for token in message.split()
        if token.strip(".,!?\"'()[]")
    ]

    entities = []
    for token in raw_tokens:
        if token.istitle() or token.isupper() and len(token) > 1:
            entities.append(token)

    return entities


def infer_memory_category(memory_text):
    lower_text = memory_text.lower()
    if "stands for" in lower_text or "acronym" in lower_text:
        return "Definition"
    if any(phrase in lower_text for phrase in ["is a", "is an", "is the", "was a", "was an", "was the"]):
        return "Identity"
    if any(word in lower_text for word in ["friend", "enemy", "lover", "relationship", "married", "dating"]):
        return "Relationship"
    if re.search(r"\b[A-Z][a-z]+\b", memory_text):
        return "Named Entity"
    return ""


def score_memory_relevance(
    memory_text,
    category,
    importance,
    user_message,
    current_story_state=None,
    recency_rank=None
):

    normalized_message = normalize_text(user_message)
    normalized_memory = normalize_text(memory_text)

    score = importance

    keyword_match_bonus = 0
    entity_match_bonus = 0
    recency_bonus = 0
    category_bonus = 0

    message_terms = set(
        term for term in normalized_message.split()
        if term
    )
    memory_terms = set(
        term for term in normalized_memory.split()
        if term
    )

    if message_terms & memory_terms:
        keyword_match_bonus = 5

    user_entities = extract_entities_from_message(user_message)
    for entity in user_entities:
        if entity.lower() in normalized_memory:
            entity_match_bonus = 10
            break

    if recency_rank is not None:
        if recency_rank < 10:
            recency_bonus = 3
        elif recency_rank < 25:
            recency_bonus = 1

    category_bonuses = {
        "Identity": 2,
        "Named Entity": 2,
        "Relationship": 2,
        "Definition": 1,
    }
    category_bonus = category_bonuses.get(category, 0)

    score += keyword_match_bonus + entity_match_bonus + recency_bonus + category_bonus

    print("\nMemory Score:")
    print(memory_text)
    print(f"Score: {score}")

    return score


def get_relevant_memories(
    cursor,
    character,
    query,
    limit=20
):

    cursor.execute("""
    SELECT *
    FROM events
    WHERE character_name = ?
    AND event_type = 'memory_extracted'
    ORDER BY day DESC
    """, (character,))

    memories = cursor.fetchall()

    scored = []
    for rank, memory in enumerate(memories):
        memory_text = str(memory[4])
        importance = memory[5]
        category = infer_memory_category(memory_text)

        score = score_memory_relevance(
            memory_text,
            category,
            importance,
            query,
            None,
            rank
        )

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

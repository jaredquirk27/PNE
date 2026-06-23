import re
import hashlib

SPEAKER_PREFIX = re.compile(r'^(?:\s*(?:User|Rue|[A-Za-z][A-Za-z0-9_ ]{0,30}):\s*)+', re.IGNORECASE)
SENTENCE_SPLIT = re.compile(r'(?<=[.!?])\s+')
GENERIC_CONTENT = re.compile(
    r'\b(?:talked about|discussed|think(?:s|ing)?|feel(?:s|ing)?|probably|maybe|could be|should be|would be|kind of|sort of|someone|something|anything|everything|a lot|well known|simple summary|project discussion|transcript|conversation|said|asked|told|reply|replied|question|answer)\b',
    re.IGNORECASE
)
GENERIC_SUBJECTS = re.compile(r'^(?:I|You|He|She|They|It|This|That|There|These|Those)\b', re.IGNORECASE)


def canonical_preference_my_favorite(match):
    field = match.group('field').strip()
    value = match.group('value').strip()
    return trim_memory_text(f"Jared's favorite {field} is {value}.")


def canonical_preference_i_like_best(match):
    item = match.group('item').strip()
    return trim_memory_text(f"Jared likes {item} best.")


def canonical_preference_my_preferred(match):
    field = match.group('field').strip()
    value = match.group('value').strip()
    return trim_memory_text(f"Jared's preferred {field} is {value}.")


def canonical_preference_my_goto(match):
    field = match.group('field').strip()
    value = match.group('value').strip()
    return trim_memory_text(f"Jared's go-to {field} is {value}.")


def canonical_preference_x_is_my_favorite(match):
    item = match.group('item').strip()
    return trim_memory_text(f"Jared's favorite is {item}.")


def canonical_preference_i_always_choose(match):
    item = match.group('item').strip()
    return trim_memory_text(f"Jared always chooses {item}.")


FACT_PATTERNS = [
    (
        re.compile(
            r'^(?P<subject>[A-Z][A-Za-z0-9 ]{0,80}?) stands for (?P<object>[^.?!]{1,120})[.?!]?$',
            re.IGNORECASE
        ),
        "Definition",
        10
    ),
    (
        re.compile(
            r'^(?P<subject>[A-Z][A-Za-z0-9 ]{0,80}?) is an acronym for (?P<object>[^.?!]{1,120})[.?!]?$',
            re.IGNORECASE
        ),
        "Definition",
        10
    ),
    (
        re.compile(
            r'^(?P<subject>[A-Z][A-Za-z0-9 ]{0,80}?) is named after (?P<object>[^.?!]{1,120})[.?!]?$',
            re.IGNORECASE
        ),
        "Identity",
        9
    ),
    (
        re.compile(
            r'^(?P<subject>[A-Z][A-Za-z0-9 ]{0,80}?) is named (?P<object>[^.?!]{1,120})[.?!]?$',
            re.IGNORECASE
        ),
        "Identity",
        8
    ),
    (
        re.compile(
            r"^(?P<owner>[A-Z][A-Za-z0-9 ]{0,80}?)'s favorite [^.?!]{1,80} is [^.?!]{1,80}[.?!]?$",
            re.IGNORECASE
        ),
        "Preference",
        8
    ),
    (
        re.compile(
            r'^(?:My|my) favorite (?P<field>[^.?!]{1,80}) is (?P<value>[^.?!]{1,80})[.?!]?$',
            re.IGNORECASE
        ),
        "Preference",
        8,
        canonical_preference_my_favorite
    ),
    (
        re.compile(
            r'^(?:My|my) favourite (?P<field>[^.?!]{1,80}) is (?P<value>[^.?!]{1,80})[.?!]?$',
            re.IGNORECASE
        ),
        "Preference",
        8,
        canonical_preference_my_favorite
    ),
    (
        re.compile(
            r'^(?:My|my) preferred (?P<field>[^.?!]{1,80}) is (?P<value>[^.?!]{1,80})[.?!]?$',
            re.IGNORECASE
        ),
        "Preference",
        8,
        canonical_preference_my_preferred
    ),
    (
        re.compile(
            r'^(?:My|my) go-to (?P<field>[^.?!]{1,80}) is (?P<value>[^.?!]{1,80})[.?!]?$',
            re.IGNORECASE
        ),
        "Preference",
        8,
        canonical_preference_my_goto
    ),
    (
        re.compile(
            r'^(?P<item>[^.?!]{1,80}) is my favorite[.?!]?$',
            re.IGNORECASE
        ),
        "Preference",
        8,
        canonical_preference_x_is_my_favorite
    ),
    (
        re.compile(
            r'^(?:I|i) like (?P<item>[^.?!]{1,80}) best[.?!]?$',
            re.IGNORECASE
        ),
        "Preference",
        8,
        canonical_preference_i_like_best
    ),
    (
        re.compile(
            r'^(?:I|i) always choose (?P<item>[^.?!]{1,80})[.?!]?$',
            re.IGNORECASE
        ),
        "Preference",
        8,
        canonical_preference_i_always_choose
    ),
    (
        re.compile(
            r'^(?P<subject>[A-Z][A-Za-z0-9 ]{0,80}?) is a shared code phrase meaning (?P<object>[^.?!]{1,120})[.?!]?$',
            re.IGNORECASE
        ),
        "Relationship",
        8
    ),
    (
        re.compile(
            r'^(?P<subject>[A-Z][A-Za-z0-9 ]{0,80}?) is (?:a|an|the) [A-Za-z][A-Za-z0-9 \- ]{1,120}[.?!]?$',
            re.IGNORECASE
        ),
        "Named Entity",
        8
    ),
    (
        re.compile(
            r'^Memory retrieval was successfully implemented[.!?]?$',
            re.IGNORECASE
        ),
        "Accomplishment",
        9
    ),
    (
        re.compile(
            r'^[A-Z][A-Za-z0-9 ]{0,80}? was successfully implemented[.!?]?$',
            re.IGNORECASE
        ),
        "Accomplishment",
        8
    ),
    (
        re.compile(
            r'^[A-Z][A-Za-z0-9 ]{0,80}? was completed[.!?]?$',
            re.IGNORECASE
        ),
        "Accomplishment",
        7
    ),
]


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
    memory_text = memory_text.strip()
    memory_hash = generate_memory_hash(memory_text)

    try:
        cursor.execute(
            """
            SELECT id
            FROM memory_candidates
            WHERE memory_hash = ?
            AND character_name = ?
            """,
            (memory_hash, character_name)
        )

        if cursor.fetchone():
            return False
    except Exception:
        pass

    try:
        cursor.execute(
            """
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
            )
        )
    except Exception:
        cursor.execute(
            """
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
            )
        )

    return True


def get_memory_candidates(cursor):
    cursor.execute(
        """
        SELECT *
        FROM memory_candidates
        WHERE accepted = 0
        ORDER BY importance DESC
        """
    )
    return cursor.fetchall()


AUTO_CANONIZATION_CATEGORIES = {
    "Definition",
    "Named Entity",
    "Identity",
    "Preference",
    "Relationship",
    "Accomplishment"
}

AUTO_CANONIZATION_MIN_IMPORTANCE = 8


def is_auto_canonizable(category, importance):
    return (
        category in AUTO_CANONIZATION_CATEGORIES and
        importance >= AUTO_CANONIZATION_MIN_IMPORTANCE
    )


def memory_already_canonized(cursor, memory_hash, memory_text):
    cursor.execute(
        """
        SELECT 1
        FROM memory_candidates
        WHERE memory_hash = ?
        AND accepted = 1
        LIMIT 1
        """,
        (memory_hash,)
    )

    if cursor.fetchone():
        return True

    cursor.execute(
        """
        SELECT 1
        FROM events
        WHERE event_type = 'memory_extracted'
        AND description = ?
        LIMIT 1
        """,
        (memory_text,)
    )

    return cursor.fetchone() is not None


def auto_canonize_memories(cursor, current_day, add_event):
    cursor.execute(
        """
        SELECT id, character_name, memory_text, importance, category, memory_hash
        FROM memory_candidates
        WHERE accepted = 0
        ORDER BY importance DESC
        """
    )

    candidates = cursor.fetchall()
    auto_accepted = []

    for candidate in candidates:
        memory_id, character_name, memory_text, importance, category, memory_hash = candidate

        if not is_auto_canonizable(category, importance):
            continue

        if memory_already_canonized(cursor, memory_hash, memory_text):
            cursor.execute(
                """
                UPDATE memory_candidates
                SET accepted = 1
                WHERE id = ?
                """,
                (memory_id,)
            )
            continue

        add_event(
            cursor,
            current_day,
            "memory_extracted",
            character_name,
            memory_text,
            importance
        )

        cursor.execute(
            """
            UPDATE memory_candidates
            SET accepted = 1
            WHERE id = ?
            """,
            (memory_id,)
        )

        print("\nAUTO-CANONIZED:\n")
        print(memory_text)
        auto_accepted.append(memory_text)

    return auto_accepted


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
        if len(memory) > 5:
            print(f"Category: {memory[5]}")
        print("-------------------")


def accept_memory_candidate(
    cursor,
    memory_id,
    get_current_day,
    add_event
):
    cursor.execute(
        """
        SELECT *
        FROM memory_candidates
        WHERE id = ?
        """,
        (memory_id,)
    )

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

    cursor.execute(
        """
        UPDATE memory_candidates
        SET accepted = 1
        WHERE id = ?
        """,
        (memory_id,)
    )


def split_into_sentences(text):
    if not text:
        return []

    clean_text = text.replace("\r\n", "\n").replace("\r", "\n")
    clean_text = re.sub(r'(?<![.?!])\n+', '. ', clean_text)
    clean_text = re.sub(
        r'(?<![.?!])\s+(?=(?:User|Rue|[A-Za-z][A-Za-z0-9_ ]{0,30}):)',
        '. ',
        clean_text
    )
    clean_text = clean_text.replace("\n", " ")

    sentences = SENTENCE_SPLIT.split(clean_text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def normalize_sentence(sentence):
    sentence = sentence.strip()
    sentence = SPEAKER_PREFIX.sub("", sentence)
    return sentence.strip()


def is_generic_sentence(sentence):
    if not sentence:
        return True

    if sentence.endswith("?"):
        return True

    if GENERIC_SUBJECTS.match(sentence):
        return True

    if GENERIC_CONTENT.search(sentence):
        return True

    if ":" in sentence:
        return True

    return False


def trim_memory_text(text):
    text = text.strip()
    if len(text) <= 150:
        return text

    return text[:150].rstrip()


def categorize_memory_sentence(sentence):
    if not sentence or is_generic_sentence(sentence):
        return None

    for entry in FACT_PATTERNS:
        if len(entry) == 3:
            pattern, category, importance = entry
            canonicalizer = None
        else:
            pattern, category, importance, canonicalizer = entry

        match = pattern.match(sentence)
        if not match:
            continue

        subject = match.groupdict().get('subject') or match.groupdict().get('owner')
        if subject and GENERIC_SUBJECTS.match(subject.strip()):
            return None

        if canonicalizer:
            memory_text = canonicalizer(match)
        else:
            memory_text = trim_memory_text(sentence)

        if len(memory_text) < 10:
            return None

        return memory_text, importance, category

    return None


def extract_fact_memories(conversation_text):
    memories = []
    for sentence in split_into_sentences(conversation_text):
        normalized = normalize_sentence(sentence)
        if not normalized:
            continue

        candidate = categorize_memory_sentence(normalized)
        if candidate:
            memories.append(candidate)

    return memories


def extract_memory_from_text(
    cursor,
    character,
    conversation_text
):
    found_memories = []

    fact_memories = extract_fact_memories(conversation_text)
    for memory_text, importance, category in fact_memories:
        added = add_memory_candidate(
            cursor,
            character,
            memory_text,
            importance,
            category=category
        )
        if added:
            found_memories.append(memory_text)

    return found_memories

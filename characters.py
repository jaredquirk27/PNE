# =====================
# CHARACTER FUNCTIONS
# =====================

def add_character(
    cursor,
    name,
    trust,
    relationship_status,
    last_interaction_day,
    persona="",
    speaking_style=""
):

    cursor.execute("""
    INSERT OR IGNORE INTO characters
    (
        name,
        trust,
        relationship_status,
        last_interaction_day,
        persona,
        speaking_style
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        name,
        trust,
        relationship_status,
        last_interaction_day,
        persona,
        speaking_style
    ))


def get_character(cursor, name):

    cursor.execute("""
    SELECT *
    FROM characters
    WHERE name = ?
    """,
    (name,))

    return cursor.fetchone()


def get_characters(cursor):

    cursor.execute("""
    SELECT *
    FROM characters
    ORDER BY name
    """)

    return cursor.fetchall()


def show_character(character):

    if not character:
        print("Character not found.")
        return

    print("\n=== Character Sheet ===\n")
    print(f"Name: {character[1]}")
    print(f"Trust: {character[2]}")
    print(f"Relationship: {character[3]}")
    print(f"Last Interaction Day: {character[4]}")

    if len(character) > 5 and character[5]:
        print(f"Persona: {character[5]}")

    if len(character) > 6 and character[6]:
        print(f"Speaking Style: {character[6]}")


def update_relationship_status(
    cursor,
    name
):

    character = get_character(
        cursor,
        name
    )

    trust = character[2]

    if trust <= 10:
        relationship = "Enemy"

    elif trust <= 25:
        relationship = "Rival"

    elif trust <= 50:
        relationship = "Acquaintance"

    elif trust <= 70:
        relationship = "Friend"

    elif trust <= 80:
        relationship = "Close Friend"

    elif trust <= 90:
        relationship = "Trusted Ally"

    else:
        relationship = "Soulmate"

    cursor.execute("""
    UPDATE characters
    SET relationship_status = ?
    WHERE name = ?
    """,
    (
        relationship,
        name
    ))


def update_trust(
    cursor,
    name,
    amount
):

    character = get_character(
        cursor,
        name
    )

    if not character:
        print(f"Character '{name}' not found.")
        return

    trust = character[2]

    new_trust = trust + amount

    if new_trust < 0:
        new_trust = 0

    elif new_trust > 100:
        new_trust = 100

    cursor.execute("""
    UPDATE characters
    SET trust = ?
    WHERE name = ?
    """,
    (
        new_trust,
        name
    ))

    update_relationship_status(
        cursor,
        name
    )


def update_last_interaction_day(
    cursor,
    name,
    day
):

    cursor.execute("""
    UPDATE characters
    SET last_interaction_day = ?
    WHERE name = ?
    """,
    (
        day,
        name
    ))


def create_character(
    cursor,
    get_current_day
):

    name = input(
        "Character Name: "
    )

    persona = input(
        "Persona (optional): "
    )

    speaking_style = input(
        "Speaking Style (optional): "
    )

    add_character(
        cursor,
        name,
        50,
        "Acquaintance",
        get_current_day(cursor),
        persona,
        speaking_style
    )

    print(f"{name} created!")

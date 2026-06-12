def initialize_initiative_settings(
    cursor,
    character_name
):

    cursor.execute("""
    INSERT OR IGNORE INTO initiative_settings
    (
        character_name,
        messages_since_last,
        generation_threshold
    )
    VALUES (?, ?, ?)
    """,
    (
        character_name,
        0,
        15
    ))


def increment_message_counter(
    cursor,
    character_name
):

    initialize_initiative_settings(
        cursor,
        character_name
    )

    cursor.execute("""
    UPDATE initiative_settings
    SET messages_since_last =
        messages_since_last + 1
    WHERE character_name = ?
    """,
    (character_name,))


def should_generate_initiative(
    cursor,
    character_name
):

    initialize_initiative_settings(
        cursor,
        character_name
    )

    cursor.execute("""
    SELECT
        messages_since_last,
        generation_threshold
    FROM initiative_settings
    WHERE character_name = ?
    """,
    (character_name,))

    row = cursor.fetchone()

    if not row:
        return False

    return row[0] >= row[1]


def reset_message_counter(
    cursor,
    character_name
):

    cursor.execute("""
    UPDATE initiative_settings
    SET messages_since_last = 0
    WHERE character_name = ?
    """,
    (character_name,))
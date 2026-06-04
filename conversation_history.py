def save_message(cursor, character_name, speaker, message, day=1):

    cursor.execute("""
        INSERT INTO conversation_history
        (character_name, speaker, message, day)
        VALUES (?, ?, ?, ?)
    """, (
        character_name,
        speaker,
        message,
        day
    ))

def get_conversation(cursor, character_name, limit=50):

    cursor.execute("""
        SELECT speaker, message, day
        FROM conversation_history
        WHERE character_name = ?
        ORDER BY id DESC
        LIMIT ?
    """, (character_name, limit))

    return cursor.fetchall()

def get_recent_conversation(cursor, character, limit=11):

    cursor.execute("""
        SELECT speaker, message
        FROM conversation_history
        WHERE character_name = ?
        ORDER BY id DESC
        LIMIT ?
    """, (character, limit))

    rows = cursor.fetchall()

    return list(reversed(rows))

# ==========================
# FLAG FUNCTIONS
# ==========================

def set_flag(cursor, flag_name, flag_value):

    cursor.execute("""
    INSERT OR REPLACE INTO story_flags
    (flag_name, flag_value)
    VALUES (?, ?)
    """,
    (flag_name, flag_value))


def get_flag(cursor, flag_name):

    cursor.execute("""
    SELECT flag_value
    FROM story_flags
    WHERE flag_name = ?
    """,
    (flag_name,))

    result = cursor.fetchone()

    if result:
        return result[0]

    return None


def get_all_flags(cursor):

    cursor.execute("""
    SELECT *
    FROM story_flags
    ORDER BY flag_name
    """)

    return cursor.fetchall()


def show_flags(flags):

    if not flags:
        print("No flags found.")
        return

    print("\n=== Story Flags ===\n")

    for flag in flags:
        print(f"{flag[0]} = {flag[1]}")
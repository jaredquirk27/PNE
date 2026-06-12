from story_state import set_story_state


# ==========================
# CREATE INITIATIVE
# ==========================

def add_initiative(
    cursor,
    character_name,
    title,
    description,
    target_location,
    target_scene,
    created_day
):

    cursor.execute("""
    INSERT INTO character_initiatives
    (
        character_name,
        title,
        description,
        target_location,
        target_scene,
        status,
        created_day,
        completed_day
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        character_name,
        title,
        description,
        target_location,
        target_scene,
        "Active",
        created_day,
        None
    ))


# ==========================
# GET INITIATIVES
# ==========================

def get_initiatives(cursor):

    cursor.execute("""
    SELECT *
    FROM character_initiatives
    ORDER BY id DESC
    """)

    return cursor.fetchall()


def get_active_initiatives(cursor):

    cursor.execute("""
    SELECT *
    FROM character_initiatives
    WHERE status = 'Active'
    ORDER BY id DESC
    """)

    return cursor.fetchall()


# ==========================
# DISPLAY
# ==========================

def show_initiatives(initiatives):

    if not initiatives:

        print("No initiatives found.")
        return

    print("\n=== Character Initiatives ===\n")

    for initiative in initiatives:

        print(f"ID: {initiative[0]}")
        print(f"Character: {initiative[1]}")
        print(f"Title: {initiative[2]}")
        print(f"Description: {initiative[3]}")
        print(f"Location: {initiative[4]}")
        print(f"Scene: {initiative[5]}")
        print(f"Status: {initiative[6]}")
        print("-------------------")


# ==========================
# COMPLETE
# ==========================

def complete_initiative(
    cursor,
    initiative_id,
    current_day
):

    cursor.execute("""
    SELECT *
    FROM character_initiatives
    WHERE id = ?
    """,
    (initiative_id,))

    initiative = cursor.fetchone()

    if not initiative:

        print("Initiative not found.")
        return

    cursor.execute("""
    UPDATE character_initiatives
    SET status = ?,
        completed_day = ?
    WHERE id = ?
    """,
    (
        "Completed",
        current_day,
        initiative_id
    ))

    set_story_state(
        cursor,
        initiative[1],
        initiative[4],
        initiative[5],
        "Character Initiative",
        initiative[2]
    )

    print("Initiative completed.")
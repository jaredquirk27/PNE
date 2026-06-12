# story_state.py

def set_story_state(
    cursor,
    character_name,
    location,
    scene,
    story_arc,
    quest
):

    cursor.execute("""
    INSERT OR REPLACE INTO story_state (
        character_name,
        current_location,
        current_scene,
        current_story_arc,
        current_quest
    )
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        character_name,
        location,
        scene,
        story_arc,
        quest
    ))


def get_story_state(
    cursor,
    character_name
):

    cursor.execute("""
    SELECT
        current_location,
        current_scene,
        current_story_arc,
        current_quest
    FROM story_state
    WHERE character_name = ?
    """,
    (character_name,))

    return cursor.fetchone()
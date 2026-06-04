from flags import get_flag


# ============================
# CHARACTER GOALS
# ============================

def add_goal(
    cursor,
    character_name,
    goal_name,
    required_flag
):

    cursor.execute("""
    INSERT INTO character_goals
    (
        character_name,
        goal_name,
        required_flag,
        status
    )
    VALUES (?, ?, ?, ?)
    """,
    (
        character_name,
        goal_name,
        required_flag,
        "Active"
    ))


def get_goals(cursor):

    cursor.execute("""
    SELECT *
    FROM character_goals
    """)

    return cursor.fetchall()


def get_active_goals(
    cursor,
    character
):

    cursor.execute("""
    SELECT *
    FROM character_goals
    WHERE character_name = ?
    AND status = 'Active'
    """,
    (character,))

    return cursor.fetchall()


def show_goals(goals):

    if not goals:
        print("No goals found.")
        return

    print("\n=== Character Goals ===\n")

    for goal in goals:

        print(f"Character: {goal[1]}")
        print(f"Goal: {goal[2]}")
        print(f"Status: {goal[4]}")
        print("-------------------")


def check_goal_completion(cursor):

    goals = get_goals(cursor)

    for goal in goals:

        flag_value = get_flag(
            cursor,
            goal[3]
        )

        if flag_value == "True":

            cursor.execute("""
            UPDATE character_goals
            SET status = ?
            WHERE id = ?
            """,
            (
                "Completed",
                goal[0]
            ))


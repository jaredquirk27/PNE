from flags import (
    get_flag,
    set_flag
)


# ==========================
# QUEST FUNCTIONS
# ==========================

def add_quest(
    cursor,
    quest_name,
    required_flag,
    reward,
    reward_flag,
    unlock_flag=None
):

    cursor.execute("""
    INSERT INTO quests
    (
        quest_name,
        status,
        required_flag,
        reward,
        reward_flag,
        unlock_flag
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        quest_name,
        "Active",
        required_flag,
        reward,
        reward_flag,
        unlock_flag
    ))


def get_quests(cursor):

    cursor.execute("""
    SELECT *
    FROM quests
    """)

    return cursor.fetchall()


def get_active_quests(cursor):

    cursor.execute("""
    SELECT *
    FROM quests
    WHERE status = 'Active'
    """)

    return cursor.fetchall()


def show_quests(
    cursor,
    quests
):

    if not quests:
        print("No quests found.")
        return

    print("\n=== Quests ===\n")

    for quest in quests:

        unlock_flag = quest[6]

        if unlock_flag:

            if get_flag(
                cursor,
                unlock_flag
            ) != "True":
                continue

        print(f"Quest: {quest[1]}")
        print(f"Status: {quest[2]}")

        objectives = get_objectives(
            cursor,
            quest[0]
        )

        print("\nObjectives:")

        for objective in objectives:

            marker = (
                "✓"
                if objective[4]
                else "□"
            )

            print(
                f"{marker} {objective[2]}"
            )

        print(f"\nReward: {quest[4]}")
        print("-------------------")


def update_objectives(cursor):

    cursor.execute("""
    SELECT *
    FROM quest_objectives
    """)

    objectives = cursor.fetchall()

    for objective in objectives:

        flag_value = get_flag(
            cursor,
            objective[3]
        )

        if flag_value == "True":

            cursor.execute("""
            UPDATE quest_objectives
            SET completed = 1
            WHERE id = ?
            """,
            (objective[0],))


def check_quest_completion(cursor):

    update_objectives(cursor)

    quests = get_quests(cursor)

    for quest in quests:

        objectives = get_objectives(
            cursor,
            quest[0]
        )

        if objectives and all(
            objective[4] == 1
            for objective in objectives
        ):

            cursor.execute("""
            UPDATE quests
            SET status = ?
            WHERE id = ?
            """,
            (
                "Completed",
                quest[0]
            ))

            reward_flag = quest[5]

            if reward_flag:

                set_flag(
                    cursor,
                    reward_flag,
                    "True"
                )


# ==============================
# QUEST OBJECTIVES
# ==============================

def add_objective(
    cursor,
    quest_id,
    objective_name,
    objective_flag
):

    cursor.execute("""
    INSERT INTO quest_objectives
    (
        quest_id,
        objective_name,
        objective_flag
    )
    VALUES (?, ?, ?)
    """,
    (
        quest_id,
        objective_name,
        objective_flag
    ))


def get_objectives(
    cursor,
    quest_id
):

    cursor.execute("""
    SELECT *
    FROM quest_objectives
    WHERE quest_id = ?
    """,
    (quest_id,))

    return cursor.fetchall()


def show_quest_ids(cursor):

    quests = get_quests(cursor)

    print("\n=== Quest IDs ===\n")

    for quest in quests:

        print(
            f"ID {quest[0]} - {quest[1]}"
        )


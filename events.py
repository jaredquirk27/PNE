from constants import EVENT_CATALOG

# These will be imported later
from characters import (
    get_character,
    update_trust
)

from flags import (
    set_flag
)


# =======================
# EVENT FUNCTIONS
# =======================

def add_event(
    cursor,
    day,
    event_type,
    character,
    description,
    importance
):

    cursor.execute("""
    INSERT INTO events
    (
        day,
        event_type,
        character_name,
        description,
        importance
    )
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        day,
        event_type,
        character,
        description,
        importance
    ))

    process_event_effects(
        cursor,
        event_type,
        character
    )


def get_events(cursor):

    cursor.execute("""
    SELECT *
    FROM events
    """)

    return cursor.fetchall()


def get_relevant_events(
    cursor,
    min_importance
):

    cursor.execute("""
    SELECT *
    FROM events
    WHERE importance >= ?
    ORDER BY day DESC
    """,
    (min_importance,))

    return cursor.fetchall()


def show_events(events):

    if not events:
        print("No events found.")
        return

    print("\n=== Event Timeline ===\n")

    for row in events:

        print(f"Day {row[1]}")
        print(f"Character: {row[3]}")
        print(f"Event: {row[2]}")
        print(f"Description: {row[4]}")
        print(f"Importance: {row[5]}")
        print("-------------------")


# =======================
# EVENT EFFECTS
# =======================

def process_event_effects(
    cursor,
    event_type,
    character
):

    for event in EVENT_CATALOG.values():

        if event["name"] == event_type:

            update_trust(
                cursor,
                character,
                event["trust_change"]
            )

            break

    set_flag(
        cursor,
        make_flag_name(
            character,
            event_type
        ),
        "True"
    )


def make_flag_name(
    character,
    event_type
):

    return f"{character}_{event_type}"


# =======================
# EVENT CREATION UI
# =======================

def choose_event_type():

    print("\nSelect Event Type:")

    for event_id, event_data in EVENT_CATALOG.items():

        print(
            f"{event_id}. "
            f"{event_data['display']}"
        )

    while True:

        choice = int(
            input("Choice: ")
        )

        if choice in EVENT_CATALOG:
            return EVENT_CATALOG[choice]

        print("Invalid choice.")


def create_event(
    cursor,
    get_current_day,
    check_quest_completion,
    check_goal_completion
):

    day = get_current_day(cursor)

    character = input(
        "Character: "
    )

    if not get_character(
        cursor,
        character
    ):
        print("Character not found.")
        return

    selected_event = choose_event_type()

    event_type = selected_event["name"]
    importance = selected_event["importance"]

    description = input(
        "Description: "
    )

    add_event(
        cursor,
        day,
        event_type,
        character,
        description,
        importance
    )

    check_quest_completion(
        cursor
    )

    check_goal_completion(
        cursor
    )

    print("\nEvent Added!")
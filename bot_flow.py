from characters import (
    add_character,
    get_character,
    get_characters,
    show_character
)
from chat import chat_with_character
from memory_extraction import (
    accept_memory_candidate,
    get_memory_candidates,
    show_memory_candidates
)


def choose_or_create_character(
    cursor,
    get_current_day
):

    characters = get_characters(cursor)

    if characters:

        print("\n=== Characters ===\n")

        for index, character in enumerate(characters, start=1):
            print(f"{index}. {character[1]}")

        print("N. Create new character")

        choice = input("\nSelect Character: ").strip()

        if choice.lower() != "n":

            try:
                selected_index = int(choice) - 1
            except ValueError:
                print("Invalid selection.")
                return None

            if 0 <= selected_index < len(characters):
                return characters[selected_index][1]

            print("Invalid selection.")
            return None

    name = input("New Character Name: ").strip()

    if not name:
        print("Character name is required.")
        return None

    existing_character = get_character(
        cursor,
        name
    )

    if existing_character:
        return name

    persona = input("Persona (optional): ").strip()

    speaking_style = input("Speaking Style (optional): ").strip()

    add_character(
        cursor,
        name,
        50,
        "Acquaintance",
        get_current_day(cursor),
        persona,
        speaking_style
    )

    print(f"{name} created.")

    return name


def get_character_memory_candidates(
    cursor,
    character
):

    return [
        candidate
        for candidate in get_memory_candidates(cursor)
        if candidate[1] == character
    ]


def review_character_memory_candidates(
    conn,
    cursor,
    character,
    get_current_day,
    add_event
):

    candidates = get_character_memory_candidates(
        cursor,
        character
    )

    if not candidates:
        print("\nNo pending memory candidates.")
        return

    show_memory_candidates(candidates)

    choice = input(
        "\nAccept memory IDs separated by commas, or press Enter to skip: "
    ).strip()

    if not choice:
        return

    candidate_ids = {
        candidate[0]
        for candidate in candidates
    }

    for raw_memory_id in choice.split(","):

        raw_memory_id = raw_memory_id.strip()

        if not raw_memory_id:
            continue

        try:
            memory_id = int(raw_memory_id)
        except ValueError:
            print(f"Skipping invalid memory ID: {raw_memory_id}")
            continue

        if memory_id not in candidate_ids:
            print(f"Skipping memory ID for another character: {memory_id}")
            continue

        accept_memory_candidate(
            cursor,
            memory_id,
            get_current_day,
            add_event
        )

    conn.commit()

    print("Selected memories accepted.")


def start_character_bot(
    conn,
    cursor,
    build_ai_prompt,
    get_current_day,
    add_event
):

    character = choose_or_create_character(
        cursor,
        get_current_day
    )

    if not character:
        return

    conn.commit()

    print("\n=== Character Bot ===")

    show_character(
        get_character(
            cursor,
            character
        )
    )

    while True:

        print("\n1. Chat")
        print("2. Review Memory Candidates")
        print("0. Back")

        choice = input("\nSelect Option: ").strip()

        if choice == "1":

            chat_with_character(
                conn,
                cursor,
                character,
                build_ai_prompt,
                get_current_day
            )

        elif choice == "2":

            review_character_memory_candidates(
                conn,
                cursor,
                character,
                get_current_day,
                add_event
            )

        elif choice == "0":
            break

        else:
            print("Invalid option.")

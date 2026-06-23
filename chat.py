from conversation_history import save_message
from characters import update_last_interaction_day
from events import add_event
from llm_provider import generate_response
from memory_extraction import extract_memory_from_text, auto_canonize_memories
from initiative_scheduler import *
from initiative_generator import generate_and_save_initiative

def persist_chat_exchange(
    cursor,
    character,
    user_message,
    response,
    current_day=1,
    auto_canonize=True
):

    save_message(
        cursor,
        character,
        "User",
        user_message,
        current_day
    )

    save_message(
        cursor,
        character,
        character,
        response,
        current_day
    )

    update_last_interaction_day(
        cursor,
        character,
        current_day
    )

    exchange_text = (
        f"User: {user_message}\n"
        f"{character}: {response}"
    )

    candidate_memories = extract_memory_from_text(
        cursor,
        character,
        exchange_text
    )

    if auto_canonize:
        auto_canonize_memories(
            cursor,
            current_day,
            add_event
        )

    return candidate_memories


def chat_with_character(
    conn,
    cursor,
    character,
    build_ai_prompt,
    get_current_day=None
):

    print(f"\nChatting with {character}")
    print("Type 'exit' to leave.")

    while True:

        user_message = input("\nYou: ")

        if user_message.lower() == "exit":
            break

        current_day = 1

        if get_current_day:
            current_day = get_current_day(cursor)

        prompt = build_ai_prompt(
            cursor,
            character,
            user_message
        )

        response = generate_response(
            prompt
        )

        print(f"\n{character}: {response}")

        found_memories = persist_chat_exchange(
            cursor,
            character,
            user_message,
            response,
            current_day
        )

        conn.commit()

        increment_message_counter(
            cursor,
            character
        )

        if should_generate_initiative(
            cursor,
            character
        ):

            initiative = (
                generate_and_save_initiative(
                    cursor,
                    character,
                    current_day
                )
            )

            reset_message_counter(
                cursor,
                character
            )

            conn.commit()

            print(
                "\n===================="
            )

            print(
                "RUE HAS A NEW IDEA"
            )

            print(
                "===================="
            )

            print(
                f"Title: {initiative['title']}"
            )

            print(
                f"Description: "
                f"{initiative['description']}"
            )

            print(
                f"Location: "
                f"{initiative['location']}"
            )

            print(
                f"Scene: "
                f"{initiative['scene']}"
            )

        if found_memories:

            print("\nMemory candidates found:")

            for memory in found_memories:
                print(f"- {memory}")

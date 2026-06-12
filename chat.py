from conversation_history import save_message
from characters import update_last_interaction_day
from llm_provider import generate_response
from memory_extraction import extract_memory_from_text


def persist_chat_exchange(
    cursor,
    character,
    user_message,
    response,
    current_day=1
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

    return extract_memory_from_text(
        cursor,
        character,
        exchange_text
    )


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

        if found_memories:

            print("\nMemory candidates found:")

            for memory in found_memories:
                print(f"- {memory}")

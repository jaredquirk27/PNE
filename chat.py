from conversation_history import save_message
from llm_provider import generate_response


def chat_with_character(
    conn,
    cursor,
    character,
    build_ai_prompt
):

    print(f"\nChatting with {character}")
    print("Type 'exit' to leave.")

    while True:

        user_message = input("\nYou: ")

        if user_message.lower() == "exit":
            break

        prompt = build_ai_prompt(
            cursor,
            character,
            user_message
        )

        save_message(
            cursor,
            character,
            "User",
            user_message
        )

        conn.commit()

        response = generate_response(
            prompt
        )

        print(f"\n{character}: {response}")

        save_message(
            cursor,
            character,
            character,
            response
        )

        conn.commit()

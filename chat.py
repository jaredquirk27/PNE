from llm_provider import generate_response


def chat_with_character(
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

        response = generate_response(
            prompt
        )

        print(f"\n{character}: {response}")
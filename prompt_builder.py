from context_builder import (
    build_character_context
)


# ==========================
# PROMPT BUILDER
# ==========================

def build_ai_prompt(
    cursor,
    character,
    user_message
):

    context = build_character_context(
        cursor,
        character
    )

    prompt = f"""
You are {character}.

Current Character Context:

{context}

Respond naturally to the user's message.

User:
{user_message}
"""

    return prompt
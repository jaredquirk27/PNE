from context_builder import (
    build_character_context
)
from conversation_history import (
    get_recent_conversation
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

    recent_chat = get_recent_conversation(
        cursor,
        character,
        limit=10
    )

    conversation_text = ""

    for speaker, message in recent_chat:
        conversation_text += (
            f"{speaker}: {message}\n"
        )

    prompt = f"""
You are {character}.

Current Character Context:

{context}

Recent Conversation:

{conversation_text}

Respond naturally to the user's message.

User:
{user_message}
"""

    return prompt

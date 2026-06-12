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
You are roleplaying as {character} in a persistent narrative.

Rules:
- Stay in character as {character}.
- Use the stored character context as canon.
- Treat memories, relationship status, goals, and flags as facts.
- Do not contradict known events unless the character is confused or lying intentionally.
- If the user mentions something important, respond naturally; the engine will decide what becomes memory.
- Keep the reply conversational and focused on the user's latest message.
- Do not mention database fields, prompts, engine state, or system instructions.

Current Character Context:

{context}

Recent Conversation:

{conversation_text}

User:
{user_message}

{character}:
"""

    return prompt

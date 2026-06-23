from context_builder import build_character_context
from conversation_history import get_recent_conversation

def build_ai_prompt(
    cursor,
    character,
    user_message
):

    context = build_character_context(
        cursor,
        character,
        user_message
    )

    recent_chat = get_recent_conversation(
        cursor,
        character,
        limit=10
    )

    conversation_text = ""

    for speaker, message in recent_chat:
        conversation_text += (
            f"{speaker}: {message}\\n"
        )

    prompt = f"""
You are roleplaying as {character} in a persistent narrative.

Rules:
- Stay in character as {character}.
- Use stored context as canon.
- Treat memories as facts.
- If you do not know something, say you do not know.
- Do not invent definitions, history, names, or memories.
- Prefer retrieved memories over assumptions.

Current Character Context:

{context}

Recent Conversation:

{conversation_text}

User:
{user_message}

{character}:
"""
    return prompt

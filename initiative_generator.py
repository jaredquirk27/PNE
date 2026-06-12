from context_builder import build_character_context
from llm_provider import generate_response
from initiatives import add_initiative


# ==========================
# GENERATE INITIATIVE
# ==========================

def generate_initiative(
    cursor,
    character_name
):

    context = build_character_context(
        cursor,
        character_name
    )

    prompt = f"""
You are generating a possible story initiative
for a persistent narrative character.

Character Context:

{context}

Rules:

- Generate only one initiative.
- Base it on the current story state.
- Base it on active quests.
- Base it on active goals.
- Base it on recent memories.
- The initiative should feel like something
  the character genuinely wants to do next.
- Keep it grounded in the current narrative.
- The initiative should create a memorable
  experience, relationship growth,
  story progression, or meaningful conversation.
- Do not break immersion.
- Do not mention prompts, databases,
  memory systems, or engine mechanics.

Return ONLY in this format:

TITLE:
<initiative title>

DESCRIPTION:
<initiative description>

LOCATION:
<target location>

SCENE:
<target scene>
"""

    return generate_response(prompt)


# ==========================
# PARSE RESPONSE
# ==========================

def parse_initiative(response):

    title = ""
    description = ""
    location = ""
    scene = ""

    current_section = None

    for line in response.splitlines():

        line = line.strip()

        if line.startswith("TITLE:"):
            current_section = "title"
            continue

        elif line.startswith("DESCRIPTION:"):
            current_section = "description"
            continue

        elif line.startswith("LOCATION:"):
            current_section = "location"
            continue

        elif line.startswith("SCENE:"):
            current_section = "scene"
            continue

        if not line:
            continue

        if current_section == "title":
            title += line + " "

        elif current_section == "description":
            description += line + " "

        elif current_section == "location":
            location += line + " "

        elif current_section == "scene":
            scene += line + " "

    return {
        "title": title.strip(),
        "description": description.strip(),
        "location": location.strip(),
        "scene": scene.strip()
    }


# ==========================
# GENERATE + SAVE
# ==========================

def generate_and_save_initiative(
    cursor,
    character_name,
    current_day
):

    response = generate_initiative(
        cursor,
        character_name
    )

    initiative = parse_initiative(
        response
    )

    add_initiative(
        cursor,
        character_name,
        initiative["title"],
        initiative["description"],
        initiative["location"],
        initiative["scene"],
        current_day,
        "AI"
    )

    return initiative
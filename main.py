import sys
print(sys.executable)

from database import initialize_database
from constants import EVENT_CATALOG

from characters import *
from events import *
from flags import *
from quests import *
from goals import *
from memories import *
from memory_extraction import *
from context_builder import *
from prompt_builder import *
from chat import chat_with_character
from llm_provider import *



# ========================
# TIME FUNCTIONS
# ========================

def get_current_day(cursor):

    cursor.execute("""
    SELECT current_day
    FROM world_state
    WHERE id = 1
    """)

    result = cursor.fetchone()

    return result[0]


def advance_day(
    cursor,
    days
):

    cursor.execute("""
    UPDATE world_state
    SET current_day = current_day + ?
    WHERE id = 1
    """,
    (days,))


def show_events_with_age(cursor):

    current_day = get_current_day(
        cursor
    )

    events = get_events(
        cursor
    )

    print("\n=== Event Timeline ===\n")

    for row in events:

        event_day = row[1]

        days_ago = (
            current_day -
            event_day
        )

        print(f"Day {event_day}")
        print(f"Character: {row[3]}")
        print(f"Description: {row[4]}")
        print(f"{days_ago} days ago")
        print("-------------------")


# ========================
# MAIN MENU
# ========================

def main_menu():

    print("\n=== Persistent Narrative Engine ===")

    print("1. Create Event")
    print("2. Show Events")
    print("3. Show Character")
    print("4. Advance Day")
    print("5. Show Current Day")
    print("6. Create Character")
    print("7. Show Character Memories")
    print("8. Show Top Memories")
    print("9. Set Story Flag")
    print("10. Show Story Flags")
    print("11. Create Quest")
    print("12. Show Quests")
    print("13. Add Quest Objective")
    print("14. Show Quest IDs")
    print("15. Create Character Goal")
    print("16. Show Character Goals")
    print("17. Show Character Context")
    print("18. Build AI Prompt")
    print("19. Show Memory Candidates")
    print("20. Accept Memory Candidate")
    print("21. Extract Memory From Conversation")
    print("22. Chat with Character")
    print("0. Exit")

    return input(
        "\nSelect Option: "
    )


# ========================
# DATABASE SETUP
# ========================

conn, cursor = initialize_database()


# ========================
# OPTIONAL TEST DATA
# ========================

# Uncomment if needed

# add_character(
#     cursor,
#     "Tali",
#     50,
#     "Friend",
#     get_current_day(cursor)
# )

# add_memory_candidate(
#     cursor,
#     "Tali",
#     "User promised to help clear her father's name.",
#     9
# )

conn.commit()


# ========================
# MAIN LOOP
# ========================

running = True

while running:

    choice = main_menu()

    # ====================
    # EVENTS
    # ====================

    if choice == "1":

        create_event(
            cursor,
            get_current_day,
            check_quest_completion,
            check_goal_completion
        )

        conn.commit()

    elif choice == "2":

        events = get_events(
            cursor
        )

        show_events(
            events
        )

    # ====================
    # CHARACTERS
    # ====================

    elif choice == "3":

        name = input(
            "Character Name: "
        )

        character = get_character(
            cursor,
            name
        )

        show_character(
            character
        )

    elif choice == "4":

        days = int(
            input(
                "Advance how many days? "
            )
        )

        advance_day(
            cursor,
            days
        )

        conn.commit()

        print("Day advanced!")

    elif choice == "5":

        print(
            f"Current Day: "
            f"{get_current_day(cursor)}"
        )

    elif choice == "6":

        create_character(
            cursor,
            get_current_day
        )

        conn.commit()

    # ====================
    # MEMORIES
    # ====================

    elif choice == "7":

        name = input(
            "Character Name: "
        )

        min_importance = int(
            input(
                "Minimum Importance (1-10): "
            )
        )

        memories = (
            get_character_memories(
                cursor,
                name,
                min_importance
            )
        )

        show_character_memories(
            memories
        )

    elif choice == "8":

        name = input(
            "Character Name: "
        )

        memories = get_top_memories(
            cursor,
            name
        )

        print(
            "\n=== Top Memories ==="
        )

        show_character_memories(
            memories
        )

    # ====================
    # FLAGS
    # ====================

    elif choice == "9":

        flag_name = input(
            "Flag Name: "
        )

        flag_value = input(
            "Flag Value: "
        )

        set_flag(
            cursor,
            flag_name,
            flag_value
        )

        conn.commit()

        print("Flag saved!")

    elif choice == "10":

        flags = get_all_flags(
            cursor
        )

        show_flags(
            flags
        )

    # ====================
    # QUESTS
    # ====================

    elif choice == "11":

        quest_name = input(
            "Quest Name: "
        )

        required_flag = input(
            "Required Flag: "
        )

        reward = input(
            "Reward: "
        )

        reward_flag = input(
            "Reward Flag (optional): "
        )

        unlock_flag = input(
            "Unlock Flag (optional): "
        )

        add_quest(
            cursor,
            quest_name,
            required_flag,
            reward,
            reward_flag,
            unlock_flag
        )

        conn.commit()

        print("Quest Created!")

    elif choice == "12":

        quests = get_quests(
            cursor
        )

        show_quests(
            cursor,
            quests
        )

    elif choice == "13":

        quest_id = int(
            input("Quest ID: ")
        )

        objective_name = input(
            "Objective Name: "
        )

        objective_flag = input(
            "Objective Flag: "
        )

        add_objective(
            cursor,
            quest_id,
            objective_name,
            objective_flag
        )

        conn.commit()

    elif choice == "14":

        show_quest_ids(
            cursor
        )

    # ====================
    # GOALS
    # ====================

    elif choice == "15":

        character_name = input(
            "Character Name: "
        )

        goal_name = input(
            "Goal Name: "
        )

        required_flag = input(
            "Required Flag: "
        )

        add_goal(
            cursor,
            character_name,
            goal_name,
            required_flag
        )

        conn.commit()

        print("Goal Created!")

    elif choice == "16":

        goals = get_goals(
            cursor
        )

        show_goals(
            goals
        )

    # ====================
    # CONTEXT
    # ====================

    elif choice == "17":

        name = input(
            "Character Name: "
        )

        context = (
            build_character_context(
                cursor,
                name
            )
        )

        print("\n")
        print(context)

    elif choice == "18":

        character = input(
            "Character Name: "
        )

        user_message = input(
            "User Message: "
        )

        prompt = (
            build_ai_prompt(
                cursor,
                character,
                user_message
            )
        )

        print(
            "\n=== AI PROMPT ===\n"
        )

        print(prompt)

    # ====================
    # MEMORY EXTRACTION
    # ====================

    elif choice == "19":

        candidates = (
            get_memory_candidates(
                cursor
            )
        )

        show_memory_candidates(
            candidates
        )

    elif choice == "20":

        memory_id = int(
            input(
                "Memory ID: "
            )
        )

        accept_memory_candidate(
            cursor,
            memory_id,
            get_current_day,
            add_event
        )

        conn.commit()

    elif choice == "21":

        character = input(
            "Character Name: "
        )

        print(
            "\nPaste conversation:"
        )

        conversation = input("> ")

        memories = (
            extract_memory_from_text(
                cursor,
                character,
                conversation
            )
        )

        conn.commit()

        if memories:

            print(
                "\nMemory Candidates Found:"
            )

            for memory in memories:
                print(
                    f"- {memory}"
                )
    elif choice == "22":

        character = input(
            "Character Name: "
       )

        chat_with_character(
            cursor,
            character,
            build_ai_prompt
        )

    # ====================
    # EXIT
    # ====================

    elif choice == "0":

        running = False


conn.close()
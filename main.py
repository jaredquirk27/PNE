from database import initialize_database
from story_state import set_story_state
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
from bot_flow import start_character_bot
from llm_provider import *
from story_state import set_story_state, get_story_state


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

    print("1. Start Character Bot")
    print("\n--- Engine Tools ---")
    print("2. Create Event")
    print("3. Show Events")
    print("4. Show Character")
    print("5. Advance Day")
    print("6. Show Current Day")
    print("7. Create Character")
    print("8. Show Character Memories")
    print("9. Show Top Memories")
    print("10. Set Story Flag")
    print("11. Show Story Flags")
    print("12. Create Quest")
    print("13. Show Quests")
    print("14. Add Quest Objective")
    print("15. Show Quest IDs")
    print("16. Create Character Goal")
    print("17. Show Character Goals")
    print("18. Show Character Context")
    print("19. Build AI Prompt")
    print("20. Show Memory Candidates")
    print("21. Accept Memory Candidate")
    print("22. Extract Memory From Conversation")
    print("23. Chat with Character")
    print("24. Set Story State")
    print("25. Show Story State")
    print("0. Exit")

    return input(
        "\nSelect Option: "
    )


# ========================
# MAIN LOOP
# ========================

def main():

    conn, cursor = initialize_database()

    set_story_state(
        cursor,
        "Baras",
        "Korriban Academy",
        "Meeting the new acolyte",
        "Sith Warrior Act 1",
        "Evaluate the Warrior"
    )

    conn.commit()

    running = True

    while running:

        choice = main_menu()

        # ====================
        # EVENTS
        # ====================

        if choice == "1":

            start_character_bot(
                conn,
                cursor,
                build_ai_prompt,
                get_current_day,
                add_event
            )

        elif choice == "2":

            create_event(
                cursor,
                get_current_day,
                check_quest_completion,
                check_goal_completion
            )

            conn.commit()

        elif choice == "3":

            events = get_events(
                cursor
            )

            show_events(
                events
            )

        # ====================
        # CHARACTERS
        # ====================

        elif choice == "4":

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

        elif choice == "5":

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

        elif choice == "6":

            print(
                f"Current Day: "
                f"{get_current_day(cursor)}"
            )

        elif choice == "7":

            create_character(
                cursor,
                get_current_day
            )

            conn.commit()

        # ====================
        # MEMORIES
        # ====================

        elif choice == "8":

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

        elif choice == "9":

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

        elif choice == "10":

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

        elif choice == "11":

            flags = get_all_flags(
                cursor
            )

            show_flags(
                flags
            )

        # ====================
        # QUESTS
        # ====================

        elif choice == "12":

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

        elif choice == "13":

            quests = get_quests(
                cursor
            )

            show_quests(
                cursor,
                quests
            )

        elif choice == "14":

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

        elif choice == "15":

            show_quest_ids(
                cursor
            )

        # ====================
        # GOALS
        # ====================

        elif choice == "16":

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

        elif choice == "17":

            goals = get_goals(
                cursor
            )

            show_goals(
                goals
            )

        # ====================
        # CONTEXT
        # ====================

        elif choice == "18":

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

        elif choice == "19":

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

        elif choice == "20":

            candidates = (
                get_memory_candidates(
                    cursor
                )
            )

            show_memory_candidates(
                candidates
            )

        elif choice == "21":

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

        elif choice == "22":

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

        elif choice == "23":

            character = input(
                "Character Name: "
           )

            chat_with_character(
                conn,
                cursor,
                character,
                build_ai_prompt,
                get_current_day
            )

        elif choice == "24":

            character = input("Character Name: ")

            location = input("Current Location: ")

            scene = input("Current Scene: ")

            story_arc = input("Current Story Arc: ")

            quest = input("Current Quest: ")

            set_story_state(
                cursor,
                character,
                location,
                scene,
                story_arc,
                quest
            )

            conn.commit()

            print("Story state updated.")

        elif choice == "25":

            character = input("Character Name: ")

            state = get_story_state(
                cursor,
                character
        )

            if state:

                print("\nStory State")
                print(f"Location: {state[0]}")
                print(f"Scene: {state[1]}")
                print(f"Story Arc: {state[2]}")
                print(f"Quest: {state[3]}")

            else:   

                print("No story state found.")

        # ====================
        # EXIT
        # ====================

        elif choice == "0":

            running = False

            conn.close()


if __name__ == "__main__":
    main()

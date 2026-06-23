import sqlite3


DB_NAME = "story_engine.db"


def get_memory_events(cursor):

    cursor.execute("""
    SELECT *
    FROM events
    WHERE event_type = 'memory_extracted'
    ORDER BY importance DESC, id
    """)

    return cursor.fetchall()


def show_memories(memories):

    if not memories:
        print("No memories found.")
        return

    print("\n=== Memories ===\n")

    for memory in memories:

        print(f"ID: {memory[0]}")
        print(f"Day: {memory[1]}")
        print(f"Character: {memory[3]}")
        print(f"Importance: {memory[5]}")
        print(f"Memory: {memory[4]}")
        print("-------------------")


def delete_memory(cursor, memory_id):

    cursor.execute("""
    DELETE FROM events
    WHERE id = ?
    AND event_type = 'memory_extracted'
    """, (memory_id,))

    print("Memory deleted.")


def export_audit(cursor):

    memories = get_memory_events(cursor)

    with open("memory_audit.txt", "w", encoding="utf-8") as f:

        for memory in memories:

            f.write(
                f"ID:{memory[0]}\n"
                f"Importance:{memory[5]}\n"
                f"{memory[4]}\n"
                f"ACTION:[KEEP/DELETE/CONDENSE]\n"
                f"{'-'*40}\n"
            )

    print("Exported memory_audit.txt")


def show_duplicates(cursor):

    cursor.execute("""
    SELECT description,
           COUNT(*)
    FROM events
    WHERE event_type = 'memory_extracted'
    GROUP BY description
    HAVING COUNT(*) > 1
    ORDER BY COUNT(*) DESC
    """)

    duplicates = cursor.fetchall()

    if not duplicates:
        print("No duplicates found.")
        return

    print("\n=== Duplicate Memories ===\n")

    for text, count in duplicates:

        print(f"Count: {count}")
        print(text[:250])
        print("-------------------")


def menu():

    print("\n=== Memory Cleanup Utility ===")
    print("1. Show Memories")
    print("2. Delete Memory")
    print("3. Export Audit")
    print("4. Show Duplicates")
    print("0. Exit")

    return input("Choice: ")


def main():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    running = True

    while running:

        choice = menu()

        if choice == "1":

            show_memories(
                get_memory_events(cursor)
            )

        elif choice == "2":

            memory_id = int(
                input("Memory ID: ")
            )

            delete_memory(
                cursor,
                memory_id
            )

            conn.commit()

        elif choice == "3":

            export_audit(cursor)

        elif choice == "4":

            show_duplicates(cursor)

        elif choice == "0":

            running = False

    conn.close()


if __name__ == "__main__":
    main()

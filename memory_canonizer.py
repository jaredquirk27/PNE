import sqlite3

DB_NAME = 'story_engine.db'


def get_memory_events(cursor):
    cursor.execute("""
    SELECT *
    FROM events
    WHERE event_type = 'memory_extracted'
    ORDER BY importance DESC, id
    """)
    return cursor.fetchall()


def show_memory(memory):
    print('\n-------------------')
    print(f'ID: {memory[0]}')
    print(f'Character: {memory[3]}')
    print(f'Importance: {memory[5]}')
    print(f'Memory: {memory[4]}')
    print('-------------------')


def create_canonical_memory(cursor, original_memory, canonical_text):
    cursor.execute("""
    INSERT INTO events
    (day,event_type,character_name,description,importance)
    VALUES (?, ?, ?, ?, ?)
    """, (
        original_memory[1],
        'memory_extracted',
        original_memory[3],
        canonical_text,
        10
    ))


def archive_memory(cursor, memory_id):
    cursor.execute("""
    UPDATE events
    SET event_type = 'memory_archived'
    WHERE id = ?
    """, (memory_id,))


def canonize_memory(cursor):
    memories = get_memory_events(cursor)

    for memory in memories:
        show_memory(memory)

        action = input('[K]eep [A]rchive [C]anonize [S]kip: ').lower()

        if action == 'a':
            archive_memory(cursor, memory[0])

        elif action == 'c':
            canonical = input('\nCanonical Memory:\n> ').strip()

            if canonical:
                create_canonical_memory(cursor, memory, canonical)
                archive_memory(cursor, memory[0])
                print('Canonical memory created.')


def show_archived(cursor):
    cursor.execute("""
    SELECT *
    FROM events
    WHERE event_type = 'memory_archived'
    ORDER BY id DESC
    """)

    for row in cursor.fetchall():
        print(f'{row[0]} | {row[4][:120]}')


def menu():
    print('\n=== Memory Canonizer ===')
    print('1. Canonize Memories')
    print('2. Show Archived Memories')
    print('0. Exit')
    return input('Choice: ')


def main():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    while True:
        choice = menu()

        if choice == '1':
            canonize_memory(cursor)
            conn.commit()

        elif choice == '2':
            show_archived(cursor)

        elif choice == '0':
            break

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()

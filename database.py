import sqlite3


def add_column_if_missing(cursor, table_name, column_name, column_definition):

    cursor.execute(f"PRAGMA table_info({table_name})")

    existing_columns = {
        row[1]
        for row in cursor.fetchall()
    }

    if column_name in existing_columns:
        return

    cursor.execute(
        f"ALTER TABLE {table_name} "
        f"ADD COLUMN {column_definition}"
    )


def initialize_database():

    conn = sqlite3.connect("story_engine.db")
    cursor = conn.cursor()

    create_tables(cursor)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character_name TEXT NOT NULL,
        speaker TEXT NOT NULL,
        message TEXT NOT NULL,
        day INTEGER DEFAULT 1,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()

    print("Database initialized and tables created (if not exist).")
    
    return conn, cursor


def create_tables(cursor):

    # ==========================
    # EVENTS
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY,
        day INTEGER,
        event_type TEXT,
        character_name TEXT,
        description TEXT,
        importance INTEGER
    )
    """)



    # ==========================
    # WORLD STATE
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS world_state (
        id INTEGER PRIMARY KEY,
        current_day INTEGER
    )
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO world_state
    (id, current_day)
    VALUES (1, 1)
    """)

    # ==========================
    # CHARACTERS
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        trust INTEGER,
        relationship_status TEXT,
        last_interaction_day INTEGER,
        persona TEXT DEFAULT '',
        speaking_style TEXT DEFAULT ''
    )
    """)

    add_column_if_missing(
        cursor,
        "characters",
        "persona",
        "persona TEXT DEFAULT ''"
    )

    add_column_if_missing(
        cursor,
        "characters",
        "speaking_style",
        "speaking_style TEXT DEFAULT ''"
    )

    # ==========================
    # STORY FLAGS
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS story_flags (
        flag_name TEXT PRIMARY KEY,
        flag_value TEXT
    )
    """)

    # ==========================
    # QUESTS
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quests (
        id INTEGER PRIMARY KEY,
        quest_name TEXT,
        status TEXT,
        required_flag TEXT,
        reward TEXT
    )
    """)

    add_column_if_missing(
        cursor,
        "quests",
        "reward_flag",
        "reward_flag TEXT"
    )

    add_column_if_missing(
        cursor,
        "quests",
        "unlock_flag",
        "unlock_flag TEXT"
    )

    # ==========================
    # QUEST OBJECTIVES
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quest_objectives (
        id INTEGER PRIMARY KEY,
        quest_id INTEGER,
        objective_name TEXT,
        objective_flag TEXT,
        completed INTEGER DEFAULT 0
    )
    """)

    # ==========================
    # CHARACTER GOALS
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS character_goals (
        id INTEGER PRIMARY KEY,
        character_name TEXT,
        goal_name TEXT,
        required_flag TEXT,
        status TEXT
    )
    """)

    # ==========================
    # MEMORY CANDIDATES
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memory_candidates (
        id INTEGER PRIMARY KEY,
        character_name TEXT,
        memory_text TEXT,
        importance INTEGER,
        accepted INTEGER DEFAULT 0
    )
    """)

# ==========================
# STORY STATE
# ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS story_state (
        character_name TEXT PRIMARY KEY,
        current_location TEXT,
        current_scene TEXT,
        current_story_arc TEXT,
        current_quest TEXT
    )
    """)
    # ==========================
    # CHARACTER INITIATIVES
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS character_initiatives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character_name TEXT,
        title TEXT,
        description TEXT,
        target_location TEXT,
        target_scene TEXT,
        status TEXT,
        created_day INTEGER,
        completed_day INTEGER,
                   initiative_source TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS initiative_settings (
        character_name TEXT PRIMARY KEY,
        messages_since_last INTEGER DEFAULT 0,
        generation_threshold INTEGER DEFAULT 10
    )
    """)
    try:

        cursor.execute("""
        ALTER TABLE character_initiatives
        ADD COLUMN initiative_source TEXT DEFAULT 'USER'
        """)

    except:

        pass

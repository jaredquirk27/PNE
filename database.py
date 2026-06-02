import sqlite3


def initialize_database():

    conn = sqlite3.connect("story_engine.db")
    cursor = conn.cursor()

    create_tables(cursor)

    conn.commit()

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
        last_interaction_day INTEGER
    )
    """)

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

    try:
        cursor.execute("""
        ALTER TABLE quests
        ADD COLUMN reward_flag TEXT
        """)
    except:
        pass

    try:
        cursor.execute("""
        ALTER TABLE quests
        ADD COLUMN unlock_flag TEXT
        """)
    except:
        pass

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

    print("Database initialized and tables created (if not exist).")
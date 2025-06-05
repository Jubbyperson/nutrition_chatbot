# Create and manage database of users

import sqlite3

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            age INTEGER,
            height REAL,
            weight REAL,
            sex TEXT,
            activity_level TEXT,
            goal TEXT
        )
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT DEFAULT CURRENT_DATE,
            weight REAL,
            calories REAL,
            protein REAL,
            carbs REAL,
            fat REAL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """)

    conn.commit()
    conn.close()
        
# add later: insert_user, get_user, insert_log, get_logs
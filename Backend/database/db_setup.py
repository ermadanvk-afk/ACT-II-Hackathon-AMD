import sqlite3
import os

# BASE_DIR is the Backend/ folder (one level up from database/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    
    # Create User_Journeys table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_journeys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            level TEXT NOT NULL,
            current_day INTEGER DEFAULT 1,
            FOREIGN KEY(user_id) REFERENCES users(id),
            UNIQUE(user_id, role, level)
        )
    """)
    
    # Create Session Cache table — stores AI agent output per user+day
    # so repeat visits pull from DB instead of re-running the agent.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            level TEXT NOT NULL,
            day INTEGER NOT NULL,
            phase TEXT NOT NULL,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, role, level, day),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


if __name__ == "__main__":
    init_db()

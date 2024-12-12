import sqlite3

DB_PATH = "db/bot.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL,
        name TEXT NOT NULL,
        username TEXT
    )
    """)
    conn.commit()
    conn.close()

# Check if a user exists by Telegram ID
def user_exists(telegram_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

# Add or update a user
def save_user(telegram_id, name, username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO users (telegram_id, name, username) 
    VALUES (?, ?, ?)
    ON CONFLICT(telegram_id) DO UPDATE SET
    name = excluded.name,
    username = excluded.username
    """, (telegram_id, name, username))
    conn.commit()
    conn.close()

def count_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    conn.close()
    return total_users

def get_user_ids():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id FROM users")
    telegram_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return telegram_ids


init_db()
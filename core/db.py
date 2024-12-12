import sqlite3
import datetime

DB_PATH = "db/bot.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL,
        name TEXT NOT NULL,
        username TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create admins table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL
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

# Add a user (only if new)
def add_user(telegram_id, name, username):
    if not user_exists(telegram_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO users (telegram_id, name, username) 
        VALUES (?, ?, ?)
        """, (telegram_id, name, username))
        conn.commit()
        conn.close()

# Count total users
def count_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    conn.close()
    return total_users

# Count users who joined in the past 24 hours
def count_new_users_last_24_hours():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    past_24_hours = datetime.datetime.now() - datetime.timedelta(hours=24)
    cursor.execute("SELECT COUNT(*) FROM users WHERE created_at >= ?", (past_24_hours,))
    new_users = cursor.fetchone()[0]
    conn.close()
    return new_users

def clear_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users")  # Clear all rows from the users table
    conn.commit()
    conn.close()

# Get all user Telegram IDs
def get_user_ids():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id FROM users")
    telegram_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return telegram_ids

def add_admin(telegram_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR IGNORE INTO admins (telegram_id) 
    VALUES (?)
    """, (telegram_id,))
    conn.commit()
    conn.close()

def remove_admin(telegram_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    DELETE FROM admins 
    WHERE telegram_id = ?
    """, (telegram_id,))
    conn.commit()
    conn.close()

def count_admins():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM admins")
    total_admins = cursor.fetchone()[0]
    conn.close()
    return total_admins

def get_admins():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id FROM admins")
    admins = [row[0] for row in cursor.fetchall()]
    conn.close()
    return admins




# Initialize the database
init_db()

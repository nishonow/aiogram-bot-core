import aiosqlite
import datetime

DB_PATH = "bot.db"

# Initialize database
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            name TEXT NOT NULL,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT UNIQUE NOT NULL -- Channel username (e.g., @your_channel)
        )
        """)
        await db.commit()

# Check if a user exists by Telegram ID
async def user_exists(telegram_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            exists = await cursor.fetchone() is not None
    return exists

# Add a user (only if new)
async def add_user(telegram_id, name, username):
    if not await user_exists(telegram_id):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
            INSERT INTO users (telegram_id, name, username) 
            VALUES (?, ?, ?)
            """, (telegram_id, name, username))
            await db.commit()

# Count total users
async def count_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            total_users = (await cursor.fetchone())[0]
    return total_users

# Count users who joined in the past 24 hours
async def count_new_users_last_24_hours():
    past_24_hours = datetime.datetime.now() - datetime.timedelta(hours=24)
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users WHERE created_at >= ?", (past_24_hours,)) as cursor:
            new_users = (await cursor.fetchone())[0]
    return new_users

# Clear all rows from the users table
async def clear_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM users")
        await db.commit()

# Get all user Telegram IDs
async def get_user_ids():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT telegram_id FROM users") as cursor:
            telegram_ids = [row[0] for row in await cursor.fetchall()]
    return telegram_ids

# Add an admin
async def add_admin(telegram_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        INSERT OR IGNORE INTO admins (telegram_id) 
        VALUES (?)
        """, (telegram_id,))
        await db.commit()

# Remove an admin
async def remove_admin(telegram_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        DELETE FROM admins 
        WHERE telegram_id = ?
        """, (telegram_id,))
        await db.commit()

# Count total admins
async def count_admins():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM admins") as cursor:
            total_admins = (await cursor.fetchone())[0]
    return total_admins

# Get all admin Telegram IDs
async def get_admins():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT telegram_id FROM admins") as cursor:
            admins = [row[0] for row in await cursor.fetchall()]
    return admins

# Get admin details
async def get_admin_details():
    admin_ids = await get_admins()
    if not admin_ids:
        return []
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(f"""
            SELECT telegram_id, name FROM users WHERE telegram_id IN ({','.join('?' for _ in admin_ids)})
        """, admin_ids) as cursor:
            admins_details = await cursor.fetchall()
    return admins_details

# Get all channel IDs
async def get_channel_ids():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT channel_id FROM channels") as cursor:
            channel_ids = [row[0] for row in await cursor.fetchall()]
    return channel_ids

# Add a channel
async def add_channel(channel_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO channels (channel_id) VALUES (?)", (channel_id,))
        await db.commit()

# Remove a channel
async def remove_channel(channel_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
        await db.commit()

async def on_startup():
    await init_db()
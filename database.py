import aiosqlite
from datetime import datetime, timedelta

DB = "ahiska.db"


async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            role TEXT DEFAULT 'user',
            queries INTEGER DEFAULT 0,
            vip INTEGER DEFAULT 0,
            vip_until TEXT,
            balance REAL DEFAULT 0,
            registered_at TEXT,
            last_bonus TEXT
        );

        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            query TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            path TEXT,
            records INTEGER DEFAULT 0,
            created_at TEXT
        );
        """)
        await db.commit()


async def get_user(user_id):
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        return await cur.fetchone()


async def create_user(user_id, username, first_name, owner_id):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT id FROM users WHERE id = ?",
            (user_id,)
        )

        exists = await cur.fetchone()

        if exists:
            await db.execute(
                "UPDATE users SET username=?, first_name=? WHERE id=?",
                (username, first_name, user_id)
            )
        else:
            role = "owner" if user_id == owner_id else "user"

            await db.execute("""
                INSERT INTO users
                (id, username, first_name, role, queries, registered_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                username,
                first_name,
                role,
                0,
                datetime.utcnow().isoformat()
            ))

        await db.commit()


async def add_queries(user_id, amount):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE users SET queries = queries + ? WHERE id = ?",
            (amount, user_id)
        )
        await db.commit()


async def use_query(user_id):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT queries, vip FROM users WHERE id=?",
            (user_id,)
        )

        row = await cur.fetchone()

        if not row:
            return False

        if row[1]:
            return True

        if row[0] <= 0:
            return False

        await db.execute(
            "UPDATE users SET queries=queries-1 WHERE id=?",
            (user_id,)
        )

        await db.commit()
        return True


async def daily_bonus(user_id):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT last_bonus FROM users WHERE id=?",
            (user_id,)
        )

        row = await cur.fetchone()

        now = datetime.utcnow()

        if row and row[0]:
            last = datetime.fromisoformat(row[0])

            if now - last < timedelta(hours=24):
                return False

        await db.execute("""
            UPDATE users
            SET queries=queries+1, last_bonus=?
            WHERE id=?
        """, (now.isoformat(), user_id))

        await db.commit()
        return True


async def save_search(user_id, query):
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            INSERT INTO searches(user_id, query, created_at)
            VALUES (?, ?, ?)
        """, (
            user_id,
            query,
            datetime.utcnow().isoformat()
        ))

        await db.commit()


async def get_stats(user_id):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("""
            SELECT
                COUNT(*),
                (SELECT queries FROM users WHERE id=?)
            FROM searches
            WHERE user_id=?
        """, (user_id, user_id))

        return await cur.fetchone()

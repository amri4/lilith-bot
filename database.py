import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "lilith.db")


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS stolen_goods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                thief_id TEXT NOT NULL,
                victim_id TEXT NOT NULL,
                amount INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bounties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                poster_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                amount INTEGER NOT NULL,
                active INTEGER DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def add_steal(guild_id, thief_id, victim_id, amount):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO stolen_goods (guild_id, thief_id, victim_id, amount) VALUES (?, ?, ?, ?)",
            (str(guild_id), str(thief_id), str(victim_id), amount),
        )
        conn.commit()


def get_hoard(guild_id, thief_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM stolen_goods WHERE guild_id = ? AND thief_id = ?",
            (str(guild_id), str(thief_id)),
        ).fetchone()
    return row[0] if row else 0


def add_bounty(guild_id, poster_id, target_id, amount):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO bounties (guild_id, poster_id, target_id, amount) VALUES (?, ?, ?, ?)",
            (str(guild_id), str(poster_id), str(target_id), amount),
        )
        conn.commit()


def get_active_bounties(guild_id):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, poster_id, target_id, amount, timestamp FROM bounties WHERE guild_id = ? AND active = 1 ORDER BY amount DESC LIMIT 10",
            (str(guild_id),),
        ).fetchall()
    return rows


def get_total_stolen(guild_id):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT thief_id, SUM(amount) as total FROM stolen_goods WHERE guild_id = ? GROUP BY thief_id ORDER BY total DESC LIMIT 5",
            (str(guild_id),),
        ).fetchall()
    return rows

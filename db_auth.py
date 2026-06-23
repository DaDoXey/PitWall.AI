import sqlite3
import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "pitwall_auth.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        name TEXT,
        auth_method TEXT,
        created_at TIMESTAMP,
        last_login TIMESTAMP
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        login_timestamp TIMESTAMP,
        last_activity TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)
    conn.commit()
    conn.close()


def create_or_update_user(user_id, email, name, auth_method):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.now().isoformat()
    c.execute("""
    INSERT OR REPLACE INTO users (user_id, email, name, auth_method, created_at, last_login)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, email, name, auth_method, now, now))
    conn.commit()
    conn.close()


def create_session(session_id, user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.now().isoformat()
    c.execute("""
    INSERT INTO sessions (session_id, user_id, login_timestamp, last_activity)
    VALUES (?, ?, ?, ?)
    """, (session_id, user_id, now, now))
    conn.commit()
    conn.close()


def update_session_activity(session_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    UPDATE sessions SET last_activity = ? WHERE session_id = ?
    """, (datetime.datetime.now().isoformat(), session_id))
    conn.commit()
    conn.close()

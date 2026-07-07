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
    # tabella sessions: predisposta, scrittura non ancora collegata
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
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    # Identità reale = email (UNIQUE). Il Custom Login genera uno user_id nuovo a
    # ogni accesso: se l'email esiste già aggiorniamo la riga esistente (preservando
    # user_id e created_at) invece di ricrearla → niente reset di created_at né
    # violazione del vincolo UNIQUE(email).
    row = c.execute("SELECT user_id FROM users WHERE email = ?", (email,)).fetchone()
    if row:
        c.execute(
            "UPDATE users SET name = ?, auth_method = ?, last_login = ? WHERE email = ?",
            (name, auth_method, now, email),
        )
    else:
        c.execute("""
        INSERT INTO users (user_id, email, name, auth_method, created_at, last_login)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, email, name, auth_method, now, now))
    conn.commit()
    conn.close()

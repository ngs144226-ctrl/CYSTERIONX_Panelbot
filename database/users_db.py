import sqlite3

DB = "cysterionx.db"


def connect():
    return sqlite3.connect(DB)


def create_users_table():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        full_name TEXT,
        username TEXT,
        referrer_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


create_users_table()


def save_user(user_id, full_name, username, referrer_id=None):

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO users
    (user_id, full_name, username, referrer_id)
    VALUES (?, ?, ?, ?)
    """,
    (user_id, full_name, username, referrer_id))

    conn.commit()
    conn.close()


def get_user(user_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT user_id, full_name, username, referrer_id FROM users WHERE user_id=?",
        (user_id,)
    )

    data = cur.fetchone()

    conn.close()

    if data:
        return {
            "user_id": data[0],
            "full_name": data[1],
            "username": data[2],
            "referrer_id": data[3]
        }

    return None


def update_user(user_id, full_name, username):

    save_user(user_id, full_name, username)

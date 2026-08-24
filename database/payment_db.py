import sqlite3

DB = "cysterionx.db"


def connect():
    return sqlite3.connect(DB)


def create_payment_table():

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS payment_sessions (
        user_id INTEGER PRIMARY KEY,
        plan_id INTEGER,
        status TEXT DEFAULT 'waiting'
    )
    """)

    conn.commit()
    conn.close()


def create_session(user_id, plan_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO payment_sessions
    (user_id, plan_id, status)
    VALUES (?, ?, 'waiting')
    """,
    (user_id, plan_id))

    conn.commit()
    conn.close()


def get_session(user_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT plan_id, status FROM payment_sessions WHERE user_id=?",
        (user_id,)
    )

    data = cur.fetchone()

    conn.close()

    return data


def remove_session(user_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM payment_sessions WHERE user_id=?",
        (user_id,)
    )

    conn.commit()
    conn.close()


create_payment_table()

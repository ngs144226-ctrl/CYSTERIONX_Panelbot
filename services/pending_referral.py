import sqlite3

DB = "cysterionx.db"


def connect():
    return sqlite3.connect(DB)


def init_pending_referral():

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS pending_referrals (
        user_id INTEGER PRIMARY KEY,
        referrer_id INTEGER
    )
    """)

    conn.commit()
    conn.close()


init_pending_referral()


def set_pending_referral(user_id, referrer_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO pending_referrals
    (user_id, referrer_id)
    VALUES (?, ?)
    """,
    (user_id, referrer_id))

    conn.commit()
    conn.close()


def get_pending_referral(user_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT referrer_id FROM pending_referrals WHERE user_id=?",
        (user_id,)
    )

    data = cur.fetchone()

    conn.close()

    if data:
        return data[0]

    return None


def clear_pending_referral(user_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM pending_referrals WHERE user_id=?",
        (user_id,)
    )

    conn.commit()
    conn.close()

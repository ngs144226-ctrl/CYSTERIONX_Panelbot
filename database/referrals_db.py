import sqlite3

DB = "cysterionx.db"


def connect():
    return sqlite3.connect(DB)


def init_referrals():
    con = connect()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS referrals (
        user_id INTEGER PRIMARY KEY,
        referral_hours INTEGER DEFAULT 0,
        deposit_hours INTEGER DEFAULT 0,
        total_hours INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS referred_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        referred_user_id INTEGER UNIQUE
    )
    """)

    con.commit()
    con.close()


init_referrals()


def is_already_referred(referred_user_id):

    con = connect()
    cur = con.cursor()

    cur.execute(
        "SELECT 1 FROM referred_users WHERE referred_user_id=?",
        (referred_user_id,)
    )

    result = cur.fetchone()
    con.close()

    return result is not None


def save_referral(user_id, referred_user_id):

    con = connect()
    cur = con.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO referrals(user_id) VALUES(?)",
        (user_id,)
    )

    cur.execute(
        "INSERT OR IGNORE INTO referred_users(user_id,referred_user_id) VALUES(?,?)",
        (user_id, referred_user_id)
    )

    con.commit()
    con.close()


def add_referral_reward(user_id, hours):

    con = connect()
    cur = con.cursor()

    cur.execute(
        """
        UPDATE referrals
        SET referral_hours = referral_hours + ?,
        total_hours = total_hours + ?
        WHERE user_id=?
        """,
        (hours, hours, user_id)
    )

    con.commit()
    con.close()


def add_deposit_reward(user_id, hours):

    con = connect()
    cur = con.cursor()

    cur.execute(
        """
        UPDATE referrals
        SET deposit_hours = deposit_hours + ?,
        total_hours = total_hours + ?
        WHERE user_id=?
        """,
        (hours, hours, user_id)
    )

    con.commit()
    con.close()


def get_referral(user_id):

    con = connect()
    cur = con.cursor()

    cur.execute(
        "SELECT referral_hours,deposit_hours,total_hours FROM referrals WHERE user_id=?",
        (user_id,)
    )

    data = cur.fetchone()

    if not data:
        con.close()
        return None

    cur.execute(
        "SELECT referred_user_id FROM referred_users WHERE user_id=?",
        (user_id,)
    )

    users = [x[0] for x in cur.fetchall()]

    con.close()

    return {
        "referred_users": users,
        "referral_hours": data[0],
        "deposit_hours": data[1],
        "total_hours": data[2]
    }


def get_referrer(referred_user_id):

    con = connect()
    cur = con.cursor()

    cur.execute(
        "SELECT user_id FROM referred_users WHERE referred_user_id=?",
        (referred_user_id,)
    )

    data = cur.fetchone()

    con.close()

    if data:
        return data[0]

    return None

import sqlite3
from datetime import datetime, timedelta

DB = "cysterionx.db"


def connect():
    return sqlite3.connect(DB)


def init_keys():
    con = connect()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS keys (
        user_id INTEGER PRIMARY KEY,
        key_value TEXT,
        key_status TEXT,
        expire_time TEXT
    )
    """)

    con.commit()
    con.close()


init_keys()


def save_key(user_id, key_value):
    con = connect()
    cur = con.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO keys VALUES (?, ?, ?, ?, ?)",
        (user_id, key_value, "Inactive", None, None)
    )

    con.commit()
    con.close()


def get_key(user_id):
    con = connect()
    cur = con.cursor()

    cur.execute(
        "SELECT user_id,key_value,key_status,expire_time,plan_name FROM keys WHERE user_id=?",
        (user_id,)
    )

    row = cur.fetchone()
    con.close()

    if row:
        expire = datetime.fromisoformat(row[3]) if row[3] else None

        if expire and expire <= datetime.now():
            con = connect()
            cur = con.cursor()

            cur.execute(
                "UPDATE keys SET key_status='Expired', plan_name=NULL WHERE user_id=?",
                (user_id,)
            )

            con.commit()
            con.close()

            row = (
                row[0],
                row[1],
                "Expired",
                row[3],
                None
            )

        elif expire and expire > datetime.now() and row[2] == "Expired":
            con = connect()
            cur = con.cursor()

            cur.execute(
                "UPDATE keys SET key_status='Active' WHERE user_id=?",
                (user_id,)
            )

            con.commit()
            con.close()

            row = (
                row[0],
                row[1],
                "Active",
                row[3],
                row[4]
            )

        return {
            "user_id": row[0],
            "key_value": row[1],
            "key_status": row[2],
            "expire_time": datetime.fromisoformat(row[3]) if row[3] else None,
            "plan_name": row[4] if len(row) > 4 else None
        }

    return None



def get_key_by_value(key_value):

    con = connect()
    cur = con.cursor()

    cur.execute(
        "SELECT user_id,key_value,key_status,expire_time,plan_name FROM keys WHERE key_value=?",
        (key_value,)
    )

    row = cur.fetchone()

    con.close()

    if row:
        return {
            "user_id": row[0],
            "key_value": row[1],
            "key_status": row[2],
            "expire_time": datetime.fromisoformat(row[3]) if row[3] else None,
            "plan_name": row[4] if len(row) > 4 else None
        }

    return None


def add_key_time(user_id, hours):

    data = get_key(user_id)

    if not data:
        return False

    now = datetime.now()

    if data["expire_time"] and data["expire_time"] > now:
        expire = data["expire_time"] + timedelta(hours=hours)
    else:
        expire = now + timedelta(hours=hours)

    con = connect()
    cur = con.cursor()

    cur.execute(
        "UPDATE keys SET key_status=?, expire_time=? WHERE user_id=?",
        ("Active", expire.isoformat(), user_id)
    )

    con.commit()
    con.close()

    return True



def update_key_expiry_minutes(user_id, minutes):

    con = connect()
    cur = con.cursor()

    cur.execute(
        "SELECT expire_time FROM keys WHERE user_id=?",
        (user_id,)
    )

    row = cur.fetchone()

    if not row:
        con.close()
        return False

    current = datetime.now()

    if row[0]:
        old_expire = datetime.fromisoformat(row[0])
        if old_expire < current and minutes > 0:
            old_expire = current
    else:
        old_expire = current

    new_expire = old_expire + timedelta(minutes=minutes)

    if new_expire <= current:
        cur.execute(
            "UPDATE keys SET key_status=?, expire_time=? WHERE user_id=?",
            (
                "Expired",
                new_expire.isoformat(),
                user_id
            )
        )
    else:
        cur.execute(
            "UPDATE keys SET key_status=?, expire_time=? WHERE user_id=?",
            (
                "Active",
                new_expire.isoformat(),
                user_id
            )
        )

    con.commit()
    con.close()

    return True


def update_plan_name(user_id, plan_name):

    con = connect()
    cur = con.cursor()

    cur.execute(
        """
        UPDATE keys
        SET plan_name=?
        WHERE user_id=?
        """,
        (
            plan_name,
            user_id
        )
    )

    con.commit()
    con.close()


def clear_plan_name(user_id):

    con = connect()
    cur = con.cursor()

    cur.execute(
        """
        UPDATE keys
        SET plan_name=NULL
        WHERE user_id=?
        """,
        (
            user_id,
        )
    )

    con.commit()
    con.close()

    return True

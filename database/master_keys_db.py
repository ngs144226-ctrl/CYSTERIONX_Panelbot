import sqlite3
from datetime import datetime, timedelta

DB_NAME = "cysterionx.db"


def connect():
    return sqlite3.connect(DB_NAME)


def create_master_keys_table():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS master_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        master_key TEXT UNIQUE,
        key_type TEXT,
        status TEXT,
        access_time INTEGER DEFAULT 0,
        expire_time TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_master_key(master_key):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO master_keys
        (master_key, key_type, status, access_time, expire_time)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            master_key,
            "Special Master Key",
            "Inactive",
            0,
            None
        )
    )

    conn.commit()
    conn.close()


def get_master_key(master_key):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM master_keys WHERE master_key=?",
        (master_key,)
    )

    row = cur.fetchone()

    conn.close()

    if not row:
        return None

    from datetime import datetime

    expire_time = datetime.fromisoformat(row[5]) if row[5] else None

    if expire_time and expire_time <= datetime.now():
        status = "Expired"
    else:
        status = row[3]

    return {
        "id": row[0],
        "master_key": row[1],
        "key_type": row[2],
        "status": status,
        "access_time": row[4],
        "expire_time": expire_time
    }



def update_master_key_time(master_key, minutes):
    from datetime import datetime, timedelta

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT expire_time FROM master_keys WHERE master_key=?",
        (master_key,)
    )

    row = cur.fetchone()

    if not row:
        conn.close()
        return False

    now = datetime.now()

    if row[0]:
        try:
            expire = datetime.fromisoformat(row[0])
        except:
            expire = now
    else:
        expire = now

    if expire < now:
        expire = now

    new_expire = expire + timedelta(minutes=minutes)

    cur.execute(
        """
        UPDATE master_keys
        SET access_time=?,
            expire_time=?,
            status=?
        WHERE master_key=?
        """,
        (
            minutes,
            new_expire.isoformat(),
            "Active",
            master_key
        )
    )

    conn.commit()
    changed = cur.rowcount
    conn.close()

    return changed > 0


def remove_master_key_time(master_key, minutes):
    from datetime import datetime, timedelta

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT expire_time FROM master_keys WHERE master_key=?",
        (master_key,)
    )

    row = cur.fetchone()

    if not row or not row[0]:
        conn.close()
        return False

    expire = datetime.fromisoformat(row[0])
    new_expire = expire - timedelta(minutes=minutes)

    now = datetime.now()

    if new_expire <= now:
        cur.execute(
            """
            UPDATE master_keys
            SET access_time=0,
                expire_time=NULL,
                status='Expired'
            WHERE master_key=?
            """,
            (master_key,)
        )
    else:
        cur.execute(
            """
            UPDATE master_keys
            SET expire_time=?,
                status='Active'
            WHERE master_key=?
            """,
            (
                new_expire.isoformat(),
                master_key
            )
        )

    conn.commit()
    changed = cur.rowcount
    conn.close()

    return changed > 0


def update_master_key_expiry_minutes(master_key, minutes):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT expire_time FROM master_keys WHERE master_key=?",
        (master_key,)
    )

    row = cur.fetchone()

    if not row:
        conn.close()
        return False

    now = datetime.now()

    if row[0]:
        old_expire = datetime.fromisoformat(row[0])

        if old_expire < now and minutes > 0:
            old_expire = now
    else:
        old_expire = now

    if minutes < 0 and old_expire <= now:
        conn.close()
        return False

    if minutes < 0:
        remove_minutes = abs(minutes)

        available_minutes = int(
            (old_expire - now).total_seconds() // 60
        )

        if remove_minutes > available_minutes:
            conn.close()
            return False

    new_expire = old_expire + timedelta(minutes=minutes)

    if new_expire <= now:
        status = "Expired"
    else:
        status = "Active"

    cur.execute(
        """
        UPDATE master_keys
        SET expire_time=?, status=?, access_time=?
        WHERE master_key=?
        """,
        (
            new_expire.isoformat(),
            status,
            int((new_expire - now).total_seconds() // 60),
            master_key
        )
    )

    conn.commit()
    conn.close()

    return True



def remove_master_key_expiry_minutes(master_key, minutes):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT expire_time FROM master_keys WHERE master_key=?",
        (master_key,)
    )

    row = cur.fetchone()

    if not row:
        conn.close()
        return False

    now = datetime.now()

    if not row[0]:
        conn.close()
        return False

    old_expire = datetime.fromisoformat(row[0])

    new_expire = old_expire - timedelta(minutes=minutes)

    if new_expire <= now:
        status = "Expired"
        remaining = 0
    else:
        status = "Active"
        remaining = int((new_expire - now).total_seconds() // 60)

    cur.execute(
        """
        UPDATE master_keys
        SET expire_time=?, status=?, access_time=?
        WHERE master_key=?
        """,
        (
            new_expire.isoformat(),
            status,
            remaining,
            master_key
        )
    )

    conn.commit()
    conn.close()

    return True

import sqlite3

DB_NAME = "cysterionx.db"


def connect():
    return sqlite3.connect(DB_NAME)


def create_upi_table():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS upi (
        id INTEGER PRIMARY KEY,
        upi_id TEXT,
        active INTEGER DEFAULT 1
    )
    """)

    cur.execute("SELECT COUNT(*) FROM upi")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO upi (upi_id, active) VALUES (?, ?)",
            ("ssr2920260@okaxis", 1)
        )

    conn.commit()
    conn.close()


def get_active_upi():
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT upi_id FROM upi WHERE active=1 LIMIT 1"
    )

    row = cur.fetchone()
    conn.close()

    return row[0] if row else None

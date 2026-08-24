import sqlite3

DB = "cysterionx.db"


def connect():
    return sqlite3.connect(DB)


def create_plans_table():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_name TEXT UNIQUE,
        duration_days INTEGER,
        price INTEGER,
        status TEXT DEFAULT 'Active'
    )
    """)

    conn.commit()
    conn.close()


def add_default_plans():

    conn = connect()
    cur = conn.cursor()

    plans = [
        ("Basic Plan", 7, 99),
        ("Pro Plan", 30, 299),
        ("Premium Plan", 60, 699)
    ]

    for plan in plans:
        cur.execute("""
        INSERT OR IGNORE INTO plans
        (plan_name, duration_days, price)
        VALUES (?, ?, ?)
        """, plan)

    conn.commit()
    conn.close()


def get_plans():

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, plan_name, duration_days, price
    FROM plans
    WHERE status='Active'
    """)

    data = cur.fetchall()

    conn.close()

    return data


create_plans_table()
add_default_plans()

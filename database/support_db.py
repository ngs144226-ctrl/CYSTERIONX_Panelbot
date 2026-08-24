import sqlite3
from datetime import datetime

DB = "cysterionx.db"


def connect():
    return sqlite3.connect(DB)


def create_support_table():

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS support_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT UNIQUE,
        user_id INTEGER,
        username TEXT,
        category TEXT,
        message TEXT,
        status TEXT DEFAULT 'Processing',
        admin_reply TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def create_ticket(ticket_id, user_id, username, category, message):

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO support_tickets
    (ticket_id, user_id, username, category, message, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        ticket_id,
        user_id,
        username,
        category,
        message,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_user_tickets(user_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM support_tickets WHERE user_id=? ORDER BY id DESC",
        (user_id,)
    )

    data = cur.fetchall()

    conn.close()

    return data


def get_ticket(ticket_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM support_tickets WHERE ticket_id=?",
        (ticket_id,)
    )

    data = cur.fetchone()

    conn.close()

    return data


def update_ticket_status(ticket_id, status):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "UPDATE support_tickets SET status=? WHERE ticket_id=?",
        (status, ticket_id)
    )

    conn.commit()
    conn.close()


def add_admin_reply(ticket_id, reply):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "UPDATE support_tickets SET admin_reply=? WHERE ticket_id=?",
        (reply, ticket_id)
    )

    conn.commit()
    conn.close()


create_support_table()


def get_user_ticket_by_id(ticket_id, user_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT * FROM support_tickets
        WHERE ticket_id=? AND user_id=?
        """,
        (
            ticket_id,
            user_id
        )
    )

    data = cur.fetchone()

    conn.close()

    return data


def get_ticket_by_id(ticket_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM support_tickets WHERE ticket_id=?",
        (ticket_id,)
    )

    data = cur.fetchone()

    conn.close()

    return data


def save_support_message_id(ticket_id, message_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "UPDATE support_tickets SET support_message_id=? WHERE ticket_id=?",
        (message_id, ticket_id)
    )

    conn.commit()
    conn.close()




def save_user_message_id(ticket_id, message_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "UPDATE support_tickets SET user_message_id=? WHERE ticket_id=?",
        (message_id, ticket_id)
    )

    conn.commit()
    conn.close()

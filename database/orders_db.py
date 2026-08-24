import sqlite3
from datetime import datetime

DB = "cysterionx.db"


def connect():
    return sqlite3.connect(DB)


def create_orders_table():

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT UNIQUE,
        user_id INTEGER,
        plan_id INTEGER,
        payment_id TEXT,
        amount INTEGER,
        status TEXT DEFAULT 'Pending',
        created_at TEXT,
        message_id INTEGER
    )
    """)

    conn.commit()
    conn.close()


def create_order(order_id, user_id, plan_id, payment_id, amount):

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO orders
    (order_id, user_id, plan_id, payment_id, amount, status, created_at, message_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        order_id,
        user_id,
        plan_id,
        payment_id,
        amount,
        "Pending",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        None
    ))

    conn.commit()
    conn.close()


def get_order(order_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM orders WHERE order_id=?",
        (order_id,)
    )

    data = cur.fetchone()

    conn.close()

    return data


create_orders_table()


def update_message_id(order_id, message_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "UPDATE orders SET message_id=? WHERE order_id=?",
        (message_id, order_id)
    )

    conn.commit()
    conn.close()


def update_order_status(order_id, status):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "UPDATE orders SET status=? WHERE order_id=?",
        (status, order_id)
    )

    conn.commit()
    conn.close()


def delete_order(order_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM orders WHERE order_id=?",
        (order_id,)
    )

    conn.commit()
    conn.close()


def get_order_by_id(order_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM orders WHERE order_id=?",
        (order_id,)
    )

    data = cur.fetchone()

    conn.close()

    return data

def save_order_message_id(order_id, message_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "UPDATE orders SET message_id=? WHERE order_id=?",
        (message_id, order_id)
    )

    conn.commit()
    conn.close()

def save_admin_message_id(order_id, admin_message_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "UPDATE orders SET admin_message_id=? WHERE order_id=?",
        (admin_message_id, order_id)
    )

    conn.commit()
    conn.close()

def save_admin_chat_id(order_id, admin_chat_id):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "UPDATE orders SET admin_chat_id=? WHERE order_id=?",
        (admin_chat_id, order_id)
    )

    conn.commit()
    conn.close()



def save_control_order_message(order_id, chat_id, message_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS control_order_messages (
            order_id TEXT PRIMARY KEY,
            chat_id INTEGER,
            message_id INTEGER
        )
    """)

    cur.execute("""
        INSERT OR REPLACE INTO control_order_messages
        (order_id, chat_id, message_id)
        VALUES (?, ?, ?)
    """,
    (
        order_id,
        chat_id,
        message_id
    ))

    conn.commit()
    conn.close()



def get_control_order_message(order_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT chat_id, message_id
        FROM control_order_messages
        WHERE order_id=?
    """,
    (order_id,))

    data = cur.fetchone()

    conn.close()

    return data


def save_order_admin_message(order_id, admin_id, message_id):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_admin_messages (
            order_id TEXT,
            admin_id INTEGER,
            message_id INTEGER,
            PRIMARY KEY (order_id, admin_id)
        )
    """)

    cur.execute("""
        INSERT OR REPLACE INTO order_admin_messages
        (order_id, admin_id, message_id)
        VALUES (?, ?, ?)
    """, (order_id, admin_id, message_id))

    conn.commit()
    conn.close()


def get_order_admin_messages(order_id):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_admin_messages (
            order_id TEXT,
            admin_id INTEGER,
            message_id INTEGER,
            PRIMARY KEY (order_id, admin_id)
        )
    """)

    cur.execute("""
        SELECT admin_id, message_id
        FROM order_admin_messages
        WHERE order_id=?
    """, (order_id,))

    rows = cur.fetchall()
    conn.close()
    return rows


def get_success_orders_count():
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM orders WHERE status='Success'"
    )

    count = cur.fetchone()[0]

    conn.close()

    return count

from config import OWNER_ID, ADMIN_IDS
from services.order_message import order_created_text


def get_admin_ids():

    admins = []

    if ADMIN_IDS:
        admins.extend(ADMIN_IDS)

    return list(set(admins))


def admin_order_text(order):
    text = order_created_text(order["order_id"])

    if not text:
        return None

    return text.replace(
        "🧾 ORDER CREATED",
        "👤 USER ORDER",
        1
    )

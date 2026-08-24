from database.orders_db import get_order_by_id
from database.plans_db import get_plans


def order_status_text(order_id, admin=False):

    order = get_order_by_id(order_id)

    if not order:
        return None

    _id, oid, user_id, plan_id, payment_id, amount, status, created_at, message_id, admin_message_id, admin_chat_id = order

    plan_name = "Unknown Plan"
    days = 0

    for pid, name, plan_days, price in get_plans():
        if pid == plan_id:
            plan_name = name
            days = plan_days
            break

    if status == "Pending":
        emoji = "⏳"
    elif status == "Processing":
        emoji = "⚙️"
    elif status == "Success":
        emoji = "✅"
    else:
        emoji = "❌"

    heading = "👤 USER ORDER" if admin else "🧾 ORDER CREATED"

    return (
        f"{heading}\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 Order ID       `{oid}`\n\n"
        f"📦 Plan           {plan_name}\n\n"
        f"⏳ Duration       {days} Days\n\n"
        f"💰 Amount         ₹{amount}\n\n"
        f"💳 Payment ID     {payment_id}\n\n"
        f"📌 Status         {emoji} {status}\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🕐 Your order status has been updated.\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )

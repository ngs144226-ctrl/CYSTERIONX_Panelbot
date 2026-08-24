from database.orders_db import get_order
from database.plans_db import get_plans


def order_created_text(order_id):

    order = get_order(order_id)

    if not order:
        return None

    _id = order[0]
    oid = order[1]
    user_id = order[2]
    plan_id = order[3]
    payment_id = order[4]
    amount = order[5]
    status = order[6]
    created_at = order[7]

    message_id = order[8] if len(order) > 8 else None
    admin_message_id = order[9] if len(order) > 9 else None


    plan_name = "Unknown Plan"
    days = 0

    plans = get_plans()

    for pid, name, plan_days, price in plans:
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

    return (
        "🧾 ORDER CREATED\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 Order ID       `{oid}`\n\n"
        f"📦 Plan           {plan_name}\n\n"
        f"⏳ Duration       {days} Days\n\n"
        f"💰 Amount         ₹{amount}\n\n"
        f"💳 Payment ID     {payment_id}\n\n"
        f"📌 Status         {emoji} {status}\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🕐 Your order has been created.\n\n"
        "Please wait for admin approval.\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )

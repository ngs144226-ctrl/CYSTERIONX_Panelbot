from database.plans_db import get_plans


def get_status_text(status):

    status_map = {
        "Pending": "⏳ Pending",
        "Processing": "⚙️ Processing",
        "Success": "✅ Success",
        "Failed": "❌ Failed"
    }

    return status_map.get(
        status,
        status
    )


def get_plan_info(plan_id):

    for pid, name, days, price in get_plans():
        if pid == plan_id:
            return name, days

    return "Unknown", 0


def trace_order_text(result):

    if result["status"] == "not_found":
        return (
            "❌ ORDER NOT FOUND\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "The Order ID you entered\n"
            "does not exist.\n\n"
            "Please check your Order ID\n"
            "and try again.\n\n"
            "━━━━━━━━━━━━━━━━━━"
        )

    if result["status"] == "denied":
        return (
            "🔒 ACCESS DENIED\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "This Order ID does not belong\n"
            "to your account.\n\n"
            "You can only track your own orders.\n\n"
            "━━━━━━━━━━━━━━━━━━"
        )

    order = result["order"]

    _id, order_id, user_id, plan_id, payment_id, amount, status, created_at, message_id, admin_message_id, admin_chat_id = order

    plan_name, days = get_plan_info(plan_id)

    return (
        "🧾 ORDER DETAILS\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 Order ID       {order_id}\n\n"
        f"📦 Plan           {plan_name}\n\n"
        f"⏳ Duration       {days} Days\n\n"
        f"💰 Amount         ₹{amount}\n\n"
        f"💳 Payment ID     {payment_id}\n\n"
        f"📌 Status         {get_status_text(status)}\n\n"
        f"📅 Date           {created_at.split()[0]}\n\n"
        f"🕒 Time           {created_at.split()[1]}\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )

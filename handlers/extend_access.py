from database.payment_db import create_session
from telebot import types
from database.plans_db import get_plans
from database.upi_db import get_active_upi


def extend_access_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    plans = get_plans()

    for plan_id, name, days, price in plans:

        if "Premium" in name:
            emoji = "👑"
        elif "Pro" in name:
            emoji = "🥈"
        else:
            emoji = "🥉"

        markup.row(
            f"{emoji} {name.replace(' Plan','')} • ₹{price}"
        )

    markup.row("⬅️ Back")

    return markup


def handle_extend_access(bot, message):

    bot.send_message(
        message.chat.id,
        "💎 EXTEND ACCESS\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🚀 Upgrade your access plan\n\n"
        "📦 Available Plans:\n\n"
        "Choose a plan to continue\n\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=extend_access_menu()
    )


def get_plan_details(plan_id):

    plans = get_plans()

    for pid, name, days, price in plans:
        if pid == plan_id:
            return {
                "id": pid,
                "name": name,
                "days": days,
                "price": price
            }

    return None


def get_plan_id_from_button(text):

    plans = get_plans()

    for plan_id, name, days, price in plans:

        if "Premium" in name:
            emoji = "👑"
        elif "Pro" in name:
            emoji = "🥈"
        else:
            emoji = "🥉"

        button_name = f"{emoji} {name.replace(' Plan','')} • ₹{price}"

        if text == button_name:
            return plan_id

    return None


def plan_details_text(plan_id):

    plan = get_plan_details(plan_id)

    if not plan:
        return None

    upi = get_active_upi()

    return (
        "💎 PLAN DETAILS\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"📦 Plan        {plan['name']}\n"
        f"⏳ Duration    {plan['days']} Days\n\n"
        f"💰 Price       ₹{plan['price']}\n\n"
        f"💳 UPI ID\n`{upi}`\n\n"
        "✨ Benefits:\n"
        "• Full Key Access\n"
        "• Instant Activation\n"
        "• Extended Validity\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )


def start_payment_session(user_id, plan_id):

    create_session(
        user_id,
        plan_id
    )

    return (
        "🧾 Send 12 Digit Payment ID\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Only numbers are allowed.\n\n"
        "Press ❌ Cancel to stop."
    )


def cancel_payment(user_id):

    from database.payment_db import remove_session

    remove_session(user_id)

    return (
        "❌ PAYMENT CANCELLED\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Your payment process has been cancelled.\n\n"
        "Choose a plan again if you want to continue."
    )


def validate_payment_id(payment_id):

    if not payment_id.isdigit():
        return False

    if len(payment_id) != 12:
        return False

    return True


def process_payment_id(user_id, payment_id):

    from database.payment_db import get_session

    session = get_session(user_id)

    if not session:
        return "❌ No active payment request found."

    if not validate_payment_id(payment_id):
        return (
            "❌ Invalid Payment ID\n\n"
            "Only 12 digit numbers are allowed."
        )

    plan_id, status = session

    return (
        "✅ Payment ID Received\n\n"
        f"Payment ID: {payment_id}\n"
        f"Plan ID: {plan_id}\n\n"
        "Processing your request..."
    )


def create_order_after_payment(user_id, payment_id):

    from database.payment_db import get_session, remove_session
    from services.order_service import create_new_order

    session = get_session(user_id)

    if not session:
        return None

    plan_id, status = session

    from database.plans_db import get_plans
    from database.upi_db import get_active_upi

    amount = None

    for pid, name, days, price in get_plans():
        if pid == plan_id:
            amount = price
            break

    order = create_new_order(
        user_id,
        plan_id,
        payment_id
    )

    remove_session(user_id)

    return order

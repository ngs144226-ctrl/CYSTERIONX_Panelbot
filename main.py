import time
import telebot
from config import BOT_TOKEN
from keyboards.main_menu import main_menu

bot = telebot.TeleBot(BOT_TOKEN)

WEB_APP_URL = "https://cysterionx-panelbot-ltm1.vercel.app"

bot.set_chat_menu_button(
    menu_button=telebot.types.MenuButtonWebApp(
        text="🌐 Open Panel",
        web_app=telebot.types.WebAppInfo(url=WEB_APP_URL)
    )
)

master_key_states = set()
confirm_master_key_states = set()

master_key_confirm_state = set()

@bot.message_handler(commands=['start'])
def start(message):
    from handlers.join_required import send_join_required
    from services.pending_referral import set_pending_referral
    from services.join_checker import is_user_joined
    from database.users_db import save_user

    args = message.text.split()

    referrer_id = None

    if len(args) > 1:
        try:
            referrer_id = int(args[1])
            set_pending_referral(
                message.from_user.id,
                referrer_id
            )
        except:
            pass

    save_user(
        message.from_user.id,
        message.from_user.first_name or "No Name",
        message.from_user.username or "No Username",
        referrer_id
    )

    if not is_user_joined(
        bot,
        message.from_user.id
    ):
        send_join_required(
            bot,
            message
        )
        return

    bot.send_message(
        message.chat.id,
        "Welcome to CYSTERIONX Panel",
        reply_markup=main_menu(message.from_user.id)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("support_status:"))
def support_status_button(call):

    from database.support_db import update_ticket_status, get_ticket
    from services.support_notify import support_ticket_text
    from keyboards.support_admin import support_admin_buttons

    _, status, ticket_id = call.data.split(":")

    update_ticket_status(
        ticket_id,
        status
    )

    bot.answer_callback_query(
        call.id,
        f"Status updated: {status}"
    )

    ticket = get_ticket(ticket_id)

    if ticket:
        data = {
            "ticket_id": ticket[1],
            "user_id": ticket[2],
            "username": ticket[3],
            "category": ticket[4],
            "message": ticket[5],
            "status": status
        }

        try:
            bot.edit_message_text(
                support_ticket_text(data),
                call.message.chat.id,
                call.message.message_id,
                reply_markup=support_admin_buttons(ticket_id, status),
                parse_mode="Markdown"
            )
        except Exception as e:
            print("Support admin edit error:", e)

        try:
            user_message_id = ticket[10]

            bot.edit_message_text(
                support_ticket_text(data),
                chat_id=ticket[2],
                message_id=user_message_id,
                parse_mode="Markdown"
            )
        except Exception as e:
            print("Support user status edit error:", repr(e))

        if status == "Failed":
            try:
                bot.send_message(
                    ticket[2],
                    "❌ SUPPORT FAILED\n\n"
                    "━━━━━━━━━━━━━━━━━━\n\n"
                    f"🎫 Ticket ID     {ticket_id}\n\n"
                    "Unfortunately, your support request could not be resolved.\n\n"
                    "Please contact support again if you still need help.\n\n"
                    "━━━━━━━━━━━━━━━━━━"
                )
            except Exception as e:
                print("Support failed user message error:", e)

            try:
                bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=None
                )
            except Exception as e:
                print("Support failed button remove error:", e)


@bot.callback_query_handler(func=lambda call: call.data.startswith("support_reply:"))
def support_reply_button(call):

    ticket_id = call.data.split(":")[1]

    start_admin_reply(
        bot,
        call,
        ticket_id
    )

    bot.answer_callback_query(
        call.id,
        "Reply mode started"
    )


@bot.message_handler(func=lambda message: get_admin_reply_ticket(message.from_user.id) is not None)
def receive_admin_reply(message):

    if message.text == "❌ Cancel":
        clear_admin_reply(
            message.from_user.id
        )

        from handlers.admin_support import admin_support_menu

        bot.send_message(
            message.chat.id,
            "❌ Reply cancelled.",
            reply_markup=admin_support_menu()
        )
        return

    from database.support_db import add_admin_reply, get_ticket, update_ticket_status

    ticket_id = get_admin_reply_ticket(
        message.from_user.id
    )

    ticket = get_ticket(ticket_id)

    if ticket:
        user_id = ticket[2]

        add_admin_reply(
            ticket_id,
            message.text
        )

        update_ticket_status(
            ticket_id,
            "Success"
        )

        bot.send_message(
            user_id,
            "💬 SUPPORT REPLY\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"🎫 Ticket ID     {ticket_id}\n\n"
            "🛠️ Admin Message:\n\n"
            f"{message.text}\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "✅ SUPPORT CLOSED\n\n"
            "Your ticket has been resolved successfully.\n\n"
            "Thank you for contacting CYSTERIONX Support.\n\n"
            "━━━━━━━━━━━━━━━━━━"
        )

        try:
            from database.support_db import get_ticket
            from services.support_notify import support_ticket_text

            updated_ticket = get_ticket(ticket_id)

            data = {
                "ticket_id": updated_ticket[1],
                "user_id": updated_ticket[2],
                "username": updated_ticket[3],
                "category": updated_ticket[4],
                "message": updated_ticket[5],
                "status": updated_ticket[6]
            }

            bot.edit_message_text(
                support_ticket_text(data),
                chat_id=message.chat.id,
                message_id=ticket[9],
                reply_markup=None,
                parse_mode="Markdown"
            )
            bot.edit_message_text(
                support_ticket_text(data),
                chat_id=user_id,
                message_id=ticket[10],
                parse_mode="Markdown"
            )


        except Exception as e:
            print("Support reply success update error:", e)

    clear_admin_reply(
        message.from_user.id
    )

    from keyboards.main_menu import main_menu

    bot.send_message(
        message.chat.id,
        "✅ Reply sent successfully.",
        reply_markup=main_menu(message.from_user.id)
    )


from handlers.my_profile import my_profile_text
from services.join_guard import check_message


@bot.message_handler(func=lambda message: message.text == "👤 My Profile")

def my_profile_button(message):

    user = message.from_user

    name = user.first_name or "No Name"
    if not check_message(bot, message):
        from handlers.join_required import send_join_required
        send_join_required(bot, message)
        return

    username = user.username or "No Username"

    response = my_profile_text(
        user.id,
        name,
        username
    )

    bot.send_message(
        message.chat.id,
        response
    )

print("CYSTERIONX Panelbot Started...")

from handlers.get_key import handle_get_key

from handlers.admin_support import admin_support_start, show_ticket_categories, ask_ticket_message, get_ticket_category, clear_ticket_category, start_admin_reply, get_admin_reply_ticket, clear_admin_reply, trace_ticket_start, is_trace_ticket_user, clear_trace_ticket, ticket_details_text


@bot.message_handler(func=lambda message: message.text == "🛠️ Admin Support")
def admin_support_button(message):
    if not check_message(bot, message):
        from handlers.join_required import send_join_required
        send_join_required(bot, message)
        return


    admin_support_start(
        bot,
        message
    )


@bot.message_handler(func=lambda message: message.text == "🔎 Trace Ticket")
def trace_ticket_button(message):

    trace_ticket_start(
        bot,
        message
    )



@bot.message_handler(func=lambda message: is_trace_ticket_user(message.from_user.id))
def trace_ticket_input(message):

    if message.text == "❌ Cancel":
        clear_trace_ticket(message.from_user.id)

        from telebot import types

        bot.send_message(
            message.chat.id,
            "✅ Trace Ticket cancelled.",
            reply_markup=main_menu(message.from_user.id)
        )

        return

    from database.support_db import get_ticket, get_user_ticket_by_id, get_ticket_by_id

    ticket_id = message.text.strip()

    ticket = get_user_ticket_by_id(
        ticket_id,
        message.from_user.id
    )

    if ticket:

        clear_trace_ticket(
            message.from_user.id
        )

        bot.send_message(
            message.chat.id,
            ticket_details_text(ticket),
            reply_markup=main_menu(message.from_user.id)
        )

    else:

        existing = get_ticket_by_id(
            ticket_id
        )

        if existing:

            from telebot import types

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row("❌ Cancel")

            bot.send_message(
                message.chat.id,
                "🔒 ACCESS DENIED\n\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "This ticket does not belong "
                "to your account.\n\n"
                "You can only view your own tickets.",
                reply_markup=markup
            )

        else:

            from telebot import types

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row("❌ Cancel")

            bot.send_message(
                message.chat.id,
                "❌ TICKET NOT FOUND\n\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "No ticket found with this ID.\n\n"
                "Please check your Ticket ID.",
                reply_markup=markup
            )

@bot.message_handler(func=lambda message: message.text in [
    "💳 Payment Issue",
    "🔑 Key / Access",
    "📦 Order Issue",
    "⚙️ Other Issue"
])
def ticket_category_button(message):

    ask_ticket_message(
        bot,
        message,
        message.text
    )


@bot.message_handler(func=lambda message: get_ticket_category(message.from_user.id) is not None)
def receive_ticket_message(message):

    if message.text == "❌ Cancel":
        clear_ticket_category(message.from_user.id)

        bot.send_message(
            message.chat.id,
            "🎫 Create Ticket Closed",
            reply_markup=main_menu(message.from_user.id)
        )
        return

    from database.support_db import create_ticket
    from services.support_id import generate_ticket_id

    category = get_ticket_category(
        message.from_user.id
    )

    ticket_id = generate_ticket_id()

    create_ticket(
        ticket_id,
        message.from_user.id,
        message.from_user.username or "No Username",
        category,
        message.text
    )

    clear_ticket_category(
        message.from_user.id
    )

    from services.support_notify import support_ticket_text
    from keyboards.support_admin import support_admin_buttons
    from services.admin_order_notify import get_admin_ids

    ticket_data = {
        "ticket_id": ticket_id,
        "user_id": message.from_user.id,
        "username": message.from_user.username or "No Username",
        "category": category,
        "message": message.text
    }

    for admin_id in get_admin_ids():
        try:
            sent = bot.send_message(
                admin_id,
                support_ticket_text(ticket_data),
                reply_markup=support_admin_buttons(ticket_id),
                parse_mode="Markdown"
            )

            from database.support_db import save_support_message_id

            save_support_message_id(
                ticket_id,
                sent.message_id
            )
        except Exception as e:
            print("Support notify error:", e)

    sent_user = bot.send_message(
        message.chat.id,
        "✅ TICKET CREATED\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🎫 Ticket ID     `{ticket_id}`\n\n"
        f"👤 User ID       {message.from_user.id}\n\n"
        f"👤 Username      @{message.from_user.username or 'No Username'}\n\n"
        f"📌 Category      {category}\n\n"
        f"📝 Message       {message.text}\n\n"
        "📌 Status        Pending\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Your request has been sent to support.",
        parse_mode="Markdown"
    )

    from database.support_db import save_user_message_id

    save_user_message_id(
        ticket_id,
        sent_user.message_id
    )

    from handlers.admin_support import admin_support_menu
    from telebot import types

    bot.send_message(
        message.chat.id,
        "Returning to Support Menu",
        reply_markup=admin_support_menu()
    )

create_ticket_category_users = set()

@bot.message_handler(func=lambda message: message.text == "🎫 Create Ticket")
def new_ticket_button(message):

    create_ticket_category_users.add(message.from_user.id)

    show_ticket_categories(
        bot,
        message
    )

@bot.message_handler(func=lambda message: message.text == "❌ Cancel" and message.from_user.id in create_ticket_category_users)
def create_ticket_category_cancel(message):

    create_ticket_category_users.discard(message.from_user.id)

    bot.send_message(
        message.chat.id,
        "🎫 Create Ticket Closed",
        reply_markup=main_menu(message.from_user.id)
    )

def admin_support_button(message):

    admin_support_start(
        bot,
        message
    )


from handlers.trace_order import trace_order
from services.trace_order_message import trace_order_text

waiting_trace_users = set()


@bot.message_handler(func=lambda message: message.text == "📦 Trace Order")
def trace_order_button(message):
    if not check_message(bot, message):
        from handlers.join_required import send_join_required
        send_join_required(bot, message)
        return


    waiting_trace_users.add(
        message.from_user.id
    )

    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("❌ Cancel")

    bot.send_message(
        message.chat.id,
        "📦 TRACE ORDER\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Send your Order ID to check status.\n\n"
        "Example  CY-2026-TTHQ-23LL\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Send ❌ Cancel to exit.",
        reply_markup=markup
    )




@bot.message_handler(func=lambda message: message.text == "❌ Cancel" and message.from_user.id in waiting_trace_users)
def cancel_trace_order(message):

    waiting_trace_users.discard(
        message.from_user.id
    )

    from telebot import types

    bot.send_message(
        message.chat.id,
        "✅ Trace Order cancelled.",
        reply_markup=main_menu(message.from_user.id)
    )


@bot.message_handler(func=lambda message: message.from_user.id in waiting_trace_users)
def trace_order_input(message):

    if not message.text.startswith("CY-"):
        bot.send_message(
            message.chat.id,
            "❌ Invalid Order ID format.\n\n"
            "Example:\nCY-2026-TTHQ-23LL"
        )
        return

    result = trace_order(
        message.text,
        message.from_user.id
    )

    if result["status"] == "success":
        waiting_trace_users.discard(
            message.from_user.id
        )

    from telebot import types

    bot.send_message(
        message.chat.id,
        trace_order_text(result),
        reply_markup=main_menu(message.from_user.id) if result["status"] == "success" else types.ReplyKeyboardMarkup(resize_keyboard=True).add("❌ Cancel")
    )

from handlers.referral_start import handle_referral_start

@bot.message_handler(func=lambda message: message.text == "🔑 Get Key")
def get_key_button(message):
    if not check_message(bot, message):
        from handlers.join_required import send_join_required
        send_join_required(bot, message)
        return

    response = handle_get_key(message.from_user.id)
    bot.send_message(
        message.chat.id,
        response,
        parse_mode="Markdown"
    )


from handlers.refer_earn import handle_refer_earn
from handlers.extend_access import handle_extend_access
from handlers.extend_access import get_plan_id_from_button, plan_details_text

@bot.message_handler(func=lambda message: message.text == "🎁 Refer & Earn")
def refer_earn_button(message):
    if not check_message(bot, message):
        from handlers.join_required import send_join_required
        send_join_required(bot, message)
        return

    response = handle_refer_earn(message.from_user.id)
    bot.send_message(
        message.chat.id,
        response
    )

@bot.message_handler(func=lambda message: message.text == "⚡ Extend Access")
def extend_access_button(message):
    if not check_message(bot, message):
        from handlers.join_required import send_join_required
        send_join_required(bot, message)
        return

    handle_extend_access(bot, message)


@bot.message_handler(func=lambda message: message.text == "⬅️ Back")
def back_button(message):
    bot.send_message(
        message.chat.id,
        "Back to Main Menu",
        reply_markup=main_menu(message.from_user.id)
    )


@bot.message_handler(func=lambda message: get_plan_id_from_button(message.text) is not None)
def plan_button(message):
    plan_id = get_plan_id_from_button(message.text)

    from handlers.extend_access import start_payment_session
    from keyboards.payment import payment_cancel_menu

    bot.send_message(
        message.chat.id,
        plan_details_text(plan_id),
        parse_mode="Markdown"
    )

    bot.send_message(
        message.chat.id,
        start_payment_session(
            message.from_user.id,
            plan_id
        ),
        reply_markup=payment_cancel_menu()
    )


@bot.message_handler(func=lambda message: message.text == "🔙 Close Admin Support")
def close_admin_support_button(message):
    bot.send_message(
        message.chat.id,
        "✅ Admin Support Closed",
        reply_markup=main_menu(message.from_user.id)
    )


@bot.message_handler(func=lambda message:
    message.text == "❌ Cancel"
    and message.from_user.id not in waiting_extend_action
    and message.from_user.id not in waiting_user_data
    and message.from_user.id not in waiting_admin_orders
    and message.from_user.id not in waiting_trace_users
      and message.from_user.id not in plan_details_states
      and message.from_user.id not in plan_details_states
    and message.from_user.id not in waiting_master_increase_key
    and message.from_user.id not in waiting_master_increase_time
    and message.from_user.id not in waiting_master_decrease_key
    and message.from_user.id not in waiting_master_decrease_time
      and message.from_user.id not in total_users_states
    and message.from_user.id not in create_ticket_category_users
)
def cancel_button(message):

    from database.payment_db import get_session
    from telebot import types

    session = get_session(
        message.from_user.id
    )

    if not session:
        bot.send_message(
            message.chat.id,
            "✅ Returned to Main Menu",
            reply_markup=main_menu(message.from_user.id)
        )
        return

    from handlers.extend_access import cancel_payment

    response = cancel_payment(
        message.from_user.id
    )

    bot.send_message(
        message.chat.id,
        response,
        reply_markup=main_menu(message.from_user.id)
    )



@bot.message_handler(func=lambda message: message.text.isdigit() and len(message.text) == 12)
def payment_id_handler(message):

    from handlers.extend_access import create_order_after_payment
    from services.order_message import order_created_text
    from database.orders_db import save_order_message_id

    from database.payment_db import get_session

    if not get_session(message.from_user.id):
        return

    order = create_order_after_payment(
        message.from_user.id,
        message.text
    )

    if not order:
        bot.send_message(
            message.chat.id,
            "❌ No active payment request found."
        )
        return

    text = order_created_text(
        order["order_id"]
    )

    from telebot import types

    sent = bot.send_message(
        message.chat.id,
        text,
        parse_mode="Markdown"
    )

    save_order_message_id(
        order["order_id"],
        sent.message_id
    )

    bot.send_message(
        message.chat.id,
        "✅ Order Created Successfully",
        reply_markup=main_menu(message.from_user.id)
    )

    from services.admin_order_notify import (
        get_admin_ids,
        admin_order_text
    )
    from keyboards.admin_order import order_admin_buttons

    admin_data = {
        "order_id": order["order_id"],
        "user_id": message.from_user.id,
        "plan_id": order["plan_id"],
        "amount": order["amount"],
        "payment_id": message.text
    }

    for admin_id in get_admin_ids():
        try:
            sent = bot.send_message(
                admin_id,
                admin_order_text(admin_data),
                reply_markup=order_admin_buttons(
                    order["order_id"]
                ),
                disable_notification=False,
                parse_mode="Markdown"
            )

            from database.orders_db import save_admin_message_id, save_admin_chat_id, save_order_admin_message

            save_admin_message_id(
                order["order_id"],
                sent.message_id
            )

            save_admin_chat_id(
                order["order_id"],
                admin_id
            )

            save_order_admin_message(
                order["order_id"],
                admin_id,
                sent.message_id
            )
        except Exception as e:
            print("Admin notify error:", e)

from database.orders_db import update_order_status, delete_order
from handlers.join_required import verify_join_callback


@bot.callback_query_handler(
    func=lambda call: call.data == "verify_join"
)
def verify_join_button(call):

    verify_join_callback(
        bot,
        call
    )




@bot.callback_query_handler(
    func=lambda call: call.data.startswith(
        ("processing:", "success:", "failed:", "delete:")
    )
)
def admin_order_callback(call):

    order_data = call.data.split(":")
    action = order_data[0]
    order_id = order_data[1]


    def update_control_order_view():

        from database.orders_db import get_control_order_message
        from services.order_status_message import order_status_text
        from keyboards.control_order import control_order_buttons

        data = get_control_order_message(order_id)

        if data:
            chat_id, message_id = data

            try:
                bot.edit_message_text(
                    order_status_text(order_id, admin=True),
                    chat_id,
                    message_id,
                    reply_markup=control_order_buttons(order_id),
                    parse_mode="Markdown"
                )
            except Exception as e:
                print("Control order edit error:", e)


    if action == "processing":
        update_order_status(
            order_id,
            "Processing"
        )

        edit_user_order_message(order_id)
        edit_admin_order_message(order_id)
        update_control_order_view()

        bot.answer_callback_query(
            call.id,
            "⚙️ Order Processing"
        )


    elif action == "success":

        from database.orders_db import get_order_by_id
        from services.access_time_service import add_access_time
        from database.plans_db import get_plans
        from database.keys_db import update_plan_name

        order = get_order_by_id(order_id)

        if order:
            user_id = order[2]
            plan_id = order[3]

            from database.keys_db import get_key
            print("DEBUG SUCCESS USER:", user_id)
            print("DEBUG KEY DATA:", get_key(user_id))

            hours = 0
            plan_name = None

            print("DEBUG ORDER PLAN ID:", plan_id)
            print("DEBUG AVAILABLE PLANS:", get_plans())

            for pid, name, days, price in get_plans():
                if pid == plan_id:
                    hours = days * 24
                    plan_name = name
                    break

            print("DEBUG FINAL PLAN NAME:", plan_name)

            if hours:
                add_access_time(
                    user_id,
                    hours
                )

            if plan_name:
                update_plan_name(
                    user_id,
                    plan_name
                )

                print("DEBUG PLAN SAVED:", user_id, plan_name)

            from database.referrals_db import get_referrer
            from services.referral_service import process_deposit_reward

            referrer_id = get_referrer(user_id)

            if referrer_id:
                process_deposit_reward(
                    bot,
                    referrer_id,
                    user_id
                )

        update_order_status(
            order_id,
            "Success"
        )

        edit_user_order_message(order_id)
        edit_admin_order_message(order_id)
        update_control_order_view()

        from database.orders_db import get_order_by_id

        order_data = get_order_by_id(order_id)

        if order_data:
            bot.send_message(
                order_data[2],
                "✅ PAYMENT APPROVED\n\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "Your plan has been activated successfully.\n\n"
                "You can check your access from My Profile.\n\n"
                "━━━━━━━━━━━━━━━━━━"
            )

        bot.answer_callback_query(
            call.id,
            "✅ Order Success"
        )


    elif action == "failed":
        update_order_status(
            order_id,
            "Failed"
        )

        edit_user_order_message(order_id)
        edit_admin_order_message(order_id)
        update_control_order_view()

        from database.orders_db import get_order_by_id
        from database.payment_db import create_session

        order_data = get_order_by_id(order_id)

        if order_data:
            bot.send_message(
                order_data[2],
                "❌ PAYMENT FAILED\n\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "Your payment was not approved.\n"
                "Please contact support if you think this is a mistake.\n\n"
                "━━━━━━━━━━━━━━━━━━"
            )

        bot.answer_callback_query(
            call.id,
            "❌ Order Failed"
        )


    elif action == "delete":

        from database.orders_db import get_order_by_id

        order = get_order_by_id(order_id)

        if order:
            user_id = order[2]
            user_message_id = order[8]
            admin_message_id = order[9]

            try:
                if user_message_id:
                    bot.delete_message(
                        user_id,
                        user_message_id
                    )
            except Exception as e:
                print("User delete error:", e)

            try:
                if admin_message_id:
                    bot.delete_message(
                        call.message.chat.id,
                        admin_message_id
                    )
            except Exception as e:
                print("Admin delete error:", e)

        delete_order(order_id)

        bot.answer_callback_query(
            call.id,
            "🗑 Order Deleted"
        )


def edit_user_order_message(order_id):

    from database.orders_db import get_order_by_id, save_order_message_id
    from services.order_status_message import order_status_text

    order = get_order_by_id(order_id)

    if not order:
        return

    _id, oid, user_id, plan_id, payment_id, amount, status, created_at, message_id, admin_message_id, admin_chat_id = order

    if message_id:

        try:
            bot.edit_message_text(
                order_status_text(order_id),
                user_id,
                message_id,
                parse_mode="Markdown"
            )

        except Exception as e:
            print("User order update error:", e)


def edit_admin_order_message(order_id):

    from database.orders_db import get_order_admin_messages
    from services.order_status_message import order_status_text
    from keyboards.admin_order import order_admin_buttons

    rows = get_order_admin_messages(order_id)

    for admin_chat_id, admin_message_id in rows:
        try:
            bot.edit_message_text(
                order_status_text(order_id, admin=True),
                admin_chat_id,
                admin_message_id,
                reply_markup=order_admin_buttons(order_id),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Admin {admin_chat_id} edit error:", e)



from keyboards.control_hub import control_hub_menu

@bot.message_handler(func=lambda message: message.text == "🎛️ Control Hub")
def control_hub(message):

    bot.send_message(
        message.chat.id,
        "🎛️ CONTROL HUB\n\nSelect Action",
        reply_markup=control_hub_menu()
    )









total_users_states = set()

# ================= TOTAL USERS VIEW =================

@bot.message_handler(func=lambda message: message.text == "👥 Total Users")
def total_users_view(message):

    total_users_states.add(message.from_user.id)

    import sqlite3
    from database.orders_db import get_success_orders_count

    conn = sqlite3.connect("cysterionx.db")
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    conn.close()

    paid_count = get_success_orders_count()

    from telebot import types

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("❌ Cancel")

    bot.send_message(
        message.chat.id,
        "👥 TOTAL USERS\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 Registered Users : {total_users}\n\n"
        f"💎 Paid Plans Sold : {paid_count}\n\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text == "❌ Cancel" and message.from_user.id in total_users_states)
def total_users_cancel(message):

    total_users_states.discard(message.from_user.id)

    from keyboards.control_hub import control_hub_menu

    bot.send_message(
        message.chat.id,
        "✅ Total Users Closed",
        reply_markup=control_hub_menu()
    )




# ================= PLAN DETAILS VIEW =================

plan_details_states = set()

@bot.message_handler(func=lambda message: message.text == "📊 Plan Details")
def plan_details_view(message):

    plan_details_states.add(message.from_user.id)

    import sqlite3
    from telebot import types
    from database.plans_db import get_plans

    conn = sqlite3.connect("cysterionx.db")
    cur = conn.cursor()

    plans = get_plans()

    text = "📊 PLAN DETAILS\n\n"
    text += "━━━━━━━━━━━━━━━━━━\n\n"

    for plan_id, name, days, price in sorted(plans, key=lambda x: x[3]):

        cur.execute(
            "SELECT COUNT(*) FROM orders WHERE plan_id=? AND status='Success'",
            (plan_id,)
        )

        count = cur.fetchone()[0]

        if name == "Basic Plan":
            icon = "🥉"
        elif name == "Pro Plan":
            icon = "🥈"
        else:
            icon = "🥇"

        text += f"{icon} {name}\n👥 Active Sales : {count}\n\n━━━━━━━━━━━━━━━━━━\n\n"

    conn.close()


    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("❌ Cancel")

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text == "❌ Cancel" and message.from_user.id in plan_details_states)
def plan_details_cancel(message):

    plan_details_states.discard(message.from_user.id)

    from keyboards.control_hub import control_hub_menu

    bot.send_message(
        message.chat.id,
        "✅ Plan Details Closed",
        reply_markup=control_hub_menu()
    )


# ================= CONTROL HUB USER DATA =================



def master_generator_menu():
    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row(
        "✨ CONFIRM GENERATION"
    )

    markup.row(
        "⏫ Increase Access",
        "⏬ Decrease Access"
    )

    markup.row(
        "❌ CANCEL"
    )

    return markup

waiting_user_data = set()




@bot.message_handler(func=lambda message: message.text == "🗝️ Generate Key")
def generate_master_key_start(message):

    master_key_states.add(message.from_user.id)

    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row(
        "✨ CONFIRM GENERATION"
    )

    markup.row(
        "⏫ Increase Access",
        "⏬ Decrease Access"
    )

    markup.row(
        "❌ CANCEL"
    )

    bot.send_message(
        message.chat.id,
        "🔑 GENERATE MASTER KEY\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Create a new\n"
        "Special Master Key.\n\n"
        "━━━━━━━━━━━━━━━━━━━━",
        reply_markup=markup
    )



@bot.message_handler(func=lambda message: message.text == "✨ CONFIRM GENERATION")
def confirm_master_key_generation(message):

    confirm_master_key_states.add(message.from_user.id)

    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row(
        "✅ CONFIRM"
    )

    markup.row(
        "❌ CANCEL"
    )

    bot.send_message(
        message.chat.id,
        "✨ CONFIRM GENERATION\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Generate a new\n"
        "Special Master Key?\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Press Confirm to continue.\n\n"
        "━━━━━━━━━━━━━━━━━━━━",
        reply_markup=markup
    )



@bot.message_handler(func=lambda message: message.text == "✅ CONFIRM")
def generate_master_key_final(message):

    from services.master_key_service import generate_master_key

    key = generate_master_key()

    confirm_master_key_states.discard(message.from_user.id)
    waiting_master_extend_key[message.from_user.id] = key

    bot.send_message(
        message.chat.id,
        "✅ MASTER KEY GENERATED\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔑 Key\n\n"
        f"`{key}`\n\n"
        "🌐 Type     Special Master Key\n\n"
        "📶 Status   🔴 Inactive\n\n"
        "━━━━━━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )

    from telebot import types

    # clear generator state after successful creation
    master_key_states.discard(message.from_user.id)
    confirm_master_key_states.discard(message.from_user.id)
    master_key_confirm_state.discard(message.from_user.id)

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("✨ CONFIRM GENERATION")
    markup.row("⏫ Increase Access", "⏬ Decrease Access")
    markup.row("❌ CANCEL")

    bot.send_message(
        message.chat.id,
        "🔑 MASTER KEY ACCESS\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Select Action\n\n"
        "━━━━━━━━━━━━━━━━━━━━",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "👤 User Data")
def user_data_button(message):

    waiting_user_data.add(
        message.from_user.id
    )

    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("❌ Cancel")

    bot.send_message(
        message.chat.id,
        "👤 USER DATA\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send User ID or Username\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text == "❌ Cancel" and message.from_user.id in waiting_user_data)
def cancel_user_data(message):

    waiting_user_data.discard(
        message.from_user.id
    )

    bot.send_message(
        message.chat.id,
        "✅ User Data closed.",
        reply_markup=control_hub_menu()
    )


@bot.message_handler(func=lambda message: message.from_user.id in waiting_user_data)
def search_user_data(message):

    from services.user_data_service import get_user_data_view
    from database.users_db import get_user

    query = message.text.strip()

    user_id = None

    if query.isdigit():
        user_id = int(query)

    else:
        from database.users_db import connect

        con = connect()
        cur = con.cursor()

        cur.execute(
            "SELECT user_id FROM users WHERE username=?",
            (query.replace("@",""),)
        )

        row = cur.fetchone()

        con.close()

        if row:
            user_id = row[0]


    if not user_id or not get_user(user_id):

        bot.send_message(
            message.chat.id,
            "❌ USER NOT FOUND\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "No user record found.\n\n"
            "Please check User ID or Username.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━",
        )

        return


    waiting_user_data.discard(
        message.from_user.id
    )


    bot.send_message(
        message.chat.id,
        get_user_data_view(user_id),
        reply_markup=control_hub_menu()
    )




# ================= CONTROL HUB EXTEND KEY =================

waiting_extend_action = set()

waiting_master_extend_key = {}

def master_key_details_menu():
    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )


    markup.row(
        "⏫ Increase Access",
        "⏬ Decrease Access"
    )

    markup.row(
        "❌ Cancel"
    )

    return markup

waiting_master_access_action = set()

waiting_master_increase_key = set()
waiting_master_increase_time = {}
waiting_master_decrease_key = set()
waiting_master_decrease_time = {}


@bot.message_handler(func=lambda message: message.text == "🔑 Extend Key")
def extend_key_button(message):

    waiting_extend_action.add(
        message.from_user.id
    )

    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("➕ Add Time", "➖ Remove Time")
    markup.row("❌ Cancel")

    bot.send_message(
        message.chat.id,
        "🔑 EXTEND KEY\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Select Action\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: (
    message.text == "❌ Cancel"
    and message.from_user.id in waiting_extend_action
    and message.from_user.id not in waiting_extend_add_key
    and message.from_user.id not in waiting_extend_add_time
    and message.from_user.id not in waiting_extend_remove_key
    and message.from_user.id not in waiting_extend_remove_time
))
def cancel_extend_key(message):

    if (
        message.from_user.id in waiting_extend_add_key
        or message.from_user.id in waiting_extend_add_time
        or message.from_user.id in waiting_extend_remove_key
        or message.from_user.id in waiting_extend_remove_time
    ):
        return

    waiting_extend_action.discard(
        message.from_user.id
    )

    bot.send_message(
        message.chat.id,
        "✅ Extend Key closed.",
        reply_markup=control_hub_menu()
    )




# ================= EXTEND KEY ADD TIME =================

waiting_extend_add_key = set()
waiting_extend_add_time = {}
waiting_extend_remove_key = set()
waiting_extend_remove_time = {}


@bot.message_handler(func=lambda message: message.text == "➕ Add Time" and message.from_user.id in waiting_extend_action)
def add_time_start(message):

    waiting_extend_add_key.add(
        message.from_user.id
    )

    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("❌ Cancel")

    bot.send_message(
        message.chat.id,
        "➕ ADD TIME\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send Key\n\n"
        "Example:\n"
        "CYX-8T4A-2KLM-91QP\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.from_user.id in waiting_extend_add_key and message.text != "❌ Cancel" and message.from_user.id not in waiting_master_extend_key)
def check_add_time_key(message):

    from telebot import types
    from database.keys_db import get_key_by_value
    key = message.text.strip()

    data = get_key_by_value(key)

    if not data:

        bot.send_message(
            message.chat.id,
            "❌ KEY NOT FOUND\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Please check your key.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        return


    from datetime import datetime
    from services.time_parser import format_remaining

    waiting_extend_add_key.discard(
        message.from_user.id
    )

    waiting_extend_add_time[message.from_user.id] = data["user_id"]

    expire = data.get("expire_time")

    if not expire or expire <= datetime.now():

        remaining_text = "Expired"

    else:

        diff = expire - datetime.now()

        remaining_minutes = round(diff.total_seconds() / 60)

        remaining_text = format_remaining(
            remaining_minutes
        )


    bot.send_message(
        message.chat.id,
        "🔑 KEY DETAILS\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔑 Key        {data['key_value']}\n\n"
        f"📶 Status     {("Inactive" if expire and expire <= datetime.now() else data['key_status'])}\n\n"
        f"⏳ Remaining  {remaining_text}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send Add Time\n\n"
        "Format:\n"
        "+10m\n"
        "+5h\n"
        "+1d\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("❌ Cancel")
    )




@bot.message_handler(func=lambda message: message.from_user.id in waiting_extend_add_time)
def process_add_time(message):

    from services.time_parser import parse_time, format_remaining
    from database.keys_db import get_key, update_key_expiry_minutes, clear_plan_name
    from datetime import datetime

    value = message.text.strip()

    if value == "❌ Cancel":
        waiting_extend_add_time.pop(message.from_user.id, None)
        waiting_extend_add_key.discard(message.from_user.id)
        waiting_extend_action.add(message.from_user.id)

        from telebot import types
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("➕ Add Time", "➖ Remove Time")
        markup.row("❌ Cancel")

        bot.send_message(
            message.chat.id,
            "🔑 EXTEND KEY\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Select Action\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=markup
        )
        return

    minutes = parse_time(value)

    if minutes is None or minutes <= 0:

        bot.send_message(
            message.chat.id,
            "❌ INVALID TIME FORMAT\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Add Time accepts only:\n\n"
            "+10m\n"
            "+5h\n"
            "+1d\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        return


    user_id = waiting_extend_add_time.get(
        message.from_user.id
    )

    data = get_key(user_id)

    if not data:

        bot.send_message(
            message.chat.id,
            "❌ KEY DATA NOT FOUND"
        )
        waiting_extend_add_time.pop(
            message.from_user.id,
            None
        )
        return


    if update_key_expiry_minutes(user_id, minutes):

        updated = get_key(user_id)

        expire = updated.get("expire_time")

        remaining = "Expired"

        if expire and expire > datetime.now():

            diff = expire - datetime.now()

            remaining = format_remaining(
                round(diff.total_seconds() / 60)
            )


        bot.send_message(
            message.chat.id,
            "✅ TIME ADDED\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔑 Key        {updated['key_value']}\n\n"
            f"➕ Added      {value}\n\n"
            f"⏳ Remaining  {remaining}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━"
        )

    else:

        bot.send_message(
            message.chat.id,
            "❌ FAILED TO UPDATE TIME"
        )


    waiting_extend_add_time.pop(
        message.from_user.id,
        None
    )

    waiting_extend_add_key.add(
        message.from_user.id
    )

    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )
    markup.row("❌ Cancel")

    bot.send_message(
        message.chat.id,
        "➕ ADD TIME\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send another Key\n\n"
        "Example:\n"
        "CYX-XXXX-XXXX-XXXX\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=markup
    )




# ================= EXTEND KEY REMOVE TIME =================

@bot.message_handler(func=lambda message: message.text == "➖ Remove Time" and message.from_user.id in waiting_extend_action)
def remove_time_start(message):

    waiting_extend_remove_key.add(
        message.from_user.id
    )

    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("❌ Cancel")

    bot.send_message(
        message.chat.id,
        "➖ REMOVE TIME\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send Key\n\n"
        "Example:\n"
        "CYX-8T4A-2KLM-91QP\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.from_user.id in waiting_extend_remove_key and message.text != "❌ Cancel" and message.from_user.id not in waiting_master_extend_key)
def check_remove_time_key(message):

    from telebot import types
    from database.keys_db import get_key_by_value
    key = message.text.strip()

    data = get_key_by_value(key)

    if not data:

        bot.send_message(
            message.chat.id,
            "❌ KEY NOT FOUND\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Please check your key.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        return


    from datetime import datetime
    from services.time_parser import format_remaining

    waiting_extend_remove_key.discard(
        message.from_user.id
    )

    waiting_extend_remove_time[message.from_user.id] = data["user_id"]

    expire = data.get("expire_time")

    if not expire or expire <= datetime.now():
        remaining_text = "Expired"
    else:
        diff = expire - datetime.now()
        remaining_text = format_remaining(
            round(diff.total_seconds() / 60)
        )


    bot.send_message(
        message.chat.id,
        "🔑 KEY DETAILS\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔑 Key        {data['key_value']}\n\n"
        f"📶 Status     {("Inactive" if expire and expire <= datetime.now() else data["key_status"])}\n\n"
        f"⏳ Remaining  {remaining_text}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send Remove Time\n\n"
        "Example:\n"
        "-10m\n"
        "-5h\n"
        "-1d\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("❌ Cancel")
    )




@bot.message_handler(func=lambda message: message.from_user.id in waiting_extend_remove_time)
def process_remove_time(message):

    from services.time_parser import parse_time, format_remaining
    from database.keys_db import get_key, update_key_expiry_minutes, clear_plan_name
    from datetime import datetime


    value = message.text.strip()

    if value == "❌ Cancel":
        waiting_extend_remove_time.pop(message.from_user.id, None)
        waiting_extend_remove_key.discard(message.from_user.id)
        waiting_extend_action.add(message.from_user.id)

        from telebot import types
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("➕ Add Time", "➖ Remove Time")
        markup.row("❌ Cancel")

        bot.send_message(
            message.chat.id,
            "🔑 EXTEND KEY\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Select Action\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=markup
        )
        return

    minutes = parse_time(value)


    if minutes is None or minutes >= 0:

        bot.send_message(
            message.chat.id,
            "❌ INVALID REMOVE TIME\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Remove Time accepts only:\n\n"
            "-10m\n"
            "-5h\n"
            "-1d\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        return


    remove_minutes = abs(minutes)


    user_id = waiting_extend_remove_time.get(
        message.from_user.id
    )


    data = get_key(user_id)


    if not data:

        bot.send_message(
            message.chat.id,
            "❌ KEY DATA NOT FOUND"
        )

        waiting_extend_remove_time.pop(
            message.from_user.id,
            None
        )

        return



    expire = data.get("expire_time")


    if not expire or expire <= datetime.now():

        bot.send_message(
            message.chat.id,
            "❌ CANNOT REMOVE TIME\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Current Remaining 0 Minutes\n\n"
            "Key is already expired.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        return



    current_minutes = int(
        (expire - datetime.now()).total_seconds() // 60
    )


    if remove_minutes > current_minutes:

        bot.send_message(
            message.chat.id,
            "❌ CANNOT REMOVE TIME\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Current Remaining {format_remaining(current_minutes)}\n\n"
            f"You tried to remove {format_remaining(remove_minutes)}.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━"
        )

        return



    if update_key_expiry_minutes(
        user_id,
        -remove_minutes
    ):

        updated = get_key(user_id)

        new_expire = updated.get("expire_time")

        if not new_expire or new_expire <= datetime.now():
            clear_plan_name(user_id)
            updated = get_key(user_id)

        if updated.get("key_status") == "Expired":
            clear_plan_name(user_id)
            updated = get_key(user_id)

        remaining = int(
            (new_expire - datetime.now()).total_seconds() // 60
        )


        bot.send_message(
            message.chat.id,
            "✅ TIME REMOVED\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔑 Key        {updated['key_value']}\n\n"
            f"➖ Removed    {value}\n\n"
            f"⏳ Remaining  {format_remaining(remaining)}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━"
        )

    else:

        bot.send_message(
            message.chat.id,
            "❌ FAILED TO REMOVE TIME"
        )


    waiting_extend_remove_time.pop(
        message.from_user.id,
        None
    )

    waiting_extend_remove_key.add(
        message.from_user.id
    )

    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )
    markup.row("❌ Cancel")

    bot.send_message(
        message.chat.id,
        "➖ REMOVE TIME\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send another Key\n\n"
        "Example:\n"
        "CYX-XXXX-XXXX-XXXX\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=markup
    )






@bot.message_handler(func=lambda message: message.text == "❌ Cancel" and (
    message.from_user.id in waiting_extend_add_key
    or message.from_user.id in waiting_extend_add_time
    or message.from_user.id in waiting_extend_remove_key
    or message.from_user.id in waiting_extend_remove_time
))
def cancel_extend_inner(message):

    waiting_extend_add_key.discard(
        message.from_user.id
    )

    waiting_extend_add_time.pop(
        message.from_user.id,
        None
    )

    waiting_extend_remove_key.discard(
        message.from_user.id
    )

    waiting_extend_remove_time.pop(
        message.from_user.id,
        None
    )

    waiting_extend_action.add(
        message.from_user.id
    )

    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("➕ Add Time", "➖ Remove Time")
    markup.row("❌ Cancel")

    bot.send_message(
        message.chat.id,
        "🔑 EXTEND KEY\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Select Action\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=markup
    )


# ================= CONTROL HUB ORDERS =================

waiting_admin_orders = set()


@bot.message_handler(func=lambda message: message.text == "📦 Orders")
def control_orders_button(message):

    waiting_admin_orders.add(
        message.from_user.id
    )

    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("❌ Cancel")

    bot.send_message(
        message.chat.id,
        "📦 ORDERS\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Send Order ID to view details.\n\n"
        "Example:  CY-2026-TTHQ-23LL\n\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=markup
    )



@bot.message_handler(func=lambda message: message.text == "❌ Cancel" and message.from_user.id in waiting_admin_orders)
def cancel_admin_orders(message):

    waiting_admin_orders.discard(
        message.from_user.id
    )

    bot.send_message(
        message.chat.id,
        "✅ Orders closed.",
        reply_markup=control_hub_menu()
    )


@bot.message_handler(func=lambda message: message.from_user.id in waiting_admin_orders)
def admin_orders_input(message):

    import re

    if not re.match(r"^CY-\d{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$", message.text):
        bot.send_message(
            message.chat.id,
            "❌ Invalid Order ID format.\n\n"
            "Example:\n"
            "CY-2026-TTHQ-23LL"
        )
        return


    from database.orders_db import get_order_by_id
    from services.order_status_message import order_status_text
    from keyboards.control_order import control_order_buttons


    order = get_order_by_id(
        message.text
    )


    if not order:
        bot.send_message(
            message.chat.id,
            "❌ ORDER NOT FOUND\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "The Order ID you entered\n"
            "does not exist.\n\n"
            "Please check your Order ID\n"
            "and try again.\n\n"
            "━━━━━━━━━━━━━━━━━━",
            reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("❌ Cancel")
        )
        return


    waiting_admin_orders.discard(
        message.from_user.id
    )


    sent = bot.send_message(
        message.chat.id,
        order_status_text(message.text),
        reply_markup=control_order_buttons(message.text),
        parse_mode="Markdown"
    )

    from database.orders_db import save_control_order_message
    from keyboards.control_hub import control_hub_menu

    save_control_order_message(
        message.text,
        message.chat.id,
        sent.message_id
    )

    bot.send_message(
        message.chat.id,
        "✅ Control Hub",
        reply_markup=control_hub_menu()
    )






@bot.message_handler(func=lambda message: message.text == "❌ CANCEL")
def master_key_cancel_back(message):

    from telebot import types
    from keyboards.control_hub import control_hub_menu

    if message.from_user.id in confirm_master_key_states:
        confirm_master_key_states.discard(message.from_user.id)

        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True
        )

        markup.row("✨ CONFIRM GENERATION")
        markup.row("⏫ Increase Access", "⏬ Decrease Access")
        markup.row("❌ CANCEL")

        bot.send_message(
            message.chat.id,
            "🔑 GENERATE MASTER KEY\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Create a new\n"
            "Special Master Key.\n\n"
            "━━━━━━━━━━━━━━━━━━━━",
            reply_markup=markup
        )
        return

    master_key_states.discard(message.from_user.id)
    confirm_master_key_states.discard(message.from_user.id)
    master_key_confirm_state.discard(message.from_user.id)
    waiting_master_extend_key.pop(message.from_user.id, None)

    bot.send_message(
        message.chat.id,
        "✅ Generator Key Closed",
        reply_markup=control_hub_menu()
    )











# ================= MASTER KEY INCREASE ACCESS =================

@bot.message_handler(func=lambda message: message.text == "⏫ Increase Access")
def master_increase_start(message):

    waiting_master_access_action.discard(
        message.from_user.id
    )

    waiting_master_increase_key.add(
        message.from_user.id
    )

    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("❌ Cancel")

    bot.send_message(
        message.chat.id,
        "⏫ INCREASE ACCESS\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send Master Key\n\n"
        "Example:  MASXXXXXXXXXXXX\n\n"
        "━━━━━━━━━━━━━━━━━━━━",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.from_user.id in waiting_master_increase_key)
def master_increase_check_key(message):

    from datetime import datetime

    from database.master_keys_db import get_master_key
    from services.master_key_service import get_master_remaining

    key = message.text.strip()

    if key == "❌ Cancel":
        waiting_master_increase_key.discard(
            message.from_user.id
        )

        waiting_master_increase_time.pop(
            message.from_user.id,
            None
        )

        waiting_master_access_action.discard(
            message.from_user.id
        )

        from telebot import types

        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True
        )

        markup.row("✨ CONFIRM GENERATION")
        markup.row("⏫ Increase Access", "⏬ Decrease Access")
        markup.row("❌ CANCEL")

        bot.send_message(
            message.chat.id,
            "🔑 MASTER KEY ACCESS\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Select Action\n\n"
            "━━━━━━━━━━━━━━━━━━━━",
            reply_markup=markup
        )
        return


    if not key.startswith("MAS"):

        bot.send_message(
            message.chat.id,
            "❌ INVALID MASTER KEY FORMAT\n\n"
            "Please send valid Master Key.\n\n"
            "Example:\n"
            "MASXXXXXXXXXXXX"
        )
        return


    data = get_master_key(key)

    if not data:

        bot.send_message(
            message.chat.id,
            "❌ MASTER KEY NOT FOUND"
        )
        return


    waiting_master_increase_key.discard(
        message.from_user.id
    )

    waiting_master_increase_time[message.from_user.id] = key

    bot.send_message(
        message.chat.id,
        "🔑 MASTER KEY DETAILS\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔑 Key        {data['master_key']}\n\n"
        f"🌐 Type       {data['key_type']}\n\n"
        f"📶 Status     {("Active" if data.get("expire_time") and data["expire_time"] > datetime.now() else "Expired")}\n\n"
        f"⏳ Remaining  {get_master_remaining(data.get('expire_time'))}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send Time\n\n"
        "Format:\n"
        "+10m\n"
        "+5h\n"
        "+1d\n\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )


@bot.message_handler(func=lambda message: message.from_user.id in waiting_master_increase_time)
def process_master_increase_time(message):

    from telebot import types
    from services.time_parser import parse_time, format_remaining
    from database.master_keys_db import update_master_key_expiry_minutes, get_master_key
    from datetime import datetime

    value = message.text.strip()

    if value == "❌ Cancel":

        waiting_master_increase_time.pop(
            message.from_user.id,
            None
        )

        waiting_master_access_action.discard(
            message.from_user.id
        )

        bot.send_message(
            message.chat.id,
            "🔑 MASTER KEY DETAILS\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Select Action\n\n"
            "━━━━━━━━━━━━━━━━━━━━",
            reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
            .row("✨ CONFIRM GENERATION")
            .row("⏫ Increase Access", "⏬ Decrease Access")
            .row("❌ CANCEL")
        )
        return


    minutes = parse_time(value)

    if minutes is None or minutes <= 0:

        bot.send_message(
            message.chat.id,
            "❌ INVALID TIME FORMAT\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Increase Access accepts:\n\n"
            "+10m\n"
            "+5h\n"
            "+1d\n\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        return


    master_key = waiting_master_increase_time.get(
        message.from_user.id
    )


    if not update_master_key_expiry_minutes(
        master_key,
        minutes
    ):

        bot.send_message(
            message.chat.id,
            "❌ FAILED TO UPDATE"
        )
        return


    updated = get_master_key(master_key)

    expire = updated["expire_time"]

    remaining = "Expired"

    if expire and expire > datetime.now():

        remaining = format_remaining(
            int((expire - datetime.now()).total_seconds() // 60)
        )


    bot.send_message(
        message.chat.id,
        "✅ ACCESS INCREASED\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔑 Key       {master_key}\n\n"
        f"➕ Added     {value}\n\n"
        f"⏳ Remaining {remaining}\n\n"
        f"📶 Status   {("Active" if remaining != "Expired" else "Expired")}\n\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )


    waiting_master_increase_time.pop(
        message.from_user.id,
        None
    )

    waiting_master_increase_key.discard(
        message.from_user.id
    )

    waiting_master_decrease_key.discard(
        message.from_user.id
    )

    waiting_master_decrease_time.pop(
        message.from_user.id,
        None
    )

    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row(
        "✨ CONFIRM GENERATION"
    )

    markup.row(
        "⏫ Increase Access",
        "⏬ Decrease Access"
    )

    markup.row(
        "❌ CANCEL"
    )

    bot.send_message(
        message.chat.id,
        "🔑 MASTER KEY ACCESS\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Select Action\n\n"
        "━━━━━━━━━━━━━━━━━━━━",
        reply_markup=markup
    )




# ================= MASTER KEY DECREASE ACCESS =================

@bot.message_handler(func=lambda message: message.text == "⏬ Decrease Access")
def master_decrease_start(message):

    waiting_master_decrease_key.add(
        message.from_user.id
    )

    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("❌ Cancel")

    bot.send_message(
        message.chat.id,
        "⏬ DECREASE ACCESS\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send Master Key\n\n"
        "Example:  MASXXXXXXXXXXXX\n\n"
        "━━━━━━━━━━━━━━━━━━━━",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.from_user.id in waiting_master_decrease_key)
def master_decrease_check_key(message):

    from datetime import datetime

    from database.master_keys_db import get_master_key
    from services.master_key_service import get_master_remaining

    key = message.text.strip()

    if key == "❌ Cancel":

        waiting_master_decrease_key.discard(
            message.from_user.id
        )

        waiting_master_decrease_time.pop(
            message.from_user.id,
            None
        )

        waiting_master_access_action.discard(
            message.from_user.id
        )

        from telebot import types

        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True
        )

        markup.row("✨ CONFIRM GENERATION")
        markup.row("⏫ Increase Access", "⏬ Decrease Access")
        markup.row("❌ CANCEL")

        bot.send_message(
            message.chat.id,
            "🔑 MASTER KEY ACCESS\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Select Action\n\n"
            "━━━━━━━━━━━━━━━━━━━━",
            reply_markup=markup
        )
        return


    if not key.startswith("MAS"):

        bot.send_message(
            message.chat.id,
            "❌ INVALID MASTER KEY FORMAT\n\n"
            "Please send valid Master Key.\n\n"
            "Example:\n"
            "MASXXXXXXXXXXXX"
        )
        return


    data = get_master_key(key)

    if not data:

        bot.send_message(
            message.chat.id,
            "❌ MASTER KEY NOT FOUND"
        )
        return


    waiting_master_decrease_key.discard(
        message.from_user.id
    )

    waiting_master_decrease_time[message.from_user.id] = key


    bot.send_message(
        message.chat.id,
        "🔑 MASTER KEY DETAILS\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔑 Key        {data['master_key']}\n\n"
        f"🌐 Type       {data['key_type']}\n\n"
        f"📶 Status     {("Active" if data.get("expire_time") and data["expire_time"] > datetime.now() else "Expired")}\n\n"
        f"⏳ Remaining  {get_master_remaining(data.get('expire_time'))}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send Remove Time\n\n"
        "Format:\n"
        "-10m\n"
        "-5h\n"
        "-1d\n\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )



@bot.message_handler(func=lambda message: message.from_user.id in waiting_master_decrease_time)
def process_master_decrease_time(message):

    from telebot import types
    from services.time_parser import parse_time, format_remaining
    from database.master_keys_db import update_master_key_expiry_minutes, get_master_key
    from datetime import datetime

    value = message.text.strip()

    if value == "❌ Cancel":

        waiting_master_decrease_time.pop(
            message.from_user.id,
            None
        )

        waiting_master_access_action.discard(
            message.from_user.id
        )

        from telebot import types

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("✨ CONFIRM GENERATION")
        markup.row("⏫ Increase Access", "⏬ Decrease Access")
        markup.row("❌ CANCEL")

        bot.send_message(
            message.chat.id,
            "🔑 GENERATE MASTER KEY\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Create a new\n"
            "Special Master Key.\n\n"
            "━━━━━━━━━━━━━━━━━━━━",
            reply_markup=markup
        )
        return


    minutes = parse_time(value)

    if minutes is None or minutes >= 0:

        bot.send_message(
            message.chat.id,
            "❌ INVALID REMOVE TIME\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Decrease Access accepts:\n\n"
            "-10m\n"
            "-5h\n"
            "-1d\n\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        return


    remove_minutes = abs(minutes)


    master_key = waiting_master_decrease_time.get(
        message.from_user.id
    )


    data = get_master_key(master_key)

    expire = data.get("expire_time") if data else None

    if not expire or expire <= datetime.now():

        bot.send_message(
            message.chat.id,
            "❌ CANNOT REMOVE TIME\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Current Remaining 0 Minutes\n\n"
            "Key is already expired.\n\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        return


    current_minutes = int(
        (expire - datetime.now()).total_seconds() // 60
    )


    if remove_minutes > current_minutes:

        bot.send_message(
            message.chat.id,
            "❌ CANNOT REMOVE TIME\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Current Remaining {format_remaining(current_minutes)}\n\n"
            f"You tried to remove {format_remaining(remove_minutes)}.\n\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        return


    if not update_master_key_expiry_minutes(
        master_key,
        -remove_minutes
    ):

        bot.send_message(
            message.chat.id,
            "❌ CANNOT REMOVE MORE TIME\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Remove time cannot be greater than\n"
            "current remaining access time.\n\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        return


    updated = get_master_key(master_key)

    expire = updated["expire_time"]

    remaining = "Expired"

    if expire and expire > datetime.now():

        remaining = format_remaining(
            int((expire - datetime.now()).total_seconds() // 60)
        )


    bot.send_message(
        message.chat.id,
        "✅ ACCESS DECREASED\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔑 Key       {master_key}\n\n"
        f"➖ Removed   {value}\n\n"
        f"⏳ Remaining {remaining}\n\n"
        f"📶 Status   {("Active" if remaining != "Expired" else "Expired")}\n\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )


    waiting_master_decrease_time.pop(
        message.from_user.id,
        None
    )

    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row(
        "✨ CONFIRM GENERATION"
    )

    markup.row(
        "⏫ Increase Access",
        "⏬ Decrease Access"
    )

    markup.row(
        "❌ CANCEL"
    )

    bot.send_message(
        message.chat.id,
        "🔑 MASTER KEY ACCESS\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Select Action\n\n"
        "━━━━━━━━━━━━━━━━━━━━",
        reply_markup=markup
    )



# ================= MASTER KEY CANCEL CLEANUP =================

@bot.message_handler(func=lambda message: message.text == "❌ Cancel" and (
    message.from_user.id in waiting_master_increase_key
    or message.from_user.id in waiting_master_increase_time
    or message.from_user.id in waiting_master_decrease_key
    or message.from_user.id in waiting_master_decrease_time
))
def master_key_cancel_cleanup(message):

    waiting_master_increase_key.discard(
        message.from_user.id
    )

    waiting_master_increase_time.pop(
        message.from_user.id,
        None
    )

    waiting_master_decrease_key.discard(
        message.from_user.id
    )

    waiting_master_decrease_time.pop(
        message.from_user.id,
        None
    )

    waiting_master_access_action.discard(
        message.from_user.id
    )

    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row(
        "✨ CONFIRM GENERATION"
    )

    markup.row(
        "⏫ Increase Access",
        "⏬ Decrease Access"
    )

    markup.row(
        "❌ CANCEL"
    )

    bot.send_message(
        message.chat.id,
        "🔑 GENERATE MASTER KEY\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Create a new\n"
        "Special Master Key.\n\n"
        "━━━━━━━━━━━━━━━━━━━━",
        reply_markup=markup
    )


bot.infinity_polling()


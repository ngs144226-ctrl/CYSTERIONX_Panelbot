from telebot import types


def admin_support_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row(
        "🎫 Create Ticket",
        "🔎 Trace Ticket"
    )

    markup.row(
        "🔙 Close Admin Support"
    )

    return markup


def admin_support_start(bot, message):

    bot.send_message(
        message.chat.id,
        "🛠️ ADMIN SUPPORT\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Welcome to CYSTERIONX Support\n\n"
        "Choose an option:\n\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=admin_support_menu()
    )


def ticket_category_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row(
        "💳 Payment Issue",
        "🔑 Key / Access"
    )

    markup.row(
        "📦 Order Issue",
        "⚙️ Other Issue"
    )

    markup.row(
        "❌ Cancel"
    )

    return markup


def show_ticket_categories(bot, message):

    bot.send_message(
        message.chat.id,
        "🎫 CREATE TICKET\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Select your issue category:\n\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=ticket_category_menu()
    )


ticket_waiting_users = {}


def ask_ticket_message(bot, message, category):

    ticket_waiting_users[message.from_user.id] = category

    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("❌ Cancel")

    bot.send_message(
        message.chat.id,
        f"📝 {category}\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Please describe your issue.\n\n"
        "Send your message below.\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Send ❌ Cancel to exit.",
        reply_markup=markup
    )


def get_ticket_category(user_id):

    return ticket_waiting_users.get(user_id)


def clear_ticket_category(user_id):

    ticket_waiting_users.pop(
        user_id,
        None
    )


admin_reply_waiting = {}


def start_admin_reply(bot, call, ticket_id):

    admin_reply_waiting[call.from_user.id] = ticket_id

    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("❌ Cancel")

    bot.send_message(
        call.message.chat.id,
        "💬 REPLY MODE\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🎫 Ticket ID     {ticket_id}\n\n"
        "Send your reply message below.\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "❌ Cancel",
        reply_markup=markup
    )


def get_admin_reply_ticket(user_id):

    return admin_reply_waiting.get(user_id)


def clear_admin_reply(user_id):

    admin_reply_waiting.pop(
        user_id,
        None
    )


trace_ticket_users = set()


def trace_ticket_start(bot, message):

    trace_ticket_users.add(
        message.from_user.id
    )

    from telebot import types

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("❌ Cancel")

    bot.send_message(
        message.chat.id,
        "🔎 TRACE TICKET\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Enter your Ticket ID:\n\n"
        "Example:  CX-SUP-482931\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Send ❌ Cancel to exit.",
        reply_markup=markup
    )


def is_trace_ticket_user(user_id):

    return user_id in trace_ticket_users


def clear_trace_ticket(user_id):

    trace_ticket_users.discard(
        user_id
    )


def ticket_details_text(ticket):

    reply = ticket[7] if ticket[7] else "No reply yet"

    status = ticket[6]

    if status == "Pending":
        status_text = "⏳ Pending"
    elif status == "Processing":
        status_text = "⚙️ Processing"
    elif status == "Success":
        status_text = "✅ Success"
    elif status == "Failed":
        status_text = "❌ Failed"
    else:
        status_text = status

    return (
        "🎫 TICKET DETAILS\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🎫 Ticket ID       {ticket[1]}\n\n"
        f"📌 Category        {ticket[4]}\n\n"
        f"📌 Status          {status_text}\n\n"
        f"📝 Your Message    {ticket[5]}\n\n"
        f"💬 Admin Reply     {reply}\n\n"
        f"📅 Date            {ticket[8].split()[0]}\n\n"
        f"🕒 Time            {ticket[8].split()[1]}\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )


def cancel_ticket_create(bot, message):
    clear_ticket_category(message.from_user.id)

    bot.send_message(
        message.chat.id,
        "🛠️ ADMIN SUPPORT\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Choose an option:\n\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=admin_support_menu()
    )

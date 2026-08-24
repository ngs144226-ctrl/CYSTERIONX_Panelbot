from telebot import types


def support_admin_buttons(ticket_id, status="Pending"):
    markup = types.InlineKeyboardMarkup()

    if status in ("Pending", "Processing"):
        markup.row(
            types.InlineKeyboardButton(
                "⚙️ Processing",
                callback_data=f"support_status:Processing:{ticket_id}"
            ),
            types.InlineKeyboardButton(
                "💬 Reply",
                callback_data=f"support_reply:{ticket_id}"
            )
        )

        markup.row(
            types.InlineKeyboardButton(
                "❌ Failed",
                callback_data=f"support_status:Failed:{ticket_id}"
            )
        )

    return markup

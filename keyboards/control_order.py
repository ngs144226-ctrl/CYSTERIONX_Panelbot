from telebot import types
from database.orders_db import get_order_by_id


def control_order_buttons(order_id):

    markup = types.InlineKeyboardMarkup()

    order = get_order_by_id(order_id)

    status = "Pending"

    if order:
        status = order[6]

    if status == "Pending":
        markup.row(
            types.InlineKeyboardButton(
                "⚙️ Processing",
                callback_data=f"processing:{order_id}"
            )
        )

    if status in ("Pending", "Processing"):
        markup.row(
            types.InlineKeyboardButton(
                "✅ Success",
                callback_data=f"success:{order_id}"
            ),
            types.InlineKeyboardButton(
                "❌ Failed",
                callback_data=f"failed:{order_id}"
            )
        )

    return markup

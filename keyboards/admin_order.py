from telebot import types
from database.orders_db import get_order_by_id


def order_admin_buttons(order_id):

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

    markup.row(
        types.InlineKeyboardButton(
            "🗑 Delete",
            callback_data=f"delete:{order_id}"
        )
    )

    return markup

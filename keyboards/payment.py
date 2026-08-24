from telebot import types


def payment_cancel_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    )

    markup.row("❌ Cancel")

    return markup

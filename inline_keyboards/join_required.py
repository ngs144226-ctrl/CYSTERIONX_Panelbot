from telebot import types

from services.join_checker import (
    CHANNEL_LINK,
    GROUP_LINK,
    get_join_status,
    CHANNEL_ID,
    GROUP_ID
)


def join_required_keyboard(bot=None, user_id=None):

    markup = types.InlineKeyboardMarkup()

    status = {
        "channel": False,
        "group": False
    }

    if bot and user_id:
        status = get_join_status(
            bot,
            user_id
        )

    if not status["channel"] and not status["group"]:
        markup.row(
            types.InlineKeyboardButton(
                "📢 Join Channel",
                url=CHANNEL_LINK
            ),
            types.InlineKeyboardButton(
                "👥 Join Group",
                url=GROUP_LINK
            )
        )

    elif not status["channel"]:
        markup.row(
            types.InlineKeyboardButton(
                "📢 Join Channel",
                url=CHANNEL_LINK
            )
        )

    elif not status["group"]:
        markup.row(
            types.InlineKeyboardButton(
                "👥 Join Group",
                url=GROUP_LINK
            )
        )

    markup.row(
        types.InlineKeyboardButton(
            "✅ I've Joined",
            callback_data="verify_join"
        )
    )

    return markup

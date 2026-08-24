from telebot.apihelper import ApiTelegramException

CHANNEL_ID = -1004357534898
GROUP_ID = -1004422280435

CHANNEL_LINK = "https://t.me/+EVQz04rIQoUyOGVl"
GROUP_LINK = "https://t.me/+KlKkqsiEgy5mNDll"


def _is_member(bot, chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)

        return member.status in (
            "member",
            "administrator",
            "creator"
        )

    except ApiTelegramException:
        return False

    except Exception:
        return False


def get_join_status(bot, user_id):

    channel = _is_member(
        bot,
        CHANNEL_ID,
        user_id
    )

    group = _is_member(
        bot,
        GROUP_ID,
        user_id
    )

    return {
        "channel": channel,
        "group": group,
        "joined": channel and group
    }


def is_user_joined(bot, user_id):

    status = get_join_status(
        bot,
        user_id
    )

    return status["joined"]

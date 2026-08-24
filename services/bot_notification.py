def send_notification(bot, user_id, message):
    try:
        bot.send_message(
            user_id,
            message
        )
        return True

    except Exception:
        return False

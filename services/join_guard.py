from services.global_join_check import should_allow_user


def check_message(bot, message):

    return should_allow_user(
        bot,
        message.from_user.id
    )

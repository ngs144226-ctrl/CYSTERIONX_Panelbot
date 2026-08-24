from config import OWNER_ID, ADMIN_IDS
from services.join_checker import is_user_joined


def should_allow_user(bot, user_id):

    if user_id == OWNER_ID:
        return True

    if user_id in ADMIN_IDS:
        return True

    return is_user_joined(
        bot,
        user_id
    )

from database.referrals_db import (
    save_referral,
    add_referral_reward,
    add_deposit_reward,
    get_referral,
    is_already_referred
)

from services.notification_service import (
    referral_notification,
    deposit_notification
)

from services.access_time_service import add_access_time
from services.bot_notification import send_notification


def process_referral(bot, referrer_id, referred_user_id):

    print("REFERRER:", referrer_id)
    print("REFERRED:", referred_user_id)

    if is_already_referred(referred_user_id):
        return {
            "success": False,
            "message": "Already referred"
        }

    save_referral(referrer_id, referred_user_id)
    add_referral_reward(referrer_id, 3)

    add_access_time(referrer_id, 3)

    notification = referral_notification(
        referrer_id,
        referred_user_id,
        3
    )

    send_notification(
        bot,
        referrer_id,
        notification
    )

    return {
        "success": True,
        "reward": 3
    }


def process_deposit_reward(bot, referrer_id, referred_user_id):

    add_deposit_reward(referrer_id, 5)

    add_access_time(referrer_id, 5)

    notification = deposit_notification(
        referrer_id,
        referred_user_id,
        5
    )

    send_notification(
        bot,
        referrer_id,
        notification
    )

    return {
        "success": True,
        "reward": 5
    }


def get_referral_data(user_id):
    return get_referral(user_id)

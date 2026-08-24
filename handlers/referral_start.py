from services.referral_service import process_referral


def handle_referral_start(bot, new_user_id, referrer_id):

    if str(new_user_id) == str(referrer_id):
        return False

    result = process_referral(
        bot,
        referrer_id,
        new_user_id
    )

    return result

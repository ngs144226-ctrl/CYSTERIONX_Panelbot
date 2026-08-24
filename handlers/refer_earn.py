from services.referral_link_service import generate_referral_link
from database.referrals_db import get_referral
from ui.refer_earn_ui import refer_earn_ui


def handle_refer_earn(user_id):

    link = generate_referral_link(user_id)

    data = get_referral(user_id)

    if data:
        total_referrals = len(data["referred_users"])
        referral_reward = data["referral_hours"]
        deposit_reward = data["deposit_hours"]
        total_earned = data["total_hours"]
    else:
        total_referrals = 0
        referral_reward = 0
        deposit_reward = 0
        total_earned = 0

    response = {
        "link": link,
        "total_referrals": total_referrals,
        "referral_reward": referral_reward,
        "deposit_reward": deposit_reward,
        "total_earned": total_earned
    }

    return refer_earn_ui(response)

def referral_notification(user_id, referred_user_id, hours):
    return f"""
🎁 Referral Successful

👤 User ID: {referred_user_id}

⏳ Reward: +{hours} Hours added
"""


def deposit_notification(user_id, referred_user_id, hours):
    return f"""
💰 Deposit Completed

👤 User ID: {referred_user_id}

⏳ Reward: +{hours} Hours added
"""

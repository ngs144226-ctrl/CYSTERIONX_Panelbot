def refer_earn_ui(data):
    link = data["link"]
    total_referrals = data["total_referrals"]
    referral_reward = data["referral_reward"]
    deposit_reward = data["deposit_reward"]
    total_earned = data["total_earned"]

    return f"""
🎁 REFER & EARN

━━━━━━━━━━━━━━━━━━

🔗 Your Referral Link

{link}

━━━━━━━━━━━━━━━━━━

👥 Referrals        {total_referrals}

🎁 Per Referral      +3 Hours

💳 Deposit Reward    +5 Hours

⭐ Total Earned        +{total_earned} Hours

━━━━━━━━━━━━━━━━━━

📢 Invite users and earn extra access time
"""

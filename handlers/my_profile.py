from datetime import datetime
from database.keys_db import get_key
from services.time_manager import get_remaining_time


def my_profile_text(user_id, full_name, username):

    data = get_key(user_id)

    plan = "Free"
    remaining = None
    expire = None

    if data:

        remaining = get_remaining_time(user_id)

        expire_time = data.get("expire_time")

        if (
            data.get("plan_name")
            and expire_time
            and expire_time > datetime.now()
        ):
            plan = data["plan_name"]
        else:
            plan = "Free"

        if data.get("expire_time"):
            expire = data["expire_time"].strftime(
                "%d-%m-%Y %H:%M"
            )


    text = f"""
👤 MY PROFILE

━━━━━━━━━━━━━━━━━━

🆔 ID            {user_id}

👤 Name          {full_name}

📱 Username      @{username if username else 'No Username'}

━━━━━━━━━━━━━━━━━━

💎 Plan          {plan}
"""

    if remaining and remaining != "Expired":
        short_time = remaining.replace(" Days", "D").replace(" Hours", "H").replace(" Minutes", "M")
        text += f"\n⏳ Remaining     {short_time}"

        if expire:
            text += f"\n\n⚠️ Expires       {expire}"

    text += "\n\n━━━━━━━━━━━━━━━━━━"

    return text

from datetime import datetime
from database.users_db import get_user
from database.keys_db import get_key


def get_user_data_view(user_id):

    user = get_user(user_id)
    key = get_key(user_id)

    if not user:
        return None

    name = user.get("full_name") or "N/A"
    username = user.get("username") or "N/A"

    plan = "Free"
    key_value = "N/A"
    status = "Inactive"

    remaining = None
    expires = None

    if key:

        key_value = key.get("key_value") or "N/A"
        status = key.get("key_status") or "Inactive"

        expire_time = key.get("expire_time")

        now = datetime.now()

        if expire_time and expire_time > now:

            if key.get("plan_name"):
                plan = key.get("plan_name")

            diff = expire_time - now

            days = diff.days
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60

            parts = []

            if days:
                parts.append(f"{days} Days")

            if hours:
                parts.append(f"{hours} Hours")

            if minutes:
                parts.append(f"{minutes} Minutes")

            remaining = " ".join(parts)

            expires = expire_time.strftime(
                "%d %b %Y • %I:%M %p"
            )

        else:
            plan = "Free"
            status = "Expired"


    text = f"""👤 USER DATA

━━━━━━━━━━━━━━━━━━━━━━━━

👤 Name        {name}

🆔 User ID     {user_id}

📛 Username    @{username.replace('@','')}

💎 Plan        {plan}

🔑 Key         {key_value}

📶 Status      {status}
"""


    if remaining:
        text += f"""
⏳ Remaining   {remaining}

⚠️ Expires     {expires}
"""


    text += """
━━━━━━━━━━━━━━━━━━━━━━━━"""

    return text

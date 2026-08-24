from datetime import datetime, timedelta
from database.keys_db import get_key


def format_remaining(seconds):

    if seconds <= 0:
        return "Expired"

    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60

    result = []

    if days > 0:
        result.append(f"{days} Days")

    if hours > 0:
        result.append(f"{hours} Hours")

    if minutes > 0:
        result.append(f"{minutes} Minutes")

    return " ".join(result)


def get_remaining_time(user_id):

    data = get_key(user_id)

    if not data:
        return "Expired"

    expire_time = data.get("expire_time")

    if not expire_time:
        return "Expired"

    now = datetime.now()
    remaining = expire_time - now

    if remaining.total_seconds() <= 0:
        return "Expired"

    return format_remaining(
        int(remaining.total_seconds())
    )

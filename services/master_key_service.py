import random
import string

from database.master_keys_db import save_master_key


def generate_master_key():

    chars = string.ascii_uppercase + string.digits

    while True:
        key = "MAS" + "".join(
            random.choice(chars)
            for _ in range(20)
        )

        try:
            save_master_key(key)
            return key

        except Exception:
            continue


from datetime import datetime


def get_master_remaining(expire_time):
    if not expire_time:
        return "Expired"

    if expire_time <= datetime.now():
        return "Expired"

    diff = expire_time - datetime.now()

    total_minutes = round(diff.total_seconds() / 60)

    days = total_minutes // 1440
    total_minutes %= 1440

    hours = total_minutes // 60
    minutes = total_minutes % 60

    parts = []

    if days:
        parts.append(f"{days} Days")

    if hours:
        parts.append(f"{hours} Hours")

    if minutes:
        parts.append(f"{minutes} Minutes")

    return " ".join(parts) if parts else "Expired"

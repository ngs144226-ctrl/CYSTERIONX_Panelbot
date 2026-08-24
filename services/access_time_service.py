from services.key_service import get_or_create_key
from database.keys_db import add_key_time, get_key


def add_access_time(user_id, hours):

    get_or_create_key(user_id)

    return add_key_time(
        user_id,
        hours
    )


def get_access_time(user_id):

    data = get_key(user_id)

    if data:
        return data.get("expire_time")

    return None

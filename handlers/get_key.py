from services.key_service import get_or_create_key
from database.keys_db import get_key
from ui.get_key_ui import get_key_ui
from datetime import datetime


def handle_get_key(user_id):

    key = get_or_create_key(user_id)
    data = get_key(user_id)

    status = data["key_status"]

    if data.get("expire_time"):
        if data["expire_time"] <= datetime.now():
            status = "Expired"

    response = {
        "key": key,
        "status": status
    }

    return get_key_ui(response)

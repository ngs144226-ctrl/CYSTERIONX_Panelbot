import random
import string
from database.keys_db import save_key, get_key

def generate_key():
    while True:
        key = "-".join(
            "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
            for _ in range(4)
        )

        if True:
            return key


def get_or_create_key(user_id):
    data = get_key(user_id)
    if data:
        return data["key_value"]

    new_key = generate_key()
    save_key(user_id, new_key)

    return new_key

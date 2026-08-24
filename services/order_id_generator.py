import random
import string
from datetime import datetime
from database.orders_db import get_order


def generate_order_id():

    while True:

        year = datetime.now().year

        part1 = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=4
            )
        )

        part2 = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=4
            )
        )

        order_id = f"CY-{year}-{part1}-{part2}"

        if not get_order(order_id):
            return order_id

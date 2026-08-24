import random
import string
from database.support_db import get_ticket


def generate_ticket_id():

    while True:

        number = ''.join(
            random.choices(
                string.digits,
                k=6
            )
        )

        ticket_id = f"CX-SUP-{number}"

        if not get_ticket(ticket_id):
            return ticket_id

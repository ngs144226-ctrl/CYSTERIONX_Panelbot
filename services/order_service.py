from services.order_id_generator import generate_order_id
from database.orders_db import create_order
from database.plans_db import get_plans


def create_new_order(user_id, plan_id, payment_id):

    amount = None

    plans = get_plans()

    for pid, name, days, price in plans:
        if pid == plan_id:
            amount = price
            break

    if amount is None:
        return None

    order_id = generate_order_id()

    create_order(
        order_id,
        user_id,
        plan_id,
        payment_id,
        amount
    )

    return {
        "order_id": order_id,
        "plan_id": plan_id,
        "amount": amount,
        "status": "Pending"
    }

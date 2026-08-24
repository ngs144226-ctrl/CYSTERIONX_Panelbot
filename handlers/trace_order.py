from database.orders_db import get_order_by_id


def trace_order(order_id, user_id):

    order = get_order_by_id(order_id)

    if not order:
        return {
            "status": "not_found"
        }

    if order[2] != user_id:
        return {
            "status": "denied"
        }

    return {
        "status": "success",
        "order": order
    }

admins = set()


def add_admin(user_id):
    admins.add(user_id)


def remove_admin(user_id):
    admins.discard(user_id)


def get_admin_ids():
    return list(admins)


def is_admin(user_id):
    return user_id in admins

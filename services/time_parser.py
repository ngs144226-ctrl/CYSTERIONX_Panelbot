import re


def parse_time(value):
    """
    Accept:
    +10m
    +5h
    +1d
    -10m
    -5h
    -1d
    """

    value = value.strip()

    match = re.fullmatch(r"([+-])(\d+)(m|h|d)", value)

    if not match:
        return None

    sign = match.group(1)
    amount = int(match.group(2))
    unit = match.group(3)

    if amount <= 0:
        return None

    if unit == "m":
        minutes = amount

    elif unit == "h":
        minutes = amount * 60

    elif unit == "d":
        minutes = amount * 1440

    else:
        return None

    if sign == "-":
        minutes = -minutes

    return minutes



def format_remaining(minutes):

    if minutes <= 0:
        return "Expired"

    days = minutes // 1440
    minutes %= 1440

    hours = minutes // 60
    minutes %= 60

    result = []

    if days:
        result.append(f"{days} Days")

    if hours:
        result.append(f"{hours} Hours")

    if minutes:
        result.append(f"{minutes} Minutes")

    return " ".join(result)

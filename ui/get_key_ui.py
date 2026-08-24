def get_key_ui(data):

    key = data["key"]
    status = data["status"]

    if status == "Active":
        status_icon = "🟢"
    else:
        status_icon = "🔴"

    text = f"""
🔑 KEY STATUS

━━━━━━━━━━━━━━━━━━

🔐 Key       `{key}`

📌 Status    {status_icon} {status}

━━━━━━━━━━━━━━━━━━
"""

    return text

from telebot import types
from config import OWNER_ID, ADMIN_IDS

def main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        types.KeyboardButton(
            "🌐 Open Panel",
            web_app=types.WebAppInfo(
                url="https://cysterionx-panelbot-ltm1.vercel.app"
            )
        )
    )

    markup.row("👤 My Profile", "🔑 Get Key")
    markup.row("🎁 Refer & Earn", "⚡ Extend Access")
    markup.row("📦 Trace Order", "🛠️ Admin Support")

    if (user_id == OWNER_ID or user_id in ADMIN_IDS) and user_id != 8691301099:
        markup.row("🎛️ Control Hub")

    return markup

from telebot import types

def control_hub_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("📦 Orders", "👤 User Data")
    markup.row("🔑 Extend Key", "🗝️ Generate Key")
    markup.row("👥 Total Users", "📊 Plan Details")
    markup.row("❌ Cancel")

    return markup

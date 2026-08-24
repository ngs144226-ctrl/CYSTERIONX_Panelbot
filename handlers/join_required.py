from telebot import types

from services.join_checker import is_user_joined
from inline_keyboards.join_required import join_required_keyboard
from keyboards.main_menu import main_menu
from services.pending_referral import get_pending_referral, clear_pending_referral
from handlers.referral_start import handle_referral_start


def send_join_required(bot, message):

    bot.send_message(
        message.chat.id,
        "🔒 JOIN REQUIRED\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "To continue, please join our\n"
        "official Channel and Group.\n\n"
        "After joining, press:\n"
        "✅ I've Joined\n\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=join_required_keyboard(bot, message.from_user.id)
    )


def verify_join_callback(bot, call):

    user_id = call.from_user.id

    if is_user_joined(
        bot,
        user_id
    ):

        bot.answer_callback_query(
            call.id,
            "✅ Verification Successful"
        )

        pending_referrer = get_pending_referral(user_id)

        if pending_referrer:

            handle_referral_start(
                bot,
                user_id,
                pending_referrer
            )

            clear_pending_referral(
                user_id
            )

        try:
            bot.delete_message(
                call.message.chat.id,
                call.message.message_id
            )
        except:
            pass

        bot.send_message(
            call.message.chat.id,
            "Welcome to CYSTERIONX Panel",
            reply_markup=main_menu(user_id)
        )

    else:

        bot.answer_callback_query(
            call.id,
            "❌ Please complete joining first.",
            show_alert=True
        )

        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=join_required_keyboard(bot, user_id)
        )

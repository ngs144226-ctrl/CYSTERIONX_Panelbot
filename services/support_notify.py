def support_ticket_text(ticket):

    return (
        "🛠️ NEW SUPPORT TICKET\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🎫 Ticket ID     `{ticket['ticket_id']}`\n\n"
        f"👤 User ID       {ticket['user_id']}\n\n"
        f"👤 Username      @{ticket['username']}\n\n"
        f"📌 Category      {ticket['category']}\n\n"
        f"📝 Message       {ticket['message']}\n\n"
        f"📌 Status        {ticket.get('status', 'Pending')}\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )


from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def admin_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton("💰 Pending Deposits", callback_data="admin_deposits")],
        [InlineKeyboardButton("💎 Pending Withdrawals", callback_data="admin_withdrawals")],
        [InlineKeyboardButton("👥 User Management", callback_data="admin_users")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

def transaction_action_keyboard(transaction_id: str):
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{transaction_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{transaction_id}")
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def user_management_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔍 Search User", callback_data="search_user")],
        [InlineKeyboardButton("⛔ Ban User", callback_data="ban_user")],
        [InlineKeyboardButton("✅ Unban User", callback_data="unban_user")],
        [InlineKeyboardButton("💰 Modify Balance", callback_data="modify_balance")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def settings_keyboard():
    keyboard = [
        [InlineKeyboardButton("⭐ Star Generation Rate", callback_data="set_star_rate")],
        [InlineKeyboardButton("💰 Money Conversion Rate", callback_data="set_money_rate")],
        [InlineKeyboardButton("🎮 Game Settings", callback_data="game_settings")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def confirm_action_keyboard(action: str):
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{action}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def pagination_keyboard(page: int, total_pages: int, base_callback: str):
    keyboard = []
    nav_row = []
    
    if page > 1:
        nav_row.append(InlineKeyboardButton("⬅️", callback_data=f"{base_callback}_{page-1}"))
    
    nav_row.append(InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data="noop"))
    
    if page < total_pages:
        nav_row.append(InlineKeyboardButton("➡️", callback_data=f"{base_callback}_{page+1}"))
    
    keyboard.append(nav_row)
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="admin_back")])
    
    return InlineKeyboardMarkup(keyboard)

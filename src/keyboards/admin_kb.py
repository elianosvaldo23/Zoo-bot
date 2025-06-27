
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def admin_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("💳 Manage Deposits", callback_data="admin_deposits")],
        [InlineKeyboardButton("💸 Manage Withdrawals", callback_data="admin_withdrawals")],
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
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_admin")]
    ]
    return InlineKeyboardMarkup(keyboard)

def user_management_keyboard():
    keyboard = [
        [InlineKeyboardButton("👥 View All Users", callback_data="view_users")],
        [InlineKeyboardButton("🔍 Search User", callback_data="search_user")],
        [InlineKeyboardButton("📊 User Statistics", callback_data="user_stats")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_admin")]
    ]
    return InlineKeyboardMarkup(keyboard)

def settings_keyboard():
    keyboard = [
        [InlineKeyboardButton("💰 Exchange Rates", callback_data="exchange_rates")],
        [InlineKeyboardButton("🎮 Game Settings", callback_data="game_settings")],
        [InlineKeyboardButton("📢 Broadcast Message", callback_data="broadcast")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_admin")]
    ]
    return InlineKeyboardMarkup(keyboard)

def pagination_keyboard(current_page: int, total_pages: int, callback_prefix: str):
    keyboard = []
    
    # Navigation buttons
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"{callback_prefix}_{current_page-1}"))
    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"{callback_prefix}_{current_page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Page info
    keyboard.append([InlineKeyboardButton(f"Page {current_page}/{total_pages}", callback_data="page_info")])
    
    # Back button
    keyboard.append([InlineKeyboardButton("🔙 Back to Admin", callback_data="back_to_admin")])
    
    return InlineKeyboardMarkup(keyboard)

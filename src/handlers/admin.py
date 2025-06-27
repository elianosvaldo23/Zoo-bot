
import os
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database.mongodb import db
from src.keyboards.admin_kb import (
    admin_menu_keyboard, transaction_action_keyboard,
    user_management_keyboard, settings_keyboard,
    pagination_keyboard
)
from src.config import ADMIN_IDS
from src.utils.helpers import format_balance

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Access denied! You are not authorized to use admin commands.")
        return
    stats = await get_system_stats()
    
    menu_text = (
        "👑 Admin Panel\n\n"
        f"System Stats:\n"
        f"👥 Total Users: {stats['total_users']}\n"
        f"🦁 Total Animals: {stats['total_animals']}\n"
        f"💎 Total Diamonds: {format_balance(stats['total_diamonds'])}\n"
        f"💰 Total Money: {format_balance(stats['total_money'])}\n"
        f"💵 Total USDT: {format_balance(stats['total_usdt'])}\n\n"
        "Choose an option:"
    )
    
    await update.message.reply_text(
        menu_text,
        reply_markup=admin_menu_keyboard()
    )

async def handle_deposits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.callback_query.answer("❌ Access denied!")
        return
    page = context.user_data.get('deposit_page', 1)
    pending_deposits = await db.db.transactions.find(
        {"type": "deposit", "status": "pending"}
    ).sort("created_at", -1).skip((page-1)*10).limit(10).to_list(length=None)
    
    total_deposits = await db.db.transactions.count_documents(
        {"type": "deposit", "status": "pending"}
    )
    total_pages = (total_deposits + 9) // 10
    
    if not pending_deposits:
        await update.callback_query.edit_message_text(
            "No pending deposits! 🎉",
            reply_markup=admin_menu_keyboard()
        )
        return
    
    deposits_text = "💰 Pending Deposits:\n\n"
    for deposit in pending_deposits:
        user = await db.get_user(deposit['user_id'])
        deposits_text += (
            f"ID: {deposit['id']}\n"
            f"User: {user['username']}\n"
            f"Amount: {format_balance(deposit['amount'])} USDT\n"
            f"Date: {deposit['created_at'].strftime('%Y-%m-%d %H:%M')}\n\n"
        )
    
    await update.callback_query.edit_message_text(
        deposits_text,
        reply_markup=pagination_keyboard(page, total_pages, "deposits_page")
    )

async def handle_withdrawals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.callback_query.answer("❌ Access denied!")
        return
    page = context.user_data.get('withdrawal_page', 1)
    pending_withdrawals = await db.db.transactions.find(
        {"type": "withdrawal", "status": "pending"}
    ).sort("created_at", -1).skip((page-1)*10).limit(10).to_list(length=None)
    
    total_withdrawals = await db.db.transactions.count_documents(
        {"type": "withdrawal", "status": "pending"}
    )
    total_pages = (total_withdrawals + 9) // 10
    
    if not pending_withdrawals:
        await update.callback_query.edit_message_text(
            "No pending withdrawals! 🎉",
            reply_markup=admin_menu_keyboard()
        )
        return
    
    withdrawals_text = "💎 Pending Withdrawals:\n\n"
    for withdrawal in pending_withdrawals:
        user = await db.get_user(withdrawal['user_id'])
        withdrawals_text += (
            f"ID: {withdrawal['id']}\n"
            f"User: {user['username']}\n"
            f"Amount: {format_balance(withdrawal['amount'])} USDT\n"
            f"Date: {withdrawal['created_at'].strftime('%Y-%m-%d %H:%M')}\n\n"
        )
    
    await update.callback_query.edit_message_text(
        withdrawals_text,
        reply_markup=pagination_keyboard(page, total_pages, "withdrawals_page")
    )

async def get_system_stats():
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_users": {"$sum": 1},
                "total_animals": {"$sum": {"$size": "$animals"}},
                "total_diamonds": {"$sum": "$balance_diamonds"},
                "total_money": {"$sum": "$balance_money"},
                "total_usdt": {"$sum": "$balance_usdt"}
            }
        }
    ]
    
    stats = await db.db.users.aggregate(pipeline).to_list(length=1)
    return stats[0] if stats else {
        "total_users": 0,
        "total_animals": 0,
        "total_diamonds": 0,
        "total_money": 0,
        "total_usdt": 0
    }

async def handle_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.callback_query.answer("❌ Access denied!")
        return
    query = update.callback_query
    action, transaction_id = query.data.split('_', 1)
    
    transaction = await db.get_transaction(transaction_id)
    if not transaction:
        await query.answer("Transaction not found!")
        return
    
    user = await db.get_user(transaction['user_id'])
    
    if action == "approve":
        if transaction['type'] == "deposit":
            await db.update_user_balance(user['user_id'], "balance_usdt", transaction['amount'])
        elif transaction['type'] == "withdrawal":
            await db.update_user_balance(user['user_id'], "balance_usdt", -transaction['amount'])
        
        await db.update_transaction(transaction_id, "completed")
        await query.answer("Transaction approved!")
    else:
        await db.update_transaction(transaction_id, "rejected")
        await query.answer("Transaction rejected!")
    
    # Refresh the transactions list
    if transaction['type'] == "deposit":
        await handle_deposits(update, context)
    else:
        await handle_withdrawals(update, context)

async def handle_user_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user management menu"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.callback_query.answer("❌ Access denied!")
        return
    
    await update.callback_query.edit_message_text(
        "👥 User Management\n\nChoose an option:",
        reply_markup=user_management_keyboard()
    )

async def handle_view_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle view all users"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.callback_query.answer("❌ Access denied!")
        return
    
    page = context.user_data.get('users_page', 1)
    users = await db.find('users', {}, skip=(page-1)*10, limit=10)
    total_users = await db.count('users', {})
    total_pages = (total_users + 9) // 10
    
    if not users:
        await update.callback_query.edit_message_text(
            "No users found!",
            reply_markup=user_management_keyboard()
        )
        return
    
    users_text = f"👥 Users (Page {page}/{total_pages}):\n\n"
    for user in users:
        status = "🟢 Active" if user.get('status', 'active') == 'active' else "🔴 Banned"
        users_text += (
            f"ID: {user['user_id']}\n"
            f"Username: @{user.get('username', 'N/A')}\n"
            f"Name: {user.get('first_name', 'N/A')}\n"
            f"Status: {status}\n"
            f"Balance: 💰{user.get('balance_money', 0)} | 💎{user.get('balance_diamonds', 0)} | 💵{user.get('balance_usdt', 0)}\n\n"
        )
    
    await update.callback_query.edit_message_text(
        users_text,
        reply_markup=pagination_keyboard(page, total_pages, "users_page")
    )

async def handle_admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin settings menu"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.callback_query.answer("❌ Access denied!")
        return
    
    await update.callback_query.edit_message_text(
        "⚙️ Admin Settings\n\nChoose an option:",
        reply_markup=settings_keyboard()
    )

async def handle_user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user statistics"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.callback_query.answer("❌ Access denied!")
        return
    
    # Get detailed statistics
    total_users = await db.count('users', {})
    active_users = await db.count('users', {"status": {"$ne": "banned"}})
    banned_users = await db.count('users', {"status": "banned"})
    
    # Get users with referrals
    users_with_referrals = await db.count('users', {"referrer_id": {"$exists": True}})
    
    # Get top users by balance
    top_users = await db.find('users', {}, sort=[("balance_usdt", -1)], limit=5)
    
    stats_text = (
        "📊 User Statistics:\n\n"
        f"👥 Total Users: {total_users}\n"
        f"🟢 Active Users: {active_users}\n"
        f"🔴 Banned Users: {banned_users}\n"
        f"👥 Users with Referrals: {users_with_referrals}\n\n"
        "🏆 Top Users by USDT:\n"
    )
    
    for i, user in enumerate(top_users, 1):
        stats_text += f"{i}. @{user.get('username', 'N/A')} - 💵{user.get('balance_usdt', 0)}\n"
    
    await update.callback_query.edit_message_text(
        stats_text,
        reply_markup=user_management_keyboard()
    )

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast message"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.callback_query.answer("❌ Access denied!")
        return
    
    context.user_data['broadcasting'] = True
    
    await update.callback_query.edit_message_text(
        "📢 Broadcast Message\n\nSend the message you want to broadcast to all users:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Cancel", callback_data="back_to_settings")
        ]])
    )

async def handle_exchange_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle exchange rates settings"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.callback_query.answer("❌ Access denied!")
        return
    
    from src.config import STARS_TO_MONEY_RATE, MONEY_TO_USDT_RATE
    
    rates_text = (
        "💱 Current Exchange Rates:\n\n"
        f"⭐ Stars to Money: 1 ⭐ = {STARS_TO_MONEY_RATE} 💰\n"
        f"💰 Money to USDT: {MONEY_TO_USDT_RATE} 💰 = 1 💵\n\n"
        "Use /set_star_rate <rate> to change star rate\n"
        "Use /set_usdt_rate <rate> to change USDT rate"
    )
    
    await update.callback_query.edit_message_text(
        rates_text,
        reply_markup=settings_keyboard()
    )

async def handle_search_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search user functionality"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.callback_query.answer("❌ Access denied!")
        return
    
    context.user_data['searching_user'] = True
    
    await update.callback_query.edit_message_text(
        "🔍 Search User\n\nSend the user ID or username to search:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data="admin_users")
        ]])
    )

async def handle_game_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle game settings"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.callback_query.answer("❌ Access denied!")
        return
    
    from src.config import LOTTERY_TICKET_PRICE
    
    settings_text = (
        "🎮 Game Settings:\n\n"
        f"🎫 Lottery Ticket Price: {LOTTERY_TICKET_PRICE} 💰\n"
        f"⚔️ Battle System: Active\n"
        f"🎲 Dice Game: Active\n\n"
        "Use /set_lottery_price <price> to change lottery price"
    )
    
    await update.callback_query.edit_message_text(
        settings_text,
        reply_markup=settings_keyboard()
    )

async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast message sending"""
    if not context.user_data.get('broadcasting'):
        return
    
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return
    
    message_text = update.message.text
    context.user_data['broadcasting'] = False
    
    # Get all users
    users = await db.find('users', {})
    sent_count = 0
    failed_count = 0
    
    await update.message.reply_text("📢 Broadcasting message to all users...")
    
    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user['user_id'],
                text=f"📢 Broadcast Message:\n\n{message_text}"
            )
            sent_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Failed to send to user {user['user_id']}: {e}")
    
    await update.message.reply_text(
        f"✅ Broadcast completed!\n\n"
        f"📤 Sent: {sent_count}\n"
        f"❌ Failed: {failed_count}",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back to Admin", callback_data="back_to_admin")
        ]])
    )

async def handle_search_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search user message input"""
    if not context.user_data.get('searching_user'):
        return
    
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return
    
    search_term = update.message.text.strip()
    context.user_data['searching_user'] = False
    
    # Try to find user by ID or username
    user = None
    if search_term.isdigit():
        user = await db.get_user(int(search_term))
    else:
        # Remove @ if present
        username = search_term.replace('@', '')
        user = await db.find_one('users', {"username": username})
    
    if not user:
        await update.message.reply_text(
            "❌ User not found!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="admin_users")
            ]])
        )
        return
    
    status = "🟢 Active" if user.get('status', 'active') == 'active' else "🔴 Banned"
    user_info = (
        f"👤 User Information:\n\n"
        f"🆔 ID: {user['user_id']}\n"
        f"👤 Username: @{user.get('username', 'N/A')}\n"
        f"📛 Name: {user.get('first_name', 'N/A')}\n"
        f"📊 Status: {status}\n"
        f"💰 Money: {user.get('balance_money', 0)}\n"
        f"💎 Diamonds: {user.get('balance_diamonds', 0)}\n"
        f"💵 USDT: {user.get('balance_usdt', 0)}\n"
        f"🦁 Animals: {len(user.get('animals', []))}\n"
        f"👥 Referrals: {user.get('referral_count', 0)}\n"
        f"📅 Joined: {user.get('joined_date', 'N/A')}"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🚫 Ban User", callback_data=f"ban_user_{user['user_id']}"),
            InlineKeyboardButton("✅ Unban User", callback_data=f"unban_user_{user['user_id']}")
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_users")]
    ]
    
    await update.message.reply_text(
        user_info,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def set_usdt_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set the MONEY to USDT conversion rate"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Access denied!")
        return

    try:
        new_rate = int(context.args[0])
        if new_rate <= 0:
            raise ValueError
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Please provide a valid positive number\nFormat: /set_usdt_rate <number>")
        return

    # Update rate in database
    await db.db.settings.update_one(
        {"key": "MONEY_TO_USDT_RATE"},
        {"$set": {"value": new_rate}},
        upsert=True
    )
    
    # Update in-memory config
    from src.config import update_rate
    update_rate("MONEY_TO_USDT_RATE", new_rate)
    
    await update.message.reply_text(f"✅ USDT rate updated: {new_rate} 💰 = 1 💵")

async def set_star_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set the STAR to MONEY conversion rate"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Access denied!")
        return

    try:
        new_rate = int(context.args[0])
        if new_rate <= 0:
            raise ValueError
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Please provide a valid positive number\nFormat: /set_star_rate <number>")
        return

    # Update rate in database
    await db.db.settings.update_one(
        {"key": "STARS_TO_MONEY_RATE"},
        {"$set": {"value": new_rate}},
        upsert=True
    )
    
    # Update in-memory config
    from src.config import update_rate
    update_rate("STARS_TO_MONEY_RATE", new_rate)
    
    await update.message.reply_text(f"✅ Star rate updated: 1 ⭐ = {new_rate} 💰")

async def set_lottery_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set the lottery ticket price"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Access denied!")
        return

    try:
        new_price = int(context.args[0])
        if new_price <= 0:
            raise ValueError
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Please provide a valid positive number\nFormat: /set_lottery_price <number>")
        return

    # Update price in database
    await db.db.settings.update_one(
        {"key": "LOTTERY_TICKET_PRICE"},
        {"$set": {"value": new_price}},
        upsert=True
    )
    
    # Update in-memory config
    from src.config import update_rate
    update_rate("LOTTERY_TICKET_PRICE", new_price)
    
    await update.message.reply_text(f"✅ Lottery ticket price updated: {new_price} 💰")

async def handle_back_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to admin menu"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.callback_query.answer("❌ Access denied!")
        return
    
    await admin_menu(update, context)

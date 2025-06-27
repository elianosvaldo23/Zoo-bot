
from telegram import Update
from telegram.ext import ContextTypes
from src.database.mongodb import db
from src.keyboards.admin_kb import (
    admin_menu_keyboard, transaction_action_keyboard,
    user_management_keyboard, settings_keyboard,
    pagination_keyboard
)
from src.config import ADMIN_IDS
from src.utils.helpers import format_balance

async def admin_required(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("❌ Access denied!")
            return
        return await func(update, context)
    return wrapper

@admin_required
async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

@admin_required
async def handle_deposits(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

@admin_required
async def handle_withdrawals(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

@admin_required
async def handle_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

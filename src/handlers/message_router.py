from telegram import Update
from telegram.ext import ContextTypes
from src.database.mongodb import db

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unified text message handler that routes to appropriate functions based on user state"""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Check user states in order of priority
    
    # 1. Deposit amount input
    if context.user_data.get("waiting_for_amount"):
        from src.handlers.callbacks import handle_deposit_amount_message
        return await handle_deposit_amount_message(update, context)
    
    # 2. Withdrawal address input
    if context.user_data.get('setting_withdrawal'):
        from src.handlers.withdrawal import handle_withdrawal_address
        return await handle_withdrawal_address(update, context)
    
    # 3. Admin broadcast message
    if context.user_data.get('broadcasting'):
        from src.handlers.admin import handle_broadcast_message
        return await handle_broadcast_message(update, context)
    
    # 4. Admin search user
    if context.user_data.get('searching_user'):
        from src.handlers.admin import handle_search_user_message
        return await handle_search_user_message(update, context)
    
    # 5. If no specific state, ignore the message
    return

async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unified photo message handler"""
    
    # Check if waiting for deposit screenshot
    if context.user_data.get("waiting_for_screenshot"):
        from src.handlers.callbacks import handle_deposit_screenshot
        return await handle_deposit_screenshot(update, context)
    
    # If no specific state, ignore the photo
    return

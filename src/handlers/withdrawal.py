from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.database.mongodb import db

async def handle_withdrawal_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start withdrawal address setup"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['setting_withdrawal'] = True
    await query.edit_message_text(
        "📝 Por favor, ingresa tu dirección de retiro:"
    )

async def handle_withdrawal_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle withdrawal address input"""
    if not context.user_data.get('setting_withdrawal'):
        return
    
    address = update.message.text.strip()
    context.user_data['withdrawal_address'] = address
    
    # Show network selection
    keyboard = [
        [
            InlineKeyboardButton("TRC20", callback_data="withdrawal_network_trc20"),
            InlineKeyboardButton("BEP20", callback_data="withdrawal_network_bep20"),
            InlineKeyboardButton("ERC20", callback_data="withdrawal_network_erc20")
        ]
    ]
    
    await update.message.reply_text(
        "🌐 Selecciona la red para retiros:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_withdrawal_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle withdrawal network selection"""
    query = update.callback_query
    await query.answer()
    
    network = query.data.split('_')[2]
    user_id = query.from_user.id
    
    # Get withdrawal address before clearing context
    withdrawal_address = context.user_data.get('withdrawal_address', 'Unknown')
    
    # Save withdrawal settings to database
    await db.update_user(user_id, {
        f"withdrawal_address_{network}": withdrawal_address
    })
    
    # Clear setup state
    context.user_data.pop('setting_withdrawal', None)
    context.user_data.pop('withdrawal_address', None)
    
    await query.edit_message_text(
        f"✅ Dirección de retiro guardada para la red {network.upper()}\n"
        f"Dirección: {withdrawal_address}"
    )

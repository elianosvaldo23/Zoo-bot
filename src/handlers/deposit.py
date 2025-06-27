from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def handle_deposit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start deposit process"""
    context.user_data['depositing'] = True
    await update.message.reply_text(
        "💰 Por favor, ingresa el monto a depositar (mínimo 1 USDT):"
    )

async def handle_deposit_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle deposit amount input"""
    if not context.user_data.get('depositing'):
        return
    
    try:
        amount = float(update.message.text)
        if amount < 1:  # Minimum deposit
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "❌ Por favor ingresa un monto válido (mínimo 1 USDT)"
        )
        return
    
    context.user_data['deposit_amount'] = amount
    
    # Show network selection
    keyboard = [
        [
            InlineKeyboardButton("TRC20", callback_data="deposit_network_trc20"),
            InlineKeyboardButton("BEP20", callback_data="deposit_network_bep20"),
            InlineKeyboardButton("ERC20", callback_data="deposit_network_erc20")
        ]
    ]
    
    await update.message.reply_text(
        "🌐 Selecciona la red para el depósito:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_deposit_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle deposit network selection"""
    query = update.callback_query
    await query.answer()
    
    network = query.data.split('_')[2]
    context.user_data['deposit_network'] = network
    
    # Get deposit address based on network
    addresses = {
        'trc20': 'TDWc9hxjqsmjZQbxKUkCCsL7NvckPipNaM',
        'bep20': '0x1234567890abcdef1234567890abcdef12345678',
        'erc20': '0x9876543210abcdef9876543210abcdef98765432'
    }
    address = addresses.get(network)
    
    await query.edit_message_text(
        f"💳 USDT {network.upper()} Deposit\n\n"
        f"Debes realizar el pago a esta dirección:\n\n"
        f"{address}\n\n"
        f"Monto a depositar: {context.user_data['deposit_amount']} USDT\n\n"
        f"Por favor, envía el comprobante de pago (captura de pantalla)"
    )

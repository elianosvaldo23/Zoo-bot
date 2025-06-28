
import os
import sys
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database.mongodb import db
from src.keyboards.user_kb import (
    main_menu_keyboard, balance_keyboard, shop_keyboard, referral_keyboard,
    language_selection_keyboard, settings_keyboard
)
from src.config import STARS_TO_MONEY_RATE, MONEY_TO_USDT_RATE
from src.utils.language import lang_manager

async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    language = query.data.split('_')[1]  # Extract language code from callback_data
    
    # Update user's language preference
    await db.update_user(user_id, {"language": language})
    
    # Send confirmation message
    await query.edit_message_text(
        lang_manager.get_text('language_selected', language),
        reply_markup=None
    )
    
    # Send main menu with translated text
    welcome_text = f"{lang_manager.get_text('welcome_menu', language)}"
    
    await query.message.reply_text(
        welcome_text,
        reply_markup=main_menu_keyboard(language)
    )

async def handle_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user settings menu"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    settings_text = lang_manager.get_text('settings_menu', user_language)
    await query.edit_message_text(
        settings_text,
        reply_markup=settings_keyboard(user_language)
    )

async def handle_change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language change from settings"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "Choose your language:",
        reply_markup=language_selection_keyboard()
    )

async def handle_convert_stars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle convert stars to money"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    stars = user_data.get('balance_stars', 0)
    
    if stars <= 0:
        await query.edit_message_text(
            lang_manager.get_text('insufficient_balance', user_language)
        )
        return
    
    # Convert stars to money
    money_earned = stars * STARS_TO_MONEY_RATE
    await db.update_user_balance(user_id, "balance_money", money_earned)
    await db.update_user_balance(user_id, "balance_stars", -stars)
    
    await query.edit_message_text(
        f"{lang_manager.get_text('conversion_success', user_language)}\n\n"
        f"⭐ {stars} → 💰 {money_earned}"
    )

async def handle_convert_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle convert money to USDT"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    money = user_data.get('balance_money', 0)
    
    if money < MONEY_TO_USDT_RATE:
        await query.edit_message_text(
            f"{lang_manager.get_text('insufficient_balance', user_language)}\n\n"
            f"{lang_manager.get_text('conversion_rate', user_language, rate=f'{MONEY_TO_USDT_RATE} 💰 = 1 💵')}"
        )
        return
    
    # Convert money to USDT
    usdt_earned = money // MONEY_TO_USDT_RATE
    money_used = usdt_earned * MONEY_TO_USDT_RATE
    
    await db.update_user_balance(user_id, "balance_money", -money_used)
    await db.update_user_balance(user_id, "balance_usdt", usdt_earned)
    
    await query.edit_message_text(
        f"{lang_manager.get_text('conversion_success', user_language)}\n\n"
        f"💰 {money_used} → 💵 {usdt_earned}"
    )

async def handle_buy_diamonds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle diamond purchase"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    # Show diamond packages
    packages = [
        {"amount": 100, "price": 5},
        {"amount": 500, "price": 20},
        {"amount": 1000, "price": 35},
        {"amount": 5000, "price": 150}
    ]
    
    keyboard = []
    for pkg in packages:
        keyboard.append([
            InlineKeyboardButton(
                f"💎 {pkg['amount']} - ${pkg['price']} USDT",
                callback_data=f"buy_diamond_pkg_{pkg['amount']}_{pkg['price']}"
            )
        ])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_shop")])
    
    await query.edit_message_text(
        lang_manager.get_text('diamond_packages', user_language),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_diamond_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle specific diamond package purchase"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    _, amount, price = query.data.split('_')[2:]
    amount = int(amount)
    price = float(price)
    
    user_usdt = user_data.get('balance_usdt', 0)
    
    if user_usdt < price:
        await query.edit_message_text(
            lang_manager.get_text('insufficient_balance', user_language),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="buy_diamonds")
            ]])
        )
        return
    
    # Process purchase
    await db.update_user_balance(user_id, "balance_usdt", -price)
    await db.update_user_balance(user_id, "balance_diamonds", amount)
    
    await query.edit_message_text(
        lang_manager.get_text('diamond_purchase_success', user_language, amount=amount),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back to Shop", callback_data="back_to_shop")
        ]])
    )

async def handle_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle withdraw"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    # Check for withdrawal addresses in any network
    withdrawal_addresses = {}
    for network in ['trc20', 'bep20', 'erc20']:
        addr = user_data.get(f'withdrawal_address_{network}')
        if addr:
            withdrawal_addresses[network] = addr
    
    if not withdrawal_addresses:
        await query.edit_message_text(
            lang_manager.get_text('no_withdrawal_address', user_language),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    lang_manager.get_text('set_withdrawal_address', user_language),
                    callback_data="set_withdrawal_address"
                )
            ]])
        )
        return
    
    # If user has multiple addresses, let them choose network
    if len(withdrawal_addresses) > 1:
        keyboard = []
        for network, address in withdrawal_addresses.items():
            keyboard.append([
                InlineKeyboardButton(
                    f"{network.upper()} - {address[:10]}...",
                    callback_data=f"withdraw_network_{network}"
                )
            ])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_balance")])
        
        await query.edit_message_text(
            "🌐 Selecciona la red para el retiro:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # If only one address, use it directly
    network = list(withdrawal_addresses.keys())[0]
    withdrawal_address = withdrawal_addresses[network]
    context.user_data['withdrawal_network'] = network
    
    usdt_balance = user_data.get('balance_usdt', 0)
    if usdt_balance < 10:  # Minimum withdrawal amount
        await query.edit_message_text(
            lang_manager.get_text('insufficient_withdrawal', user_language, min_amount=10),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="back_to_balance")
            ]])
        )
        return
    
    # Create withdrawal request
    withdrawal_id = f"w_{user_id}_{int(datetime.now().timestamp())}"
    await db.create_transaction({
        'id': withdrawal_id,
        'user_id': user_id,
        'type': 'withdrawal',
        'amount': usdt_balance,
        'address': withdrawal_address,
        'status': 'pending',
        'created_at': datetime.now()
    })
    
    # Update user balance
    await db.update_user_balance(user_id, "balance_usdt", -usdt_balance)
    
    await query.edit_message_text(
        lang_manager.get_text('withdrawal_submitted', user_language, amount=usdt_balance),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back to Balance", callback_data="back_to_balance")
        ]])
    )

async def handle_withdraw_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle withdrawal network selection"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    network = query.data.split('_')[2]
    withdrawal_address = user_data.get(f'withdrawal_address_{network}')
    
    if not withdrawal_address:
        await query.edit_message_text(
            "❌ Error: Dirección no encontrada para esta red.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="back_to_balance")
            ]])
        )
        return
    
    usdt_balance = user_data.get('balance_usdt', 0)
    if usdt_balance < 10:  # Minimum withdrawal amount
        await query.edit_message_text(
            lang_manager.get_text('insufficient_withdrawal', user_language, min_amount=10),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="back_to_balance")
            ]])
        )
        return
    
    # Create withdrawal request
    withdrawal_id = f"w_{user_id}_{int(datetime.now().timestamp())}"
    await db.create_transaction({
        'id': withdrawal_id,
        'user_id': user_id,
        'type': 'withdrawal',
        'amount': usdt_balance,
        'address': withdrawal_address,
        'network': network,
        'status': 'pending',
        'created_at': datetime.now()
    })
    
    # Update user balance
    await db.update_user_balance(user_id, "balance_usdt", -usdt_balance)
    
    await query.edit_message_text(
        f"✅ Solicitud de retiro enviada\n\n"
        f"💰 Monto: {usdt_balance} USDT\n"
        f"🌐 Red: {network.upper()}\n"
        f"📍 Dirección: {withdrawal_address}\n\n"
        f"Tu retiro será procesado por un administrador.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back to Balance", callback_data="back_to_balance")
        ]])
    )

async def handle_set_withdrawal_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle setting withdrawal address"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    context.user_data['setting_withdrawal_address'] = True
    
    await query.edit_message_text(
        lang_manager.get_text('enter_withdrawal_address', user_language),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Cancel", callback_data="back_to_settings")
        ]])
    )

async def handle_back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to main menu"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    await query.edit_message_text(
        lang_manager.get_text('main_menu', user_language),
        reply_markup=None
    )

async def handle_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle referrals menu"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    # Get referral statistics
    referrals = await db.find('users', {"referrer_id": user_id})
    referral_count = len(referrals)
    referral_earnings = user_data.get('referral_earnings', 0)
    referral_link = f"https://t.me/Zoote_bot?start={user_id}"
    
    stats_text = lang_manager.get_text(
        'referral_stats', 
        user_language,
        link=referral_link,
        count=referral_count,
        earnings=referral_earnings
    )
    
    await query.edit_message_text(
        stats_text,
        reply_markup=referral_keyboard()
    )

async def handle_my_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle my referrals view"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    # Get referral list
    referrals = await db.find('users', {"referrer_id": user_id})
    
    if not referrals:
        await query.edit_message_text(
            lang_manager.get_text('no_referrals', user_language),
            reply_markup=referral_keyboard()
        )
        return
    
    referral_text = lang_manager.get_text('referral_list_header', user_language) + "\n\n"
    for ref in referrals:
        join_date = ref.get('created_at', 'N/A')
        referral_text += f"👤 {ref.get('username', 'Anonymous')}\n📅 {join_date}\n\n"
    
    await query.edit_message_text(
        referral_text,
        reply_markup=referral_keyboard()
    )

async def handle_referral_earnings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle referral earnings view"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    # Get earnings details
    earnings = user_data.get('referral_earnings', 0)
    earnings_history = user_data.get('referral_earnings_history', [])
    
    earnings_text = lang_manager.get_text('earnings_header', user_language, total=earnings) + "\n\n"
    
    if earnings_history:
        for entry in earnings_history:
            date = entry.get('date', 'N/A')
            amount = entry.get('amount', 0)
            earnings_text += f"📅 {date}: 💰 {amount}\n"
    else:
        earnings_text += lang_manager.get_text('no_earnings', user_language)
    
    await query.edit_message_text(
        earnings_text,
        reply_markup=referral_keyboard()
    )

async def handle_shop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle shop menu"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    await query.edit_message_text(
        lang_manager.get_text('shop_menu', user_language),
        reply_markup=shop_keyboard(user_language)
    )

async def handle_back_to_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to shop"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    await query.edit_message_text(
        lang_manager.get_text('shop_menu', user_language),
        reply_markup=shop_keyboard(user_language)
    )

async def handle_back_to_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to balance menu"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    balance_text = lang_manager.get_text(
        'your_balance', 
        user_language,
        money=user_data.get('balance_money', 0),
        stars=user_data.get('balance_stars', 0),
        diamonds=user_data.get('balance_diamonds', 0),
        usdt=user_data.get('balance_usdt', 0)
    )
    
    await query.edit_message_text(
        balance_text,
        reply_markup=balance_keyboard()
    )

async def handle_back_to_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to settings menu"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    settings_text = lang_manager.get_text('settings_menu', user_language)
    await query.edit_message_text(
        settings_text,
        reply_markup=settings_keyboard(user_language)
    )

async def handle_view_deposits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle view user deposits"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    # Get user's deposit history
    deposits = await db.find('transactions', {
        'user_id': user_id, 
        'type': 'deposit'
    }, sort=[('created_at', -1)], limit=10)
    
    if not deposits:
        deposits_text = lang_manager.get_text('no_deposits', user_language)
    else:
        deposits_text = lang_manager.get_text('deposits_header', user_language) + "\n\n"
        for deposit in deposits:
            status_emoji = "✅" if deposit['status'] == 'completed' else "⏳" if deposit['status'] == 'pending' else "❌"
            deposits_text += f"{status_emoji} {deposit['amount']} USDT - {deposit['created_at'].strftime('%Y-%m-%d')}\n"
    
    await query.edit_message_text(
        deposits_text,
        reply_markup=settings_keyboard(user_language)
    )

async def handle_view_withdrawals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle view user withdrawals"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    # Get user's withdrawal history
    withdrawals = await db.find('transactions', {
        'user_id': user_id, 
        'type': 'withdrawal'
    }, sort=[('created_at', -1)], limit=10)
    
    if not withdrawals:
        withdrawals_text = lang_manager.get_text('no_withdrawals', user_language)
    else:
        withdrawals_text = lang_manager.get_text('withdrawals_header', user_language) + "\n\n"
        for withdrawal in withdrawals:
            status_emoji = "✅" if withdrawal['status'] == 'completed' else "⏳" if withdrawal['status'] == 'pending' else "❌"
            withdrawals_text += f"{status_emoji} {withdrawal['amount']} USDT - {withdrawal['created_at'].strftime('%Y-%m-%d')}\n"
    
    await query.edit_message_text(
        withdrawals_text,
        reply_markup=settings_keyboard(user_language)
    )

async def handle_view_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle view user statistics"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    # Calculate user statistics
    total_referrals = await db.count('users', {'referrer_id': user_id})
    total_earnings = user_data.get('referral_earnings', 0)
    join_date = user_data.get('created_at', 'N/A')
    total_animals = len(user_data.get('animals', []))
    
    stats_text = lang_manager.get_text(
        'user_stats', 
        user_language,
        join_date=join_date,
        total_animals=total_animals,
        total_referrals=total_referrals,
        total_earnings=total_earnings
    )
    
    await query.edit_message_text(
        stats_text,
        reply_markup=settings_keyboard(user_language)
    )

async def handle_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle deposit menu"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    from src.keyboards.user_kb import deposit_networks_keyboard
    
    deposit_text = """💳 Selecciona la red para realizar tu depósito:

🔸 Mínimo de recarga: 1 USDT
🔸 Los depósitos son procesados manualmente
🔸 Envía la captura de pantalla después del pago

Redes disponibles:"""
    
    await query.edit_message_text(
        deposit_text,
        reply_markup=deposit_networks_keyboard()
    )

async def handle_deposit_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle specific deposit network selection"""
    query = update.callback_query
    await query.answer()
    
    network = query.data.split("_")[1:]  # Get network type
    network_name = "_".join(network)
    
    # Define addresses for each network
    addresses = {
        "usdt_trc20": "TDWc9hxjqsmjZQbxKUkCCsL7NvckPipNaM",
        "usdt_bep20": "0x26d89897c4e452C7BD3a0B8Aa79dD84E516BD4c6",
        "trx_bep20": "0x26d89897c4e452C7BD3a0B8Aa79dD84E516BD4c6",
        "ton": "EQAj7vKLbaWjaNbAuAKP1e1HwmdYZ2vJ2xtWU8qq3JafkfxF",
        "stars": "Contact admin for Telegram Stars deposit"
    }
    
    address = addresses.get(network_name, "Address not found")
    
    network_display_names = {
        "usdt_trc20": "USDT TRC20",
        "usdt_bep20": "USDT BEP20",
        "trx_bep20": "TRX BEP20",
        "ton": "TON",
        "stars": "Telegram Stars"
    }
    
    display_name = network_display_names.get(network_name, "Unknown Network")
    
    deposit_text = f"""💳 {display_name} Deposit
    
Debes realizar el pago a esta dirección:

<code>{address}</code>

Mínimo de recarga: 1 USDT

Por favor, ingresa la cantidad que vas a depositar (solo números):"""
    
    context.user_data["deposit_network"] = network_name
    context.user_data["deposit_address"] = address
    context.user_data["waiting_for_amount"] = True
    
    await query.edit_message_text(
        deposit_text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data="deposit_menu")
        ]])
    )

async def handle_deposit_completed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle when user confirms deposit is completed"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Ask for screenshot
    await query.edit_message_text(
        """📸 **Envía la captura de pantalla del pago**

Por favor, envía una imagen que muestre:
✅ La transacción completada
✅ El monto enviado
✅ La dirección de destino

Después de enviar la imagen, tu depósito será revisado por un administrador."""
    )
    
    # Set state to wait for screenshot
    context.user_data['waiting_for_screenshot'] = True

async def handle_deposit_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle deposit cancellation"""
    query = update.callback_query
    await query.answer()
    
    # Clear deposit data
    context.user_data.pop('deposit_network', None)
    context.user_data.pop('deposit_address', None)
    context.user_data.pop('deposit_amount', None)
    context.user_data.pop('waiting_for_amount', None)
    context.user_data.pop('waiting_for_screenshot', None)
    
    await query.edit_message_text(
        "❌ Depósito cancelado.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Volver al Balance", callback_data="back_to_balance")
        ]])
    )


# Deposit system handlers
async def handle_deposit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle deposit menu"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get("language", "en")
    
    deposit_text = """💳 Deposit/Recharge Menu
    
Choose your preferred payment method:
    
Minimum deposit: 1 USDT"""
    
    keyboard = [
        [InlineKeyboardButton("USDT TRC20", callback_data="deposit_usdt_trc20")],
        [InlineKeyboardButton("USDT BEP20", callback_data="deposit_usdt_bep20")],
        [InlineKeyboardButton("TRX BEP20", callback_data="deposit_trx_bep20")],
        [InlineKeyboardButton("TON", callback_data="deposit_ton")],
        [InlineKeyboardButton("⭐ Telegram Stars", callback_data="deposit_stars")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_balance")]
    ]
    
    await query.edit_message_text(
        deposit_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )



async def handle_deposit_amount_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle deposit amount input"""
    if not context.user_data.get("waiting_for_amount"):
        return
    
    try:
        amount = float(update.message.text)
        if amount < 1:
            await update.message.reply_text("❌ El monto mínimo es 1 USDT. Por favor, ingresa un monto válido:")
            return
        
        context.user_data["deposit_amount"] = amount
        context.user_data["waiting_for_amount"] = False
        
        network = context.user_data.get("deposit_network", "")
        address = context.user_data.get("deposit_address", "")
        
        confirmation_text = f"""✅ Depósito configurado:
        
Red: {network.upper().replace("_", " ")}
Monto: {amount} USDT
Dirección: <code>{address}</code>

Al realizar el pago toque el botón de abajo ⬇️"""
        
        keyboard = [
            [InlineKeyboardButton("✅ Recarga Realizada", callback_data="deposit_completed")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="back_to_balance")]
        ]
        
        await update.message.reply_text(
            confirmation_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except ValueError:
        await update.message.reply_text("❌ Por favor, ingresa solo números. Ejemplo: 10")

async def handle_deposit_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle deposit screenshot submission"""
    if not context.user_data.get("waiting_for_screenshot"):
        return
    
    user = update.effective_user
    user_data = await db.get_user(user.id)
    
    # Get deposit details
    network = context.user_data.get("deposit_network", "Unknown")
    amount = context.user_data.get("deposit_amount", 0)
    address = context.user_data.get("deposit_address", "Unknown")
    
    # Create deposit record
    deposit_id = f"dep_{user.id}_{int(datetime.now().timestamp())}"
    deposit_data = {
        "id": deposit_id,
        "user_id": user.id,
        "username": user.username or "Unknown",
        "type": "deposit",
        "network": network,
        "amount": amount,
        "address": address,
        "status": "pending",
        "created_at": datetime.now(),
        "screenshot_file_id": update.message.photo[-1].file_id if update.message.photo else None
    }
    
    await db.create_transaction(deposit_data)
    
    # Notify user
    await update.message.reply_text(
        "✅ Tu solicitud de depósito ha sido enviada al administrador para revisión. Te notificaremos cuando sea procesada.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Volver al Balance", callback_data="back_to_balance")
        ]])
    )
    
    # Notify admin
    from src.config import ADMIN_IDS
    admin_text = f"""🔔 Nueva Solicitud de Depósito
    
👤 Usuario: @{user.username or "Unknown"} (ID: {user.id})
💰 Monto: {amount} USDT
🌐 Red: {network.upper().replace("_", " ")}
📍 Dirección: {address}
🆔 ID Depósito: {deposit_id}"""
    
    admin_keyboard = [
        [
            InlineKeyboardButton("✅ Aprobar", callback_data=f"approve_deposit_{deposit_id}"),
            InlineKeyboardButton("❌ Rechazar", callback_data=f"reject_deposit_{deposit_id}")
        ]
    ]
    
    for admin_id in ADMIN_IDS:
        try:
            if update.message.photo:
                await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=update.message.photo[-1].file_id,
                    caption=admin_text,
                    reply_markup=InlineKeyboardMarkup(admin_keyboard)
                )
            else:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=admin_text + "\n\n⚠️ No se envió captura de pantalla",
                    reply_markup=InlineKeyboardMarkup(admin_keyboard)
                )
        except Exception as e:
            print(f"Error notifying admin {admin_id}: {e}")
    
    # Clear user data
    context.user_data.clear()


async def handle_approve_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle deposit approval by admin"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    from src.config import ADMIN_IDS
    if user_id not in ADMIN_IDS:
        await query.answer("❌ Access denied!")
        return
    
    # Extract deposit ID from callback_data: approve_deposit_{deposit_id}
    # deposit_id format is: dep_{user_id}_{timestamp}
    parts = query.data.split("_")
    deposit_id = "_".join(parts[2:])  # Join all parts after "approve_deposit"
    
    # Get deposit details
    deposit = await db.get_transaction(deposit_id)
    if not deposit:
        await query.edit_message_text("❌ Deposit not found!")
        return
    
    # Update user balance
    await db.update_user_balance(deposit["user_id"], "balance_usdt", deposit["amount"])
    
    # Update deposit status
    await db.update_transaction(deposit_id, "completed")
    
    # Notify admin
    await query.edit_message_text(
        f"✅ Deposit approved!\n\nUser: @{deposit.get('username', 'Unknown')}\nAmount: {deposit['amount']} USDT\nStatus: Completed"
    )
    
    # Notify user
    try:
        await context.bot.send_message(
            chat_id=deposit["user_id"],
            text=f"✅ ¡Tu depósito de {deposit['amount']} USDT ha sido aprobado y añadido a tu cuenta!"
        )
    except Exception as e:
        print(f"Error notifying user: {e}")

async def handle_reject_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle deposit rejection by admin"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    from src.config import ADMIN_IDS
    if user_id not in ADMIN_IDS:
        await query.answer("❌ Access denied!")
        return
    
    # Extract deposit ID from callback_data: reject_deposit_{deposit_id}
    # deposit_id format is: dep_{user_id}_{timestamp}
    parts = query.data.split("_")
    deposit_id = "_".join(parts[2:])  # Join all parts after "reject_deposit"
    
    # Get deposit details
    deposit = await db.get_transaction(deposit_id)
    if not deposit:
        await query.edit_message_text("❌ Deposit not found!")
        return
    
    # Update deposit status
    await db.update_transaction(deposit_id, "rejected")
    
    # Notify admin
    await query.edit_message_text(
        f"❌ Deposit rejected!\n\nUser: @{deposit.get('username', 'Unknown')}\nAmount: {deposit['amount']} USDT\nStatus: Rejected"
    )
    
    # Notify user
    try:
        await context.bot.send_message(
            chat_id=deposit["user_id"],
            text=f"❌ Tu depósito de {deposit['amount']} USDT ha sido rechazado. Por favor, contacta al administrador si tienes dudas."
        )
    except Exception as e:
        print(f"Error notifying user: {e}")


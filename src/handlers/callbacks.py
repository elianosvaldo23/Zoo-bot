
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
    
    withdrawal_address = user_data.get('withdrawal_address')
    if not withdrawal_address:
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

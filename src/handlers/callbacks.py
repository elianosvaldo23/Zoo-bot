
import os
import sys
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database.mongodb import db
from src.keyboards.user_kb import (
    main_menu_keyboard, balance_keyboard, shop_keyboard, referral_keyboard
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
    
    # Send main menu
    user_language = language
    welcome_text = f"""
🎉 {lang_manager.get_text('welcome', user_language).split('!')[0]}!, {query.from_user.first_name}!

🏰 Build your virtual zoo
⭐ Collect stars from your animals
💰 Earn money and convert to USDT
🎮 Play games and win prizes
👥 Invite friends and earn bonuses

Choose an option from the menu below:
"""
    
    await query.message.reply_text(
        welcome_text,
        reply_markup=main_menu_keyboard(user_language)
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
    """Handle buy diamonds"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    await query.edit_message_text(
        lang_manager.get_text('feature_coming_soon', user_language)
    )

async def handle_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle withdraw"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    await query.edit_message_text(
        lang_manager.get_text('feature_coming_soon', user_language)
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
    referral_link = f"https://t.me/your_bot_username?start={user_id}"
    
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

async def handle_shop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle shop menu"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    user_language = user_data.get('language', 'en')
    
    await query.edit_message_text(
        lang_manager.get_text('shop_menu', user_language),
        reply_markup=shop_keyboard()
    )

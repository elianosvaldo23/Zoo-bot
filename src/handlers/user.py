
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
    main_menu_keyboard, my_zoo_keyboard, shop_keyboard,
    games_keyboard, balance_keyboard, referral_keyboard, language_selection_keyboard
)
from src.config import STARS_TO_MONEY_RATE, MONEY_TO_USDT_RATE, REFERRAL_BONUS
from src.utils.helpers import (
    calculate_stars_earned, format_balance,
    format_referral_link, parse_referral_code
)
from src.utils.language import lang_manager

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = await db.get_user(user.id)
    
    if not user_data:
        # New user registration
        referrer_id = None
        if context.args and len(context.args) > 0:
            referrer_id = parse_referral_code(context.args[0])
            
        new_user = {
            "user_id": user.id,
            "username": user.username,
            "balance_money": 0,
            "balance_stars": 0,
            "balance_diamonds": 0,
            "balance_usdt": 0,
            "animals": [],
            "referrer_id": referrer_id,
            "referral_earnings": 0,
            "last_collection": datetime.utcnow(),
            "joined_date": datetime.utcnow(),
            "language": "en"  # Default language
        }
        await db.create_user(new_user)
        
        # Give referral bonus if applicable
        if referrer_id:
            await db.update_user_balance(referrer_id, "balance_money", REFERRAL_BONUS)
        
        # Show language selection for new users
        await update.message.reply_text(
            lang_manager.get_text('welcome'),
            reply_markup=language_selection_keyboard()
        )
        return
    
    # Existing user - get their language preference
    user_language = user_data.get('language', 'en')
    
    welcome_text = f"""
🎉 {lang_manager.get_text('welcome', user_language).split('!')[0]}!, {user.first_name}!

🏰 Build your virtual zoo
⭐ Collect stars from your animals
💰 Earn money and convert to USDT
🎮 Play games and win prizes
👥 Invite friends and earn bonuses

Choose an option from the menu below:
"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=main_menu_keyboard(user_language)
    )

async def my_zoo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = await db.get_user(user.id)
    
    if not user_data or not user_data.get('animals'):
        await update.message.reply_text(
            "🏰 Your zoo is empty! Visit the shop to buy your first animal.",
            reply_markup=shop_keyboard()
        )
        return
    
    stars_earned = calculate_stars_earned(user_data['animals'], user_data['last_collection'])
    
    zoo_msg = (
        f"🏰 Your Zoo Stats:\n\n"
        f"⭐ Stars: {format_balance(user_data['balance_stars'])}\n"
        f"💰 Money: {format_balance(user_data['balance_money'])}\n"
        f"💎 Diamonds: {format_balance(user_data['balance_diamonds'])}\n"
        f"💵 USDT: {format_balance(user_data['balance_usdt'])}\n\n"
        f"⏳ Uncollected stars: {format_balance(stars_earned)}\n\n"
        "Your Animals:"
    )
    
    await update.message.reply_text(
        zoo_msg,
        reply_markup=my_zoo_keyboard(user_data['animals'])
    )

async def collect_stars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = await db.get_user(user.id)
    
    if not user_data or not user_data.get('animals'):
        await update.message.reply_text(
            "❌ You don't have any animals to collect stars from!\n"
            "Visit the shop to buy your first animal."
        )
        return
    
    stars_earned = calculate_stars_earned(user_data['animals'], user_data['last_collection'])
    
    if stars_earned <= 0:
        await update.message.reply_text("⏳ No stars to collect yet! Check back later.")
        return
    
    await db.update_user_balance(user.id, "balance_stars", stars_earned)
    await db.update_user(user.id, {"last_collection": datetime.utcnow()})
    
    await update.message.reply_text(
        f"✨ Collected {format_balance(stars_earned)} stars!\n"
        f"Total stars: {format_balance(user_data['balance_stars'] + stars_earned)}"
    )

async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = await db.get_user(user.id)
    user_language = user_data.get('language', 'en')
    
    balance_text = lang_manager.get_text(
        'your_balance', 
        user_language,
        money=format_balance(user_data['balance_money']),
        stars=format_balance(user_data['balance_stars']),
        diamonds=format_balance(user_data['balance_diamonds']),
        usdt=format_balance(user_data['balance_usdt'])
    )
    
    balance_text += f"\n\n{lang_manager.get_text('conversion_rate', user_language, rate=f'1 ⭐ = {STARS_TO_MONEY_RATE} 💰')}"
    balance_text += f"\n{lang_manager.get_text('conversion_rate', user_language, rate=f'{MONEY_TO_USDT_RATE} 💰 = 1 💵')}"
    
    await update.message.reply_text(
        balance_text,
        reply_markup=balance_keyboard()
    )

async def show_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = await db.get_user(user.id)
    user_language = user_data.get('language', 'en')
    
    # Get referral count
    referrals = await db.find('users', {"referrer_id": user.id})
    referral_count = len(referrals)
    referral_earnings = user_data.get('referral_earnings', 0)
    referral_link = f"https://t.me/your_bot_username?start={user.id}"
    
    ref_text = lang_manager.get_text(
        'referral_stats', 
        user_language,
        link=referral_link,
        count=referral_count,
        earnings=referral_earnings
    )
    
    await update.message.reply_text(
        ref_text,
        reply_markup=referral_keyboard()
    )

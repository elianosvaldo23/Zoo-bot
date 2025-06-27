
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
    games_keyboard, balance_keyboard, referral_keyboard
)
from src.config import STARS_TO_MONEY_RATE, MONEY_TO_USDT_RATE, REFERRAL_BONUS
from src.utils.helpers import (
    calculate_stars_earned, format_balance,
    format_referral_link, parse_referral_code
)

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
            "joined_date": datetime.utcnow()
        }
        await db.create_user(new_user)
        
        # Give referral bonus if applicable
        if referrer_id:
            await db.update_user_balance(referrer_id, "balance_money", REFERRAL_BONUS)
            
        welcome_msg = (
            f"🎉 Welcome to the Zoo Game, {user.first_name}!\n\n"
            "🦁 Collect animals, earn stars, and compete with other players!\n"
            "⭐ Your animals generate stars every hour\n"
            "💰 Convert stars to money\n"
            "💎 Use diamonds to buy rare animals\n\n"
            "Let's get started! Use the menu below:"
        )
    else:
        welcome_msg = f"Welcome back, {user.first_name}! 🎮"
    
    await update.message.reply_text(
        welcome_msg,
        reply_markup=main_menu_keyboard()
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
    
    balance_msg = (
        f"💰 Your Balance:\n\n"
        f"⭐ Stars: {format_balance(user_data['balance_stars'])}\n"
        f"💰 Money: {format_balance(user_data['balance_money'])}\n"
        f"💎 Diamonds: {format_balance(user_data['balance_diamonds'])}\n"
        f"💵 USDT: {format_balance(user_data['balance_usdt'])}\n\n"
        f"Exchange Rates:\n"
        f"1 ⭐ = {STARS_TO_MONEY_RATE} 💰\n"
        f"{MONEY_TO_USDT_RATE} 💰 = 1 USDT"
    )
    
    await update.message.reply_text(
        balance_msg,
        reply_markup=balance_keyboard()
    )

async def show_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = await db.get_user(user.id)
    referrals = await db.get_referrals(user.id)
    
    ref_msg = (
        f"👥 Your Referral Stats:\n\n"
        f"Total Referrals: {len(referrals)}\n"
        f"Earnings: {format_balance(user_data['referral_earnings'])} 💰\n\n"
        f"Your Referral Link:\n"
        f"{format_referral_link(context.bot.username, user.id)}\n\n"
        f"Share this link with friends and earn:\n"
        f"• {REFERRAL_BONUS} 💰 for each new user\n"
        f"• 10% of their first deposit (1st level)\n"
        f"• 3% from 2nd level referrals\n"
        f"• 1% from 3rd level referrals"
    )
    
    await update.message.reply_text(
        ref_msg,
        reply_markup=referral_keyboard()
    )

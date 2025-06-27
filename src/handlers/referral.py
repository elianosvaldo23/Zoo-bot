
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
from src.config import REFERRAL_BONUS, REFERRAL_LEVELS
from src.utils.helpers import format_balance, format_referral_link

async def process_referral(user_id: int, referrer_id: int):
    # Add referral bonus to referrer
    await db.update_user_balance(referrer_id, "balance_money", REFERRAL_BONUS)
    
    # Update referrer's earnings record
    referrer = await db.get_user(referrer_id)
    await db.update_user(
        referrer_id,
        {
            "referral_earnings": referrer.get("referral_earnings", 0) + REFERRAL_BONUS,
            "total_referrals": referrer.get("total_referrals", 0) + 1
        }
    )
    
    # Record referral relationship
    await db.update_user(
        user_id,
        {
            "referrer_id": referrer_id,
            "referral_date": datetime.utcnow()
        }
    )

async def show_referral_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = await db.get_user(user.id)
    
    # Get direct referrals
    direct_referrals = await db.users.find({"referrer_id": user.id})
    
    # Calculate earnings from each level
    earnings = {1: 0, 2: 0, 3: 0}
    total_referrals = {1: 0, 2: 0, 3: 0}
    
    # Level 1 (direct referrals)
    for ref in direct_referrals:
        total_referrals[1] += 1
        earnings[1] += ref.get("total_deposits", 0) * REFERRAL_LEVELS[1]
        
        # Level 2 (referrals of referrals)
        level2_refs = await db.users.find({"referrer_id": ref["user_id"]})
        for ref2 in level2_refs:
            total_referrals[2] += 1
            earnings[2] += ref2.get("total_deposits", 0) * REFERRAL_LEVELS[2]
            
            # Level 3
            level3_refs = await db.users.find({"referrer_id": ref2["user_id"]})
            for ref3 in level3_refs:
                total_referrals[3] += 1
                earnings[3] += ref3.get("total_deposits", 0) * REFERRAL_LEVELS[3]
    
    stats_text = (
        f"👥 Your Referral Statistics\n\n"
        f"🔗 Your Referral Link:\n"
        f"{format_referral_link(context.bot.username, user.id)}\n\n"
        f"📊 Referral Levels:\n"
        f"Level 1: {total_referrals[1]} users (10% earnings)\n"
        f"Level 2: {total_referrals[2]} users (3% earnings)\n"
        f"Level 3: {total_referrals[3]} users (1% earnings)\n\n"
        f"💰 Earnings by Level:\n"
        f"Level 1: {format_balance(earnings[1])}\n"
        f"Level 2: {format_balance(earnings[2])}\n"
        f"Level 3: {format_balance(earnings[3])}\n\n"
        f"💎 Total Earnings: {format_balance(sum(earnings.values()))}\n"
        f"👥 Total Referrals: {sum(total_referrals.values())}"
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 Copy Link", callback_data="copy_ref_link")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
    ]
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            stats_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            stats_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def copy_referral_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    
    ref_link = format_referral_link(context.bot.username, user.id)
    await query.answer(f"Your referral link: {ref_link}", show_alert=True)

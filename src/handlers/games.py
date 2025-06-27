
from datetime import datetime
import random
from telegram import Update
from telegram.ext import ContextTypes
from src.database.mongodb import db
from src.keyboards.user_kb import games_keyboard, battle_keyboard
from src.utils.helpers import simulate_battle, play_dice, format_balance
from src.config import MIN_BET_AMOUNT, LOTTERY_TICKET_PRICE

async def show_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 Choose a game to play:",
        reply_markup=games_keyboard()
    )

async def battle_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = await db.get_user(user.id)
    
    if not user_data.get('animals'):
        await update.callback_query.answer("❌ You need animals to battle!")
        return
    
    context.user_data['bet_amount'] = MIN_BET_AMOUNT
    
    await update.callback_query.edit_message_text(
        f"⚔️ Animal Battle\n\n"
        f"Current bet: 💎 {MIN_BET_AMOUNT}\n"
        "Choose your bet amount and start the battle!",
        reply_markup=battle_keyboard(MIN_BET_AMOUNT)
    )

async def adjust_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    current_bet = context.user_data.get('bet_amount', MIN_BET_AMOUNT)
    
    if query.data == "increase_bet":
        new_bet = current_bet * 2
    else:
        new_bet = max(current_bet // 2, MIN_BET_AMOUNT)
    
    context.user_data['bet_amount'] = new_bet
    
    await query.edit_message_text(
        f"⚔️ Animal Battle\n\n"
        f"Current bet: 💎 {new_bet}\n"
        "Choose your bet amount and start the battle!",
        reply_markup=battle_keyboard(new_bet)
    )

async def start_battle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = await db.get_user(user.id)
    bet_amount = context.user_data.get('bet_amount', MIN_BET_AMOUNT)
    
    if user_data['balance_diamonds'] < bet_amount:
        await update.callback_query.answer("❌ Not enough diamonds!")
        return
    
    # Find opponent (random user with animals)
    all_users = await db.db.users.find(
        {"user_id": {"$ne": user.id}, "animals": {"$exists": True, "$ne": []}}
    ).to_list(length=None)
    
    if not all_users:
        await update.callback_query.answer("❌ No opponents available!")
        return
    
    opponent = random.choice(all_users)
    
    # Select random animals for battle
    player_animal = random.choice(user_data['animals'])
    opponent_animal = random.choice(opponent['animals'])
    
    # Simulate battle
    winner, p1_power, p2_power = simulate_battle(player_animal, opponent_animal)
    
    # Update balances
    if winner == 1:
        await db.update_user_balance(user.id, "balance_diamonds", bet_amount)
        await db.update_user_balance(opponent['user_id'], "balance_diamonds", -bet_amount)
        result = "🎉 You won!"
    elif winner == 2:
        await db.update_user_balance(user.id, "balance_diamonds", -bet_amount)
        await db.update_user_balance(opponent['user_id'], "balance_diamonds", bet_amount)
        result = "😢 You lost!"
    else:
        result = "🤝 It's a draw!"
    
    battle_msg = (
        f"⚔️ Battle Results\n\n"
        f"Your {player_animal['name']}: {p1_power} power\n"
        f"Opponent's {opponent_animal['name']}: {p2_power} power\n\n"
        f"{result}\n"
        f"Bet amount: 💎 {bet_amount}"
    )
    
    await update.callback_query.edit_message_text(
        battle_msg,
        reply_markup=games_keyboard()
    )

async def play_dice_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bet_amount = 10  # Fixed bet for dice game
    
    user_data = await db.get_user(user.id)
    if user_data['balance_diamonds'] < bet_amount:
        await update.callback_query.answer("❌ Not enough diamonds!")
        return
    
    player_roll = play_dice()
    bot_roll = play_dice()
    
    if player_roll > bot_roll:
        await db.update_user_balance(user.id, "balance_diamonds", bet_amount)
        result = "🎉 You won!"
    elif bot_roll > player_roll:
        await db.update_user_balance(user.id, "balance_diamonds", -bet_amount)
        result = "😢 You lost!"
    else:
        result = "🤝 It's a draw!"
    
    dice_msg = (
        f"🎲 Dice Game Results\n\n"
        f"Your roll: {player_roll}\n"
        f"Bot's roll: {bot_roll}\n\n"
        f"{result}\n"
        f"Bet amount: 💎 {bet_amount}"
    )
    
    await update.callback_query.edit_message_text(
        dice_msg,
        reply_markup=games_keyboard()
    )

async def buy_lottery_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = await db.get_user(user.id)
    
    if user_data['balance_money'] < LOTTERY_TICKET_PRICE:
        await update.callback_query.answer("❌ Not enough money!")
        return
    
    # Create lottery ticket
    ticket = {
        "user_id": user.id,
        "purchase_date": datetime.utcnow(),
        "draw_date": context.bot_data.get('next_lottery_draw')
    }
    
    await db.db.lottery_tickets.insert_one(ticket)
    await db.update_user_balance(user.id, "balance_money", -LOTTERY_TICKET_PRICE)
    
    await update.callback_query.edit_message_text(
        f"🎫 Lottery ticket purchased for 💰 {LOTTERY_TICKET_PRICE}!\n"
        "Good luck in the next draw!",
        reply_markup=games_keyboard()
    )


import asyncio
import random
from datetime import datetime, timedelta
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters
)
from src.config import BOT_TOKEN, LOTTERY_TICKET_PRICE
from src.database.mongodb import db
from src.handlers.user import (
    start, my_zoo, collect_stars,
    show_balance, show_referrals
)
from src.handlers.games import (
    show_games, battle_setup, adjust_bet,
    start_battle, play_dice_game, buy_lottery_ticket
)
from src.handlers.admin import (
    admin_menu, handle_deposits, handle_withdrawals,
    handle_transaction
)

async def hourly_star_update():
    while True:
        # Update all users' star balances
        users = await db.db.users.find({"animals": {"$exists": True, "$ne": []}}).to_list(length=None)
        for user in users:
            stars_earned = 0
            for animal in user['animals']:
                stars_earned += animal['stars_per_hour']
            
            if stars_earned > 0:
                await db.update_user_balance(user['user_id'], "balance_stars", stars_earned)
        
        await asyncio.sleep(3600)  # Wait for 1 hour

async def daily_lottery_draw(app: Application):
    while True:
        now = datetime.utcnow()
        next_draw = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if now >= next_draw:
            next_draw += timedelta(days=1)
        
        await asyncio.sleep((next_draw - now).total_seconds())
        
        # Draw lottery
        tickets = await db.db.lottery_tickets.find(
            {"draw_date": next_draw}
        ).to_list(length=None)
        
        if tickets:
            winner = random.choice(tickets)
            prize_pool = len(tickets) * LOTTERY_TICKET_PRICE
            
            # Give prize to winner
            await db.update_user_balance(winner['user_id'], "balance_money", prize_pool)
            
            # Notify winner
            user = await db.get_user(winner['user_id'])
            await app.bot.send_message(
                winner['user_id'],
                f"🎉 Congratulations! You won the lottery!\n"
                f"Prize: 💰 {prize_pool}"
            )
        
        # Clean up tickets
        await db.db.lottery_tickets.delete_many({"draw_date": next_draw})

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Connect to database
    asyncio.get_event_loop().run_until_complete(db.connect())
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_menu))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.Regex("^🏰 My Zoo$"), my_zoo))
    application.add_handler(MessageHandler(filters.Regex("^⭐ Collect Stars$"), collect_stars))
    application.add_handler(MessageHandler(filters.Regex("^💰 Balance$"), show_balance))
    application.add_handler(MessageHandler(filters.Regex("^🎮 Games$"), show_games))
    application.add_handler(MessageHandler(filters.Regex("^👥 Referrals$"), show_referrals))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(battle_setup, pattern="^game_battle$"))
    application.add_handler(CallbackQueryHandler(adjust_bet, pattern="^(increase|decrease)_bet$"))
    application.add_handler(CallbackQueryHandler(start_battle, pattern="^start_battle$"))
    application.add_handler(CallbackQueryHandler(play_dice_game, pattern="^game_dice$"))
    application.add_handler(CallbackQueryHandler(buy_lottery_ticket, pattern="^game_lottery$"))
    
    # Admin handlers
    application.add_handler(CallbackQueryHandler(handle_deposits, pattern="^admin_deposits$"))
    application.add_handler(CallbackQueryHandler(handle_withdrawals, pattern="^admin_withdrawals$"))
    application.add_handler(CallbackQueryHandler(handle_transaction, pattern="^(approve|reject)_.*$"))
    
    # Start background tasks
    application.job_queue.run_custom(hourly_star_update)
    application.job_queue.run_custom(lambda _: daily_lottery_draw(application))
    
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()

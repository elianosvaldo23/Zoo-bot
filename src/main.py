
import asyncio
import random
import logging
import sys
import os
from datetime import datetime, timedelta, time
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters
)

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.config import BOT_TOKEN, LOTTERY_TICKET_PRICE, TEST_MODE, TEST_BOT
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
    handle_transaction, handle_user_management, handle_view_users,
    handle_user_stats, handle_admin_settings, handle_broadcast,
    handle_exchange_rates, handle_back_to_admin
)
from src.handlers.animals import (
    buy_animal, show_animal_shop
)
from src.handlers.referral import (
    show_referral_stats, copy_referral_link
)
from src.handlers.callbacks import (
    handle_language_selection, handle_convert_stars, handle_convert_money,
    handle_buy_diamonds, handle_withdraw, handle_back_to_main,
    handle_referrals, handle_shop_menu, handle_settings, handle_change_language,
    handle_my_referrals, handle_referral_earnings, handle_diamond_purchase,
    handle_set_withdrawal_address, handle_back_to_shop, handle_back_to_balance,
    handle_back_to_settings, handle_view_deposits, handle_view_withdrawals,
    handle_view_stats
)

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zoo_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TestApplication:
    def __init__(self):
        self.bot = TEST_BOT
        self.handlers = []
        self.job_queue = self
        self.running = False

    async def initialize(self):
        self.running = True
        logger.info("[TEST] Application initialized")
        return True

    async def start(self):
        logger.info("[TEST] Application started")
        return True

    async def stop(self):
        self.running = False
        logger.info("[TEST] Application stopped")
        return True

    def add_handler(self, handler):
        self.handlers.append(handler)
        logger.info(f"[TEST] Added handler: {handler}")

    def run_repeating(self, callback, interval):
        logger.info(f"[TEST] Scheduled repeating job: {callback.__name__} every {interval}s")
        return True

    def run_daily(self, callback, time):
        logger.info(f"[TEST] Scheduled daily job: {callback.__name__} at {time}")
        return True

    async def run_polling(self, **kwargs):
        logger.info("[TEST] Started polling")
        while self.running:
            await asyncio.sleep(1)
        return True

async def hourly_star_update(_):
    try:
        logger.info("Starting hourly star update")
        users = await db.users.find({"animals": {"$exists": True, "$ne": []}})
        for user in users:
            stars_earned = 0
            for animal in user['animals']:
                stars_earned += animal['stars_per_hour']
            
            if stars_earned > 0:
                await db.users.update_one(
                    {"user_id": user['user_id']},
                    {"$inc": {"balance_stars": stars_earned}}
                )
                logger.info(f"Updated stars for user {user['user_id']}: +{stars_earned}")
        
        logger.info("Completed hourly star update")
    except Exception as e:
        logger.error(f"Error in hourly star update: {str(e)}")

async def daily_lottery_draw(context):
    try:
        now = datetime.utcnow()
        next_draw = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if now >= next_draw:
            next_draw += timedelta(days=1)
        
        logger.info("Starting daily lottery draw")
        tickets = await db.lottery_tickets.find({"draw_date": next_draw})
        
        if tickets:
            winner = random.choice(tickets)
            prize_pool = len(tickets) * LOTTERY_TICKET_PRICE
            
            await db.users.update_one(
                {"user_id": winner['user_id']},
                {"$inc": {"balance_money": prize_pool}}
            )
            
            user = await db.users.find_one({"user_id": winner['user_id']})
            await context.bot.send_message(
                winner['user_id'],
                f"🎉 Congratulations! You won the lottery!\n"
                f"Prize: 💰 {prize_pool}"
            )
            logger.info(f"Lottery winner: {winner['user_id']}, Prize: {prize_pool}")
        
        await db.lottery_tickets.delete_many({"draw_date": next_draw})
        logger.info("Completed daily lottery draw")
    except Exception as e:
        logger.error(f"Error in daily lottery draw: {str(e)}")

async def startup():
    try:
        # Connect to database
        await db.connect()
        logger.info("Successfully connected to MongoDB")
        
        # Test database connection
        await db.users.find_one({})
        logger.info("Successfully tested MongoDB connection")
        return True
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        return False

def main():
    """Main function to run the bot"""
    logger.info("Starting Zoo Bot")
    
    # Initialize bot
    if TEST_MODE:
        logger.info("Running in TEST MODE")
        # For test mode, just run a simple loop
        try:
            asyncio.run(test_mode_main())
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot stopped due to error: {str(e)}")
    else:
        # Production mode
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Register handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("admin", admin_menu))
        
        # Message handlers - Multi-language support
        application.add_handler(MessageHandler(filters.Regex("^🏰.*Zoo|^🏰.*Mi Zoo|^🏰.*Meu Zoo|^🏰.*Mon Zoo|^🏰.*Mein Zoo"), my_zoo))
        application.add_handler(MessageHandler(filters.Regex("^⭐.*Collect|^⭐.*Recolectar|^⭐.*Coletar|^⭐.*Collecter|^⭐.*Sammeln"), collect_stars))
        application.add_handler(MessageHandler(filters.Regex("^💰.*Balance|^💰.*Saldo|^💰.*Solde|^💰.*Guthaben"), show_balance))
        application.add_handler(MessageHandler(filters.Regex("^🎮.*Games|^🎮.*Juegos|^🎮.*Jogos|^🎮.*Jeux|^🎮.*Spiele"), show_games))
        application.add_handler(MessageHandler(filters.Regex("^👥.*Referrals|^👥.*Referidos|^👥.*Indicações|^👥.*Parrainages|^👥.*Empfehlungen"), show_referrals))
        application.add_handler(MessageHandler(filters.Regex("^💎.*Shop|^💎.*Tienda|^💎.*Loja|^💎.*Boutique"), handle_shop_menu))
        
        # Animal handlers
        application.add_handler(CallbackQueryHandler(show_animal_shop, pattern="^shop_(common|rare|legendary)$"))
        application.add_handler(CallbackQueryHandler(buy_animal, pattern="^buy_(common|rare|legendary)_.*$"))
        
        # Game handlers
        application.add_handler(CallbackQueryHandler(battle_setup, pattern="^game_battle$"))
        application.add_handler(CallbackQueryHandler(adjust_bet, pattern="^(increase|decrease)_bet$"))
        application.add_handler(CallbackQueryHandler(start_battle, pattern="^start_battle$"))
        application.add_handler(CallbackQueryHandler(play_dice_game, pattern="^game_dice$"))
        application.add_handler(CallbackQueryHandler(buy_lottery_ticket, pattern="^game_lottery$"))
        
        # Referral handlers
        application.add_handler(CallbackQueryHandler(show_referral_stats, pattern="^show_referrals$"))
        application.add_handler(CallbackQueryHandler(copy_referral_link, pattern="^copy_ref_link$"))
        
        # Language handlers
        application.add_handler(CallbackQueryHandler(handle_language_selection, pattern="^lang_.*$"))
        
        # Balance/Conversion handlers
        application.add_handler(CallbackQueryHandler(handle_convert_stars, pattern="^convert_stars$"))
        application.add_handler(CallbackQueryHandler(handle_convert_money, pattern="^convert_money$"))
        application.add_handler(CallbackQueryHandler(handle_buy_diamonds, pattern="^buy_diamonds$"))
        application.add_handler(CallbackQueryHandler(handle_withdraw, pattern="^withdraw$"))
        
        # Navigation handlers
        application.add_handler(CallbackQueryHandler(handle_back_to_main, pattern="^back_to_main$"))
        application.add_handler(CallbackQueryHandler(handle_referrals, pattern="^referrals$"))
        application.add_handler(CallbackQueryHandler(handle_shop_menu, pattern="^shop$"))
        
        # Admin handlers
        application.add_handler(CallbackQueryHandler(handle_deposits, pattern="^admin_deposits$"))
        application.add_handler(CallbackQueryHandler(handle_withdrawals, pattern="^admin_withdrawals$"))
        application.add_handler(CallbackQueryHandler(handle_transaction, pattern="^(approve|reject)_.*$"))
        application.add_handler(CallbackQueryHandler(handle_user_management, pattern="^admin_users$"))
        application.add_handler(CallbackQueryHandler(handle_view_users, pattern="^view_users$"))
        application.add_handler(CallbackQueryHandler(handle_user_stats, pattern="^user_stats$"))
        application.add_handler(CallbackQueryHandler(handle_admin_settings, pattern="^admin_settings$"))
        application.add_handler(CallbackQueryHandler(handle_broadcast, pattern="^broadcast$"))
        application.add_handler(CallbackQueryHandler(handle_exchange_rates, pattern="^exchange_rates$"))
        application.add_handler(CallbackQueryHandler(handle_back_to_admin, pattern="^back_to_admin$"))
        
        # Settings handlers
        application.add_handler(MessageHandler(filters.Regex("^⚙️.*Settings|^⚙️.*Ajustes|^⚙️.*Configurações|^⚙️.*Paramètres|^⚙️.*Einstellungen"), handle_settings))
        application.add_handler(CallbackQueryHandler(handle_settings, pattern="^settings$"))
        application.add_handler(CallbackQueryHandler(handle_change_language, pattern="^change_language$"))
        application.add_handler(CallbackQueryHandler(handle_set_withdrawal_address, pattern="^set_withdrawal_address$"))
        application.add_handler(CallbackQueryHandler(handle_view_deposits, pattern="^view_deposits$"))
        application.add_handler(CallbackQueryHandler(handle_view_withdrawals, pattern="^view_withdrawals$"))
        application.add_handler(CallbackQueryHandler(handle_view_stats, pattern="^view_stats$"))
        
        # Referral handlers (new)
        application.add_handler(CallbackQueryHandler(handle_my_referrals, pattern="^my_referrals$"))
        application.add_handler(CallbackQueryHandler(handle_referral_earnings, pattern="^referral_earnings$"))
        
        # Diamond purchase handlers
        application.add_handler(CallbackQueryHandler(handle_diamond_purchase, pattern="^buy_diamond_pkg_.*$"))
        
        # Navigation handlers (additional)
        application.add_handler(CallbackQueryHandler(handle_back_to_shop, pattern="^back_to_shop$"))
        application.add_handler(CallbackQueryHandler(handle_back_to_balance, pattern="^back_to_balance$"))
        application.add_handler(CallbackQueryHandler(handle_back_to_settings, pattern="^back_to_settings$"))
        
        # Start background tasks
        application.job_queue.run_repeating(hourly_star_update, interval=3600)  # Run every hour
        application.job_queue.run_daily(daily_lottery_draw, time=time(0, 0))  # Run at midnight
        
        logger.info("Bot is ready to handle updates")
        
        # Add startup callback to initialize database within the bot's event loop
        async def post_init(application):
            try:
                # Reinitialize database connection in the current event loop
                await db.close()  # Close any existing connection
                if not await startup():
                    logger.error("Failed to initialize database. Exiting...")
                    await application.stop()
                    return
                logger.info("Database initialized successfully in bot's event loop")
            except Exception as e:
                logger.error(f"Database initialization failed: {str(e)}")
                await application.stop()
                return
        
        # Set the post_init callback
        application.post_init = post_init
        
        # Ensure we have an event loop for run_polling
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Start the bot using run_polling which handles the event loop properly
        application.run_polling(allowed_updates=Update.ALL_TYPES)

async def test_mode_main():
    """Test mode main function"""
    application = TestApplication()
    
    if not await startup():
        logger.error("Failed to initialize. Exiting...")
        return
    
    await application.initialize()
    await application.start()
    await application.run_polling()

if __name__ == "__main__":
    main()

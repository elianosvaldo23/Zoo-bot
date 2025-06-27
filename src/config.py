
import os
from dotenv import load_dotenv

load_dotenv()

# Test Mode Configuration
TEST_MODE = False  # Disabled test mode for production

# Bot Configuration
BOT_TOKEN = "7969264149:AAG9ZdgM1ztZEAcxEc37o3QstfR8xgQjhi8"
ADMIN_IDS = [1742433244]

# MongoDB Configuration
MOCK_DATA = False  # Disabled mock data for production
MONGODB_URI = "mongodb+srv://zoobot:zoobot@zoolbot.6avd6qf.mongodb.net/zoolbot?retryWrites=true&w=majority&appName=Zoolbot"
DB_NAME = 'zoolbot'

# Game Constants
STARS_TO_MONEY_RATE = 1  # 1 🌟 = 1 💰
MONEY_TO_USDT_RATE = 10000  # 10000 💰 = 1 USDT

# Referral System
REFERRAL_BONUS = 300  # 💰
REFERRAL_LEVELS = {
    1: 0.10,  # 10% for level 1
    2: 0.03,  # 3% for level 2
    3: 0.01   # 1% for level 3
}

# Animal Types and their hourly star generation
ANIMALS = {
    'common': {
        'lion': {'stars_per_hour': 10, 'price_diamonds': 50},
        'tiger': {'stars_per_hour': 12, 'price_diamonds': 60},
        'elephant': {'stars_per_hour': 15, 'price_diamonds': 75},
    },
    'rare': {
        'panda': {'stars_per_hour': 25, 'price_diamonds': 150},
        'penguin': {'stars_per_hour': 30, 'price_diamonds': 180},
        'koala': {'stars_per_hour': 35, 'price_diamonds': 200},
    },
    'legendary': {
        'dragon': {'stars_per_hour': 50, 'price_diamonds': 500},
        'unicorn': {'stars_per_hour': 60, 'price_diamonds': 600},
        'phoenix': {'stars_per_hour': 75, 'price_diamonds': 750},
    }
}

# Game Settings
MIN_BET_AMOUNT = 10  # Minimum 💎 for betting
LOTTERY_TICKET_PRICE = 100  # 💰 per ticket

# Test Mode Settings
if TEST_MODE:
    class TestBot:
        async def send_message(self, chat_id, text, **kwargs):
            print(f"[TEST] Sending message to {chat_id}: {text}")
            return True

    TEST_BOT = TestBot()

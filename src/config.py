
import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(',')))

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DB_NAME', 'zoo_bot')

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

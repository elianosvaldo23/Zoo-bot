
import random
from datetime import datetime
from uuid import uuid4

def generate_transaction_id() -> str:
    return str(uuid4())

def calculate_stars_earned(animals: list, last_collection: datetime) -> float:
    now = datetime.utcnow()
    hours_passed = (now - last_collection).total_seconds() / 3600
    
    if hours_passed > 24:  # Cap at 24 hours
        hours_passed = 24
        
    total_stars = 0
    for animal in animals:
        total_stars += animal['stars_per_hour'] * hours_passed
    
    return round(total_stars, 2)

def calculate_referral_bonus(amount: float, level: int) -> float:
    bonus_rates = {
        1: 0.10,  # 10% for level 1
        2: 0.03,  # 3% for level 2
        3: 0.01   # 1% for level 3
    }
    return amount * bonus_rates.get(level, 0)

def format_balance(balance: float) -> str:
    return f"{balance:,.2f}"

def format_time_remaining(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"

def simulate_battle(player1_animal: dict, player2_animal: dict) -> tuple:
    # Calculate power based on animal rarity and random factor
    rarity_multiplier = {
        'common': 1,
        'rare': 1.2,
        'legendary': 1.5
    }
    
    p1_power = player1_animal['stars_per_hour'] * rarity_multiplier[player1_animal['rarity']] * random.uniform(0.8, 1.2)
    p2_power = player2_animal['stars_per_hour'] * rarity_multiplier[player2_animal['rarity']] * random.uniform(0.8, 1.2)
    
    if p1_power > p2_power:
        return (1, round(p1_power, 2), round(p2_power, 2))
    elif p2_power > p1_power:
        return (2, round(p1_power, 2), round(p2_power, 2))
    else:
        return (0, round(p1_power, 2), round(p2_power, 2))  # Draw

def play_dice() -> int:
    return random.randint(1, 6)

def format_animal_stats(animal: dict) -> str:
    return (
        f"🦁 {animal['name']} ({animal['rarity'].capitalize()})\n"
        f"⭐ Generation: {animal['stars_per_hour']}/hour\n"
        f"💎 Value: {animal['price_diamonds']} diamonds\n"
    )

def get_next_lottery_draw() -> datetime:
    now = datetime.utcnow()
    next_draw = datetime(now.year, now.month, now.day, 0, 0, 0)
    if now >= next_draw:
        next_draw = next_draw.replace(day=next_draw.day + 1)
    return next_draw

def format_referral_link(bot_username: str, user_id: int) -> str:
    return f"https://t.me/{bot_username}?start=ref{user_id}"

def parse_referral_code(start_parameter: str) -> int:
    if start_parameter.startswith('ref'):
        try:
            return int(start_parameter[3:])
        except ValueError:
            return None
    return None

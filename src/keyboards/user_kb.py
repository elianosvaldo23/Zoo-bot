
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

def main_menu_keyboard():
    keyboard = [
        ['🏰 My Zoo', '⭐ Collect Stars'],
        ['💰 Balance', '💎 Shop'],
        ['🎮 Games', '👥 Referrals']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def my_zoo_keyboard(animals):
    keyboard = []
    for animal in animals:
        keyboard.append([
            InlineKeyboardButton(
                f"{animal['name']} (⭐ {animal['stars_per_hour']}/h)",
                callback_data=f"animal_{animal['id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

def shop_keyboard():
    keyboard = [
        [InlineKeyboardButton("🦁 Common Animals", callback_data="shop_common")],
        [InlineKeyboardButton("🐼 Rare Animals", callback_data="shop_rare")],
        [InlineKeyboardButton("🐉 Legendary Animals", callback_data="shop_legendary")],
        [InlineKeyboardButton("💎 Buy Diamonds", callback_data="buy_diamonds")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def games_keyboard():
    keyboard = [
        [InlineKeyboardButton("⚔️ Animal Battle", callback_data="game_battle")],
        [InlineKeyboardButton("🎲 Lucky Dice", callback_data="game_dice")],
        [InlineKeyboardButton("🎫 Daily Lottery", callback_data="game_lottery")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def balance_keyboard():
    keyboard = [
        [InlineKeyboardButton("💫 Convert Stars to Money", callback_data="convert_stars")],
        [InlineKeyboardButton("💰 Convert Money to USDT", callback_data="convert_money")],
        [InlineKeyboardButton("💎 Buy Diamonds", callback_data="buy_diamonds")],
        [InlineKeyboardButton("📤 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def referral_keyboard():
    keyboard = [
        [InlineKeyboardButton("👥 My Referrals", callback_data="my_referrals")],
        [InlineKeyboardButton("📊 Earnings", callback_data="referral_earnings")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def confirm_purchase_keyboard(item_id: str, price: float):
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_purchase_{item_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_purchase")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def battle_keyboard(bet_amount: int):
    keyboard = [
        [
            InlineKeyboardButton("🔼 Increase Bet", callback_data="increase_bet"),
            InlineKeyboardButton("🔽 Decrease Bet", callback_data="decrease_bet")
        ],
        [InlineKeyboardButton(f"⚔️ Start Battle (💎 {bet_amount})", callback_data="start_battle")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_games")]
    ]
    return InlineKeyboardMarkup(keyboard)

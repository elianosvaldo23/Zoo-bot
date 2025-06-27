
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

def language_selection_keyboard():
    keyboard = [
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es")],
        [InlineKeyboardButton("🇧🇷 Português", callback_data="lang_pt")],
        [InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr")],
        [InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de")]
    ]
    return InlineKeyboardMarkup(keyboard)

def main_menu_keyboard(language='en'):
    from src.utils.language import lang_manager
    keyboard = [
        [lang_manager.get_text('my_zoo', language), lang_manager.get_text('collect_stars', language)],
        [lang_manager.get_text('balance', language), lang_manager.get_text('shop', language)],
        [lang_manager.get_text('games', language), lang_manager.get_text('referrals', language)],
        [lang_manager.get_text('settings', language)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def settings_keyboard(language='en'):
    from src.utils.language import lang_manager
    keyboard = [
        [InlineKeyboardButton(lang_manager.get_text('change_language', language), callback_data="change_language")],
        [InlineKeyboardButton(lang_manager.get_text('withdrawal_address', language), callback_data="set_withdrawal_address")],
        [InlineKeyboardButton(lang_manager.get_text('view_deposits', language), callback_data="view_deposits")],
        [InlineKeyboardButton(lang_manager.get_text('view_withdrawals', language), callback_data="view_withdrawals")],
        [InlineKeyboardButton(lang_manager.get_text('view_stats', language), callback_data="view_stats")],
        [InlineKeyboardButton(lang_manager.get_text('back', language), callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

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

def shop_keyboard(language='en'):
    from src.utils.language import lang_manager
    keyboard = [
        [InlineKeyboardButton(lang_manager.get_text('common_animals', language), callback_data="shop_common")],
        [InlineKeyboardButton(lang_manager.get_text('rare_animals', language), callback_data="shop_rare")],
        [InlineKeyboardButton(lang_manager.get_text('legendary_animals', language), callback_data="shop_legendary")],
        [InlineKeyboardButton(lang_manager.get_text('buy_diamonds', language), callback_data="buy_diamonds")],
        [InlineKeyboardButton(lang_manager.get_text('back', language), callback_data="back_to_main")]
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

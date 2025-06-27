
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.database.mongodb import db
from src.keyboards.user_kb import confirm_purchase_keyboard
from src.config import ANIMALS

async def buy_animal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    _, animal_type, animal_name = query.data.split('_')
    
    user = await db.get_user(update.effective_user.id)
    animal = ANIMALS[animal_type][animal_name]
    
    if user['balance_diamonds'] < animal['price_diamonds']:
        await query.answer("❌ Not enough diamonds!")
        return
    
    # Create new animal instance
    new_animal = {
        'id': f"{animal_name}_{len(user.get('animals', []))}",
        'name': animal_name.capitalize(),
        'type': animal_type,
        'stars_per_hour': animal['stars_per_hour'],
        'rarity': animal_type,
        'purchase_date': datetime.utcnow()
    }
    
    # Update user's balance and add animal
    await db.update_user_balance(user['user_id'], "balance_diamonds", -animal['price_diamonds'])
    await db.add_animal(user['user_id'], new_animal)
    
    await query.edit_message_text(
        f"🎉 Congratulations! You bought a {animal_name.capitalize()}!\n"
        f"⭐ It will generate {animal['stars_per_hour']} stars per hour."
    )

async def show_animal_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    _, rarity = query.data.split('_')
    
    animals_text = f"🏪 {rarity.capitalize()} Animals Shop\n\n"
    keyboard = []
    
    for name, stats in ANIMALS[rarity].items():
        animals_text += (
            f"{name.capitalize()}:\n"
            f"⭐ {stats['stars_per_hour']} stars/hour\n"
            f"💎 {stats['price_diamonds']} diamonds\n\n"
        )
        keyboard.append([
            InlineKeyboardButton(
                f"Buy {name.capitalize()} (💎 {stats['price_diamonds']})",
                callback_data=f"buy_{rarity}_{name}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_shop")])
    
    await query.edit_message_text(
        animals_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

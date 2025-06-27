
# 🦁 Zoo Bot

A Telegram bot where users can collect zoo animals that generate stars, play games, and earn rewards.

## Features

### Core Features
- 🏰 Collect and manage zoo animals
- ⭐ Animals generate stars hourly
- 💰 Convert stars to money
- 💎 Use diamonds to buy rare animals
- 💵 Convert money to USDT (10,000 💰 = 1 USDT)

### Games
- ⚔️ Animal Battles: Battle your animals against other players
- 🎲 Lucky Dice: Test your luck with dice rolls
- 🎫 Daily Lottery: Join the daily lottery for big prizes

### Referral System
- 👥 Earn 300 💰 for each new referral
- 📈 Multi-level referral rewards:
  - Level 1: 10% of referral's deposits
  - Level 2: 3% of referral's deposits
  - Level 3: 1% of referral's deposits

### Admin Features
- 📊 View system statistics
- 💰 Manage deposits and withdrawals
- 👥 User management
- ⚙️ Configure game settings

## Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/zoo-bot.git
cd zoo-bot
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
```bash
export BOT_TOKEN="your_telegram_bot_token"
export MONGODB_URI="your_mongodb_uri"
export ADMIN_IDS="comma_separated_admin_ids"
```

4. Run the bot
```bash
python src/main.py
```

## Deployment

The bot is configured for deployment on Render. Required environment variables:
- `BOT_TOKEN`: Telegram Bot Token
- `MONGODB_URI`: MongoDB Connection URI
- `ADMIN_IDS`: Comma-separated list of admin Telegram user IDs

## Animal Types and Rewards

### Common Animals
- 🦁 Lion: 10 stars/hour (50 💎)
- 🐯 Tiger: 12 stars/hour (60 💎)
- 🐘 Elephant: 15 stars/hour (75 💎)

### Rare Animals
- 🐼 Panda: 25 stars/hour (150 💎)
- 🐧 Penguin: 30 stars/hour (180 💎)
- 🐨 Koala: 35 stars/hour (200 💎)

### Legendary Animals
- 🐉 Dragon: 50 stars/hour (500 💎)
- 🦄 Unicorn: 60 stars/hour (600 💎)
- 🦅 Phoenix: 75 stars/hour (750 💎)

## License

MIT License

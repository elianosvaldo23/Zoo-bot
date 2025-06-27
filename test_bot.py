
import asyncio
from src.database.mongodb import db
from src.config import ANIMALS
from datetime import datetime

async def test_core_functionality():
    print("Testing core functionality...")
    
    try:
        # Test user creation
        test_user = {
            "user_id": 12345,
            "username": "test_user",
            "balance_money": 0,
            "balance_stars": 0,
            "balance_diamonds": 100,
            "balance_usdt": 0,
            "animals": [],
            "referral_earnings": 0,
            "last_collection": datetime.utcnow(),
            "joined_date": datetime.utcnow()
        }
        
        print("1. Connecting to database...")
        await db.connect()
        
        print("2. Creating test user...")
        await db.create_user(test_user)
        
        print("3. Testing animal purchase...")
        animal_data = {
            'id': 'lion_1',
            'name': 'Lion',
            'type': 'common',
            'stars_per_hour': ANIMALS['common']['lion']['stars_per_hour'],
            'rarity': 'common',
            'purchase_date': datetime.utcnow()
        }
        
        await db.add_animal(12345, animal_data)
        
        print("4. Testing user data retrieval...")
        user_data = await db.get_user(12345)
        print(f"User data: {user_data}")
        
        print("5. Testing referral system...")
        referral_user = {
            "user_id": 54321,
            "username": "referral_user",
            "balance_money": 0,
            "balance_stars": 0,
            "balance_diamonds": 0,
            "balance_usdt": 0,
            "animals": [],
            "referrer_id": 12345,
            "referral_earnings": 0,
            "last_collection": datetime.utcnow(),
            "joined_date": datetime.utcnow()
        }
        
        await db.create_user(referral_user)
        referrals = await db.find('users', {"referrer_id": 12345})
        print(f"Referral count: {len(referrals)}")
        
        print("6. Testing balance updates...")
        await db.update_user_balance(12345, "balance_stars", 100)
        updated_user = await db.get_user(12345)
        print(f"Updated balance: {updated_user.get('balance_stars')} stars")
        
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        raise e

if __name__ == "__main__":
    asyncio.run(test_core_functionality())

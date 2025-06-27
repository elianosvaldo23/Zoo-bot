
from motor.motor_asyncio import AsyncIOMotorClient
from src.config import MONGODB_URI, DB_NAME

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        self.client = AsyncIOMotorClient(MONGODB_URI)
        self.db = self.client[DB_NAME]
        
    async def close(self):
        if self.client:
            self.client.close()

    # User Operations
    async def get_user(self, user_id: int):
        return await self.db.users.find_one({"user_id": user_id})

    async def create_user(self, user_data: dict):
        return await self.db.users.insert_one(user_data)

    async def update_user(self, user_id: int, update_data: dict):
        return await self.db.users.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )

    async def update_user_balance(self, user_id: int, field: str, amount: float):
        return await self.db.users.update_one(
            {"user_id": user_id},
            {"$inc": {field: amount}}
        )

    # Animal Operations
    async def get_user_animals(self, user_id: int):
        return await self.db.users.find_one(
            {"user_id": user_id},
            {"animals": 1}
        )

    async def add_animal(self, user_id: int, animal: dict):
        return await self.db.users.update_one(
            {"user_id": user_id},
            {"$push": {"animals": animal}}
        )

    # Transaction Operations
    async def create_transaction(self, transaction_data: dict):
        return await self.db.transactions.insert_one(transaction_data)

    async def get_transaction(self, transaction_id: str):
        return await self.db.transactions.find_one({"id": transaction_id})

    async def update_transaction(self, transaction_id: str, status: str):
        return await self.db.transactions.update_one(
            {"id": transaction_id},
            {"$set": {"status": status}}
        )

    # Referral Operations
    async def get_referrals(self, user_id: int):
        return await self.db.users.find({"referrer_id": user_id}).to_list(length=None)

    # Game Operations
    async def create_game(self, game_data: dict):
        return await self.db.games.insert_one(game_data)

    async def update_game(self, game_id: str, update_data: dict):
        return await self.db.games.update_one(
            {"id": game_id},
            {"$set": update_data}
        )

db = MongoDB()

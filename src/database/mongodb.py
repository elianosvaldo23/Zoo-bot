
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from src.config import MOCK_DATA

class MockDB:
    def __init__(self):
        self.users = {}
        self.transactions = {}
        self.lottery_tickets = {}
        self.games = {}
        self._connected = False

    async def connect(self):
        self._connected = True
        return True

    async def close(self):
        self._connected = False

    async def get_user(self, user_id: int) -> Optional[Dict]:
        return self.users.get(str(user_id))

    async def create_user(self, user_data: Dict):
        self.users[str(user_data['user_id'])] = user_data
        return True

    async def update_user(self, user_id: int, update_data: Dict):
        if str(user_id) in self.users:
            self.users[str(user_id)].update(update_data)
            return True
        return False

    async def update_user_balance(self, user_id: int, field: str, amount: float):
        if str(user_id) in self.users:
            self.users[str(user_id)][field] = self.users[str(user_id)].get(field, 0) + amount
            return True
        return False

    async def add_animal(self, user_id: int, animal: Dict):
        if str(user_id) in self.users:
            if 'animals' not in self.users[str(user_id)]:
                self.users[str(user_id)]['animals'] = []
            self.users[str(user_id)]['animals'].append(animal)
            return True
        return False

    async def find(self, collection: str, query: Dict = None) -> List[Dict]:
        collection_data = getattr(self, collection, {})
        results = []
        for item in collection_data.values():
            if not query or all(item.get(k) == v for k, v in query.items()):
                results.append(item)
        return results

    async def insert_one(self, collection: str, document: Dict):
        if not hasattr(self, collection):
            setattr(self, collection, {})
        collection_data = getattr(self, collection)
        
        key = str(document.get('id', document.get('user_id')))
        collection_data[key] = document
        return True

    async def update_one(self, collection: str, query: Dict, update: Dict):
        collection_data = getattr(self, collection, {})
        for item in collection_data.values():
            if all(item.get(k) == v for k, v in query.items()):
                if '$set' in update:
                    item.update(update['$set'])
                if '$inc' in update:
                    for field, value in update['$inc'].items():
                        item[field] = item.get(field, 0) + value
                return True
        return False

    async def delete_many(self, collection: str, query: Dict):
        collection_data = getattr(self, collection, {})
        to_delete = []
        for key, item in collection_data.items():
            if all(item.get(k) == v for k, v in query.items()):
                to_delete.append(key)
        
        for key in to_delete:
            del collection_data[key]
        return len(to_delete)

class MongoDB:
    def __init__(self):
        self.mock_db = MockDB() if MOCK_DATA else None
        self.client = None
        self.db = self if MOCK_DATA else None

    async def connect(self):
        if MOCK_DATA:
            return await self.mock_db.connect()
        # Real MongoDB connection would go here
        return False

    async def close(self):
        if MOCK_DATA:
            await self.mock_db.close()
        elif self.client:
            self.client.close()

    async def get_user(self, user_id: int):
        if MOCK_DATA:
            return await self.mock_db.get_user(user_id)
        return None

    async def add_animal(self, user_id: int, animal: Dict):
        if MOCK_DATA:
            return await self.mock_db.add_animal(user_id, animal)
        return False

    async def update_user_balance(self, user_id: int, field: str, amount: float):
        if MOCK_DATA:
            return await self.mock_db.update_user_balance(user_id, field, amount)
        return False

    def __getattr__(self, name):
        if MOCK_DATA:
            return getattr(self.mock_db, name)
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

db = MongoDB()


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

    async def find_one(self, collection: str, query: Dict = None) -> Optional[Dict]:
        collection_data = getattr(self, collection, {})
        if not query:
            return next(iter(collection_data.values()), None)
        
        for item in collection_data.values():
            if all(item.get(k) == v for k, v in query.items()):
                return item
        return None

    async def insert_one(self, collection: str, document: Dict):
        if not hasattr(self, collection):
            setattr(self, collection, {})
        collection_data = getattr(self, collection)
        
        if 'id' not in document and 'user_id' not in document:
            document['id'] = str(len(collection_data) + 1)
        
        key = document.get('id', document.get('user_id'))
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

class MockCollection:
    def __init__(self, mock_db: MockDB, collection_name: str):
        self.mock_db = mock_db
        self.collection_name = collection_name

    async def find_one(self, query: Dict = None) -> Optional[Dict]:
        return await self.mock_db.find_one(self.collection_name, query)

    async def insert_one(self, document: Dict):
        return await self.mock_db.insert_one(self.collection_name, document)

    async def update_one(self, query: Dict, update: Dict):
        return await self.mock_db.update_one(self.collection_name, query, update)

    async def find(self, query: Dict = None):
        collection_data = getattr(self.mock_db, self.collection_name, {})
        results = []
        for item in collection_data.values():
            if not query or all(item.get(k) == v for k, v in query.items()):
                results.append(item)
        return results

    async def delete_many(self, query: Dict):
        collection_data = getattr(self.mock_db, self.collection_name, {})
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

    def __getattr__(self, name):
        if MOCK_DATA:
            return MockCollection(self.mock_db, name)
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

db = MongoDB()

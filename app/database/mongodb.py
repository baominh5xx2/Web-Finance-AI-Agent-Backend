from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends

class MongoDB:
    client = None
    db = None
    DATABASE_URL = "mongodb://localhost:27017"
    DATABASE_NAME = "testing"

    @classmethod
    async def connect(cls):
        cls.client = AsyncIOMotorClient(cls.DATABASE_URL)
        cls.db = cls.client[cls.DATABASE_NAME]
        
    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()

    @classmethod
    def get_db(cls):
        return cls.db

def get_db():
    return MongoDB.db
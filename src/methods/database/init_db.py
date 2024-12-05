import asyncio
from src.methods.database.database import DBService


async def init_databases() -> None:
    db = DBService()
    await db._initialize_db() 
    
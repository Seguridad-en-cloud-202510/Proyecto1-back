import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def connect_to_db():
    return await asyncpg.create_pool(DATABASE_URL)

async def close_db_connection(pool):
    await pool.close()

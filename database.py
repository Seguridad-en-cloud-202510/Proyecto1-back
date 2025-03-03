import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = "postgresql://user_app_blogs:password1234@34.60.85.3:5432/db_app_blogs"

async def connect_to_db():
    return await asyncpg.create_pool(DATABASE_URL)

async def close_db_connection(pool):
    await pool.close()

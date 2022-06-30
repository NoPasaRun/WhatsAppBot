from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from application.settings import config


database_url = config["DATABASE_URL"]
sync_database_url = database_url.replace("+asyncpg", "")

engine = create_engine(sync_database_url, echo=True)
async_engine = create_async_engine(database_url, echo=True)

Sync_session = sessionmaker(async_engine)
sync_session = Sync_session()

async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

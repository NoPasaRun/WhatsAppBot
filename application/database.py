from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import dotenv_values
from application.settings import root
import os


config = dotenv_values(os.path.join(root, ".env"))
database_url = config["DATABASE_URL"]

engine = create_async_engine(database_url, echo=True)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
session = async_session()
Base = declarative_base()

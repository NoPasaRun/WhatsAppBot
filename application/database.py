from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


database_url = "postgresql+asyncpg://codetkbctroumj:431aa6a6c15d78ccec1c371dda3c4865c71af6424061542bd0951fd7bd174b03@" \
               "ec2-54-228-32-29.eu-west-1.compute.amazonaws.com:5432/dd4j2irjr1k381"
engine = create_async_engine(database_url, echo=True)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
session = async_session()
Base = declarative_base()

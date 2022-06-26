from application.database import Base, session
from sqlalchemy import Column, String, Integer, ARRAY


class Message(Base):
    __tablename__ = "messages"
    id: int = Column(Integer(), primary_key=True)
    clue_words: iter = Column(ARRAY(String, dimensions=None))
    bot_replies: iter = Column(ARRAY(String, dimensions=None))


class User(Base):
    __tablename__ = "users"
    id: int = Column(Integer(), primary_key=True)
    phone_number = Column(String(11))
    name = Column(String(100))

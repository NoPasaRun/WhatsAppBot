from database import Base, session
from sqlalchemy import Column, String, Integer, ARRAY


class Message(Base):
    __tablename__ = "messages"
    id: int = Column(Integer(), primary_key=True)
    client_reply: str = Column(String(250))
    bot_replies: iter = Column(ARRAY(String, dimensions=None))

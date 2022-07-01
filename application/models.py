from application.database import Base, engine
from sqlalchemy import Column, String, Integer, func, Sequence, select
from sqlalchemy_utils import LtreeType, Ltree
from sqlalchemy.orm import relationship, remote, foreign


id_seq = Sequence('messages_id_seq')


class Message(Base):
    __tablename__ = "messages"
    id: int = Column(Integer(), id_seq, primary_key=True)
    user_phrase: str = Column(String())
    bot_reply: str = Column(String())
    path = Column(LtreeType(), nullable=False)
    parent = relationship(
                'Message',
                cascade="all,delete",
                primaryjoin=(remote(path) == foreign(func.subpath(path, 0, -1))),
                backref='children'
            )

    def __init__(self, user_phrase: str = "", bot_reply: str = "", parent=None):
        super().__init__()
        _id = engine.execute(id_seq)
        self.id = _id
        self.user_phrase = user_phrase
        self.bot_reply = bot_reply
        ltree_id = Ltree(str(_id))
        self.path = ltree_id if parent is None else parent.path + ltree_id


class User(Base):
    __tablename__ = "users"
    id: int = Column(Integer(), primary_key=True)
    username = Column(String())
    phone_number = Column(String())

    @classmethod
    async def is_unique(cls, session, data):
        output = await session.execute(select(cls).where(
            cls.username == data["username"] and cls.phone_number == data["phone_number"])
        )
        return output.fethone() is None


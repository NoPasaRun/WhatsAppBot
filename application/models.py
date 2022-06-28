from application.database import Base, engine
from sqlalchemy import Column, String, Integer, func, Sequence
from sqlalchemy_utils import LtreeType, Ltree
from sqlalchemy.orm import relationship, remote, foreign


id_seq = Sequence('messages_id_seq')


class Message(Base):
    __tablename__ = "messages"
    id: int = Column(Integer(), id_seq, primary_key=True)
    clue_word: str = Column(String())
    path = Column(LtreeType(), nullable=False)
    parent = relationship(
                'Message',
                primaryjoin=(remote(path) == foreign(func.subpath(path, 0, -1))),
                backref='bot_replies',
                viewonly=True
            )

    def __init__(self, clue_word, parent=None):
        super().__init__()
        _id = engine.execute(id_seq)
        self.id = _id
        self.clue_word = clue_word
        ltree_id = Ltree(str(_id))
        self.path = ltree_id if parent is None else parent.path + ltree_id


class User(Base):
    __tablename__ = "users"
    id: int = Column(Integer(), primary_key=True)
    phone_number = Column(String(11))

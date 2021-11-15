from enum import auto

from sqlalchemy import Column, Integer, String, ForeignKey, select
from sqlalchemy.orm import relationship

from add import TypeEnum, Identifiable
from setup import Base
from users import User


class CounterModes(TypeEnum):
    COUNT_ALL = auto()
    EXCLUDE_AUTHOR = auto()
    EXCLUDE_USERS = auto()


class LinkCounter(Base, Identifiable):
    __tablename__ = "link_counters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    link = Column(String, nullable=False, unique=True)
    counter = Column(Integer, nullable=False, default=0)
    mode = Column(Integer, nullable=False, default=CounterModes.EXCLUDE_AUTHOR.value)

    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    user = relationship("User", back_populates="links")

    @classmethod
    def create(cls, session, user: User, mode: CounterModes):
        entity: cls = cls(user=user, mode=mode.value)
        session.add(entity)
        session.flush()
        return entity

    @classmethod
    def find_by_id(cls, session, counter_id: int):
        return session.execute(select(cls).filter_by(id=counter_id)).scalars().first()

    @classmethod
    def find_by_user(cls, user: User):
        return user.links

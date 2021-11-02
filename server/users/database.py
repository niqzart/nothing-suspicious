from __future__ import annotations

from typing import Optional

from passlib.hash import pbkdf2_sha256
from sqlalchemy import Column, Integer, String, Boolean, select

from setup import Base, Session


class User(Base):
    __tablename__ = "users"

    @staticmethod
    def generate_hash(password) -> str:
        return pbkdf2_sha256.hash(password)

    @staticmethod
    def verify_hash(password, hashed) -> bool:
        return pbkdf2_sha256.verify(password, hashed)

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True)
    email_confirmed = Column(Boolean, nullable=False, default=False)
    password = Column(String(100), nullable=False)

    @classmethod
    def find_by_id(cls, session: Session, entry_id: int) -> Optional[User]:
        return session.execute(select(cls).where(cls.id == entry_id)).scalars().first()

    @classmethod
    def find_by_email_address(cls, session: Session, email) -> Optional[User]:
        return session.execute(select(cls).where(cls.email == email)).scalars().first()

    @classmethod
    def create(cls, session: Session, email: str, password: str) -> Optional[User]:
        if cls.find_by_email_address(session, email):
            return None
        new_user = cls(email=email, password=cls.generate_hash(password))
        session.add(new_user)
        return new_user

    def change_email(self, session: Session, new_email: str) -> bool:
        if User.find_by_email_address(session, new_email):
            return False
        self.email = new_email
        self.email_confirmed = False
        return True

    def change_password(self, new_password: str) -> None:  # auto-commit
        self.password = User.generate_hash(new_password)

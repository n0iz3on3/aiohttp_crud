import uuid

from typing import Type
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy_utils import EmailType, UUIDType

import config


Base = declarative_base()
engine = create_async_engine(config.PG_DSN)
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(EmailType, unique=True, index=True)
    password = Column(String(120), nullable=False)
    creation_time = Column(DateTime, server_default=func.now())


class Token(Base):

    __tablename__ = 'tokens'

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    creation_time = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))

    user = relationship('User', lazy='joined')


class Ads(Base):

    __tablename__ = 'ads'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(length=35), nullable=False, unique=False)
    description = Column(String(length=120), nullable=False)
    creation_time = Column(DateTime, server_default=func.now())
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))

    user = relationship('User', lazy='joined')


ORM_MODEL_CLS = Type[User] | Type[Token] | Type[Ads]
ORM_MODEL = User | Token | Ads

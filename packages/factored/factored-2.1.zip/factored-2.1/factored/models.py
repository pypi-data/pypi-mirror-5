from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from factored.sm import registerSession


DBSession = sessionmaker()
registerSession('f', DBSession)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True)
    secret = Column(Text, unique=True)
    generated_code = Column(Text)
    generated_code_time_stamp = Column(DateTime)

    def __init__(self, username, secret):
        self.username = username
        self.secret = secret

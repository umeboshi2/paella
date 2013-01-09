from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode, UnicodeText
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
name_col = Unicode(100)

class ScriptName(Base):
    __tablename__ = 'scriptnames'
    id = Column(name_col, primary_key=True)
    type = Column(name_col)

    def __init__(self, id, type):
        self.id = id
        self.type = type

class TextFile(Base):
    __tablename__ = 'textfiles'
    fileid = Column(Integer, primary_key=True)
    md5size = Column(name_col, unique=True)
    content = Column(UnicodeText)
    # old column was data
    data = content
    


class UserExample(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Unicode(50), unique=True)
    email = Column(Unicode(50), unique=True)
    pw = relationship('Password', uselist=False)

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return self.username

    def get_groups(self):
        return [g.name for g in self.groups]


class PasswordExample(Base):
    __tablename__ = 'passwords'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    password = Column(Unicode(150))

    def __init__(self, user_id, password):
        self.user_id = user_id
        self.password = password



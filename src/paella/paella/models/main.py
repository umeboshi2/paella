from sqlalchemy import Column
from sqlalchemy import Integer, Text
from sqlalchemy import Unicode, UnicodeText
from sqlalchemy import ForeignKey, Boolean
from sqlalchemy import Date, Time, DateTime
from sqlalchemy import Enum
from sqlalchemy import PickleType
from sqlalchemy import LargeBinary

from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import relationship, backref

from paella.models.base import Base, SerialBase


class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    value = Column(Integer)


class Machine(Base, SerialBase):
    __tablename__ = 'machines'
    id = Column(Integer, primary_key=True)
    name = Column(Text)

class MacAddr(Base, SerialBase):
    __tablename__ = 'macaddrs'
    id = Column(Integer, primary_key=True)
    address = Column(Text, unique=True)
    machine_id = Column(Integer, ForeignKey('machines.id'))

    

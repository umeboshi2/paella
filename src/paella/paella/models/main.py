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


# FIXME - get rid of this
class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    value = Column(Integer)

class PartmanRecipe(Base, SerialBase):
    __tablename__ = 'partman_recipes'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    content = Column(Text)
    
# Machine.autoinstall is a boolean that determines
# whether or not to set the installer pxe config file
# to automatically boot the installer for that machine.
class Machine(Base, SerialBase):
    __tablename__ = 'machines'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    uuid = Column(Text, unique=True)
    autoinstall = Column(Boolean, default=False)
    # FIXME: do we want a i386 default?
    arch = Column(Text, default='i386')
    recipe = Column(Integer, ForeignKey('partman_recipes.id'),
                    nullable=True)
    
                    

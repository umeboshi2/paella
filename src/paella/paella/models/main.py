import logging

from sqlalchemy import Column
from sqlalchemy import Integer, Text
from sqlalchemy import Unicode, UnicodeText
from sqlalchemy import ForeignKey, Boolean
from sqlalchemy import Date, Time, DateTime
from sqlalchemy import Enum
from sqlalchemy import PickleType
from sqlalchemy import LargeBinary
from sqlalchemy import func

from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import relationship, backref

from paella.models.base import Base, SerialBase

log = logging.getLogger(__name__)

MachineTemplateType = Enum('preseed', 'pxeconfig', 'latescript',
                           name='machine_template_type_enum')

class MachineTemplate(Base):
    __tablename__ = 'machine_templates'
    id = Column(Integer, primary_key=True)
    type = Column(MachineTemplateType)
    name = Column(Unicode, unique=True)
    content = Column(UnicodeText)
    

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
    
class PartmanRaidRecipe(Base, SerialBase):
    __tablename__ = 'partman_raid_recipes'
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
    # ostype is either debian or mswindows
    ostype = Column(Text, default='debian')
    # a NULL release is the default release for the ostype
    release = Column(Text, nullable=True)
    autoinstall = Column(Boolean, default=False)
    # the arch is specified in debian terms and is
    # translated as needed
    # FIXME: do we want a i386 default?
    arch = Column(Text, default='i386')

    # recipe_id is ignored for ostype mswindows
    recipe_id = Column(Integer, ForeignKey('partman_recipes.id'),
                       nullable=True)
    # raid_recipe_id is ignored for ostype mswindows
    raid_recipe_id = Column(Integer, ForeignKey('partman_raid_recipes.id'),
                            nullable=True)
    # imagepath is ignored for ostype debian
    imagepath = Column(Text, nullable=True)

    # if there is more than one network interface that is discovered
    # by the debian-installer, this is the interface that will be used
    # during the install.
    iface = Column(Text, default='eth0')


    # make way for overriding default scripts
    preseed = Column(Integer, ForeignKey('machine_templates.id'),
                     nullable=True)
    pxeconfig = Column(Integer, ForeignKey('machine_templates.id'),
                       nullable=True)
    latescript = Column(Integer, ForeignKey('machine_templates.id'),
                        nullable=True)
    

class SaltKey(Base, SerialBase):
    __tablename__ = 'machine_salt_keys'
    id = Column(Integer, ForeignKey('machines.id'),
                primary_key=True)
    public = Column(Text, nullable=False)
    private = Column(Text, nullable=False)
    created = Column(DateTime, default=func.now())


# traits

class Trait(Base, SerialBase):
    __tablename__ = 'traits'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)
    description = Column(UnicodeText)
    
class TraitParent(Base, SerialBase):
    __tablename__ = 'trait_parents'
    trait_id = Column(Integer, ForeignKey('traits.id'),
                primary_key=True)
    parent_id = Column(Integer, ForeignKey('traits.id'),
                primary_key=True)
    
class TraitVariable(Base, SerialBase):
    __tablename__ = 'trait_variables'
    trait_id = Column(Integer, ForeignKey('traits.id'),
                primary_key=True)
    name = Column(Unicode, primary_key=True)
    value = Column(UnicodeText)
    pickled = Column(PickleType)
    

# families

class Family(Base, SerialBase):
    __tablename__ = 'families'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)
    description = Column(UnicodeText)

class FamilyParent(Base, SerialBase):
    __tablename__ = 'family_parents'
    family_id = Column(Integer, ForeignKey('families.id'),
                       primary_key=True)
    parent_id = Column(Integer, ForeignKey('families.id'),
                       primary_key=True)

class FamilyVariable(Base, SerialBase):
    __tablename__ = 'family_variables'
    family_id = Column(Integer, ForeignKey('families.id'),
                       primary_key=True)
    name = Column(Unicode, primary_key=True)
    value = Column(UnicodeText)
    pickled = Column(PickleType)
    

    
    
    
    
                    

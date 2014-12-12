import logging
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from zope.sqlalchemy import ZopeTransactionExtension

log = logging.getLogger(__name__)

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class SerialBase(object):
    def serialize(self):
        data = dict()
        table = self.__table__
        for column in table.columns:
            name = column.name
            try:
                pytype = column.type.python_type
            except NotImplementedError:
                print "NOTIMPLEMENTEDERROR", column.type
            value = getattr(self, name)
            if pytype is datetime:
                value = value.isoformat()
            data[name] = value
        return data
    
                

from useless.base import NoExistError
from useless.base.util import Gpg
from useless.sqlgen.clause import Eq

class NoAptKeyError(NoExistError):
    pass

class AptKeyHandler(object):
    def __init__(self, conn):
        self.conn = conn
        self.cursor = self.conn.cursor(statement=True)

    def get_rows(self):
        return self.cursor.select(table='archive_keys', order=['name'])
    
    def get_row(self, name):
        clause = Eq('name', name)
        try:
            row = self.cursor.select_row(table='archive_keys', clause=clause)
            return row
        except NoExistError:
            msg = "There's no apt key named %s in the database" % name
            raise NoAptKeyError , msg
        
    def get_keyid(self, keydata):
        gpg = Gpg()
        return gpg.importkey(keydata)
        

    def insert_key(self, name, data):
        keyid = self.get_keyid(data)
        row = dict(name=name, keyid=keyid, data=data)
        self.cursor.insert(table='archive_keys', data=row)

    def get_key(self, name):
        row = self.get_row(name)
        return row.data

    def delete_key(self, name):
        clause = Eq('name', name)
        self.cursor.delete(table='archive_keys', clause=clause)

    def update_key(self, name, rowdata):
        clause = Eq(name=name)
        self.cursor.update(table='archive_keys', data=rowdata, clause=clause)

    def get_keys(self):
        return self.get_rows()



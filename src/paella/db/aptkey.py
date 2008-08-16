import os

from useless.base import debug
from useless.sqlgen.clause import Eq

class AptKeyHandler(object):
    def __init__(self, conn):
        self.conn = conn
        self.cursor = self.conn.cursor(statement=True)

    def get_rows(self):
        return self.cursor.select(table='archive_keys', order=['name'])
    
    def get_row(self, name):
        clause = Eq('name', name)
        return self.cursor.select_row(table='archive_keys', clause=clause)

    def insert_key(self, name, data, fingerprint=None):
        row = dict(name=name, fingerprint=fingerprint, data=data)
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



import os
from os.path import join, isdir, isfile

from pyPgSQL.libpq import PgQuoteString as quote

from paella.base import Error, debug
from paella.base.config import Configuration
from paella.base.util import makepaths
from paella.base.objects import Parser

from paella.sqlgen.statement import Statement

from lowlevel import QuickConn
from midlevel import StatementCursor

def dquote(string):
    return '"%s"' %string

class AdminConnection(object):
    def __init__(self, cfg, dbname):
        object.__init__(self)
        self.conn = QuickConn(cfg)
        self.cursor = StatementCursor(self.conn, name='AdminConnection')
        self.stmt = Statement('select')
        self.dbname = dbname
        self.set_path(cfg.get('database', 'export_path'))

    def set_path(self, directory):
        self.path = directory
        makepaths(self.path)
        os.system('chmod 777 %s' % self.path)
        
    def to_tsv(self, table, key=None):
        self.stmt.table = table
        query = self.stmt.select(order=key)
        tsv = file(join(self.path, table + '.tsv'), 'w')
        self.cursor.execute(query)
        fields = [x[0] for x in self.cursor.description]
        tsv.write('\t'.join(map(quote, fields))+'\n')
        row = self.cursor.fetchone()
        while row:
            line = []
            for field in row:
                if field == None:
                    field = 'NULL'
                else:
                    field = str(field)
                line.append(quote(field))
            tsv.write('\t'.join(line)+'\n')
            row = self.cursor.fetchone()
        tsv.close()
        
    def set_table(self, table):
        self.stmt.set_table(table)

    def insert(self, table):
        self.cursor.set_table(table)
        tsv = Parser(join(self.path, table + '.tsv'))
        for row in tsv:
            self.cursor.insert(data=row)

    def copyto(self, table):
        path = join(self.path, table + '.bkup')
        self.cursor.copyto(table, path)

    def copyfrom(self, table):
        path = join(self.path, table + '.bkup')
        self.cursor.copyfrom(table, path)


    def backup(self):
        map(self.copyto, self.cursor.tables())

        
        

if __name__ == '__main__':
    g = Configuration(files=['/etc/paellarc'])
    ac = AdminConnection(g, 'paella')
    #ac.set_path('/home/umeboshi/workspace/dbackup')
    table = 'current_environment'

from useless.base.util import ujoin

from paella.debian.dpkg import ConfigObject

from useless.db.lowlevel import QuickConn
from useless.db.midlevel import StatementCursor
from useless.sqlgen.write import insert

from paella.schema.dpkg_schema import FilelistTable, Md5sumsTable
from paella.schema.dpkg_schema import StatusTable, AvailableTable


dpkg_tables = ['available', 'status', 'filelist', 'md5sums', 'conffiles']
other_tables = ['current']



def create_and_insert(cursor, table, data):
    cursor.create_table(table)
    for package, pdata in data.items():
        ndata = {}
        for field, value in pdata.items():
            if field.find('-') > -1:
                field = field.replace('-', '')
            ndata[field] = value
        cursor.insert(table.name, ndata)

def _insert_items(cursor, table, data, cols=None):
    if not cols:
        cols = [c.name for c in table.columns]

def mk_filelist_table(cursor, table, data):
    cursor.create_table(table)
    cols = [c.name for c in table.columns]
    for package, filelist in data.items():
        for afile in filelist:
            idict = dict(zip(cols, [package, afile]))
            cursor.insert(table.name, idict)
        
def mk_md5sums_table(cursor, table, data):
    cursor.create_table(table)
    cols = [c.name for c in table.columns]
    for package, filedict in data.items():
        for afile, asum in filedict.items():
            idict = dict(zip(cols, [package, afile, asum]))
            cursor.insert(table.name, idict)

def mk_current_table(cursor, table, data):
    cursor.create_table(table)
    cols = [c.name for c in table.columns]
    for package, filelist in data.items():
        for afile in filelist:
            idict = dict(zip(cols, [package, afile]))
            cursor.insert(table.name, idict)

def insert_status(config, cursor, table):
    data = config.status
    create_and_insert(cursor, table, data)

def insert_available(config, cursor, table):
    data = config.available
    create_and_insert(cursor, table, data)
        

class DpkgDb(object):
    def __init__(self, name, conn):
        object.__init__(self)
        self.name = name
        self.cmd = StatementCursor(conn, 'DpkgDb')

    def _table(self, table):
        return ujoin(self.name, table)

    def get_available(self, fields, **args):
        return self.cmd.getall(fields, self._table('available'), **args)
    def get_status(self, fields, **args):
        return self.cmd.getall(fields, self._table('status'), **args)

    def create(self, config):
        print 'making status'
        sttable = StatusTable(self._table('status'))
        create_and_insert(self.cmd, sttable, config.get_status())
        print 'making available'
        avtable = AvailableTable(self._table('available'))
        create_and_insert(self.cmd, avtable, config.get_available())
        print 'making filelist'
        fltable = FilelistTable(self._table('files'))
        mk_filelist_table(self.cmd, fltable, config.get_files())
        print 'making conffiles'
        cftable = FilelistTable(self._table('conffiles'))
        mk_filelist_table(self.cmd, cftable, config.get_conffiles())
        print 'making md5sums'
        mdtable = Md5sumsTable(self._table('md5sums'))
        mk_md5sums_table(self.cmd, mdtable, config.get_md5sums())
        print 'making current'
        cutable = Md5sumsTable(self._table('current'))
        mk_current_table(self.cmd, cutable, config.get_files())
        
    
if __name__ == '__main__':
    from useless.base.config import Configuration
    cfg = Configuration()
    Host = cfg['dbhost']
    Dbname = 'sysconfig'
    User = cfg['dbusername']
    Password = cfg['dbpassword']
    dsn = dict(dbhost=cfg['dbhost'],
               dbname='sysconfig',
               dbusername=cfg['dbusername'],
               dbpassword=cfg['dbpassword'])               
    c = QuickConn(dsn)
    cmd = CommandCursor(c, 'dsfsdf')
    #cmd.execute('create table %s' %t)
    co = ConfigObject()
    #co.set_every_config()
    #at = Table('atable', available_columns)
    #st = Table('stable', status_columns)
    def dtable():
        cmd.execute('drop table ptable')

    def dtables():
        for t in cmd.tables():
            if t != 'footable':
                cmd.execute('drop table %s' %t)
    #dtables()
    #insert_status(co, cmd, st)
    #insert_available(co, cmd, at)
    dd = DpkgDb('newmack', c)
    ft = FilelistTable('fftable')
    

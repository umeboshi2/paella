
from pyPgSQL import PgSQL
from pyPgSQL.PgSQL import Connection, Cursor, PgLargeObject
from pyPgSQL.libpq import IntegrityError, OperationalError

from sqlite.main import Connection as Connection_lite
from sqlite.main import Cursor as Cursor_lite

from paella.base import Error, debug
from paella.base.util import Pkdictrows
from paella.sqlgen.select import complex_select as select
from paella.sqlgen.write import insert, delete, update


tquery_lite = "SELECT name from sqlite_master where type='table'"
tquery_pg = "SELECT tablename from pg_tables"# where tablename not like 'pg_%'"

class LocalConnection(Connection_lite):
    def __init__(self, dbname='test.db', autocommit=1):
        Connection_lite.__init__(self, dbname, autocommit=autocommit)
        

class BasicConnection(Connection):
    def __init__(self, user=None, host=None, dbname=None, passwd=None,
                 port=5432):
        if passwd:
            conninfo = 'user=%s host=%s dbname=%s password=%s port=%s' \
                       %(user, host, dbname, passwd, str(port))
        else:
            conninfo = 'user=%s host=%s dbname=%s port=%s' %(user, host, dbname, str(port))
        Connection.__init__(self, conninfo)

    def createfile(self, mode=00644):
        return self.conn.lo_creat(mode)

    def importfile(self, path):
        return self.conn.lo_import(path)

    def exportfile(self, oid, path):
        return self.conn.lo_export(oid, path)
    
    def removefile(self, oid):
        self.conn.lo_unlink(oid)

class BaseConnection(BasicConnection):
    pass


class QuickConn(BasicConnection):
    def __init__(self, cfg=None):
        if cfg is None:
            raise Error, 'need config now'
        user = cfg['dbusername']
        host = cfg['dbhost']
        dbname = cfg['dbname']
        passwd = cfg['dbpassword']
        autocommit = 0
        if cfg['autocommit'] == 'true':
            autocommit = 1
        BasicConnection.__init__(self, user=user, host=host,
                                dbname=dbname, passwd=passwd)
        self.autocommit = autocommit


class _Simple(object):
    def fields(self, table):
        query = 'select * from %s where NULL' % table
        self.execute(query)
        return [col[0] for col in self.description]

    def copyto(self, table, path):
        self.execute("copy %s to '%s'" %(table, path))

    def copyfrom(self, table, path):
        self.execute("copy %s from '%s'" %(table, path))

    def has_table(self, table):
        return table in self.tables()

    def tables(self):
        self.execute(self.__tquery__)
        return [t[0] for t in self.fetchall() if t[0][:3] not in [ 'pg_', 'sql']]

    def create_table(self, table):
        if table.name not in self.tables():
            self.execute('create table %s' %table)
        else:
            raise Error, 'Table %s already Exists' % table.name

    def create_sequence(self, seq):
        if seq.name not in self.sequences():
            self.execute('create sequence %s' % seq)
        else:
            raise Error, 'Sequence %s already Exists' % seq.name

    def create_trigger(self, trigger):
        self.execute('create trigger %s' % trigger)
        

    def sequences(self):
        query = "select relname from pg_class where relkind='S'"
        self.execute(query)
        return [s[0] for s in self.fetchall()]

    def create_database(self, dbname):
        self.execute('create database %s' % dbname)
        
    
class FakeCursor(_Simple):
    def __init__(self, conn, name=None):
        if issubclass(conn.__class__, BasicConnection):
            self.__dbtype__ = 'pg'
            self.__tquery__ = tquery_pg
        elif conn.__class__.__name__ == 'LocalConnection':
            self.__dbtype__ = 'lite'
            self.__tquery__ = tquery_lite
        else:
            print 'WARNING NO CURSOR', conn.__class__
        self.__real_cursor__ = conn.cursor()
        self._already_selected = False
        
    def close(self):
        self.__real_cursor__.close()

    def commit(self):
        self.__real_cursor__.commit()
    def execute(self, query, *args):
        #debug(query)
        try:
            self.__real_cursor__.execute(query, *args)
        except IntegrityError, error:
            raise IntegrityError, '%s: %s' % (error, query)
        except OperationalError, error:
            raise OperationalError, '%s: %s' % (error, query)
        self.description = self.__real_cursor__.description

    def executemany(self, query, args):
        self.__real_cursor__.executemany(query, args)
        self.description = self.__real_cursor__.description

    def fetchone(self):
        return self.__real_cursor__.fetchone()

    def fetchmany(self, size=None):
        return self.__real_cursor__.fetchmany(sz=size)

    def fetchall(self):
        return self.__real_cursor__.fetchall()

    def next(self):
        row = self.__real_cursor__.fetchone()
        if not row:
            self._already_selected = False
            raise StopIteration
        return row

    def __iter__(self):
        if not self._already_selected:
            return self.iselect()
        return self
    
    def __len__(self):
        return self.__real_cursor__._rows_

class CommandCursor(FakeCursor):
    def __init__(self, conn, name=None):
        FakeCursor.__init__(self, conn, name=name)
        
    def __fselect__(self, function, field, table, clause=None):
        query = 'select %s(%s) from %s' %(function, field, table)
        if clause:
            query += ' where %s' % clause
        return query

    def max(self, field, table, clause=None):
        self.execute(self.__fselect__('max', field, table, clause=clause))
        return self.fetchall()
    def min(self, field, table, clause=None):
        self.execute(self.__fselect__('min', field, table, clause=clause))
        return self.fetchall()
    def count(self, field, table, clause=None):
        self.execute(self.__fselect__('count', field, table, clause=clause))
        return self.fetchall()

    def _select(self, fields, table, **args):
        query = select(table, columns=fields, **args)
        print query
        self.execute(query)
        
    def insert(self, table, adict):
        query = insert(table, adict)
        #print query
        self.execute(query)

    def update(self, table, adict,  clause=None):
        query = update(table, adict, clause=clause)
        self.execute(query)

    def delete(self, table, clause=None):
        query = delete(table, clause=clause)
        self.execute(query)
    def get(self, query):
        self.execute(query)
        return self.fetchall()
        
    def getall(self, fields, table, **args):
        self._select(fields, table, **args)
        return self.fetchall()

    def as_dict(self, table, keyfield, fields=None, **args):
        if not fields:
            fields = ['*']
        self._select(fields, table, **args)
        return Pkdictrows(self.fetchall(), keyfield)

    def drop(self, table):
        self.execute('drop table %s' % table)

    def file(self, conn):
        f = conn.createfile('rw')
        oid = int(f.name)
        f = PgLargeObject(conn.conn, oid)
        f.open('rw')
        return f

    def openfile(self, conn, oid, mode='rw'):
        f = PgLargeObject(conn.conn, int(oid))
        f.open(mode)
        return f

    def removefile(self, conn, oid):
        conn.removefile(oid)

    
class TrackerCursor(CommandCursor):
    def __init__(self, conn, basename, name='TrackerCursor'):
        CommandCursor.__init__(self, conn, name=name)
        self.basename = basename
        


    
if __name__ == '__main__':
    #s = Simple(c, name = 'foocursor')
    cc = CommandCursor
    cmd = CommandCursor(c, 'dsfsdf')
    lc = LocalConnection()
    #cc = SimpleLocal(lc)
    #db1 = _Simple2(c)
    #db2 = _Simple2(lc)
    

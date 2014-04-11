import os

from useless.base import Error, NoExistError
from useless.base.util import ujoin

from useless.db.lowlevel import BasicConnection
from useless.db.midlevel import StatementCursor

from paella.base import PaellaConfig
from paella.base.objects import VariablesConfig

from base import SuiteCursor

class PaellaConnection(BasicConnection):
    def __init__(self, dsn=None, cfg=None):
        if dsn is None:
            dsn = PaellaConfig('database').get_dsn()
        if cfg is not None:
            deprecated('cfg parameter to PaellaConnection is deprecated')
            dsn = None
            if type(cfg) is PaellaConfig:
                dsn = cfg.get_dsn()
        if dsn is None:
            raise RuntimeError , 'Problem with the arguments to PaellaConnection'
        if os.environ.has_key('PAELLA_DBHOST'):
            dsn['dbhost'] = os.environ['PAELLA_DBHOST']
        if os.environ.has_key('PAELLA_DBNAME'):
            dsn['dbname'] = os.environ['PAELLA_DBNAME']
        if os.environ.has_key('PAELLA_DBPORT'):
            dsn['dbport'] = int(os.environ['PAELLA_DBPORT'])
            if dsn['dbport'] not in range(1, 65536):
                raise ValueError, 'bad database port %s' % dsn['dbport']
        if os.environ.has_key('PAELLA_DBUSER'):
            dsn['dbusername'] = os.environ['PAELLA_DBUSER']
        user = dsn['dbusername']
        host = dsn['dbhost']
        dbname = dsn['dbname']
        passwd = dsn['dbpassword']
        if 'dbport' in dsn:
            port = dsn['dbport']
        else:
            port = 5432
        BasicConnection.__init__(self, user=user, host=host,
                                dbname=dbname, passwd=passwd, port=port)
        self.autocommit = 1
        self.__dict__['suitecursor'] = SuiteCursor(self)
        
    # this is kind of hacky looking
    # don't know if I'll keep this or not
    # this should keep me from having to import StatementCursor
    # everywhere I need the connection object
    def cursor(self, statement=False):
        if statement:
            return StatementCursor(self)
        else:
            return BasicConnection.cursor(self)

    def get_dsn(self):
        return dict(dbusername=self.conn.user, dbhost=self.conn.host,
                    dbname=self.conn.db, dbpassword=self.conn.password)
    
class DefaultEnvironment(VariablesConfig):
    def __init__(self, conn):
        VariablesConfig.__init__(self, conn, 'default_environment',
                                 'section', option='option')
        
class CurrentEnvironment(VariablesConfig):
    def __init__(self, conn):
        VariablesConfig.__init__(self, conn, 'current_environment',
                                 'hostname', option='name')
        
if __name__ == '__main__':
    c = PaellaConnection()
    vc = VariablesConfig(c, 'family_environment', 'trait',
                         'family', 'test2')
    

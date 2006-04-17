import os

from useless.base import Error, NoExistError
from useless.base.util import ujoin

from useless.db.lowlevel import BasicConnection
from useless.db.midlevel import StatementCursor

from paella.base import PaellaConfig
from paella.base.objects import VariablesConfig

class PaellaConnection(BasicConnection):
    def __init__(self, cfg=None):
        if cfg is None:
            cfg = PaellaConfig('database')
        if type(cfg) is not dict:
            dsn = cfg.get_dsn()
        else:
            dsn = cfg
        if os.environ.has_key('PAELLA_DBHOST'):
            dsn['dbhost'] = os.environ['PAELLA_DBHOST']
        if os.environ.has_key('PAELLA_DBNAME'):
            dsn['dbname'] = os.environ['PAELLA_DBNAME']
        if os.environ.has_key('PAELLA_DBPORT'):
            dsn['dbport'] = int(os.environ['PAELLA_DBPORT'])
            if dsn['dbport'] not in range(1, 65536):
                raise ValueError, 'bad database port %s' % dsn['dbport']
        user = dsn['dbusername']
        host = dsn['dbhost']
        dbname = dsn['dbname']
        passwd = dsn['dbpassword']
        autocommit = 0
        if dsn['autocommit'] == 'true':
            autocommit = 1
        if 'dbport' in dsn:
            port = dsn['dbport']
        else:
            port = 5432
        BasicConnection.__init__(self, user=user, host=host,
                                dbname=dbname, passwd=passwd, port=port)
        self.autocommit = autocommit
        
class ProfileStruct(object):
    name = 'myprofile'
    suite = 'sid'
    traits = ['admin']
    environ = {}
    template = 'path_to_template'

class TraitStruct(object):
    name = 'mytrait'
    suite = 'sid'
    parents = ['another_trait', 'maybe_another_trait']
    packages = dict.fromkeys(['bash', 'apache', 'python'], 'install')
    environ = {'name' : 'value'}
    templates = ['rel_path_to_template1',
                 'rel_path_to_template2']


class Suites(StatementCursor):
    def __init__(self, conn):
        StatementCursor.__init__(self, conn, name='Suites')
        self.set_table('suites')
        self.current = None

    def list(self):
        return [x.suite for x in self.select()]

    def set(self, suite):
        if suite not in self.list():
            raise NoExistError, 'bad suite'
        self.current = suite

class AllTraits(StatementCursor):
    def __init__(self, conn):
        StatementCursor.__init__(self, conn, name='AllTraits')
        self.set_table('traits')

    def list(self):
        return [x.trait for x in self.select()]

class Traits(StatementCursor):
    def __init__(self, conn, suite):
        StatementCursor.__init__(self, conn, name='AllTraits')
        self.set_suite(suite)
        
        
    def set_suite(self, suite):
        self.suite = suite
        self.set_table(ujoin(self.suite, 'traits'))
        

    def list(self):
        return [x.trait for x in self.select(order=['trait'])]
    

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
    

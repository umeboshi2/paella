from os.path import join

from useless.base import Error
from useless.base.util import ujoin, strfile, filecopy
from useless.db.midlevel import StatementCursor

from useless.sqlgen.admin import grant_public
from useless.sqlgen.clause import Eq

from paella.base.objects import TextFileManager
from schema.tables import suite_tables

class Suites(StatementCursor):
    def __init__(self, conn):
        StatementCursor.__init__(self, conn, name='Suites')
        self.set_table('suites')
        self.current = None

    def list(self):
        return [x.suite for x in self.select()]

    def set(self, suite):
        if suite not in self.list():
            raise Error, 'bad suite'
        self.current = suite


class SuiteCursor(StatementCursor):
    def __init__(self, conn):
        StatementCursor.__init__(self, conn, name='SuiteCursor')
        self.current = None

    def get_suites(self):
        return [x.suite for x in self.select(table='suites', order=['suite'])]
    
    def set_suite(self, suite):
        self.current = suite

    def get_apt_rows(self, suite=None):
        if suite is None:
            suite = self.current
        table = 'suite_apt_sources natural join apt_sources'
        return self.select(table=table, clause=Eq('suite', suite), order='ord')

    def make_suite_tables(self, suite=None):
        if suite is None:
            suite = self.current
        tables = suite_tables(suite)
        for table in tables:
            self.cursor.create_table(table)
        self.cursor.execute(grant_public[t.name for t in tables])
        

    # the base suite is the dist column of the first apt source of a suite
    def get_base_suite(self, suite):
        row = self.get_apt_rows(suite=suite)[0]
        return row.dist

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
    
def get_traits(conn, profile):
    cursor = StatementCursor(conn)
    cursor.set_table('profile_trait')
    cursor.set_clause([('profile', profile)])
    return [r.trait for r in cursor.select()]

def get_suite(conn, profile):
    cursor = StatementCursor(conn)
    cursor.set_table('profiles')
    cursor.set_clause([('profile', profile)])
    return [r.suite for r in cursor.select()][0]

class ScriptCursor(StatementCursor):
    def __init__(self, conn, table, keyfield):
        StatementCursor.__init__(self, conn, name='AllTraits')
        self.set_table(table)
        self.textfiles = TextFileManager(conn)
        self._keyfield = keyfield
        self._jtable = '%s as s join textfiles as t ' % table
        self._jtable += 'on s.scriptfile = t.fileid' 

    def _clause(self, name, keyfield=None):
        # clause = Eq(self._keyfield, keyfield) & Eq('script', name)
        # return clause
        raise Error, 'this member must be overridden'
    
    def insert_script(self, name, scriptfile):
        # current_key = self.current_trait
        # self._insert_script(name, scriptfile, current_key)
        raise Error, 'insert_script must be overridden'

    def scripts(self, key=None):
        # this is not called with the keyword arg
        # returns rows of script names for
        # current key
        raise Error, 'scripts must be overridden'
    
    def scriptfile(self, name):
        return strfile(self.scriptdata(name))
            
    def _script_row(self, name):
        table = self._jtable
        clause = self._clause(name)
        return self.select_row(fields=['*'], table=table, clause=clause)
        
    def _script_id(self, name):
        return self._script_row(name).scriptfile
        
    def scriptdata(self, name):
        return self._script_row(name).data
        
    def save_script(self, name, scriptfile):
        id = self.textfiles.insert_file(scriptfile)
        clause = self._clause(name)
        self.update(data=dict(scriptfile=str(id)), clause=clause)

    def remove_scriptfile(self, name):
        print 'remove_scriptfile deprecated'
        raise Error, 'remove_scriptfile is deprecated'
    
    def get(self, name):
        clause = self._clause(name)
        rows = self.select(clause=clause)
        if len(rows) == 1:
            return self.scriptfile(name)
        else:
            return None

    def read_script(self, name):
        return self.scriptdata(name)

    def _insert_script(self, name, scriptfile, current_key):
        insert_data = {}
        insert_data[self._keyfield] = current_key
        insert_data['script'] = name
        id = self.textfiles.insert_file(scriptfile)
        insert_data['scriptfile'] = str(id)
        self.insert(data=insert_data)
        
    def update_script(self, name, scriptfile):
        id = self.textfiles.insert_file(scriptfile)
        clause = self._clause(name)
        data = dict(scriptfile=str(id))
        self.update(data=data, clause=clause)

    def update_scriptdata(self, name, data):
        clause = self._clause(name)
        id = self.textfiles.insert_data(data)
        self.update(data=dict(scriptfile=str(id)), clause=clause)

    def export_scripts(self, bkup_path):
        for row in self.scripts():
            npath = join(bkup_path, 'script-%s' % row.script)
            nfile = self.scriptfile(row.script)
            filecopy(nfile, npath)
            nfile.close()

    def delete_script(self, name):
        clause = self._clause(name)
        self.delete(clause=clause)
        
        
        
if __name__ == '__main__':
    from paella.db import PaellaConnection
    from paella.base.objects import VariablesConfig
    c = PaellaConnection()
    #tp = TraitParent(c, 'woody')
    #pp = TraitPackage(c, 'woody')
    #ct = ConfigTemplate()
    #p = Parser('var-table.csv')
    vc = VariablesConfig(c, 'family_environment', 'trait',
                         'family', 'test2')
    

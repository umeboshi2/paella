from useless.base import NoExistError
from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq

from paella.base.util import edit_dbfile


class MachineType(object):
    def __init__(self, mtype):
        object.__init__(self)
        self.name = mtype
        self.parent = None
        self.kernel = None
        self.diskconfig = None
        self.scripts = []
        self.families = []
        self.variables = []

    def __repr__(self):
        return '<MachineType:  %s>' % self.name

    def append_modules(self, modules):
        self.modules = modules

    def append_script(self, name, data):
        self.scripts.append((name, data))

    def append_family(self, family):
        self.families.append(family)

    def append_variable(self, trait, name, value):
        self.variables.append((trait, name, value))
        
class MachineModules(list):
    def __init__(self, mtype, modules):
        list.__init__(self, modules)
        self.mtype = mtype
        
class Machine(dict):
    def __init__(self, name, mtype, kernel, profile):
        dict.__init__(self, name=name,
                      machine_type=mtype,
                      kernel=kernel,
                      profile=profile)
        
class DiskConfigHandler(object):
    def __init__(self, conn):
        self.conn = conn
        self.cursor = self.conn.cursor(statement=True)
        self.cursor.set_table('diskconfig')

    def get(self, name):
        clause = Eq('name', name)
        return self.cursor.select_row(clause=clause)

    def set(self, name, data=None):
        if data is None:
            data = {}
        insert = False
        try:
            self.get(name)
        except NoExistError:
            insert = True
        if insert:
            data['name'] = name
            self.cursor.insert(data=data)
        else:
            clause = Eq('name', name)
            self.cursor.update(data=data, clause=clause)

    def delete(self, name):
        clause = Eq('name', name)
        self.cursor.delete(clause=clause)

    def edit_diskconfig(self, name):
        row = self.get(name)
        content = row.content
        if content is None:
            content = ''
        data = edit_dbfile(name, content, 'diskconfig')
        if data is not None:
            self.set(name, data=dict(content=data))
            

if __name__ == '__main__':
    pass

    

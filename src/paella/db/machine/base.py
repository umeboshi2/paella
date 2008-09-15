from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq


class MachineType(object):
    def __init__(self, mtype):
        object.__init__(self)
        self.name = mtype
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
        

if __name__ == '__main__':
    pass

    

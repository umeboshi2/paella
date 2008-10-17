from useless.base import NoExistError
from useless.sqlgen.clause import Eq

from paella.base.util import edit_dbfile

class NoSuchKernelError(NoExistError):
    pass

def Table_cursor(conn, table):
    cursor = conn.cursor(statement=True)
    cursor.set_table(table)
    return cursor

class Machine(object):
    """This class is used to hold information about
    a machine from the xml parser."""
    
    def __init__(self, name):
        object.__init__(self)
        self.name = name
        self.parent = None
        self.kernel = None
        self.diskconfig = None
        self.scripts = []
        self.families = []
        self.variables = []

    def __repr__(self):
        return '<Machine:  %s>' % self.name

    def append_modules(self, modules):
        self.modules = modules

    def append_script(self, name):
        self.scripts.append(name)

    def append_family(self, family):
        self.families.append(family)

    def append_variable(self, trait, name, value):
        self.variables.append((trait, name, value))
        
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

class KernelsHandler(object):
    def __init__(self, conn):
        self.conn = conn
        self.cursor = self.conn.cursor(statement=True)
        self.cursor.set_table('kernels')

    def _check_kernel_exists(self, kernel):
            clause = Eq('package', kernel)
            return self.cursor.select(table='apt_source_packages', clause=clause)
            
    def get_kernel_rows(self):
        return self.cursor.select(order=['kernel'])

    def get_kernels(self):
        return [row.kernel for row in self.get_kernel_rows()]

    def add_kernel(self, kernel):
        # this check keeps from just any package as
        # a kernel, but also ties this to linux
        if not kernel.startswith('linux-image'):
            raise RuntimeError , "%s doesn't seem to be a kernel package" % kernel
        if self._check_kernel_exists(kernel):
            self.cursor.insert(data=dict(kernel=kernel))
        else:
            raise NoExistError, "There's no package named %s" % kernel
        
    def delete_kernel(self, kernel):
        clause = Eq('kernel', kernel)
        self.cursor.delete(clause=clause)
        

class BaseMachineDbObject(object):
    def __init__(self, conn, table=None):
        self.conn = conn
        self.cursor = self.conn.cursor(statement=True)
        self.current_machine = None
        if table is not None:
            self.cursor.set_table(table)
            
    def set_machine(self, machine):
        clause = Eq('machine', machine)
        try:
            row = self.cursor.select_row(table='machines', clause=clause)
        except NoExistError:
            msg = "There's no machine named %s" % machine
            raise NoExistError , msg
        self.current_machine = machine

    def _check_machine_set(self):
        if self.current_machine is None:
            name = self.__class__.__name__
            raise RuntimeError , "Machine isn't set in %s" % name

    def _machine_clause_(self, machine=None):
        if machine is None:
            self._check_machine_set()
            machine = self.current_machine
        return Eq('machine', machine)
    
class BaseMachineHandler(BaseMachineDbObject):
    def __init__(self, conn):
        BaseMachineDbObject.__init__(self, conn, table='machines')
        self.kernels = Table_cursor(self.conn, 'kernels')

    def set_machine(self, machine):
        BaseMachineDbObject.set_machine(self, machine)
        clause = self._machine_clause_()
        row = self.cursor.select_row(clause=clause)
        self.diskconfig = row.diskconfig
        self.kernel = row.kernel
        self.profile = row.profile
        
    def set_autoinstall(self, auto=True):
        self._check_machine_set()
        if auto:
            value = 'True'
        else:
            value = 'False'
        machine = self.current_machine
        table = 'default_environment'
        data = dict(section='autoinstall', option=machine, value=value)
        clause = Eq('section', 'autoinstall') & Eq('option', machine)
        rows = self.cursor.select(table=table, clause=clause)
        if not len(rows):
            self.cursor.insert(table=table, data=data)
        elif len(rows) == 1:
            self.cursor.update(table=table, data=dict(value=value),
                               clause=clause)
        else:
            raise Error, 'too many rows for this machine: %s' % machine
        
        
    def _update_row(self, data):
        self._check_machine_set()
        self.cursor.update(data=data, clause=self._machine_clause_())
        
    def set_profile(self, profile):
        if profile is None:
            self._clear_attribute('profile')
            return
        data = dict(profile=profile)
        self._update_row(data)
        # reset this object's attributes
        self.set_machine(self.current_machine)

    def _check_kernel_exists(self, kernel):
            clause = Eq('package', kernel)
            return self.cursor.select(table='apt_source_packages', clause=clause)
            
    def set_kernel(self, kernel):
        if kernel is None:
            self._clear_attribute('kernel')
            return
        # This list of kernels should be rather small
        # else we need to use a clause to determine
        # if the kernel is already present.
        # FIXME: Adding a fixme here to make sure
        # we use a clause to do this properly.
        kernels = [r.kernel for r in self.kernels.select()]
        data = dict(kernel=kernel)
        if kernel not in kernels:
            if self._check_kernel_exists(kernel):
                self.kernels.insert(data=data)
            else:
                msg = "There's no kernel named %s in the package list" % kernel
                raise NoSuchKernelError , msg
        self._update_row(data)
        # reset this object's attributes
        self.set_machine(self.current_machine)

    def set_diskconfig(self, diskconfig):
        if diskconfig is None:
            self._clear_attribute('diskconfig')
            return
        data = dict(diskconfig=diskconfig)
        self._update_row(data)
        # reset this object's attributes
        self.set_machine(self.current_machine)

    def _clear_attribute(self, attribute):
        self._check_machine_set()
        data = {attribute : None}
        self._update_row(data)
        # reset this object's attributes
        self.set_machine(self.current_machine)
        

if __name__ == '__main__':
    pass

    

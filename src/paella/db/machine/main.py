from os.path import basename, dirname, join
from xml.dom.minidom import parseString

from useless.base import NoExistError
from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq

from base import DiskConfigHandler
from mtype import MachineTypeHandler
from xmlparse import MachineDatabaseParser
from xmlgen import MachineDatabaseElement

def Table_cursor(conn, table):
    cursor = StatementCursor(conn, table)
    cursor.set_table(table)
    return cursor

class BaseMachineHandler(object):
    def __init__(self, conn):
        self.conn = conn
        self.cursor = Table_cursor(self.conn, 'machines')
        self.cursor.set_table('machines')
        self.kernels = Table_cursor(self.conn, 'kernels')
        self.mtype = MachineTypeHandler(self.conn)
        self.diskconfig = DiskConfigHandler(self.conn)
        self.current = None
        
    def set_machine(self, machine):
        self._machine_clause_ = Eq('machine', machine)
        self.current = self.cursor.select_row(clause=self._machine_clause_)
        mtype = self.current.machine_type
        self.mtype.set_machine_type(mtype)
        
    def approve_machine_ids(self):
       machine = self.current.machine
       table = 'current_environment'
       clause = "name like 'hwaddr_%'" + " and value='%s'" % machine
       fields = ["'machines' as section", 'name as option', 'value']
       rows = self.cursor.select(fields=fields, table=table, clause=clause)
       for row in rows:
           self.cursor.insert(table='default_environment', data=row)

    def set_autoinstall(self, auto=True):
        if auto:
            value = 'True'
        else:
            value = 'False'
        machine = self.current.machine
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
        
        
    def _update_field_(self, name, value):
        self.cursor.update(data={name:value}, clause=self._machine_clause_)
        self.set_machine(self.current.machine)
        
    def set_profile(self, profile):
        self._update_field_('profile', profile)

    def set_kernel(self, kernel):
        kernels = [r.kernel for r in self.kernels.select()]
        if kernel not in kernels:
            self.kernels.insert(data={'kernel' : kernel})
        self._update_field_('kernel', kernel)

    def set_machine_type(self, mtype):
        self._update_field_('machine_type', mtype)
        self.set_machine(self.current.machine)
        
    def rename_machine(self, newname):
        self._update_field_('machine', newname)
        self.set_machine(newname)

    
class MachineHandler(BaseMachineHandler):
    def add_machine_type(self, mtype):
        self.mtype.add_new_type(mtype)
        
    def add_new_kernel(self, kernel):
        self.kernels.insert(data=dict(kernel=kernel))

    def make_a_machine(self, machine, mtype, profile, kernel):
        self.cursor.insert(table='machines',
                           data=dict(machine=machine,
                                     machine_type=mtype,
                                     profile=profile,
                                     kernel=kernel))

    def update_a_machine(self, machine, mtype, profile, kernel):
        clause = Eq('machine', machine)
        data = dict(machine_type=mtype, profile=profile,
                    kernel=kernel)
        self.cursor.update(table='machines', data=data, clause=clause)
        
    def insert_parsed_element(self, element):
        map(self.add_new_kernel, element.kernels)
        for mtype in element.mtypes:
            print 'mtype is', mtype
            #self.mtype.insert_parsed_element(mtype)
            self.mtype.import_machine_type(element, mtype)
            
        for machine in element.machines:
            data = {}
            data.update(machine)
            del data['name']
            data['machine'] = machine['name']
            self.cursor.insert(table='machines', data=data)

    def parse_xmlfile(self, path):
        element = parseString(file(path).read())
        return MachineDatabaseParser(dirname(path), element.firstChild)
    
    def restore_machine_database(self, path):
        mdbfile = join(path, 'machine_database.xml')
        parsed = self.parse_xmlfile(mdbfile)
        self.insert_parsed_element(parsed)
        
    def export_machine_database(self, path):
        me = MachineDatabaseElement(self.conn)
        mdfile = file(join(path, 'machine_database.xml'), 'w')
        mtypepath = join(path, 'machine_types')
        mdfile.write(me.toprettyxml())
        mdfile.close()
        for mtype in me.mtypes.machine_types:
            name = mtype.getAttribute('name')
            self.mtype.set_machine_type(name)
            self.mtype.export_machine_type(name, mtypepath)
            
    def get_modules(self, machine_type=None):
        return self.mtype.get_modules()

    def append_modules(self, modules, machine_type=None):
        self.mtype.append_modules(modules)

    def get_script(self, name):
        return self.mtype.get_script(name)

    def list_all_machine_types(self):
        rows = self.cursor.select(table='machine_types')
        return [r.machine_type for r in rows]
    
    def list_all_kernels(self):
        return [r.kernel for r in self.kernels.select()]

    def list_all_profiles(self):
        rows = self.cursor.select(table='profiles')
        return [r.profile for r in rows]

    def get_diskconfig(self):
        #mtype = self.current.machine_type
        return self.mtype.get_diskconfig()
            
if __name__ == '__main__':
    from os.path import join
    from paella.db import PaellaConnection
    conn = PaellaConnection()

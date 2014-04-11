from os.path import join
from xml.dom.minidom import Element

from useless.base import NoExistError
from useless.base.xmlfile import TextElement
from useless.base.util import makepaths
from useless.base.path import path

from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq, In

from paella.db.xmlgen import BaseVariableElement

class MachineScriptElement(Element):
    def __init__(self, name):
        Element.__init__(self, 'script')
        self.setAttribute('name', name)

class MachineVariableElement(BaseVariableElement):
    def __init__(self, trait, name, value):
        BaseVariableElement.__init__(self, 'machine_variable',
                                     trait, name, value)

class MachineFamilyElement(TextElement):
    def __init__(self, family):
        TextElement.__init__(self, 'family', family)
        
class MachineElement(Element):
    def __init__(self, conn, name):
        Element.__init__(self, 'machine')
        self.conn = conn
        self.cursor = StatementCursor(self.conn)
        self.setAttribute('name', name)
        self.scripts = []
        self.families = []
        self.variables = []
        self.machine = name
        clause = Eq('machine', name)
        self.set_attributes(clause)
        self._append_scripts(clause)
        self._append_families(clause)
        self._append_variables(clause)

    def set_attributes(self, clause):
        self.set_parent(clause)
        row = self.cursor.select_row(table='machines',
                                     clause=clause)
        if row.diskconfig is not None:
            self.setAttribute('diskconfig', row.diskconfig)
        if row.kernel is not None:
            self.setAttribute('kernel', row.kernel)
        if row.profile is not None:
            self.setAttribute('profile', row.profile)
            
    def set_parent(self, clause):
        try:
            row = self.cursor.select_row(table='machine_parent',
                                         clause=clause)
            parent = row.parent
        except NoExistError:
            parent = None
        if parent is not None:
            self.setAttribute('parent', parent)
            
    def append_family(self, family):
        fam_element = MachineFamilyElement(family)
        self.families.append(fam_element)
        self.appendChild(fam_element)

    def _append_families(self, clause):
        table = 'machine_family'
        fams = self.cursor.select(table=table, clause=clause, order='family')
        for row in fams:
            self.append_family(row.family)
        
    def append_script(self, name):
        script_element = MachineScriptElement(name)
        self.scripts.append(script_element)
        self.appendChild(script_element)

    def _append_scripts(self, clause):
        table = 'machine_scripts'
        scripts = self.cursor.select(table=table, clause=clause, order='script')
        for row in scripts:
            self.append_script(row.script)
    
    def append_variable(self, trait, name, value):
        variable_element = MachineVariableElement(trait, name, value)
        self.variables.append(variable_element)
        self.appendChild(variable_element)

    def _append_variables(self, clause):
        table = 'machine_variables'
        vlist = self.cursor.select(table=table, clause=clause, order=['name'])
        for row in vlist:
            self.append_variable(row.trait, row.name, row.value)

    def export_directory(self, machinetopdir):
        machine = self.getAttribute('name')
        dirname = path(machinetopdir) / machine
        return dirname

    def export(self, machinetopdir):
        dirname = self.export_directory(machinetopdir)
        makepaths(dirname)
        xmlfile = dirname / 'machine.xml'
        xmlfile.write_text(self.toprettyxml())

class MachineListElement(Element):
    def __init__(self, conn, machines=None):
        Element.__init__(self, 'machines')
        self.conn = conn
        self.cursor = StatementCursor(self.conn)
        if machines is None:
            rows = self.cursor.select(table='machines', order='machine')
            machines = [r.machine for r in rows]
        self.machines = []
        for machine in machines:
            machine_element = Element('machine')
            machine_element.setAttribute('name', machine)
            self.machines.append(machine_element)
            self.appendChild(machine_element)

class KernelElement(TextElement):
    def __init__(self, name):
        TextElement.__init__(self, 'kernel', name)
            
class KernelsElement(Element):
    def __init__(self, conn):
        Element.__init__(self, 'kernels')
        self.conn = conn
        self.cursor = StatementCursor(self.conn)
        self.kernels = []
        kernels = [r.kernel for r in self.cursor.select(table='kernels', order='kernel')]
        for k in kernels:
            k_element = KernelElement(k)
            self.kernels.append(k_element)
            self.appendChild(k_element)
            
class MachineDatabaseElement(Element):
    def __init__(self, conn):
        Element.__init__(self, 'machine_database')
        self.conn = conn
        self.kernels = KernelsElement(conn)
        self.machines = MachineListElement(conn)

        for e in [self.machines, self.kernels]:
            self.appendChild(e)
            
class ClientMachineDatabaseElement(Element):
    def __init__(self, conn, machines=None):
        raise RuntimeError , "ClientMachineDatabaseElement isn't working"
        Element.__init__(self, 'machine_database')
        self.conn = conn
        if machines is not None:
            self.machines = MachinesElement(conn, machines)
            self.appendChild(self.machines)
            

if __name__ == '__main__':
    from paella.db import PaellaConfig, PaellaConnection
    cfg = PaellaConfig()
    conn = PaellaConnection()

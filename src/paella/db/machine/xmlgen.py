from os.path import join
from xml.dom.minidom import Element

from useless.base import NoExistError
from useless.base.xmlfile import TextElement
from useless.base.util import makepaths
from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq, In

from paella.db.xmlgen import BaseVariableElement

class MachineModuleElement(TextElement):
    def __init__(self, mtype, module, order):
        TextElement.__init__(self, 'module', module)
        self.setAttribute('machine_type', mtype)
        self.setAttribute('order', order)
        
class MachineScriptElement(Element):
    def __init__(self, name):
        Element.__init__(self, 'script')
        self.setAttribute('name', name)

class MachineTypeVariableElement(BaseVariableElement):
    def __init__(self, trait, name, value):
        BaseVariableElement.__init__(self, 'machine_type_variable',
                                     trait, name, value)

class MachineTypeFamilyElement(TextElement):
    def __init__(self, family):
        TextElement.__init__(self, 'family', family)
        
class MachineTypeElement(Element):
    def __init__(self, conn, name):
        Element.__init__(self, 'machine_type')
        self.conn = conn
        self.cursor = StatementCursor(self.conn)
        self.setAttribute('name', name)
        self.modules = []
        self.scripts = []
        self.families = []
        self.variables = []
        self.machine_type = name
        clause = Eq('machine_type', name)
        #self.set_parent(clause)
        self.set_attributes(clause)
        self._append_modules(clause)
        self._append_scripts(clause)
        self._append_families(clause)
        # FIXME - we're not using variables yet
        self._append_variables(clause)

    def set_attributes(self, clause):
        self.set_parent(clause)
        row = self.cursor.select_row(table='machine_types',
                                     clause=clause)
        if row.diskconfig is not None:
            self.setAttribute('diskconfig', row.diskconfig)
            
    def set_parent(self, clause):
        try:
            row = self.cursor.select_row(table='machine_type_parent',
                                         clause=clause)
            parent = row.parent
        except NoExistError:
            parent = None
        if parent is not None:
            self.setAttribute('parent', parent)
            
    def append_module(self, module, order):
        mod_element = MachineModuleElement(self.machine_type,
                                           module, order)
        self.modules.append(mod_element)
        self.appendChild(mod_element)

    def _append_modules(self, clause):
        table = 'machine_modules'
        mods = self.cursor.select(table=table, clause=clause, order='ord')
        for row in mods:
            self.append_module(row.module, str(row.ord))
    
    def append_family(self, family):
        fam_element = MachineTypeFamilyElement(family)
        self.families.append(fam_element)
        self.appendChild(fam_element)

    def _append_families(self, clause):
        table = 'machine_type_family'
        fams = self.cursor.select(table=table, clause=clause, order='family')
        for row in fams:
            self.append_family(row.family)
        
    def append_script(self, name):
        script_element = MachineScriptElement(name)
        self.scripts.append(script_element)
        self.appendChild(script_element)

    def _append_scripts(self, clause):
        table = 'machine_type_scripts'
        scripts = self.cursor.select(table=table, clause=clause, order='script')
        for row in scripts:
            self.append_script(row.script)
    
    def append_variable(self, trait, name, value):
        variable_element = MachineTypeVariableElement(name, value)
        self.variables.append(variable_element)
        self.appendChild(variable_element)

    def _append_variables(self, clause):
        table = 'machine_type_variables'
        vlist = self.cursor.select(table=table, clause=clause, order=['name'])
        for row in vlist:
            self.append_variable(row.trait, row.name, row.value)
        
    def export(self, mtypepath):
        mtype = self.getAttribute('name')
        path = join(mtypepath, mtype)
        makepaths(path)
        xfile = file(join(path, 'machine_type.xml'), 'w')
        xfile.write(self.toprettyxml())
        xfile.close()

class MachineTypesElement(Element):
    def __init__(self, conn, mtypes=None):
        Element.__init__(self, 'machine_types')
        self.conn = conn
        self.cursor = StatementCursor(self.conn)
        if mtypes is None:
            rows = self.cursor.select(table='machine_types', order='machine_type')
            mtypes = [r.machine_type for r in rows]
        self.machine_types = []
        for mtype in mtypes:
            mtype_element = Element('machine_type')
            mtype_element.setAttribute('name', mtype)
            #mtype_element = MachineTypeElement(conn, mtype)
            self.machine_types.append(mtype_element)
            self.appendChild(mtype_element)

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
            
class MachineElement(TextElement):
    def __init__(self, machine, machine_type, kernel, profile):
        TextElement.__init__(self, 'machine', machine)
        self.setAttribute('machine_type', machine_type)
        self.setAttribute('kernel', kernel)
        self.setAttribute('profile', profile)

class MachinesElement(Element):
    def __init__(self, conn, machines=None):
        Element.__init__(self, 'machines')
        self.conn = conn
        self.cursor = StatementCursor(self.conn)
        self.machines = []
        if machines is None:
            machines = self.cursor.select(table='machines', order='machine')
        else:
            clause = In('machine', machines)
            machines = self.cursor.select(table='machines', clause=clause, order='machine')
        for m in machines:
            machine_element = MachineElement(m.machine, m.machine_type,
                                             m.kernel, m.profile)
            self.machines.append(machine_element)
            self.appendChild(machine_element)

class MachineDatabaseElement(Element):
    def __init__(self, conn):
        Element.__init__(self, 'machine_database')
        self.conn = conn
        self.mtypes = MachineTypesElement(conn)
        self.kernels = KernelsElement(conn)
        self.machines = MachinesElement(conn)

        for e in [self.machines, self.mtypes, self.kernels]:
            self.appendChild(e)
            
class ClientMachineDatabaseElement(Element):
    def __init__(self, conn, mtypes=None, machines=None):
        Element.__init__(self, 'machine_database')
        self.conn = conn
        if mtypes is not None:
            self.mtypes = MachineTypesElement(conn, mtypes)
            self.appendChild(self.mtypes)
        if machines is not None:
            self.machines = MachinesElement(conn, machines)
            self.appendChild(self.machines)
            

if __name__ == '__main__':
    from paella.profile.base import PaellaConfig, PaellaConnection
    cfg = PaellaConfig()
    conn = PaellaConnection(cfg)

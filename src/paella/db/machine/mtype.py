from os.path import join
from xml.dom.minidom import parseString

from useless.base.util import strfile
from useless.base import NoExistError
from useless.db.midlevel import StatementCursor, Environment
from useless.sqlgen.clause import Eq

from paella.base.util import edit_dbfile
from paella.base.objects import VariablesConfig
from paella.db.base import ScriptCursor
from paella.db.family import Family

from xmlgen import MachineTypeElement
from xmlparse import MachineTypeParser

class MachineTypeVariablesConfig(VariablesConfig):
    def __init__(self, conn, mtype):
        VariablesConfig.__init__(self, conn, 'machine_type_variables',
                                 'trait', 'machine_type', mtype)
        
class BaseMachineTypeObject(object):
    def __init__(self):
        object.__init__(self)
        self.current = None
        
    def _mtype_clause(self):
        return Eq('machine_type', self.current)

    def set_machine_type(self, machine_type):
        self.current = machine_type

class BaseMachineTypeCursor(BaseMachineTypeObject, StatementCursor):
    def __init__(self, conn, table):
        BaseMachineTypeObject.__init__(self)
        StatementCursor.__init__(self, conn)
        self.set_table(table)
        self.conn = conn
        
class BaseMachineTypeHandler(BaseMachineTypeCursor):
    def __init__(self, conn):
        BaseMachineTypeCursor.__init__(self, conn, 'machine_types')
        
    def add_disk(self, diskname, device):
        table = 'machine_disks'
        data = dict(machine_type=self.current,
                    diskname=diskname,
                    device=device)
        self.insert(table=table, data=data)

    def add_new_type(self, machine_type):
        data = dict(machine_type=machine_type)
        self.insert(data=data)

    def get_machine_types(self):
        return [row.machine_type for row in self.select()]
    
    def get_disk_devices(self):
        table = 'machine_disks'
        clause = self._mtype_clause()
        rows = self.select(fields=['device'], table=table, clause=clause)
        return [r.device for r in rows]

    def check_machine_disks(self):
        table = 'machine_disks'
        clause = self._mtype_clause()
        rows = self.select(table=table, clause=clause)
        dn_dict = {}
        for row in rows:
            if row.diskname not in dn_dict.keys():
                dn_dict[row.diskname] = []
            dn_dict[row.diskname].append(row.device)
        return dn_dict

    def make_partition_dump(self, diskname, device):
        table = 'partitions'
        clause = Eq('diskname', diskname)
        rows = self.select(table=table, clause=clause, order='partition')
        firstline = '# partition table of %s' % device
        secondline = 'unit: sectors'
        blankline = ''
        plines = []
        for row in rows:
            line = '%s%s : start=%9d, size=%9d, Id=%d' % \
                   (device, row.partition, int(row.start), int(row.size), int(row.id))
            plines.append(line)
        return '\n'.join([firstline, secondline, blankline] + plines) + '\n'
    


    def array_hack(self):
        dn_dict = self.check_machine_disks()
        disknames = dn_dict.keys()
        if len(disknames) == 1:
            diskname = disknames[0]
            if len(dn_dict[diskname]) > 1:
                device = '/dev/md'
            else:
                device = dn_dict[diskname][0]
        elif not len(dn_dict.keys()):
            device = '/dev/hda'
        else:
            raise Error, "can't handle more than one disktype now"
        return device
        

    def make_fstab(self, filesystem):
        machine_type = self.current
        fsmounts = self.get_all_fsmounts(filesystem=filesystem)
        device = self.array_hack()
        mddev = False
        if device == '/dev/md':
            mdnum = 0
            mddev = True
        fstab = []
        for row in fsmounts:
            fstype = row.fstype
            if int(row.partition) == 0:
                if fstype in ['tmpfs', 'proc', 'sysfs']:
                    _dev = fstype
                else:
                    _dev = '/dev/null'
            else:
                if mddev:
                    _dev = '/dev/md%d' % mdnum
                    mdnum += 1
                else:
                    _dev = '%s%s' % (device, row.partition)
            line = '%s\t%s\t%s' % (_dev, row.mnt_point, row.fstype)
            line += '\t%s\t%s\t%s' % (row.mnt_opts, row.dump, row['pass'])
            fstab.append(line)
        return '\n'.join(fstab) + '\n'

    def get_all_fsmounts(self, filesystem):
        table = 'filesystem_mounts natural join mounts'
        clause = Eq('filesystem', filesystem)
        return self.select(table=table, clause=clause, order='ord')

    def get_installable_fsmounts(self, filesystem):
        fsmounts = self.get_all_fsmounts(filesystem)
        return [r for r in fsmounts if int(r.partition)]

    def get_ordered_fsmounts(self, filesystem):
        table = 'filesystem_mounts natural join mounts'
        clause = Eq('filesystem', filesystem)
        return self.select(table=table, clause=clause, order='mnt_point')
    
    def get_modules(self):
        clause = self._mtype_clause()
        rows = self.select(table='machine_modules',
                           clause=clause, order='ord')
        return [r.module for r in rows]

    def append_modules(self, modules):
        data = dict(machine_type=self.current)
        current_mods = self.get_modules()
        next_ord = len(current_mods)        
        new_mods = [m for m in modules if m not in current_mods]
        for mod in new_mods:
            data['ord'] = next_ord
            data['module'] = mod
            self.insert(table='machine_modules', data=data)
            next_ord += 1
        
class MachineTypeScript(BaseMachineTypeObject, ScriptCursor):
    def __init__(self, conn):
        BaseMachineTypeObject.__init__(self)
        ScriptCursor.__init__(self, conn, 'machine_type_scripts', 'machine_type')

    def _clause(self, name):
        return Eq('script', name) & self._mtype_clause()

    def insert_script(self, name, scriptfile):
        self._insert_script(name, scriptfile, self.current)
        
    def scripts(self, key=None):
        return self.select(clause=self._mtype_clause())


# machine types can only have one parent
# unlike traits
class MachineTypeParent(BaseMachineTypeCursor):
    def __init__(self, conn):
        BaseMachineTypeCursor.__init__(self, conn, 'machine_type_parent')

    def get_parent(self, mtype):
        clause = Eq('machine_type', mtype)
        try:
            row = self.select_row(clause=clause)
            # NoExistError should be raised on above statement
            # if parent doesn't exist
            return row.parent
        except NoExistError:
            return None

    def set_parent(self, mtype, parent):
        data = dict(parent=parent)
        if self.get_parent(mtype) is None:
            data.update(dict(machine_type=mtype))
            self.insert(data=data)
        else:
            clause = Eq('machine_type', mtype)
            self.update(data=data, clause=clause)
        

    def get_parent_list(self, mtype, childfirst=True):
        parents = []
        parent = self.get_parent(mtype)
        while parent is not None:
            parents.append(parent)
            parent = self.get_parent(parent)
        if not childfirst:
            parents.reverse()
        return parents
    
        
        
class MachineTypeFamily(BaseMachineTypeCursor):
    def __init__(self, conn):
        BaseMachineTypeCursor.__init__(self, conn, 'machine_type_family')

class MachineTypeEnvironment(BaseMachineTypeObject, Environment):
    def __init__(self, conn, machine_type):
        BaseMachineTypeObject.__init__(self)
        Environment.__init__(self, conn, 'machine_type_variables', 'trait')
        self.current = machine_type

    def _single_clause_(self):
        return self._mtype_clause() & Eq('trait', self.__main_value__)

    def set_trait(self, trait):
        self.set_main(trait)

    def _make_superdict_(self):
        clause = self._mtype_clause()
        return Environment._make_superdict_(self, clause)
    
        
class MachineTypeHandler(BaseMachineTypeHandler):
    def __init__(self, conn):
        BaseMachineTypeHandler.__init__(self, conn)
        self._parents = MachineTypeParent(self.conn)
        self._mtfam = MachineTypeFamily(self.conn)
        self._fam = Family(self.conn)
        self._mtscript = MachineTypeScript(self.conn)
        self.parent = None

    def set_machine_type(self, machine_type):
        BaseMachineTypeHandler.set_machine_type(self, machine_type)
        self._mtenv = MachineTypeEnvironment(self.conn, machine_type)
        self._mtcfg = MachineTypeVariablesConfig(self.conn, machine_type)
        self._mtscript.set_machine_type(machine_type)
        self.parent = self._parents.get_parent(machine_type)
        
    def family_rows(self):
        clause = self._mtype_clause()
        return self._mtfam.select(clause=clause, order='family')

    def _family_clause(self, family):
        return self._mtype_clause() & Eq('family', family)
    
    def append_family(self, family):
        if family not in self.get_families():
            data = dict(machine_type=self.current, family=family)
            self._mtfam.insert(data=data)

    def delete_family(self, family):
        clause  = self._family_clause(family)
        self._mtfam.delete(clause=clause)

    def update_family(self, oldfam, newfam):
        clause = self._family_clause(oldfam)
        self._mtfam.update(data=dict(family=newfam), clause=clause)
        
    def append_variable(self, trait, name, value):
        data = dict(trait=trait, name=name, value=value,
                    machine_type=self.current)
        self._mtenv.cursor.insert(data=data)

    def _variable_clause(self, trait, name):
        return self._mtype_clause() & Eq('trait', trait) & Eq('name', name)
    
    def delete_variable(self, trait, name):
        clause = self._variable_clause(trait, name)
        self._mtenv.cursor.delete(clause=clause)

    def update_variable(self, trait, name, value):
        clause = self._variable_clause(trait, name)
        self._mtenv.update(data=dict(value=value), clause=clause)

    def edit_variables(self):
        newvars = self._mtcfg.edit()
        self._mtcfg.update(newvars)

    def edit_script(self, name):
        script = self.get_script(name)
        if script is not None:
            data = edit_dbfile(name, script.read(), 'script')
            if data is not None:
                self._mtscript.save_script(name, strfile(data))
                print 'need to update'
                
    def get_families(self):
        return [r.family for r in self.family_rows()]

    def get_family_data(self):
        families = self.get_families()
        return self._fam.FamilyData(families)

    def get_machine_type_data(self):
        data = self.get_family_data()
        data.update(self.MachineTypeData())
        return data

    def MachineTypeData(self):
        return self._mtenv._make_superdict_()
    
    def get_script(self, name):
        return self._mtscript.get(name)

    def insert_script(self, name, scriptfile):
        self._mtscript.insert_script(name, scriptfile)

    def delete_script(self, name):
        self._mtscript.delete_script(name)
        
    
    def insert_parsed_element(self, mtype_element, path):
        mtype = mtype_element.mtype
        self.add_new_type(mtype.name)
        self.set_machine_type(mtype.name)
        mdisktable = 'machine_disks'
        for mdisk in  mtype.disks:
            mdisk['machine_type'] = mtype.name
            self.insert(table=mdisktable, data=mdisk)
                
        mod_items = zip(range(len(mtype.modules)), mtype.modules)
        data = dict(machine_type=mtype.name)
        for i in range(len(mtype.modules)):
            data['ord'] = str(i)
            data['module'] = mtype.modules[i]
            self.insert(table='machine_modules', data=data)
        data = dict(machine_type=mtype.name)
        for f in mtype.families:
            data['family'] = f
            self.insert(table='machine_type_family', data=data)
        for s, d in mtype.scripts:
            scriptfile = file(join(path, 'script-%s' % s))
            self._mtscript.insert_script(s, scriptfile)
            print 'imported %s' % s
        for trait, name, value in mtype.variables:
            data = dict(machine_type=mtype.name,
                        trait=trait, name=name, value=value)
            self.insert(table='machine_type_variables', data=data)
        
    def import_machine_type_ignore(self, name, mtypepath):
        path = join(mtypepath, name)

    def import_machine_type(self, element, name):
        path = join(element.mtypepath, name)
        element = parseString(file(join(path, 'machine_type.xml')).read())
        parsed = MachineTypeParser(element.firstChild)
        self.insert_parsed_element(parsed, path)
        
    def export_machine_type(self, mtype, mtypepath):
        path = join(mtypepath, mtype)
        element = MachineTypeElement(self.conn, mtype)
        element.export(mtypepath)
        self._mtscript.export_scripts(path)
        
if __name__ == '__main__':
    from os.path import join
    from paella.db import PaellaConnection
    conn = PaellaConnection()
    pmtypes = ['ggf', 'gf', 'f', 's', 'gs', 'ggs']
    mp = MachineTypeParent(conn)
    mt = MachineTypeHandler(conn)
    

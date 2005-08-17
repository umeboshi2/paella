from os.path import basename, dirname, join
from xml.dom.minidom import parseString

from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq

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
        self.filesystems = Table_cursor(self.conn, 'filesystems')
        self.mounts = Table_cursor(self.conn, 'mounts')
        self.fsmounts = Table_cursor(self.conn, 'filesystem_mounts')
        self.disks = Table_cursor(self.conn, 'disks')
        self.partitions = Table_cursor(self.conn, 'partitions')
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

    def get_disk_devices(self):
        return self.mtype.get_disk_devices()
    
    
class MachineHandler(BaseMachineHandler):
    def add_disk(self, diskname, device):
        self.mtype.add_disk(diskname, device)
        
    def add_machine_type(self, mtype):
        self.mtype.add_new_type(mtype)
        
    def add_new_filesystem(self, filesystem):
        self.filesystems.insert(data=dict(filesystem=filesystem))

    def add_new_kernel(self, kernel):
        self.kernels.insert(data=dict(kernel=kernel))

    def add_new_mount(self, name, mtpt, fstype, opts, dump, pass_):
        data = dict(mnt_name=name, mnt_point=mtpt, fstype=fstype,
                    mnt_opts=mnt_opts, dump=dump)
        data['pass'] = pass_
        self.mounts.insert(data=data)
        
    def add_mount_to_filesystem(self, mnt_name, filesystem, ord, partition, size):
        self.fsmounts.insert(data=dict(mnt_name=mnt_name, filesystem=filesystem,
                                       ord=ord, partition=partition, size=size))

    def make_a_machine(self, machine, mtype, profile, fs):
        self.cursor.insert(table='machines',
                           data=dict(machine=machine,
                                     machine_type=machine_type,
                                     filesystem=fs, profile=profile))

    def insert_parsed_element(self, element):
        map(self.add_new_kernel, element.kernels)
        for mount in element.mounts:
            self.mounts.insert(data=mount)
        for filesystem in element.filesystems:
            self.add_new_filesystem(filesystem.name)
            for fsmount in filesystem.mounts:
                fsmount['filesystem'] = filesystem.name
                self.fsmounts.insert(data=fsmount)
        for disk in element.disks:
            self.disks.insert(data=dict(diskname=disk.name))
            for partition in disk.partitions:
                data = dict(diskname=disk.name)
                data.update(partition)
                print partition, data
                self.partitions.insert(data=data)
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
            
    
    def check_machine_disks(self):
        return self.mtype.check_machine_disks()

    def make_partition_dump(self, diskname, device):
        return self.mtype.make_partition_dump(diskname, device)
    
    def array_hack(self):
        return self.mtype.array_hack()

    def make_fstab(self, filesystem=None, machine_type=None):
        if filesystem is None:
            filesystem = self.current.filesystem
        return self.mtype.make_fstab(filesystem)

    def get_all_fsmounts(self, filesystem=None):
        if filesystem is None:
            filesystem = self.current.filesystem
        return self.mtype.get_all_fsmounts(filesystem)

    def get_installable_fsmounts(self, filesystem=None):
        if filesystem is None:
            filesystem = self.current.filesystem
        return self.mtype.get_installable_fsmounts(filesystem)

    def get_ordered_fsmounts(self, filesystem=None):
        if filesystem is None:
            filesystem = self.current.filesystem
        return self.mtype.get_ordered_fsmounts(filesystem)
    
    def get_modules(self, machine_type=None):
        return self.mtype.get_modules()

    def append_modules(self, modules, machine_type=None):
        self.mtype.append_modules(modules)

    def get_script(self, name):
        return self.mtype.get_script(name)

    def list_all_machine_types(self):
        rows = self.cursor.select(table='machine_types')
        return [r.machine_type for r in rows]
    
    def list_all_filesystems(self):
        rows = self.filesystems.select()
        return [r.filesystem for r in rows]
    
    def list_all_kernels(self):
        return [r.kernel for r in self.kernels.select()]
    
    def make_disk_config_info(self, device, filesystem=None, curenv=None):
        if filesystem is None:
            filesystem = self.current.filesystem
        rows = self.get_installable_fsmounts(filesystem=filesystem)
        lines = []
        if device[:4] == '/dev':
            device = basename(device)
        lines.append('disk_config %s' % device)
        for row in rows:
            ptype = 'logical'
            if int(row.partition) < 5:
                ptype = 'primary'
            size = row.size
            if curenv is not None:
                if row.mnt_name in curenv.keys():
                    size = 'preserve'
            line = '%s\t%s\t%s\t%s' % (ptype, row.mnt_point, size, row.mnt_opts)
            fstype = row.fstype
            if fstype == 'reiserfs':
                fstype = 'reiser'
            fline = '%s\t; %s' % (line, fstype)
            lines.append(fline)
        return '\n'.join(lines) + '\n'


            
if __name__ == '__main__':
    from os.path import join
    from paella.db import PaellaConnection
    conn = PaellaConnection()
    from xmlgen import MachineDatabaseElement
    from paella.db import CurrentEnvironment
    mh = MachineHandler(conn)
    mods = ['via82cxxx', 'ide-generic', 'ide-disk']
    
    def quick_wipe(conn):
        cursor = StatementCursor(conn)
        cursor.delete(table='machines')
        cursor.delete(table='partition_workspace')
        cursor.delete(table='partitions')
        cursor.delete(table='filesystem_mounts')
        cursor.delete(table='filesystem_disks')
        cursor.delete(table='partition_mounts')
        cursor.delete(table='machine_disks')
        cursor.delete(table='machine_types')
        cursor.delete(table='mounts')
        cursor.delete(table='disks')
        cursor.delete(table='filesystems')
        cursor.delete(table='kernels')
        

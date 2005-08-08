from os.path import join
from xml.dom.minidom import Element

from useless.base.xmlfile import TextElement, DictElement
from useless.base.util import makepaths
from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq, In

from paella.db.xmlgen import BaseVariableElement

class PartitionElement(Element):
    def __init__(self, partition, start, size, id):
        Element.__init__(self, 'partition')
        self.setAttribute('partition', partition)
        self.setAttribute('start', start)
        self.setAttribute('size', size)
        self.setAttribute('Id', id)

class DiskElement(Element):
    def __init__(self, diskname):
        Element.__init__(self, 'diskname')
        self.setAttribute('name', diskname)
        self.partitions = []
        self.diskname = diskname

    def set_partitions(self):
        pass
        
    def append_partition(self, partition, start, size, id):
        p_element = PartitionElement(partition, str(start), str(size), str(id))
        self.partitions.append(p_element)
        self.appendChild(p_element)
        
class MachineDiskElement(Element):
    def __init__(self, diskname, device):
        Element.__init__(self, 'machine_disk')
        self.setAttribute('diskname', diskname)
        self.setAttribute('device', device)


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
        self.devices = []
        self.modules = []
        self.scripts = []
        self.families = []
        self.variables = []
        self.machine_type = name
        clause = Eq('machine_type', name)
        self._append_devices(clause)
        self._append_modules(clause)
        self._append_scripts(clause)
        self._append_families(clause)
        self._append_variables(clause)
        
    def append_device(self, diskname, device):
        mdisk_element = MachineDiskElement(diskname, device)
        self.devices.append(mdisk_element)
        self.appendChild(mdisk_element)

    def _append_devices(self, clause):
        table = 'machine_disks'
        mdisks = self.cursor.select(table=table, clause=clause, order='device')
        for row in mdisks:
            self.append_device(row.diskname, row.device)
            
    def set_devices(self):
        pass

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
        variable_element = MachineTypeVariableElement(trait, name, value)
        self.variables.append(variable_element)
        self.appendChild(variable_element)

    def _append_variables(self, clause):
        table = 'machine_type_variables'
        vlist = self.cursor.select(table=table, clause=clause, order=['trait', 'name'])
        for row in vlist:
            self.append_variable(row.trait, row.name, row.value)
        
    def export(self, mtypepath):
        mtype = self.getAttribute('name')
        path = join(mtypepath, mtype)
        makepaths(path)
        xfile = file(join(path, 'machine_type.xml'), 'w')
        xfile.write(self.toprettyxml())
        xfile.close()

class MountElement(Element):
    def __init__(self, mnt_name, mnt_point, fstype, mnt_opts,
                 dump, pass_):
        Element.__init__(self, 'mount')
        self.setAttribute('mnt_name', mnt_name)
        self.setAttribute('mnt_point', mnt_point)
        self.setAttribute('fstype', fstype)
        self.setAttribute('mnt_opts', mnt_opts)
        self.setAttribute('dump', dump)
        self.setAttribute('pass', pass_)

class MountsElement(Element):
    def __init__(self, conn):
        Element.__init__(self, 'mounts')
        self.conn = conn
        self.cursor = StatementCursor(self.conn)
        self.cursor.set_table('mounts')
        self.mounts = []
        rows = self.cursor.select(order='mnt_name')
        for r in rows:
            self.append_mount(r.mnt_name, r.mnt_point, r.fstype,
                              r.mnt_opts, r.dump, r['pass'])
            
        
        
    def append_mount(self, mnt_name, mnt_point, fstype,
                     mnt_opts, dump, pass_):
        mnt_element = MountElement(mnt_name, mnt_point, fstype,
                                   mnt_opts, dump, pass_)
        self.mounts.append(mnt_element)
        self.appendChild(mnt_element)
    

class FilesystemMountElement(Element):
    def __init__(self, mnt_name, ord, partition, size):
        Element.__init__(self, 'filesystem_mount')
        self.setAttribute('mnt_name', mnt_name)
        self.setAttribute('ord', ord)
        self.setAttribute('partition', partition)
        self.setAttribute('size', size)
        
        

class FilesystemElement(Element):
    def __init__(self, conn, filesystem):
        Element.__init__(self, 'filesystem')
        self.conn = conn
        self.cursor = StatementCursor(self.conn)
        self.cursor.set_table('filesystem_mounts')
        self.setAttribute('name', filesystem)
        self.mounts = []
        self.filesystem = filesystem
        clause = Eq('filesystem', filesystem)
        rows = self.cursor.select(clause=clause, order='mnt_name')
        for r in rows:
            self.append_fs_mount(r.mnt_name, r.ord, r.partition, r.size)
            
        
    def append_fs_mount(self, mnt_name, ord, partition, size):
        fs_mount_element = FilesystemMountElement(mnt_name,
                                                  str(ord), str(partition), str(size))
        self.mounts.append(fs_mount_element)
        self.appendChild(fs_mount_element)


class FilesystemsElement(Element):
    def __init__(self, conn):
        Element.__init__(self, 'filesystems')
        self.conn = conn
        self.cursor = StatementCursor(self.conn)
        filesystems = [r.filesystem for r in self.cursor.select(table='filesystems',
                                                                order='filesystem')]
        self.filesystems = []
        for filesystem in filesystems:
            fs_element = FilesystemElement(self.conn, filesystem)
            self.filesystems.append(fs_element)
            self.appendChild(fs_element)

class DisksElement(Element):
    def __init__(self, conn, disks=None):
        Element.__init__(self, 'disks')
        self.conn = conn
        self.cursor = StatementCursor(self.conn)
        if disks is None:
            disks = [r.diskname for r in self.cursor.select(table='disks', order='diskname')]
        self.disks = []
        for diskname in disks:
            disk_element = DiskElement(diskname)
            clause = Eq('diskname', diskname)
            partitions = self.cursor.select(table='partitions',
                                            clause=clause, order='partition')
            for p in partitions:
                disk_element.append_partition(p.partition, p.start, p.size, p.id)
            self.disks.append(disk_element)
            self.appendChild(disk_element)

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
    def __init__(self, machine, machine_type, kernel, profile, filesystem):
        TextElement.__init__(self, 'machine', machine)
        self.setAttribute('machine_type', machine_type)
        self.setAttribute('kernel', kernel)
        self.setAttribute('profile', profile)
        self.setAttribute('filesystem', filesystem)

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
                                             m.kernel, m.profile, m.filesystem)
            self.machines.append(machine_element)
            self.appendChild(machine_element)

class MachineDatabaseElement(Element):
    def __init__(self, conn):
        Element.__init__(self, 'machine_database')
        self.conn = conn
        self.filesystems = FilesystemsElement(conn)
        self.disks = DisksElement(conn)
        self.mounts = MountsElement(conn)
        self.mtypes = MachineTypesElement(conn)
        self.kernels = KernelsElement(conn)
        self.machines = MachinesElement(conn)

        for e in [self.machines, self.mtypes, self.disks, self.mounts,
                  self.filesystems, self.kernels]:
            self.appendChild(e)
            
    def export_machine_database(self, path):
        pass
    
class ClientMachineDatabaseElement(Element):
    def __init__(self, conn, disks=None, mtypes=None, machines=None):
        Element.__init__(self, 'machine_database')
        self.conn = conn
        if disks is not None:
            self.disks = DisksElement(conn, disks)
            self.appendChild(self.disks)
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
    #f = FilesystemElement('newfs', 'home', 5)
    filesystems = FilesystemsElement(conn)
    disks = DisksElement(conn)
    mounts = MountsElement(conn)
    mtypes = MachineTypesElement(conn)
    kernels = KernelsElement(conn)
    machines = MachinesElement(conn)
    md = MachineDatabaseElement(conn)

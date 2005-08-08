from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq


class Mount(dict):
    def __init__(self, mnt_name, mnt_point, fstype, mnt_opts,
                 dump, pass_):
        dict.__init__(self, mnt_name=mnt_name, mnt_point=mnt_point,
                      fstype=fstype, mnt_opts=mnt_opts, dump=dump)
        self['pass'] = pass_
        
class Partition(dict):
    def __init__(self, partition, start, size, id):
        dict.__init__(self, partition=partition, start=start, size=size, id=id)

class Disk(object):
    def __init__(self, diskname):
        object.__init__(self)
        self.partitions = []
        self.name = diskname

    def __repr__(self):
        return '<Disk:  %s>' % self.name

    def append_partition(self, partition):
        if type(partition) == Partition:
            self.partitions.append(partition)
        else:
            raise Error, 'bad partition'

class FilesystemMount(dict):
    def __init__(self, mnt_name, ord, partition, size):
        dict.__init__(self, mnt_name=mnt_name, ord=ord, partition=partition, size=size)


class Filesystem(object):
    def __init__(self, filesystem):
        object.__init__(self)
        self.name = filesystem
        self.mounts = []
        
    def __repr__(self):
        return '<Filesystem:  %s>' % self.name

    def append_mount(self, fsmount):
        if type(fsmount) == FilesystemMount:
            self.mounts.append(fsmount)
        else:
            raise Error, 'bad fsmount'

class MachineDisk(dict):
    def __init__(self, diskname, device):
        dict.__init__(self, diskname=diskname, device=device)

class MachineType(object):
    def __init__(self, mtype):
        object.__init__(self)
        self.name = mtype
        self.disks = []
        self.scripts = []
        self.families = []
        self.variables = []

    def __repr__(self):
        return '<MachineType:  %s>' % self.name

    def append_disk(self, disk):
        if type(disk) == MachineDisk:
            self.disks.append(disk)
        else:
            raise Error, 'bad disk'

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
    def __init__(self, name, mtype, filesystem, kernel, profile):
        dict.__init__(self, name=name, machine_type=mtype,
                      filesystem=filesystem, kernel=kernel,
                      profile=profile)
        

if __name__ == '__main__':
    from paella.profile.base import PaellaConfig, PaellaConnection
    cfg = PaellaConfig()
    conn = PaellaConnection(cfg)
    s = StatementCursor(conn)
    #m = Machines(conn)
    m = MachineModules('shuttle_bob', ['tulip', '8139too'])
    

from useless.base.xmlfile import ParserHelper
from useless.base import Error

from base import Mount, Partition, FilesystemMount, MachineDisk
from base import Machine, MachineType, Disk, Filesystem, MachineModules

def get_child(element):
    return element.firstChild.data.encode().strip()

def get_attribute(attribute, element):
    return element.getAttribute(attribute).encode().strip()

def parse_mount(element):
    mnt_name = get_attribute('mnt_name', element)
    mnt_point = get_attribute('mnt_point', element)
    fstype = get_attribute('fstype', element)
    mnt_opts = get_attribute('mnt_opts', element)
    dump = get_attribute('dump', element)
    pass_ = get_attribute('pass', element)
    return Mount(mnt_name, mnt_point, fstype, mnt_opts, dump, pass_)

def parse_partition(element):
    partition = get_attribute('partition', element)
    start = get_attribute('start', element)
    size = get_attribute('size', element)
    id = get_attribute('Id', element)
    return Partition(partition, start, size, id)

def parse_fsmount(element):
    mnt_name = get_attribute('mnt_name', element)
    ord = get_attribute('ord', element)
    partition = get_attribute('partition', element)
    return FilesystemMount(mnt_name, ord, partition)

def parse_mdisk(element):
    diskname = get_attribute('diskname', element)
    device = get_attribute('device', element)
    return MachineDisk(diskname, device)

def parse_module(element):
    module = get_child(element)
    order = get_attribute('order', element)
    return int(order), module

def parse_machine(element):
    name = get_child(element)
    mtype = get_attribute('machine_type', element)
    filesystem = get_attribute('filesystem', element)
    kernel = get_attribute('kernel', element)
    profile = get_attribute('profile', element)
    return Machine(name, mtype, filesystem, kernel, profile)

class MachineDatabaseParser(ParserHelper):
    def __init__(self, element):
        ParserHelper.__init__(self)
        name = element.tagName.encode()
        get_em = self.get_elements_from_section
        self.kernels = map(get_child, get_em(element, 'kernels', 'kernel'))
        self.mounts = map(parse_mount, get_em(element, 'mounts', 'mount'))
        self.filesystems = map(self._parse_filesystem,
                               get_em(element, 'filesystems', 'filesystem'))
        self.disks = map(self._parse_disk, get_em(element, 'disks', 'diskname'))
        self.mtypes = map(self._parse_mtype, get_em(element, 'machine_types',
                                                    'machine_type'))
        self.machines = map(parse_machine, get_em(element, 'machines', 'machine'))
        
    def _parse_disk(self, element):
        diskname = get_attribute('name', element)
        p_elements = element.getElementsByTagName('partition')
        disk = Disk(diskname)
        map(disk.append_partition, map(parse_partition, p_elements))
        return disk

    def _parse_filesystem(self, element):
        filesystem = get_attribute('name', element)
        fs_elements = element.getElementsByTagName('filesystem_mount')
        fs = Filesystem(filesystem)
        map(fs.append_mount, map(parse_fsmount, fs_elements))
        return fs

    def _parse_mtype(self, element):
        name = get_attribute('name', element)
        md_elements = element.getElementsByTagName('machine_disk')
        mod_elements = element.getElementsByTagName('module')
        mtype = MachineType(name)
        map(mtype.append_disk, map(parse_mdisk, md_elements))
        moddict = dict(map(parse_module, mod_elements))
        modorder = moddict.keys()
        modorder.sort()
        modules = []
        for i in modorder:
            modules.append(moddict[i])
        mtype.append_modules(modules)
        return mtype
    
if __name__ == '__main__':
    from os.path import join
    from xml.dom.minidom import parseString
    from paella.profile.base import PaellaConfig, PaellaConnection
    cfg = PaellaConfig()
    
    xfile = file(join(cfg['export_path'], 'machine_database.xml'))
    mdata = xfile.read()
    xfile.close()
    
    element = parseString(mdata)
    
    md = MachineDatabaseParser(element.firstChild)
    

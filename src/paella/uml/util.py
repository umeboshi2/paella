import os
import commands

from paella.base import Error
from paella.base.defaults import MB
from paella.base.util import makepaths
from paella.installer.util import make_sources_list, set_root_passwd
from paella.installer.util import myline, make_fstab, make_filesystem, mount_tmp
from paella.installer.util import ready_base_for_install as _ready_base_for_install
from paella.installer.fstab import UmlFstab

def create_sparse_file(path, size=100):
    if os.path.isfile(path):
        os.remove(path)
    fs = file(path, 'w')
    fs.truncate(int(size)*MB)
    fs.close()


def mount(mtpnt, fstype='hostfs', export=None):
    if fstype == 'nfs':
        if export is None:
            raise Error, 'nfs needs export passed'
        dev = export
        opts = 'nolock'
    elif fstype == 'hostfs':
        dev = '/host'
        opts = 'rw'
    else:
        raise Error, 'unsupported fstype %s' % fstype
    mount_command = 'mount -t %s %s %s -o %s' % (fstype, dev, mtpnt, opts)
    mounted = os.system(mount_command)
    if mounted:
        raise Error, 'problem with %s' % mount

def mount_target(target, device='/dev/ubd/1'):
    makepaths(target)
    os.system('mount %s %s' % (device, target))
    print target, 'mounted'


def mkrootfs(fstype='ext2', primary='/dev/ubd/1',
             secondary='/dev/ubd1'):
    make_filesystem(primary, fstype)
    make_filesystem(secondary, fstype)
    
def setup_target(target='/tmp/target', device='/dev/ubd/1'):
    mount_tmp()
    mkrootfs(primary=device)
    mount_target(target, device)
    

#this is done after bootstrap or
#this is done after extracting the base tar
def ready_base_for_install(target, cfg, suite):
    _ready_base_for_install(target, cfg, suite, UmlFstab())
    rdev = os.path.join(target, 'dev/ubd')
    for partition in map(str, range(6)):
        os.system('mknod %s b 98 %s' % (rdev + partition, partition))
    modpath = os.path.join(target, 'lib/modules')
    kernel_version = commands.getoutput('uname -r')
    umlmodpath = os.path.join('/usr/lib/uml/modules', kernel_version)
    os.system('cp -R %s %s' % (umlmodpath, modpath))
    
    

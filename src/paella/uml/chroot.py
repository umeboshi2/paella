import os, sys
from os.path import join

from useless.base import Error
from useless.base import debug
from useless.base.path import path
from useless.base.util import makepaths, runlog
from useless.base.util import parse_proc_mounts
from useless.base.util import shell

from paella.installer.util.filesystem import mount_tmpfs
from paella.installer.util.filesystem import make_filesystem
from paella.installer.util.misc import make_interfaces_simple
from paella.installer.util.misc import backup_target_command
from paella.installer.util.misc import extract_tarball


from base import Uml, UmlConfig
from base import host_mode, guest_mode
from util import mount, mount_target, setup_target
from util import ready_base_for_install

# This is a class that runs under hostfs,
# and intends to chroot into target ubd filesystem
# at ubd1
class UmlChroot(Uml):
    def __init__(self, cfg=None):
        Uml.__init__(self)
        if cfg is None:
            raise Error, 'need config for UmlChroot'
        self.cfg = cfg
        lvar = 'LOGFILE'
        if lvar in os.environ:
            logfile = os.environ[lvar]
        else:
            logfile = cfg['host_logfile']
            os.environ[lvar] = logfile
        logfile = path(logfile).expand()
        self.set_options()
        
        
    def set_options(self):
        opts = self.options
        opts['root'] = '/dev/root'
        opts['rootflags'] = '/'
        opts['rootfstype'] = 'hostfs'
        opts['paella_action'] = 'nothing'
        opts['devfs'] = 'nomount'
        opts['init'] = path(self.cfg['uml_initscript']).expand()
        backup_filesystem = self.cfg.get('umlmachines', 'backup_filesystem')
        if backup_filesystem == 'hostfs':
            p = path(self.cfg.get('umlmachines', 'hostfs_backup_path'))
            opts['hostfs_backup_path'] = p.expand()
        opts.update(self.cfg.get_umlopts())
        

                
    def set_mode(self, mode):
        Uml.set_mode(self, mode)
        if self.mode == 'guest':
            self._init_uml_system()

    @host_mode
    def set_targetimage(self, filename, device='ubda'):
        self.options[device] = path(filename).expand()
        
    @guest_mode
    def set_target(self, target='/tmp/target'):
        self.target = path(target)

    @guest_mode
    def make_filesystem(self):
        import warnings
        warnings.warn('UmlChroot.make_filesystem hardcoded')
        make_filesystem('/dev/ubda', 'ext2')
        
    @guest_mode
    def mount_dev(self):
        mount_tmpfs(target='/dev')

    @guest_mode
    def mount_tmp(self):
        mount_tmpfs(target='/tmp')

    @guest_mode
    def mount_target(self):
        mount_target(self.target, device='/dev/ubda')

    @guest_mode
    def mount_backup(self, mtpnt, fstype='hostfs', export=None):
        mounts = parse_proc_mounts()
        mounted = False
        for m in mounts:
            if m['mtpnt'] == mtpnt:
                mounted = True
        if fstype == 'nfs':
            export = self.cfg.get('umlmachines', 'nfs_backup_export')
        if not mounted:
            print mtpnt, fstype, export
            mount(mtpnt, fstype=fstype, export=export)
            print '%s mounted' % mtpnt
        else:
            print '%s is already mounted' % mtpnt
            

    @guest_mode
    def backup_target_nfs(self, name):
        self.mount_backup('/mnt', 'nfs')
        tarname = os.path.join('/mnt', '%s.tar' % name)
        dirname = os.path.dirname(tarname)
        if not os.path.isdir(dirname):
            print dirname, "doesn't exist.  Creating now."
            makepaths(dirname)
        tarcmd = backup_target_command(self.target, tarname)
        print tarcmd
        shell(tarcmd)
        shell('umount /mnt')

    @guest_mode
    def backup_target_hostfs(self, name):
        self.mount_backup('/mnt', 'hostfs')
        #bkup_path = path(self.cfg.get('umlmachines', 'hostfs_backup_path')).expand()
        bkup_path = path(self.options['hostfs_backup_path'].value)
        while bkup_path.startswith('/'):
            bkup_path = bkup_path[1:]
        mnt = path('/mnt')
        tarname = mnt / bkup_path / path('%s.tar' % name)        
        #tarname = os.path.join('/mnt', bkup_path, name) + '.tar'
        #dirname = os.path.dirname(tarname)
        dirname = tarname.dirname()
        if not dirname.isdir():
            print dirname, "doesn't exist.  Creating now."
            makepaths(dirname)
        tarcmd = backup_target_command(self.target, tarname)
        print 'tarcmd is', tarcmd
        shell(tarcmd)
        shell('umount /mnt')
        
    @guest_mode
    def backup_target(self, name):
        fs = self.cfg.get('umlmachines', 'backup_filesystem')
        if fs == 'nfs':
            self.backup_target_nfs(name)
        elif fs == 'hostfs':
            self.backup_target_hostfs(name)
        else:
            raise Error, 'unsupported backup filesystem'
        
    @guest_mode
    def extract_root_tarball(self, basetarball):
        extract_tarball(self.target, basetarball)

    @guest_mode
    def setup_target(self, target='/tmp/target', device='/dev/ubda'):
        self.set_target(target)
        setup_target(self.target, device=device)
        
        
if __name__ == '__main__':
    c = UmlConfig()
    u = UmlChroot(c)
    

import os
from os.path import join
import subprocess

from useless.base import Error
from useless.base.util import makepaths, runlog
from useless.base.util import parse_proc_mounts

from paella.installer.util import mount_tmp, backup_target_command
from paella.installer.util import make_interfaces_simple, extract_tarball
from paella.installer.util import mount_tmpfs

from base import Uml, UmlConfig
from util import mount, mount_target, mkrootfs, setup_target
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
        self.set_options()
        
        
    def set_options(self):
        o = self.options
        o['root'] = '/dev/root'
        o['rootflags'] = '/'
        o['rootfstype'] = 'hostfs'
        o['paella_action'] = 'nothing'
        o['devfs'] = 'nomount'
        o['init'] = self.cfg['uml_initscript']
        o.update(self.cfg.get_umlopts())

                
    def set_mode(self, mode):
        Uml.set_mode(self, mode)
        if self.mode == 'guest':
            self._init_uml_system()
            
    def set_targetimage(self, path):
        self.check_host()
        self.options['ubd1'] = path
        
    def run_uml(self):
        self.check_host()
        #return os.system(str(self))
        cmd = str(self)
        PIPE = subprocess.PIPE
        STDOUT = subprocess.STDOUT
        # make dummy PIPE until fix stdout.read()
        PIPE = None
        p = subprocess.Popen(cmd, shell=True, stdin=PIPE,
                             stdout=PIPE, stderr=STDOUT, close_fds=True)
        self.run_process = p
        print 'running', p
        
        #bgcmd = '%s &' % cmd
        #return subprocess.call(bgcmd, shell=True)
        
    def _init_uml_system(self):
        self.check_guest()
        print 'initializing uml system'
        for target in ['/tmp', '/dev']:
            mount_tmpfs(target=target)
        # we need something better here
        os.system('mknod /dev/null c 1 3')
        os.system('mknod /dev/ubd0 b 98 0')
        os.system('mknod /dev/ubd1 b 98 16')

        
    def set_target(self, target='/tmp/target'):
        self.check_guest()
        self.target = target

    def mount_dev(self):
        self.check_guest()
        mount_tmpfs(target='/dev')

    def mount_tmp(self):
        self.check_guest()
        mount_tmpfs(target='/tmp')

    def mount_target(self):
        self.check_guest()
        mount_target(self.target, device='/dev/ubd1')

    def mount_backup(self, mtpnt, fstype='hostfs', export=None):
        self.check_guest()
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
            

    def backup_target_nfs(self, name):
        self.check_guest()
        self.mount_backup('/mnt', 'nfs')
        tarname = os.path.join('/mnt', '%s.tar' % name)
        dirname = os.path.dirname(tarname)
        if not os.path.isdir(dirname):
            print dirname, "doesn't exist.  Creating now."
            makepaths(dirname)
        tarcmd = backup_target_command(self.target, tarname)
        print tarcmd
        os.system(tarcmd)
        os.system('umount /mnt')

    def backup_target_hostfs(self, name):
        self.check_guest()
        self.mount_backup('/mnt', 'hostfs')
        bkup_path = self.cfg.get('umlmachines', 'hostfs_backup_path')
        while bkup_path.startswith('/'):
            bkup_path = bkup_path[1:]
        tarname = os.path.join('/mnt', bkup_path, name) + '.tar'
        dirname = os.path.dirname(tarname)
        if not os.path.isdir(dirname):
            print dirname, "doesn't exist.  Creating now."
            makepaths(dirname)
        tarcmd = backup_target_command(self.target, tarname)
        print 'tarcmd is', tarcmd
        os.system(tarcmd)
        os.system('umount /mnt')
        
    def backup_target(self, name):
        self.check_guest()
        fs = self.cfg.get('umlmachines', 'backup_filesystem')
        if fs == 'nfs':
            self.backup_target_nfs(name)
        elif fs == 'hostfs':
            self.backup_target_hostfs(name)
        else:
            raise Error, 'unsupported backup filesystem'
        
    def mkrootfs(self):
        self.check_guest()
        mkrootfs()
        
    def extract_root_tarball(self, basetarball):
        self.check_guest()
        extract_tarball(self.target, basetarball)

    def setup_target(self, target='/tmp/target', device='/dev/ubd1'):
        self.check_guest()
        self.set_target(target)
        setup_target(self.target, device=device)
        
        
if __name__ == '__main__':
    c = UmlConfig()
    u = UmlChroot(c)
    

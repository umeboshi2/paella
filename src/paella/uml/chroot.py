import os
from os.path import join

from useless.base import Error
from useless.base.util import makepaths, runlog
from useless.base.util import parse_proc_mounts

from paella.installer.util import mount_tmp, backup_target_command
from paella.installer.util import make_interfaces_simple, extract_tarball


from base import Uml, UmlConfig
from util import mount, mount_target, mkrootfs, setup_target
from util import ready_base_for_install


class UmlChroot(Uml):
    def __init__(self, cfg=None):
        Uml.__init__(self)
        if cfg is None:
            raise Error, 'need config for UmlChroot'
        self.cfg = cfg
        try:
            logfile = os.environ['LOGFILE']
        except KeyError:
            logfile = cfg['host_LOGFILE']
        os.environ['LOGFILE'] = logfile
        self.set_options()
        
    def set_options(self):
        o = self.options
        o['root'] = '/dev/root'
        o['rootflags'] = '/'
        o['rootfstype'] = 'hostfs'
        o['paella_action'] = 'nothing'
        o['devfs'] = 'mount'
        o['init'] = self.cfg['uml_initscript']
        o.update(self.cfg.get_umlopts())

                
    def set_targetimage(self, path):
        self.check_host()
        self.options['ubd1'] = path
        
    def run_uml(self):
        self.check_host()
        return os.system(str(self))

    def set_target(self, target='/tmp/target'):
        self.check_guest()
        self.target = target

    def mount_tmp(self):
        self.check_guest()
        mount_tmp()

    def mount_target(self):
        self.check_guest()
        mount_target(self.target, device='/dev/ubd/1')

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

    def backup_target_nfs(self, name):
        self.check_guest()
        self.mount_backup('/mnt', 'nfs')
        tarname = os.path.join('/mnt', '%s.tar' % name)
        tarcmd = backup_target_command(self.target, tarname)
        print tarcmd
        os.system(tarcmd)
        os.system('umount /mnt')

    def backup_target_hostfs(self, name):
        self.check_guest()
        self.mount_backup('/mnt', 'hostfs')
        bkup_path = self.cfg.get('umlmachines', 'hostfs_backup_path')
        if bkup_path[0] == '/':
            bkup_path = bkup_path[1:]
        tarname = os.path.join('/mnt', bkup_path, name) + '.tar'
        tarcmd = backup_target_command(self.target, tarname)
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

    def setup_target(self, target='/tmp/target', device='/dev/ubd/1'):
        self.check_guest()
        self.set_target(target)
        setup_target(self.target, device=device)
        
        
if __name__ == '__main__':
    c = UmlConfig()
    u = UmlChroot(c)
    

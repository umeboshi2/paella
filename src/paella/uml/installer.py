import os
from os.path import isfile, join, dirname
import tarfile

from paella.profile.base import get_suite, PaellaConfig
from paella.installer.util import extract_tarball
from paella.installer.profile import ProfileInstaller

from util import ready_base_for_install, create_sparse_file
from chroot import UmlChroot

class UmlInstaller(UmlChroot):
    def __init__(self, conn=None, cfg=None):
        self.conn = conn
        UmlChroot.__init__(self, cfg=cfg)
        self.options['paella_action'] = 'install'
        self.paellarc = PaellaConfig(files=[self.cfg['paellarc']])
        
        
    def set_suite(self, suite):
        self.check_guest()
        self.installer = ProfileInstaller(self.conn, self.paellarc)
        self._suite = suite
        
    def set_profile(self, profile):
        if self.mode == 'host':
            self.options['paellaprofile'] = profile
        else:
            self.check_guest()
            self.set_suite(get_suite(self.conn, profile))
            self.installer.set_profile(profile)
            if hasattr(self, 'target'):
                self.installer.set_target(self.target)

    def set_template_path(self, path=None): 
        self.check_guest()
        self.installer.set_template_path(path)

    def process(self):
        self.check_guest()
        self.installer.process()

    def make_root_device(self, path, size=None):
        self.check_host()
        if size is None:
            size = self.cfg['basefile_size']
        msg = 'making uml root device of size %s at %s' % (size, path)
        print msg
        create_sparse_file(path, size)
        self.set_targetimage(path)
        
    def install_profile(self, profile, path):
        self.check_host()
        self.set_profile(profile)
        self.make_root_device(path)
        self.run_uml()

    def restore_profile(self, name, path):
        self.check_host()
        self.options['paella_action'] = 'restore'
        self.options['paellaprofile'] = name
        self.options['paellasuite'] = 'none'
        self.make_root_device(path)
        self.run_uml()
        
    def extract_base_tarball(self):
        self.check_guest()
        suite = self._suite
        fstype = self.cfg.get('umlmachines', 'backup_filesystem')
        if fstype == 'hostfs':
            backup_path = self.cfg.get('umlmachines', 'hostfs_backup_path')
        else:
            backup_path = '/mnt'
        basetarball = join(backup_path, '%s.base.tar' % suite)
        extract_tarball(self.target, basetarball)

    def ready_base_for_install(self):
        ready_base_for_install(self.target, self.paellarc, self._suite)
        

if __name__ == '__main__':
    pass

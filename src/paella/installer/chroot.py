import os
from os.path import join

from paella.base import Error
from paella.base.util import makepaths, runlog
from paella.debian.base import debootstrap
from paella.profile.base import PaellaConnection, get_suite, PaellaConfig
from paella.db.midlevel import StatementCursor
from paella.sqlgen.clause import Eq, Gt


#from base import Installer
from util import ready_base_for_install, make_filesystem
from util import install_kernel
from profile import ProfileInstaller

class ChrootInstaller(object):
    def __init__(self, conn, cfg):
        object.__init__(self)
        self.conn = conn
        self.cfg = cfg
        self.cursor = StatementCursor(self.conn)
        self.target = None
        self.installer = None
        self._mounted = None
        self._bootstrapped = None
        self.debmirror = self.cfg.get('debrepos', 'http_mirror')
                
    def _check_target(self):
        if not self.target:
            raise Error, 'no target specified'

    def _check_installer(self):
        if not self.installer:
            raise Error, 'no installer available'

    def _check_bootstrap(self):
        self._check_target()
        if not self._bootstrapped:
            raise Error, 'target not bootstrapped'
        
    def set_target(self, target):
        self.target = target

    def set_profile(self, profile):
        self.profile = profile
        
    def ready_target(self):
        self._check_target()
        
    def setup_installer(self):
        self.installer = ProfileInstaller(self.conn, self.cfg)
        self.installer.set_profile(self.profile)
        self.suite = get_suite(self.conn, self.profile)
                        
    def bootstrap_target(self):
        self._check_target()
        self._check_installer()
        runlog(debootstrap(self.suite, self.target, self.debmirror))
        self._bootstrapped = True
        
    def ready_base_for_install(self):
        self._check_bootstrap()
        self._check_installer()
        fstab = '#unconfigured for chroot install\n'
        ready_base_for_install(self.target, self.cfg, self.suite, fstab)
        
    def install_to_target(self):
        os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
        self._check_target()
        self._check_installer()
        self.installer.set_target(self.target)
        self.installer.process()        

    def post_install(self):
        print 'post_install'
        kernel = self.machine.current.kernel
        print 'installing kernel', kernel
        install_kernel(kernel, self.target)
        print 'kernel installed'
        
    
    def install(self, profile, target):
        self.set_profile(profile)
        self.setup_installer()
        self.set_target(target)
        self.ready_target()
        self.bootstrap_target()
        self.ready_base_for_install()
        self.install_to_target()
        #self.post_install()
        

if __name__ == '__main__':
    pass
    

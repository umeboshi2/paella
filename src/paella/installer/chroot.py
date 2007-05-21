import os
from os.path import join

from useless.base import Error
from useless.base.util import makepaths, runlog
from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq, Gt


from paella.base import PaellaConfig
from paella.debian.base import debootstrap
from paella.db import PaellaConnection
#from paella.db.base import get_suite



#from base import Installer
from base import BaseChrootInstaller
from util.preinst import ready_base_for_install
from util.filesystem import make_filesystem
from util.postinst import install_kernel
from util.base import make_fake_start_stop_daemon
from util.base import remove_fake_start_stop_daemon

from profile import ProfileInstaller

class ChrootInstaller(BaseChrootInstaller):
    def __init__(self, conn, logfile=None):
        BaseChrootInstaller.__init__(self, conn)
        self.conn = conn
        self.cursor = StatementCursor(self.conn)
        self._mounted = None
        self._installer_ready  = False
        self._base_ready = False
        if logfile is None:
            self.set_logfile(logfile)
        if logfile and type(logfile) is str:
            if not os.environ.has_key('PAELLA_LOGFILE'):
                os.environ['PAELLA_LOGFILE'] = logfile
            self.set_logfile(logfile)
        if logfile is False:
            pass
        
    def _check_base_ready(self):
        if not self._base_ready:
            raise InstallError, 'base is not ready for install.'
        
    def set_profile(self, profile):
        self.profile = profile
        
    def ready_target(self):
        self._check_target_exists()
        
    def setup_installer(self):
        self.installer = ProfileInstaller(self.conn)
        self.installer.log = self.log
        self.installer.set_profile(self.profile)
        self.suite = self.installer.suite
        self._installer_ready = True
                        
    def bootstrap_target(self):
        self._bootstrap_target()
        self._check_bootstrap()
        
        
    def ready_base_for_install(self):
        self._check_bootstrap()
        fstab = '#unconfigured for chroot install\n'
        ready_base_for_install(self.target, self.conn, self.suite, fstab)
        self._mount_target_proc()
        self._check_target_proc()
        cmd = self.command('apt-get', '-y update', chroot=True)
        runvalue = runlog(cmd)
        if runvalue:
            raise InstallError, 'problem updating the apt lists.'
        if os.environ.has_key('FAKE_START_STOP_DAEMON'):
            make_fake_start_stop_daemon(self.target)
        self._base_ready = True
        
    def install_to_target(self):
        self._check_base_ready()
        os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
        self.installer.set_target(self.target)
        self.installer.process()        

    def post_install(self):
        self._umount_target_proc()
        if os.environ.has_key('FAKE_START_STOP_DAEMON'):
            remove_fake_start_stop_daemon(self.target)        
    
    def install(self, profile, target):
        self.set_profile(profile)
        self.setup_installer()
        self.set_target(target)
        self.ready_target()
        self.bootstrap_target()
        self.ready_base_for_install()
        self.install_to_target()
        self.post_install()

if __name__ == '__main__':
    pass
    

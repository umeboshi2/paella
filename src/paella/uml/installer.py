import os
from os.path import isfile, join, dirname
import tarfile

from useless.base.path import path

from paella.base import PaellaConfig
from paella.db.base import get_suite
from paella.db.base import SuiteCursor

from paella.installer.util.misc import extract_tarball
from paella.oldinstaller.profile import ProfileInstaller
from paella.oldinstaller.machine import MachineInstaller
from paella.installer.base import CurrentEnvironment

from base import host_mode, guest_mode
from util import ready_base_for_install, create_sparse_file
from chroot import UmlChroot

class BaseUmlInstaller(UmlChroot):
    def __init__(self, conn=None, cfg=None):
        self.conn = conn
        UmlChroot.__init__(self, cfg=cfg)
        self.options['paella_action'] = 'install'
        paellarc = path(self.cfg['paellarc']).expand()
        self.paellarc = PaellaConfig(files=[paellarc])
        self.options['paellarc'] = paellarc
        
    def setup_target(self, **kwargs):
        UmlChroot.setup_target(self, **kwargs)
    
    @guest_mode
    def process(self):
        self.installer.process()

    @host_mode
    def make_root_device(self, rpath, size=None):
        if size is None:
            size = self.cfg['basefile_size']
        dirname = path(rpath).dirname()
        if not dirname.isdir():
            if not dirname.exists():
                print "Creating directory %s" % str(dirname)
                dirname.makedirs()
            else:
                print "Can't create directory %s" % str(dirname)
                raise ValueError, "file exists that should be a directory"
        msg = 'making uml root device of size %s at %s' % (size, rpath)
        print msg
        create_sparse_file(rpath, size)
        self.set_targetimage(rpath)
        
class UmlProfileInstaller(BaseUmlInstaller):
    @guest_mode
    def set_suite(self, suite):
        self.installer = ProfileInstaller(self.conn)
        self._suite = suite
        self.suitecursor = SuiteCursor(self.conn)

    @guest_mode
    def _set_profile_in_guest(self, profile):
        self.set_suite(get_suite(self.conn, profile))
        self.installer.set_profile(profile)
        if hasattr(self, 'target'):
            self.installer.set_target(self.target)
            
    def set_profile(self, profile):
        if self.mode == 'host':
            self.options['paellaprofile'] = profile
        elif self.mode == 'guest':
            self._set_profile_in_guest(profile)
        else:
            raise ValueError, 'bad mode %s' % self.mode
        
    @guest_mode
    def set_template_path(self, path=None): 
        self.installer.set_template_path(path)

    @host_mode
    def install_profile(self, profile, path):
        self.set_profile(profile)
        self.make_root_device(path)
        self.run_uml(popen=True)

    @host_mode
    def restore_profile(self, name, path):
        self.options['paella_action'] = 'restore'
        self.options['paellaprofile'] = name
        self.options['paellasuite'] = 'none'
        self.make_root_device(path)
        self.run_uml(popen=False)
        
    @guest_mode
    def extract_base_tarball(self):
        suite = self.suitecursor.get_base_suite(self._suite)
        fstype = self.cfg.get('umlmachines', 'backup_filesystem')
        if fstype == 'hostfs':
            #backup_path = path(self.cfg.get('umlmachines', 'hostfs_backup_path')).expand()
            backup_path = path(self.options['hostfs_backup_path'].value)
        else:
            backup_path = path('/mnt')
        basetarball = backup_path / path('%s.base.tar.gz' % suite)
        if not basetarball.isfile():
            basetarball = backup_path / path('%s.base.tar' % suite)
        if basetarball.isfile():
            extract_tarball(self.target, basetarball)
        else:
            raise RuntimeError, 'No base tarball found for suite %s' % suite
        
    @guest_mode
    def ready_base_for_install(self):
        cfg = self.installer.defenv
        ready_base_for_install(self.target, self.conn, self._suite)

    @guest_mode
    def perform_install(self, profile=None, backup_filesystem=None):
        machine = os.environ['PAELLA_MACHINE']
        curenv = CurrentEnvironment(self.conn, machine)
        curenv['current_trait'] = 'None'
        curenv['current_trait_process'] = 'None'
        curenv['traitlist'] = ''
        mpkey = 'current_machine_process'
        if backup_filesystem is not None:
            curenv[mpkey] = 'mount_backup'
            self.mount_backup('/mnt', backup_filesystem)
        curenv[mpkey] = 'setup_target'
        self.setup_target()
        curenv[mpkey] = 'set_profile'
        self.set_profile(profile)
        curenv[mpkey] = 'extract_base_tarball'
        self.extract_base_tarball()
        curenv[mpkey] = 'ready_base_for_install'
        self.ready_base_for_install()
        curenv[mpkey] = 'set_template_path'
        self.set_template_path()
        curenv[mpkey] = 'process'
        self.process()
        
class UmlMachineInstaller(BaseUmlInstaller):
    def __init__(self, conn=None, cfg=None):
        self.conn = conn
        UmlChroot.__init__(self, cfg=cfg)
        self.options['paella_action'] = 'install'
        paellarc_files = [self.cfg['paellarc']]
        self.paellarc = PaellaConfig(files=paellarc_files)
        
    def setup_target(self, **kwargs):
        UmlChroot.setup_target(self, **kwargs)
        
UmlInstaller = UmlProfileInstaller

if __name__ == '__main__':
    pass

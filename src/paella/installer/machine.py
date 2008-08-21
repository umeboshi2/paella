import os
from os.path import join, basename, dirname

from useless.base.path import path

from paella.debian.base import debootstrap
from paella.db.machine import MachineHandler

from base import CurrentEnvironment
from base import InstallError
from base import runlog

from chroot import ChrootInstaller
from chroot import requires_target_set
from chroot import requires_target_exists
from chroot import requires_install_complete


from profile import ProfileInstaller
from machinehelper import MachineInstallerHelper

from util.base import make_script
from util.disk import create_mdadm_conf
from util.filesystem import mount_target


from util.base import makedev
from util.aptsources import make_sources_list
from util.aptsources import make_official_sources_list
from util.filesystem import make_fstab
from util.filesystem import mount_target_proc
from util.main import setup_modules
from util.misc import myline, set_root_passwd
from util.misc import make_interfaces_simple
from util.misc import extract_tarball
from util.preinst import ready_base_for_install
from util.postinst import install_kernel

# an error class to help me remember to finish things
class NotYetWrittenError(StandardError):
    pass


def requires_machine_set(func):
    @requires_target_set
    def wrapper(self, *args, **kw):
        if self.machine.current is None:
            raise UnsatisfiedRequirementsError, 'machine needs to be set first'
        return func(self, *args, **kw)
    return wrapper


def requires_disks_setup(func):
    @requires_machine_set
    def wrapper(self, *args, **kw):
        if not self._disks_setup:
            raise UnsatisfiedRequirementsError, 'disk devices needs to be setup first'
        return func(self, *args, **kw)
    return wrapper

def requires_target_mounted(func):
    @requires_target_exists
    @requires_disks_setup
    def wrapper(self, *args, **kw):
        if not self._target_mounted:
            raise UnsatisfiedRequirementsError, 'target needs to be mounted first'
        return func(self, *args, **kw)
    return wrapper

#from profile import ProfileInstaller
#from fstab import HdFstab
DEFAULT_PROCESSES = [
    'pre',
    'setup_disks',
    'ready_target',
    'mount_target',
    'bootstrap',
    'mount_target_proc',
    'mount_target_sys',
    'make_device_entries',
    'mount_target_devpts',
    'apt_sources_installer',
    'ready_base_for_install',
    'pre_install',
    'install',
    'post_install',
    'install_fstab',
    'install_modules',
    'install_kernel',
    'apt_sources_final',
    'umount_target_sys',
    'umount_target_proc',
    'post'
    ]

class MachineInstaller(ChrootInstaller):
    def __init__(self, conn):
        ChrootInstaller.__init__(self, conn)
        # the processes are mostly the same as in the
        # ChrootInstaller
        self._processes = list(DEFAULT_PROCESSES)
        pmap = dict(setup_disks=self.setup_disks,
                    mount_target=self.mount_target,
                    install_fstab=self.install_fstab,
                    install_modules=self.install_modules,
                    install_kernel=self.install_kernel
                    )
        self._process_map.update(pmap)
        self.machine = MachineHandler(self.conn)
        self.helper = None
        self._target_mounted = False
        self._disks_setup = False
        
    @requires_target_set
    def set_machine(self, machine):
        self.machine.set_machine(machine)
        # this needs to be a configuration option
        # in the default environment
        logdir = path('/paellalog')
        if not logdir.isdir():
            logdir.mkdir()
        logfile = logdir / 'paella-install-%s.log' % machine
        os.environ['PAELLA_MACHINE'] = machine
        self.disklogpath = logdir / ('disklog-%s'  % machine)
        if not self.disklogpath.isdir():
            self.disklogpath.mkdir()
        self.set_logfile(logfile)
        self.log.info('machine set to %s' % machine)
        # we need to set mtypedata before setting the profile
        # so that the mtypedata is passed to the profile and trait installers
        self.mtypedata = self.machine.mtype.get_machine_type_data()
        profile = self.machine.current.profile
        self.set_profile(profile)
        self.curenv = CurrentEnvironment(self.conn, machine)
        self.helper = MachineInstallerHelper(self)
        self.helper.curenv = self.curenv

    @requires_machine_set
    def make_script(self, procname):
        script = self.machine.get_script(procname)
        if script is not None:
            return make_script(procname, script, '/')
        else:
            return None
        
    @requires_target_mounted
    def ready_base_for_install(self):
        # run ready_base_for_install from chroot installer first
        ChrootInstaller.ready_base_for_install(self)
        self.log.info('checking for raid devices')
        raid_devices = self.helper.get_raid_devices()
        if raid_devices:
            self.log.info('raid devices found')
            create_mdadm_conf(self.target, raid_devices)
        else:
            self.log.info('no raid devices found')
        
    @requires_install_complete
    def install_modules(self):
        self.helper.install_modules()

    @requires_install_complete
    def install_kernel(self):
        self.helper.install_kernel()

    @requires_install_complete
    def install_fstab(self):
        self.helper.install_fstab()

    def setup_disks(self):
        self.helper.setup_disks()
        self._disks_setup = True
        
    @requires_target_exists
    @requires_disks_setup
    def mount_target(self):
        device = self.machine.array_hack()
        mounts = self.machine.get_installable_fsmounts()
        mount_target(self.target, mounts, device)
        self._target_mounted = True
        
if __name__ == '__main__':
    pass
    

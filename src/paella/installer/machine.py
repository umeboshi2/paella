import os
from os.path import join, basename, dirname

from useless.base.path import path

from paella.db.machine import MachineHandler

from base import CurrentEnvironment
from base import InstallError
from base import runlog

from chroot import ChrootInstaller
from chroot import UnsatisfiedRequirementsError

from profile import ProfileInstaller
from machinehelper import MachineInstallerHelper

from util.base import make_script

# an error class to help me remember to finish things
class NotYetWrittenError(StandardError):
    pass


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
    'prepare_bootloader',
    'apt_sources_final',
    'umount_target_sys',
    'umount_target_proc',
    'umount_target_devpts',
    'post'
    ]

class BaseMachineInstaller(ChrootInstaller):
    def check_machine_set(self):
        if self.machine.current_machine is None:
            raise UnsatisfiedRequirementsError, "need to set machine first"

    def check_disks_setup(self):
        self.check_machine_set()
        if not self._disks_setup:
            raise UnsatisfiedRequirementsError, "disk devices need to be setup first"

    def check_target_mounted(self):
        self.check_target_exists()
        self.check_disks_setup()
        if not self._target_mounted:
            raise UnsatisfiedRequirementsError, "target needs to be mounted first"
        
            
class MachineInstaller(BaseMachineInstaller):
    def __init__(self, conn):
        BaseMachineInstaller.__init__(self, conn)
        # the processes are mostly the same as in the
        # ChrootInstaller
        self._processes = list(DEFAULT_PROCESSES)
        pmap = dict(setup_disks=self.setup_disks,
                    mount_target=self.mount_target,
                    install_fstab=self.install_fstab,
                    install_modules=self.install_modules,
                    install_kernel=self.install_kernel,
                    prepare_bootloader=self.prepare_bootloader
                    )
        self._process_map.update(pmap)
        self.machine = MachineHandler(self.conn)
        self.helper = None
        self._target_mounted = False
        self._disks_setup = False
        
    def set_machine(self, machine):
        self.check_target_set()
        self.machine.set_machine(machine)
        logdir = path(self.defenv.get('installer', 'base_log_directory'))
        if not logdir.isdir():
            logdir.mkdir()
        logfile = logdir / 'paella-install-%s.log' % machine
        os.environ['PAELLA_MACHINE'] = machine
        disklogpath = path(self.defenv.get('installer', 'disk_log_directory'))
        self.disklogpath = disklogpath / ('disklog-%s'  % machine)
        if not self.disklogpath.isdir():
            self.disklogpath.makedirs()
        self.set_logfile(logfile)
        self.log.info('machine set to %s' % machine)
        # we need to set machine_data before setting the profile
        # so that the machine_data is passed to the profile and trait installers
        self.machine_data = self.machine.get_machine_data()
        profile = self.machine.get_profile()
        self.set_profile(profile)
        self.curenv = CurrentEnvironment(self.conn, machine)
        self.helper = MachineInstallerHelper(self)
        self.helper.curenv = self.curenv

    def make_script(self, procname):
        self.check_machine_set()
        script = self.machine.relation.get_script(procname, inherited=True)
        if script is not None:
            return make_script(procname, script, '/')
        else:
            return None
        
    def ready_base_for_install(self):
        self.check_target_mounted()
        # run ready_base_for_install from chroot installer first
        ChrootInstaller.ready_base_for_install(self)
        
    def install_modules(self):
        self.check_install_complete()
        self.log.info("install_modules isn't being used anymore.")
        msg = "This step is still here, in case you need to use a script"
        msg += " to add modules to /etc/modules ."
        self.log.info(msg)
        if False:
            self.helper.install_modules()

    def install_kernel(self):
        self.check_install_complete()
        self.helper.install_kernel()

    def prepare_bootloader(self):
        self.helper.prepare_bootloader()
        
    def install_fstab(self):
        self.check_install_complete()
        self.helper.install_fstab()

    def setup_disks(self):
        self.helper.setup_disks()
        self._disks_setup = True
        
    def mount_target(self):
        self.check_target_exists()
        self.check_disks_setup()
        self.helper.mount_target()
        self._target_mounted = True
        
    def log_all_processes_started(self):
        machine = self.machine.current_machine
        installer = self.__class__.__name__
        self.log.info('Starting all processes for %s(%s)' % (installer, machine))
        
    def log_all_processes_finished(self):
        machine = self.machine.current_machine
        installer = self.__class__.__name__
        self.log.info('Finished all processes for %s(%s)' % (installer, machine))

            
if __name__ == '__main__':
    pass
    

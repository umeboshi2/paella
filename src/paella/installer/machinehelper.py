import os
from os.path import join, basename, dirname

from useless.base import Error
from useless.base.util import echo

# some helper methods are now
# used in the chroot installer
from paella import deprecated

from paella.debian.base import debootstrap

from base import CurrentEnvironment
from base import runlog

# this import should probably be removed
from base import InstallError


from util.disk import setup_disk_fai
from util.disk import partition_disk
from util.disk import create_raid_partition
from util.disk import wait_for_resync
from util.filesystem import make_filesystems
from util.filesystem import make_fstab
from util.misc import extract_tarball

from util.main import setup_modules
from util.postinst import install_kernel

class BootLoaderNotImplementedError(InstallError):
    pass

class MachineInstallerHelper(object):
    def __init__(self, installer):
        if installer.machine.current is None:
            raise InstallError, 'installer must have machine selected'
        if installer.target is None:
            raise InstallError, 'installer must have target set'
        self.installer = installer
        name = self.__class__.__name__
        self.installer.mainlog.add_logger(name)
        self.log = self.installer.mainlog.loggers[name]
        self.machine = self.installer.machine
        self.conn = self.machine.conn
        self.target = self.installer.target
        self.disklogpath = self.installer.disklogpath
        self.defenv = self.installer.defenv
        self.curenv = None
        
    def _partition_disk(self, diskname, device):
        msg = 'partitioning %s %s' % (diskname, device)
        self.log.info(msg)
        dump = self.machine.make_partition_dump(diskname, device)
        partition_disk(dump, device)
            
    def set_machine(self, machine):
        self.machine.set_machine(machine)

    def partition_disks(self):
        disks = self.machine.check_machine_disks()
        for diskname in disks:
            for device in disks[diskname]:
                self._partition_disk(diskname, device)
            if len(disks[diskname]) > 1:
                self._raid_setup = True
                self._raid_drives = {}
                self._raid_drives[diskname] = disks[diskname]
                self.log.info('doing raid setup on %s' % diskname)
                fsmounts = self.machine.get_installable_fsmounts()
                pnums = [r.partition for r in fsmounts]
                mdnum = 0 
                for p in pnums:
                    runvalue = create_raid_partition(disks[diskname], p,
                                                     mdnum, raidlevel=1)
                    mdnum += 1
                wait_for_resync()
                    
    def check_raid_setup(self):
        raid_setup = False
        disks = self.machine.check_machine_disks()
        for diskname in disks:
            if len(disks[diskname]) > 1:
                raid_setup = True
        return raid_setup

    def get_raid_devices(self):
        disks = self.machine.check_machine_disks()
        for diskname in disks:
            if len(disks[diskname]) > 1:
                return disks[diskname]
        return []
    
    def make_filesystems(self):
        device = self.machine.mtype.array_hack()
        all_fsmounts = self.machine.get_installable_fsmounts()
        env = CurrentEnvironment(self.conn, self.machine.current.machine)
        make_filesystems(device, all_fsmounts, env)

    def check_if_mounted(self, device):
        mounts = file('/proc/mounts')
        for line in file:
            if line.startswith(device):
                return True
        return False

    def unmount_device(self, device):
        mounted = os.system('umount %s' % device)

    def _get_disks(self):
        return self.machine.check_machine_disks()
    
    def setup_disks(self):
        disks = self._get_disks()
        if not disks:
            self._setup_disk_fai('/dev/hda')
        else:
            self.partition_disks()
            self.make_filesystems()
            

    def _setup_disk_fai(self, device):
        disk_config = self.machine.make_disk_config_info(device, curenv=self.curenv)
        setup_disk_fai(disk_config, self.disklogpath)

    def install_fstab(self):
        fstab = self.machine.make_fstab()
        make_fstab(fstab, self.target)

    def install_modules(self):
        modules = self.machine.get_modules()
        setup_modules(self.target, modules)

    def install_kernel(self):
        self.log.info('Preparing grub bootloader before installing kernel')
        basecmd = 'grub-install --root-directory=%s --recheck' % self.target
        if not self._get_disks():
            device = '/dev/hda'
        else:
            self.log.info('disks are %s' % str(self._get_disks()))
            self.log.info('we are currently unable to handle this method.')
            raise BootLoaderNotImplementedError, "grub is not implemented on this setup yet"
        grubcmd = '%s %s' % (basecmd, device)
        runlog(grubcmd)
        self.log.info('grub-install completed.')
        chrootcmd = 'chroot %s update-grub -y' % self.target
        self.log.info('running update-grub in target')
        runlog(chrootcmd)
        self.log.info('update-grub completed.')
        kernel = self.machine.current.kernel
        #install_kernel(kernel, self.target)
        cmd = 'apt-get -y install %s' % kernel
        chrootcmd = 'chroot %s %s' % (self.target, cmd)
        self.log.info('installing kernel with command: %s' % chrootcmd)
        runlog(chrootcmd)
        self.log.info('Kernel installation is complete.')
        

if __name__ == '__main__':
    pass
    

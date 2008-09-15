import os
from os.path import join, basename, dirname

from useless.base import Error
from useless.base.util import echo
from useless.base.path import path

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

class BaseHelper(object):
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

# I don't really like making this
# class, since it can go into the
# the MachineInstallerHelper class,
# but I don't want to make that class
# too big.  Eventually, all of the
# machine installer code needs
# to be reorganized
class KernelHelper(BaseHelper):
    def __init__(self, installer):
        BaseHelper.__init__(self, installer)
        self.targetdev = self.target / 'dev'
        self.targetdevpts = self.targetdev / 'pts'
        self.chroot_precommand = ['chroot', str(self.target)]
        self.aptinstall = ['apt-get', '-y', 'install']
        
    def bind_mount_dev(self):
        mount_cmd = ['mount', '-o', 'bind', '/dev', self.targetdev]
        mount_devpts = ['mount', '-t', 'devpts', 'devpts', '/dev/pts']
        runlog(mount_cmd)
        runlog(self.chroot_precommand + mount_devpts)

    def umount_dev(self):
        umount_devpts = ['umount', '/dev/pts']
        runlog(self.chroot_precommand + umount_devpts)
        umount_cmd = ['umount', self.targetdev]
        runlog(umount_cmd)

    # pass a keyword arg, since there's a grub2 now
    def install_grub_package(self, grub='grub'):
        cmd = self.chroot_precommand + self.aptinstall + [grub]
        runlog(cmd)
        
    # It's really bad form to specify /dev/hda here
    def install_grub(self, device='/dev/hda', floppy=False):
        if not device.startswith('/dev'):
            device = '/dev/%s' % device
        opts = ['--recheck']
        if not floppy:
            opts.append('--no-floppy')
        bin = '/usr/sbin/grub-install'
        runlog(self.chroot_precommand + [bin] + opts + [device])
        
    def update_grub(self):
        runlog(self.chroot_precommand + ['update-grub'])

    def install_kernel_package(self):
        self.log.info('called install_kernel_package')
        kernel = self.machine.current.kernel
        cmd = self.chroot_precommand + self.aptinstall + [kernel]
        self.log.info('install cmd is: %s' % ' '.join(cmd))
        kimgconf = self.target / 'etc' / 'kernel-img.conf'
        kimgconf_old = path('%s.paella-orig' % kimgconf)
        kimgconflines = ['do_bootloader = No',
                         'do_initrd = Yes',
                         'warn_initrd = No'
                         ]
        if kimgconf.exists():
            self.log.info('/etc/kernel-img.conf already exists')
            k = '/etc/kernel-img.conf'
            msg ='renaming %s to %s.paella-orig' % (k, k)
            self.log.info(msg)
            if kimgconf_old.exists():
                raise RuntimeError , '%s already exists, aborting install.' % kimgconf_old
            os.rename(kimgconf, kimgconf_old)
        kimgconf.write_lines(kimgconflines)
        runlog(cmd)
        self.log.info('Kernel installation is complete.')
        if kimgconf_old.exists():
            self.log.info('Restoring /etc/kernel-img.conf')
            os.remove(kimgconf)
            os.rename(kimgconf_old, kimgconf)

    def install_kernel(self, bootdevice='/dev/hda'):
        self.bind_mount_dev()
        self.install_kernel_package()
        self.umount_dev()        

    def prepare_bootloader(self, bootdevice='/dev/hda'):
        self.bind_mount_dev()
        self.install_grub_package()
        self.install_grub(device=bootdevice)
        self.update_grub()
        self.umount_dev()
        
class MachineInstallerHelper(BaseHelper):
    def set_machine(self, machine):
        self.machine.set_machine(machine)

    def check_if_mounted(self, device):
        mounts = file('/proc/mounts')
        for line in file:
            if line.startswith(device):
                return True
        return False

    def unmount_device(self, device):
        #mounted = os.system('umount %s' % device)
        # this is how the command should look
        #mounted = runlog(['umount', device])
        # LOOK FOR WHERE THIS IS CALLED
        # why assign the return to mounted if I wasn't going
        # to return it?
        # passing str to runlog to find where this
        # is called.
        mounted = runlog('umount %s' % device)
        # return mounted
        
    def setup_disks(self):
        self.log.warn('HARDCODED /dev/hda in machinehelper.setup_disks')
        self._setup_disk_fai('/dev/hda')

    def _setup_disk_fai(self, device):
        disk_config = self.machine.make_disk_config_info(device, curenv=self.curenv)
        cmd = setup_disk_fai(disk_config, self.disklogpath)
        runlog(cmd)
        for var in ['sfdisk', 'LOGDIR', 'diskvar']:
            if var in os.environ:
                self.log.info('%s in os.environ' % var)
                self.log.info('deleting %s from os.environ' % var)
                del os.environ[var]
            else:
                self.log.info('%s not defined' % var)

    def install_fstab(self):
        fstab = self.machine.make_fstab()
        make_fstab(fstab, self.target)

    def install_modules(self):
        modules = self.machine.get_modules()
        setup_modules(self.target, modules)


    
    # this is still an ugly way
    # to install the kernel.  This method
    # could use some work.
    def install_kernel(self, bootdevice='/dev/hda'):
        khelper = KernelHelper(self.installer)
        khelper.install_kernel(bootdevice=bootdevice)

    def prepare_bootloader(self, bootdevice='/dev/hda'):
        khelper = KernelHelper(self.installer)
        khelper.prepare_bootloader(bootdevice=bootdevice)
        
        

if __name__ == '__main__':
    pass
    

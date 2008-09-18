import os
import re
from os.path import join, basename, dirname
import subprocess

from useless.base import Error
from useless.base.util import echo
from useless.base.path import path

# some helper methods are now
# used in the chroot installer
from paella import deprecated

from base import CurrentEnvironment
from base import runlog

# this import should probably be removed
from base import InstallError


from util.disk import setup_disk_fai
from util.disk import setup_storage_fai
from util.disk import partition_disk
from util.disk import create_raid_partition
from util.disk import wait_for_resync
from util.filesystem import make_filesystems
from util.filesystem import make_fstab
from util.misc import extract_tarball

from util.main import setup_modules
from util.postinst import install_kernel

def determine_mods_from_diskconfig(diskconfig):
    lines = diskconfig.split('\n')
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line.startswith('disk_config') or line.startswith('raid')]
    modules = []
    mods = dict(lvm='dm-mod', raid0='raid0', raid1='raid1',
                raid5='raid5')
    for line in lines:
        split_line = line.split()
        for mod in mods:
            if mod in split_line:
                if mods[mod] not in modules:
                    modules.append(mods[mod])
    return modules
    
def append_unique(item, list):
    if item not in list:
        list.append(item)
        
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
        self.diskconfig = None
        
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
        # some re's for obtaining info from disk_var.sh
        self.bootdevice_re = re.compile('BOOT_DEVICE="(?P<device>.*)"')
        self.root_partition_re = re.compile('ROOT_PARTITION=(?P<root_partition>.*)')
        
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
        extra_modules = self.determine_extra_modules_from_diskconfig()
        if extra_modules:
            self.log.info('Checking if extra packages are required before kernel install.')
            self.install_packages_for_extra_modules(extra_modules)
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

    def prepare_bootloader(self, bootdevice, root_partition):
        self.bind_mount_dev()
        self.install_grub_package()
        self.install_grub(device=bootdevice)
        self.fix_root_partition_in_grub_menu(root_partition)
        self.update_grub()
        self.umount_dev()

    def fix_root_partition_in_grub_menu(self, root_partition):
        filename = self._grub_menu_filename()
        if filename.exists():
            menu = self._grub_menu_lines()
            new_menu = self._fix_root_in_grub(menu, root_partition)
            filename.write_text(new_menu)
            
    def _grub_menu_filename(self):
        return self.target / 'boot/grub/menu.lst'

    def _grub_menu_lines(self):
        filename = self._grub_menu_filename()
        menu = [line for line in file(filename).readlines()]
        return menu

    def _fix_root_in_grub(self, menu, root_partition):
        kopt = [line for line in menu if line.startswith('# kopt=')]
        if len(kopt) != 1:
            raise RuntimeError , "There's no kopt line in the /boot/grub/menu.lst"
        index = menu.index(kopt[0])
        kopt_line = menu[index]
        # split the line by spaces
        kopt_line_split = kopt_line.split()
        # find the part that defines where root is
        root_pieces = [piece for piece in kopt_line_split if piece.find('root=') > -1]
        if len(root_pieces) != 1:
            msg = "kopt line has wrong amount of root= options: %s" % kopt_line
            raise RuntimeError , msg
        # there should only be one root= option
        root_piece = root_pieces[0]
        kopt_index = kopt_line_split.index(root_piece)
        # we can't be sure that the piece is just root=
        # since the default grub has kopt=root=/dev/root_partition
        # but we know that it's the last piece when it's split by '='
        root_piece_split = root_piece.split('=')
        # change the root partition here
        root_piece_split[-1] = root_partition
        # put it back into it's original form
        new_root_piece = '='.join(root_piece_split)
        # stick it back into the split line
        kopt_line_split[kopt_index] = new_root_piece
        # put the line back into shape
        new_kopt_line = ' '.join(kopt_line_split)
        # put the new line into the menu
        menu[index] = new_kopt_line
        # join the menu lines back together
        new_menu = ''.join(menu)
        return new_menu
    

    def _get_diskvar(self):
        filename = self.disklogpath / 'disk_var.sh'
        diskvar = file(filename).read()
        return diskvar
    
    def get_bootdevice_from_diskvar(self):
        diskvar = self._get_diskvar()
        searched = self.bootdevice_re.search(diskvar)
        groupdict = searched.groupdict()
        if 'device' in groupdict:
            return groupdict['device']
        else:
            raise RuntimeError , "boot device not found in diskvar"

    def get_rootpartition_from_diskvar(self):
        diskvar = self._get_diskvar()
        searched = self.root_partition_re.search(diskvar)
        groupdict = searched.groupdict()
        if 'root_partition' in groupdict:
            return groupdict['root_partition']
        else:
            raise RuntimeError , "root partition not found in diskvar"
        
    def determine_extra_modules_from_diskconfig(self):
        if self.diskconfig is None:
            raise RuntimeError , "diskconfig isn't set yet"
        return determine_mods_from_diskconfig(self.diskconfig)

    def add_extra_modules_to_initrd(self, modules):
        filename = self.target / 'etc/initramfs-tools/initramfs.conf'
        filename = self.target / 'etc/initramfs-tools/modules'
        filename.write_lines(modules, append=True)

    def update_initrd_with_extra_modules(self, modules):
        self.add_extra_modules_to_initrd(extra_modules)
        msg = 'adding these extra modules to initrd: %s' % ', '.join(extra_modules)
        self.log.info(msg)
        cmd = self.chroot_precommand + ['update-initramfs', '-u']
        if 'DEBUG' in os.environ:
            cmd.append('-v')
        runlog(cmd)
        

    # The packages that are installed are probably not complete
    # and more testing needs to be done on this to insure that
    # the proper packages are installed for each filesystem
    # requirement, and that unnecessary packages aren't being
    # installed.
    def install_packages_for_extra_modules(self, modules):
        """Install the packages required to handle these modules."""
        cmd = self.chroot_precommand + self.aptinstall
        packages = []
        for module in modules:
            if module == 'dm-mod':
                append_unique('lvm2', packages)
                append_unique('dmsetup', packages)
            if module.startswith('raid'):
                append_unique('mdadm', packages)
        msg = "Installing these extra packages: %s" % ', '.join(packages)
        self.log.info(msg)
        cmd += packages
        runlog(cmd)
    
                
        
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
        self._setup_storage_fai()
        
    def _setup_storage_fai(self):
        row = self.machine.get_diskconfig()
        diskconfig = row.content
        self.diskconfig = diskconfig
        disklist = row.disklist
        if disklist is None:
            disklist = []
            cmd = ['/usr/lib/fai/disk-info']
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            retval = proc.wait()
            if retval:
                raise RuntimeError , 'disk-info returned %d' % retval
            for line in proc.stdout:
                disklist.append(line.split()[0])
            print disklist
        #os.environ['DEBUG'] = 'true'
        cmd = setup_storage_fai(disklist, diskconfig, self.disklogpath)
        runlog(cmd)
        print "done", self.disklogpath
    
    def mount_target(self):
        print "in mount_target"
        fstab_filename = self.disklogpath / 'fstab'
        if not fstab_filename.isfile():
            msg = "couldn't find fstab at %s" % fstab_filename
            raise RuntimeError , msg
        fstab_lines = [line.split() for line in fstab_filename.open() if not line.startswith('#')]
        #print fstab_lines
        # start mounting
        for line in fstab_lines:
            #print line
            device = line[0]
            mtpt = line[1]
            fstype = line[2]
            #print 'device, mtpt, fstype', device, mtpt, fstype
            if mtpt.startswith('/'):
                target_path = self.target / mtpt[1:]
                if not target_path.isdir():
                    target_path.mkdir()
                # in case we're mounting /tmp as tmpfs
                # or similar
                if fstype not in ['tmpfs']:
                    cmd = ['mount', '-t', fstype, device, target_path]
                    #print ' '.join(cmd)
                    runlog(cmd)
                else:
                    self.log.info('not mounting %s with %s fstype' % (mtpt, fstype))
                    
    def install_fstab(self):
        fstab_filename = self.disklogpath / 'fstab'
        target_fstab = self.target / 'etc/fstab'
        target_fstab.write_text(fstab_filename.text())
        # we need some code to add certaing filesystems
        # to the fstab like /tmp on tmpfs
        # or some standard nfs mounts
        # while this step can be hooked with a script that
        # does this, it would be nice to have some sort of
        # support in the framework to do this, or at least help
        
        
    def install_modules(self):
        modules = self.machine.get_modules()
        setup_modules(self.target, modules)


    # this is still an ugly way
    # to install the kernel.  This method
    # could use some work.
    def install_kernel(self, bootdevice=None):
        khelper = KernelHelper(self.installer)
        khelper.diskconfig = self.diskconfig
        if bootdevice is None:
            bootdevice = khelper.get_bootdevice_from_diskvar()
        khelper.install_kernel(bootdevice=bootdevice)
        # we need code to add needed modules
        # to the initrd.  we can determine some of
        # these by looking at the diskconfig for raid and lvm
        # but there may be more.
        

    def prepare_bootloader(self, bootdevice=None, root_partition=None):
        khelper = KernelHelper(self.installer)
        if bootdevice is None:
            bootdevice = khelper.get_bootdevice_from_diskvar()
        if root_partition is None:
            root_partition = khelper.get_rootpartition_from_diskvar()
        khelper.prepare_bootloader(bootdevice, root_partition)
        
        

if __name__ == '__main__':
    pass
    

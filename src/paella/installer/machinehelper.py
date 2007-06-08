import os
from os.path import join, basename, dirname

from useless.base import Error
from useless.base.util import echo

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
from util.misc import extract_tarball

class MachineInstallerHelper(object):
    def __init__(self, installer):
        object.__init__(self)
        if installer.machine.current is None:
            raise InstallError, 'installer must have machine selected'
        if installer.target is None:
            raise InstallError, 'installer must have target set'
        self.installer = installer
        self.machine = self.installer.machine
        self.conn = self.machine.conn
        self.target = self.installer.target
        self.disklogpath = self.installer.disklogpath
        self.defenv = self.installer.defenv
        self.curenv = None
        
    def _partition_disk(self, diskname, device):
        print 'partitioning', diskname, device
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
                print 'doing raid setup on %s' % diskname
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
        
    def setup_disks(self):
        disks = self.machine.check_machine_disks()
        disknames = disks.keys()
        if not len(disknames):
            self._setup_disk_fai('/dev/hda')
        else:
            self.partition_disks()
            self.make_filesystems()
            

    def _setup_disk_fai(self, device):
        disk_config = self.machine.make_disk_config_info(device, curenv=self.curenv)
        setup_disk_fai(disk_config, self.disklogpath)
        
    def extract_basebootstrap(self):
        echo('extracting premade base tarball')
        suite_path = self.defenv.get('installer', 'suite_storage')
        basefile = join(suite_path, '%s.tar' % self.installer.suite)
        runvalue = extract_tarball(self.target, basefile)
        if runvalue:
            raise InstallError, 'problems extracting %s to %s' % (basefile, self.target)

    def debootstrap_target(self):
        suite = self.installer.suite
        debmirror = self.installer.debmirror
        cmd = debootstrap(suite, self.target, debmirror)
        info = self.installer.log.info
        info('running debootstrap with cmd %s' % cmd)
        runvalue = runlog(debootstrap(self.installer.suite, self.target, self.installer.debmirror))
        if runvalue:
            raise InstallError, 'problems bootstrapping with %s' % cmd

    def bootstrap_target(self):
        if self.defenv.is_it_true('installer', 'bootstrap_target'):
            self.debootstrap_target()
        else:
            self.extract_basebootstrap()
    

if __name__ == '__main__':
    pass
    

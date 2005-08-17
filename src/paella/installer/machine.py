import os
from os.path import join, basename, dirname

from useless.base import Error
from useless.base.util import makepaths, runlog
from useless.base.util import echo

from paella.debian.base import debootstrap
from paella.db.machine import MachineHandler

from base import CurrentEnvironment
from base import BaseChrootInstaller
from base import InstallError
from profile import ProfileInstaller
from util import ready_base_for_install, make_filesystem
from util import make_filesystems
from util import install_kernel, setup_modules
from util import setup_disk_fai, partition_disk
from util import create_raid_partition, mount_target
from util import wait_for_resync, make_sources_list
from util import make_fstab, makedev
from util import myline, set_root_passwd, make_interfaces_simple
from util import create_mdadm_conf, extract_tarball
from util import mount_target_proc, make_script
from util import make_official_sources_list

#from profile import ProfileInstaller
#from fstab import HdFstab
DEFAULT_PROCESSES = [
    'pre', 'setup_disks', 'mount_target',
    'bootstrap', 'make_device_entries',
    'apt_sources_installer', 'ready_base',
    'mount_target_proc',
    'pre_install', 'install', 'post_install',
    'install_fstab', 'install_modules', 'install_kernel',
    'apt_sources_final', 'umount_target_proc', 'post'
    ]

def scriptinfo(name):
    return dict(start='%s script started' % name,
                done='%s script finished' % name)

class MachineInstallerHelper(object):
    def __init__(self, installer):
        object.__init__(self)
        if installer.machine.current is None:
            raise Error, 'installer must have machine selected'
        if installer.target is None:
            raise Error, 'installer must have target set'
        self.installer = installer
        self.machine = self.installer.machine
        self.conn = self.machine.conn
        self.target = self.installer.target
        self.disklogpath = self.installer.disklogpath
        self.defenv = self.installer.defenv
        
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
        disk_config = self.machine.make_disk_config_info(device)
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
    
class MachineInstaller(BaseChrootInstaller):
    def __init__(self, conn):
        BaseChrootInstaller.__init__(self, conn)
        self.machine = MachineHandler(self.conn)
        self.processes = DEFAULT_PROCESSES
        self._process_map = {
            'setup_disks' : self.setup_disks,
            'mount_target' : self.mount_target,
            'bootstrap' : self.bootstrap_target,
            'make_device_entries' : self.make_device_entries,
            'apt_sources_installer' : self.setup_apt_sources_installer,
            'ready_base' : self.ready_base_for_install,
            'mount_target_proc' : self.mount_target_proc,
            'install' : self.install_to_target,
            'install_fstab' : self.install_fstab,
            'install_modules' : self.install_modules,
            'install_kernel' : self.install_kernel,
            'apt_sources_final' : self.setup_apt_sources_final,
            'umount_target_proc' : self.umount_target_proc
            }
        self.helper = None
        
    def process(self):
        mach = self.machine.current.machine
        self.log.info('Starting machine install process for %s' % mach)
        for proc in self.processes:
            self.log.info('processing %s for machine %s' % (proc, mach))
            self.run_process(proc)
            self.log.info('processed %s for machine %s' % (proc, mach))
        self.log.info('Ending machine install process for %s' % mach)
        
    def _make_script(self, name):
        script = self.machine.get_script(name)
        if script is not None:
            return make_script(name, script, self.target)
        else:
            return None
        
    def run_process(self, proc):
        info = self.log.info
        self.start_process(proc)
        script = self._make_script(proc)
        mtype = self.machine.current.machine_type
        if script is None:
            info('No script for process %s on machine type %s' % (proc, mtype))
            if proc in self._process_map:
                info('Running default process %s' % proc)
                self._process_map[proc]()
            else:
                info('Nothing to do for process %s' % proc)
        else:
            self.log.info('%s script exists for %s' % (proc, mtype))
            self.run_process_script(proc, script)
        self.finish_process(proc)

    def start_process(self, proc):
        self._check_target()
        if proc == 'bootstrap':
            self._check_target_exists()
            
    def finish_process(self, proc):
        if proc == 'mount_target':
            self._mounted = True
            self.log.info('Target should be mounted now.')
        elif proc == 'bootstrap':
            self.log.info('Target should be bootstrapped now.')
            self._bootstrapped = True
    
    def _runscript(self, script, name, info):
        self.log.info(info['start'])
        runvalue = self.run(name, script, chroot=False)
        os.remove(script)
        self.log.info(info['done'])
        return runvalue
    
    def run_process_script(self, proc, script):
        info = scriptinfo(proc)
        if self._runscript(script, proc, info):
            raise InstallError, 'Error running script %s' % proc
        

    def _check_mounted(self):
        self._check_target_exists()
        if not self._mounted:
            raise InstallError, 'target not mounted'

    def _check_bootstrap(self):
        self._check_mounted()
        BaseChrootInstaller._check_bootstrap(self)
        
    def set_machine(self, machine):
        self.machine.set_machine(machine)
        try:
            logfile = os.environ['LOGFILE']
        except KeyError:
            logfile = '/paellalog/paella-install-%s.log' % machine
        os.environ['PAELLA_LOGFILE'] = logfile
        # this needs to be removed sometime
        os.environ['LOGFILE'] = logfile
        os.environ['PAELLA_MACHINE'] = machine
        disklogpath = join(dirname(logfile), 'disklog')
        if not os.path.isdir(disklogpath):
            makepaths(disklogpath)
        self.disklogpath = disklogpath
        self.curenv = CurrentEnvironment(self.conn, self.machine.current.machine)
        self.set_logfile(logfile)
        self.log.info('Machine Installer set machine to %s' % machine)
        self.mtypedata = self.machine.mtype.get_machine_type_data()
        
    def install(self, machine, target):
        self.set_machine(machine)
        self.setup_installer()
        self.set_target(target)
        self.log.info('Installer set to install %s to %s' % (machine, target))
        self.helper = MachineInstallerHelper(self)
        self.process()
        
    def setup_installer(self):
        machine = self.machine.current.machine
        profile = self.machine.current.profile
        self.log.info('Setting up profile installer for %s' % machine)
        self.installer = ProfileInstaller(self.conn)
        self.installer.log = self.log
        self.installer.mtypedata = self.mtypedata
        self.installer.set_profile(profile)
        self.suite = self.installer.suite
        self._installer_ready = True
        self.log.info('Profile installer ready for %s' % machine)
        
    
    def setup_disks(self):
        "this is a default process"
        self.helper.setup_disks()

    def mount_target(self):
        "this is a default process"
        self._check_target()
        makepaths(self.target)
        device = self.machine.array_hack()
        mounts = self.machine.get_ordered_fsmounts()
        mount_target(self.target, mounts, device)
        self._mounted = True
        
    def bootstrap_target(self):
        "this is a default process"
        self.helper.bootstrap_target()

    def make_device_entries(self):
        "this is a default process"
        if self.defenv.is_it_true('installer', 'use_devices_tarball'):
            runlog('echo extracting devices tarball')
            self._extract_devices_tarball()
        else:
            runlog('echo using MAKEDEV to make generic devices')
            self.make_generic_devices()
        self.make_disk_devices()
        
    def setup_apt_sources_installer(self):
        "this is a default process"
        make_sources_list(self.defenv, self.target, self.suite)

    def ready_base_for_install(self):
        "this is a default process"
        set_root_passwd(self.target, myline)
        make_interfaces_simple(self.target)
        devices = self.helper.get_raid_devices()
        if devices:
            create_mdadm_conf(self.target, devices)

    def mount_target_proc(self):
        "this is a default process"
        echo('mounting target /proc')
        mount_target_proc(self.target)
        
    def install_to_target(self):
        "this is a default process"
        os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
        self._check_target()
        self._check_installer()
        self.installer.set_target(self.target)
        self.installer.process()        

    def install_modules(self):
        "this is a default process"
        modules = self.machine.get_modules()
        setup_modules(self.target, modules)

    def install_kernel(self):
        "this is a default process"
        kernel = self.machine.current.kernel
        echo('installing kernel %s' % kernel)
        install_kernel(kernel, self.target)
        
    def setup_apt_sources_final(self):
        "this is a default process"
        make_official_sources_list(self.defenv, self.target, self.suite)
    def install_fstab(self):
        "this is a default process"
        fstab = self.machine.make_fstab()
        make_fstab(fstab, self.target)
        
    def umount_target_proc(self):
        "this is a default process"
        echo('unmounting target /proc')
        mount_target_proc(self.target, umount=True)

        
    def _extract_devices_tarball(self):
        dtball = self.defenv.get('installer', 'devices_tarball')
        devpath = join(self.target, 'dev')
        runvalue = extract_tarball(devpath, dtball)
        if runvalue:
            raise Error, 'problem extracting devices tarball'

    def make_generic_devices(self):
        makedev(self.target, ['generic'])

    def make_disk_devices(self):
        devices = map(basename, self.machine.get_disk_devices())
        makedev(self.target, devices)
        
if __name__ == '__main__':
    pass
    

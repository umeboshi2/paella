import os
import subprocess

from useless.base.util import makepaths
from useless.base.path import path
from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq, Gt


from paella.debian.base import debootstrap

from base import BaseInstaller
from base import runlog
from base import BaseInstallError, InstallError

from util.base import make_fake_start_stop_daemon
from util.base import remove_fake_start_stop_daemon
from util.aptsources import make_sources_list
from util.aptsources import make_official_sources_list
from util.filesystem import make_filesystem
from util.postinst import install_kernel
from util.preinst import ready_base_for_install

from profile import ProfileInstaller

class UnsatisfiedRequirementsError(BaseInstallError):
    pass

class InstallTargetError(BaseInstallError):
    pass

# here are some decorators to check requirements
# needed to invoke a method

# make sure target is set to a value
def requires_target_set(func):
    def wrapper(self, *args, **kw):
        if self.target is None:
            raise UnsatisfiedRequirementsError, "need to set target first"
        return func(self, *args, **kw)
    return wrapper

# make sure the suite is set
def requires_suite_set(func):
    def wrapper(self, *args, **kw):
        if self.suite is None:
            raise UnsatisfiedRequirementsError, "need to set suite first"
        if self.base_suite is None:
            raise UnsatisfiedRequirementsError, "base_suite unset, need to set suite first"
        return func(self, *args, **kw)
    return wrapper
    

# make sure target is directory
def requires_target_exists(func):
    @requires_target_set
    def wrapper(self, *args, **kw):
        if not self.target.isdir():
            msg = "need to create target directory at %s first" % self.target
            raise UnsatisfiedRequirementsError, msg
        return func(self, *args, **kw)
    return wrapper

# make sure target is bootstrapped
def requires_bootstrap(func):
    @requires_target_exists
    def wrapper(self, *args, **kw):
        if not self._bootstrapped:
            msg = "need to bootstrap target directory at %s first" % self.target
            raise UnsatisfiedRequirementsError, msg
        return func(self, *args, **kw)
    return wrapper


# make sure target /proc is mounted
def requires_target_proc_mounted(func):
    @requires_bootstrap
    def wrapper(self, *args, **kw):
        if not self._target_proc_mounted():
            msg = "target /proc needs to be mounted first"
            raise UnsatisfiedRequirementsError, msg
        return func(self, *args, **kw)
    return wrapper

# make sure target /sys is mounted
def requires_target_sys_mounted(func):
    @requires_bootstrap
    def wrapper(self, *args, **kw):
        if not self._target_sys_mounted():
            msg = "target /sys needs to be mounted first"
            raise UnsatisfiedRequirementsError, msg
        return func(self, *args, **kw)
    return wrapper
    
# this may not be used later
def requires_installer_set(func):
    def wrapper(self, *args, **kw):
        if self.installer is None:
            raise UnsatisfiedRequirementsError, "need to set installer first"
        return func(self, *args, **kw)
    return wrapper


def requires_install_complete(func):
    def wrapper(self, *args, **kw):
        if not self._install_finished:
            raise UnsatisfiedRequirementsError, 'install needs to be complete first'
        return func(self, *args, **kw)
    return wrapper


# basic operation:
# 1. setup installer db connection
# 2. init ChrootInstaller
# 3. set logfile
# 4. set target
# 5. set profile
# 6. run_all_processes
class ChrootInstaller(BaseInstaller):
    # we may need more __init__ args later
    def __init__(self, conn):
        BaseInstaller.__init__(self, conn)
        self._bootstrapped = False
        self._install_finished = False
        
        self._processes = [
            'ready_target',
            'bootstrap',
            'mount_target_proc',
            'mount_target_sys',
            'make_device_entries',
            'apt_sources_installer',
            'ready_base_for_install',
            'pre_install',
            'install',
            'post_install',
            'apt_sources_final',
            'umount_target_sys',
            'umount_target_proc'
            ]
        # pre_install is unmapped
        # post_install is unmapped
        self._process_map = dict(ready_target=self.create_target_directory,
                                 bootstrap=self.bootstrap_target,
                                 mount_target_proc=self.mount_target_proc,
                                 mount_target_sys=self.mount_target_sys,
                                 make_device_entries=self.make_device_entries,
                                 apt_sources_installer=self.apt_sources_installer,
                                 ready_base_for_install=self.ready_base_for_install,
                                 install=self.install,
                                 apt_sources_final=self.apt_sources_final,
                                 umount_target_sys=self.umount_target_sys,
                                 umount_target_proc=self.umount_target_proc
                                 )
        # this is only used in the machine installer
        self.mtypedata = {}
    
    # the default script for the chroot installer is None
    def make_script(self, procname):
        return None

    def set_logfile(self, logfile):
        BaseInstaller.set_logfile(self, logfile)
        self.log.info('-'*30)
        msg = '%s initialized' % self.__class__.__name__
        self.log.info(msg)
        self.log.info('-'*30)
        
    @requires_target_set
    def set_profile(self, profile):
        self.installer = ProfileInstaller(self)
        self.installer.mtypedata.update(self.mtypedata)
        self.installer.set_profile(profile)
        self.set_suite(self.installer.suite)
    
    
    @requires_target_exists
    def _bootstrap_with_tarball(self, suite):
        suite_path = path(self.defenv.get('installer', 'suite_storage'))
        filename = '%s.tar.gz' % suite
        basefile = suite_path / filename
        taropts = '-xzf'
        if not basefile.exists():
            filename = '%s.tar' % suite
            basefile = suite_path / filename
            taropts = '-xf'
        cmd = 'tar -C %s %s %s' % (self.target, taropts, basefile)
        # if cmd returns nonzero, runlog will raise an error
        runlog(cmd)
        self._bootstrapped = True
            
    @requires_target_exists
    def _bootstrap_with_debootstrap(self, suite):
        mirror = self.defenv.get('installer', 'http_mirror')
        cmd = debootstrap(suite, self.target, mirror)
        # if cmd returns nonzero, runlog will raise an error
        runlog(cmd)
        self._bootstrapped = True

    @requires_suite_set
    def bootstrap_target(self):
        if not self.target.exists():
            self.target.mkdir()
        if not self.target.isdir():
            raise InstallTargetError, "%s is not a directory" % self.target
        if self.defenv.getboolean('installer', 'bootstrap_target'):
            self.log.info('bootstrapping with debootstrap')
            self._bootstrap_with_debootstrap(self.base_suite)
        else:
            self.log.info('bootstrapping with premade tarball')
            self._bootstrap_with_tarball(self.base_suite)

    @requires_bootstrap
    def make_device_entries(self):
        self.log.info('nothing done for make_device_entries yet')
        
    @requires_bootstrap
    def apt_sources_installer(self):
        make_sources_list(self.conn, self.target, self.suite)
        
    @requires_install_complete
    def apt_sources_final(self):
        sourceslist = self.target / 'etc/apt/sources.list'
        sourceslist_installer = path('%s.installer' % sourceslist)
        os.rename(sourceslist, sourceslist_installer)
        make_official_sources_list(self.conn, self.target, self.suite)

    # this is probably not useful anymore
    # it still has a purpose in the machine installer -
    #  it sets up the mdadm.conf file with the raid devices it creates
    #  if it creates any.
    @requires_bootstrap
    def ready_base_for_install(self):
        # update the package lists
        self.chroot('apt-get -y update')
        
        
    # common method for mounting /proc and /sys
    # here fs is either 'proc' or 'sys'
    def _mount_target_virtfs(self, fs):
        fstype = dict(proc='proc', sys='sysfs')
        cmd = 'mount -t %s none %s' % (fstype[fs], self.target / fs)
        runlog(cmd)
        
        
    def _umount_target_virtfs(self, fs):
        # work around binfmt-support /proc locking
        # found this idea while messing around in live-helper
        if fs == 'proc':
            binfmt_misc = self.target / 'proc/sys/fs/binfmt_misc'
            status = binfmt_misc / 'status'
            if status.exists():
                self.log.info('Unmounting /proc/sys/fs/binfmt_misc in chroot')
                cmd = 'umount %s' % binfmt
                runlog(cmd)
        cmd = 'umount %s' % (self.target / fs)
        runlog(cmd)
        
    def _target_proc_mounted(self):
        testfile = self.target / 'proc/version'
        return testfile.isfile()

    def _target_sys_mounted(self):
        testdir = self.target / 'sys/kernel'
        return testdir.isdir()
    
    @requires_bootstrap
    def mount_target_proc(self):
        self._mount_target_virtfs('proc')

    @requires_bootstrap
    def mount_target_sys(self):
        self._mount_target_virtfs('sys')

    @requires_target_proc_mounted
    def umount_target_proc(self):
        self._umount_target_virtfs('proc')

    @requires_target_sys_mounted
    def umount_target_sys(self):
        self._umount_target_virtfs('sys')

    @requires_target_proc_mounted
    @requires_target_sys_mounted
    @requires_installer_set
    def install(self):
        self.installer.run_all_processes()
        self._install_finished = True

    def log_all_processes_finished(self):
        self.log.info('-'*30)
        self.log.info('%s processes finished' % self.__class__.__name__)
        self.log.info('-'*30)

    def save_logfile_in_target(self):
        install_log = self.target / 'root/paella/install.log'
        self.mainlog.filename.copyfile(install_log)
        
        
        
if __name__ == '__main__':
    from paella.db import PaellaConnection
    conn = PaellaConnection()
    ci = ChrootInstaller(conn)
    

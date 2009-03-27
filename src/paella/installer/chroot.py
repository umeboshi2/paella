import os
import subprocess

from useless.base.util import makepaths
from useless.base.path import path
from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq, Gt


from paella.db.aptkey import AptKeyHandler, NoAptKeyError
from paella.base.util import get_architecture

from base import BaseInstaller
from base import runlog
from base import BaseInstallError, InstallError

# The fake start-stop-daemon functions
# aren't being used until I can determine
# a good way to add it into the base code.
# These functions can be used in the pre
# and post steps of the trait install process
# to keep unwanted servers from starting.

#from util.base import make_fake_start_stop_daemon
#from util.base import remove_fake_start_stop_daemon

from util.aptsources import make_sources_list
from util.aptsources import make_official_sources_list

from profile import ProfileInstaller

class UnsatisfiedRequirementsError(BaseInstallError):
    pass

class InstallTargetError(BaseInstallError):
    pass




# the arch argument is ignored
def debootstrap(suite, root, mirror=None, script='', arch='i386'):
    cmd = ['debootstrap', suite, root]
    if mirror is not None:
        cmd.append(mirror)
    if script:
        cmd.append(script)
    return cmd

class BaseChrootInstaller(BaseInstaller):
    "this class will not work unless subclassed"
    def check_target_set(self):
        if self.target is None:
            raise UnsatisfiedRequirementsError, "need to set target first"

    def check_suite_set(self):
        if self.suite is None:
            raise UnsatisfiedRequirementsError, "need to set suite first"
        if self.base_suite is None:
            msg = "base_suite unset, need to set suite first"
            raise UnsatisfiedRequirementsError, msg

    def check_target_exists(self):
        self.check_target_set()
        if not self.target.isdir():
            msg = "need to create target directory at %s first" % self.target
            raise UnsatisfiedRequirementsError, msg

    def check_bootstrap(self):
        self.check_target_exists()
        if not self._bootstrapped:
            msg = "need to bootstrap target directory at %s first" % self.target
            raise UnsatisfiedRequirementsError, msg

    def check_target_proc_mounted(self):
        self.check_bootstrap()
        if not self._target_proc_mounted():
            msg = "target /proc needs to be mounted first"
            raise UnsatisfiedRequirementsError, msg

    def check_target_sys_mounted(self):
        self.check_bootstrap()
        if not self._target_sys_mounted():
            msg = "target /sys needs to be mounted first"
            raise UnsatisfiedRequirementsError, msg

    def check_installer_set(self):
        if self.installer is None:
            msg = "need to set installer first"
            raise UnsatisfiedRequirementsError, msg

    def check_install_complete(self):
        if not self._install_finished:
            msg = "install needs to be complete first"
            raise UnsatisfiedRequirementsError, msg
    
# basic operation:
# 1. setup installer db connection
# 2. init ChrootInstaller
# 3. set logfile
# 4. set target
# 5. set profile
# 6. run_all_processes
class ChrootInstaller(BaseChrootInstaller):
    # we may need more __init__ args later
    def __init__(self, conn):
        BaseChrootInstaller.__init__(self, conn)
        self._bootstrapped = False
        self._install_finished = False
        
        self._processes = [
            'ready_target',
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
            'apt_sources_final',
            'umount_target_sys',
            'umount_target_proc',
            'umount_target_devpts'
            ]
        # pre_install is unmapped
        # post_install is unmapped
        self._process_map = dict(ready_target=self.create_target_directory,
                                 bootstrap=self.bootstrap_target,
                                 mount_target_proc=self.mount_target_proc,
                                 mount_target_sys=self.mount_target_sys,
                                 make_device_entries=self.make_device_entries,
                                 mount_target_devpts=self.mount_target_devpts,
                                 apt_sources_installer=self.apt_sources_installer,
                                 ready_base_for_install=self.ready_base_for_install,
                                 install=self.install,
                                 apt_sources_final=self.apt_sources_final,
                                 umount_target_sys=self.umount_target_sys,
                                 umount_target_proc=self.umount_target_proc,
                                 umount_target_devpts=self.umount_target_devpts
                                 )
        # this is only used in the machine installer
        self.machine_data = {}
    
    # the default script for the chroot installer is None
    def make_script(self, procname):
        return None

    def set_logfile(self, logfile):
        BaseInstaller.set_logger(self, filename=logfile)
        self.log.info('-'*30)
        msg = '%s initialized' % self.__class__.__name__
        self.log.info(msg)
        self.log.info('-'*30)
        
    def set_profile(self, profile):
        self.check_target_set()
        self.installer = ProfileInstaller(self)
        if os.environ.has_key('DEBUG'):
            self.log.info("ChrootInstaller.machine_data: %s" % self.machine_data)
        self.installer.machine_data.update(self.machine_data)
        if os.environ.has_key('DEBUG'):
            self.log.info("ProfileInstaller.machine_data: %s" % self.installer.machine_data)
        self.installer.set_profile(profile)
        self.set_suite(self.installer.suite)
    
    
    def _bootstrap_with_tarball(self, suite):
        self.check_target_exists()
        suite_path = path(self.defenv.get('installer', 'suite_storage'))
        arch = get_architecture()
        filename = '%s-%s.tar.gz' % (suite, arch)
        basefile = suite_path / filename
        taropts = '-xzf'
        # we normally expect a tar.gz
        # but we'll check for a plain tar also
        if not basefile.exists():
            filename = '%s-%s.tar' % (suite, arch)
            basefile = suite_path / filename
            taropts = '-xf'
        if not basefile.exists():
            # We don't really want to ruin an install
            # by not having a tarball, so we log a warning
            # and proceed with a debootstrap.
            msg = "base tarball not found, reverting to debootstrap"
            self.log.warn(msg)
            self._bootstrap_with_debootstrap(suite)
        else:
            #cmd = 'tar -C %s %s %s' % (self.target, taropts, basefile)
            cmd = ['tar', '-C', str(self.target), taropts, str(basefile)]
            # if cmd returns nonzero, runlog will raise an error
            runlog(cmd)
            # we need to do certain things after extraction
            # that debootstrap does for us,
            # like copy /etc/resolv.conf to the target.
            # these things should be done in the
            # ready_base_for_install process
            self._bootstrapped = True
            
    def _bootstrap_with_debootstrap(self, suite):
        self.check_target_exists()
        mirror = self.defenv.get('installer', 'http_mirror')
        # debug stuff
        cmd = debootstrap(suite, self.target, mirror)
        # if cmd returns nonzero, runlog will raise an error
        runlog(cmd)
        self._bootstrapped = True

    def bootstrap_target(self):
        self.check_suite_set()
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
        # here we add the apt keys that are needed
        # we should probably split this part off into
        # another process.  This step needs to be done
        # before the ready_base_for_install process, or
        # at least at the beginning of that process.
        aptkeys = AptKeyHandler(self.conn)
        keys = self.defenv.get_list('archive_keys', 'installer')
        for key in keys:
            try:
                row = aptkeys.get_row(key)
            except NoAptKeyError:
                msg = "There's no apt key named %s in the database" % key
                self.log.error(msg)
                raise UnsatisfiedRequirementsError , msg
            filename = self.target / ('%s.key' % key)
            if filename.exists():
                msg = "%s already exists" % filename
                self.log.error(msg)
                raise RuntimeError , msg
            keyfile = file(filename, 'w')
            keyfile.write(row.data)
            keyfile.close()
            self.chroot(['apt-key', 'add', '%s.key' % key])
            os.remove(filename)
            if filename.exists():
                msg = "%s wasn't deleted" % filename
                self.log.error(msg)
                raise RuntimeError , msg
            self.log.info('added key %s (%s) to apt' % (key, row.keyid))
        
    def make_device_entries(self):
        self.check_bootstrap()
        self.log.info('nothing done for make_device_entries yet')
        
    def apt_sources_installer(self):
        self.check_bootstrap()
        make_sources_list(self.conn, self.target, self.suite)
        
    def apt_sources_final(self):
        self.check_install_complete()
        sourceslist = self.target / 'etc/apt/sources.list'
        sourceslist_installer = path('%s.installer' % sourceslist)
        os.rename(sourceslist, sourceslist_installer)
        make_official_sources_list(self.conn, self.target, self.suite)

    
    def ready_base_for_install(self):
        """This gets the base that was either
        debootstrapped or extracted ready
        to install packages.  Since the
        install hasn't happened yet, replacing
        files like /etc/resolv.conf and the
        package lists shouldn't affect anything.
        the apt_sources_installer process is called
        right before this one, so there should be
        an appropriate sources.list to update packages
        with.
        """
        self.check_bootstrap()
        # 'copy' /etc/resolv.conf to target
        resolvconf = file('/etc/resolv.conf').read()
        target_resolvconf = self.target / 'etc/resolv.conf'
        target_resolvconf.write_text(resolvconf)
        # update the package lists
        self.chroot(['apt-get', '-y', 'update'])
        
        
    # common method for mounting /proc and /sys
    # here fs is either 'proc' or 'sys' or 'devpts'
    def _mount_target_virtfs(self, fs):
        fstype = dict(proc='proc', sys='sysfs', devpts='devpts')
        target = self.target / fs
        if fs == 'devpts':
            target = self.target / 'dev' / 'pts'
        if not target.isdir():
            self.log.info('creating %s' % target)
            target.mkdir()
        #cmd = 'mount -t %s none %s' % (fstype[fs], target)
        cmd = ['mount', '-t', fstype[fs], 'none', str(target)]
        runlog(cmd)
        
        
    def _umount_target_virtfs(self, fs):
        self.log.info('running umount for %s' % fs)
        # work around binfmt-support /proc locking
        # found this idea while messing around in live-helper
        target = self.target / fs
        if fs == 'proc':
            binfmt_misc = self.target / 'proc/sys/fs/binfmt_misc'
            status = binfmt_misc / 'status'
            if status.exists():
                self.log.info('Unmounting /proc/sys/fs/binfmt_misc in chroot')
                #cmd = 'umount %s' % binfmt
                cmd = ['umount', str(binfmt_misc)]
                runlog(cmd)
            # hack to stop mdadm on target
            mdstat = self.target / 'proc/mdstat'
            if mdstat.isfile():
                mdadm_initscript = self.target / 'etc/init.d/mdadm'
                if mdadm_initscript.isfile():
                    self.log.info("Stopping mdadm from running on target.")
                    cmd = ['chroot', self.target, '/etc/init.d/mdadm', 'stop']
                    runlog(cmd)
        if fs == 'devpts':
            target = self.target / 'dev' / 'pts'
        #cmd = 'umount %s' % target
        cmd = ['umount', str(target)]
        runlog(cmd)
        
    def _target_proc_mounted(self):
        testfile = self.target / 'proc/version'
        return testfile.isfile()

    def _target_sys_mounted(self):
        testdir = self.target / 'sys/kernel'
        return testdir.isdir()
    
    def mount_target_proc(self):
        self.check_bootstrap()
        self._mount_target_virtfs('proc')

    def mount_target_sys(self):
        self.check_bootstrap()
        self._mount_target_virtfs('sys')

    def mount_target_devpts(self):
        self.check_bootstrap()
        self._mount_target_virtfs('devpts')
        
    def umount_target_proc(self):
        self.check_target_proc_mounted()
        self._umount_target_virtfs('proc')

    def umount_target_sys(self):
        self.check_target_sys_mounted()
        self._umount_target_virtfs('sys')

    def umount_target_devpts(self):
        self._umount_target_virtfs('devpts')
        
    def install(self):
        self.check_target_proc_mounted()
        self.check_target_sys_mounted()
        self.check_installer_set()
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
    

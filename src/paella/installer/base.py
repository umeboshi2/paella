import os
from os.path import isdir, isfile, join, basename, dirname

from useless.base import Log, Error
from useless.base.config import Configuration
from useless.base.util import ujoin, makepaths, runlog
from useless.base.objects import Parser

from useless.db.midlevel import Environment

from paella.debian.base import debootstrap

from paella.base import PaellaConfig
from paella.db import PaellaConnection, DefaultEnvironment
from paella.db.base import get_traits, get_suite


class InstallError(SystemExit):
    pass

class InstallSetupError(InstallError):
    pass

class InstallerConnection(PaellaConnection):
    """force the connection to be the paella user"""
    def __init__(self, cfg=None):
        if cfg is None:
            cfg = PaellaConfig()
        dsn = cfg.get_dsn()
        # enforce user to be paella
        dsn['dbusername'] = 'paella'
        PaellaConnection.__init__(self, dsn)
        print 'installer connection made'


class CurrentEnvironment(Environment):
    def __init__(self, conn, hostname):
        Environment.__init__(self, conn, 'current_environment', 'hostname')
        self.set_main(hostname)
        
    
class BaseProcessor(object):
    def __init__(self):
        self._processes = []
        self._process_map = {}
        
    def append_process(self, name, function):
        if name not in self._processes:
            self._processes.append(name)
            self._process_map[name] = function
        else:
            raise ValueError, '%s is already in process list' % name

    def run_all_processes(self):
        self.log_all_processes_started()
        for procname in self._processes:
            self.run_process(procname)
        self.log_all_processes_finished()

    def run_process(self, procname):
        self.pre_process(procname)
        script = self.make_script(procname)
        if script is None:
            self.log_script_not_present(procname)
            if procname in self._process_map:
                self.log_process_started(procname)
                self._process_map[procname]()
                self.log_process_finished(procname)
            else:
                self.log_process_unmapped(procname)
        else:
            self.log_script_started(procname)
            self.run_process_script(procname, script)
            self.log_script_finished(procname)
        self.post_process(procname)

    # define this in a subclass if there is something to do
    # before running particular processes.
    # Ex: if procname = 'bootstrap':
    #          self.make_target_directory_exist()
    def pre_process(self, procname):
        pass

    # define this in a subclass if there is something to do
    # after running particular processes.
    # Ex: if procname = 'install':
    #          self.remove_excess_cruft()
    def post_process(self, procname):
        pass
    
    # This method is responsible for creating a script
    # for the procname (if one exists). None is returned if
    # there is no script to be made, else a filename for the script.
    # This needs to be implemented in a subclass.
    def make_script(self, procname):
        raise NotImplementedError, '_make_script not implemented in BaseProcessor'

    # below are logging methods that should be overridden in subclasses

    def log_all_processes_started(self):
        self.log.info('Starting all processes')
        
    def log_all_processes_finished(self):
        self.log.info('Finished all processes')

    def log_process_started(self, procname):
        self.log.info('Starting %s process' % procname)

    def log_process_finished(self, procname):
        self.log.info('Finished %s process' % procname)

    def log_script_not_present(self, procname):
        self.log.info('Script not present for process %s' % procname)

    def log_script_started(self, procname):
        self.log.info('Running script for process %s' % procname)

    def log_script_finished(self, procname):
        self.log.info('Finished script for process %s' % procname)

    def log_process_unmapped(self, procname):
        self.log.info('Process %s has no entry in the process map' % procname)

class BaseInstaller(BaseProcessor):
    def __init__(self, conn):
        self.conn = conn
        self.target = None
        self.defenv = DefaultEnvironment(self.conn)
        #check for default environment
        rows = self.defenv.cursor.select()
        if not len(rows):
            raise InstallSetupError, 'There is no data in the default_environment table'
        
    def set_target(self, target):
        self.target = target
        self.paelladir = os.path.join(target, 'root/paella')
        os.environ['PAELLA_TARGET'] = target
        

class Installer(object):
    def __init__(self, conn):
        object.__init__(self)
        self.conn = conn
        self.target = None
        self.defenv = DefaultEnvironment(self.conn)
        #check for default environment
        rows = self.defenv.cursor.select()
        if not len(rows):
            raise InstallSetupError, 'There is no data in the default_environment table'
        
    def set_logfile(self, logfile=None):
        env = os.environ
        if logfile is None:
            if env.has_key('PAELLA_LOGFILE'):
                self.logfile = env['PAELLA_LOGFILE']
            elif env.has_key('LOGFILE'):
                self.logfile = env['LOGFILE']
            elif self.defenv.has_option('installer', 'default_logfile'):
                self.logfile = self.defenv.get('installer', 'default_logfile')
            else:
                raise InstallSetupError, 'There is no log file defined, giving up.'
        else:
            self.logfile = logfile
        logdir = os.path.dirname(self.logfile)
        if logdir:
            makepaths(os.path.dirname(self.logfile))
        format = '%(name)s - %(asctime)s - %(levelname)s: %(message)s'
        self.log = Log('paella-installer', self.logfile, format)
        bkup = '%s.bkup' % self.logfile
        if not os.path.exists(bkup):
            os.link(self.logfile, bkup)
        
        
    def set_target(self, target):
        self.target = target
        self.paelladir = os.path.join(target, 'root/paella')
        os.environ['PAELLA_TARGET'] = target
        
    def command(self, command, args='', chroot=True):
        cmd = '%s %s' % (command, args)
        if chroot:
            return 'chroot %s %s' % (self.target, cmd)
        else:
            return cmd
        
    def with_proc(self, command, args=''):
        mount = 'mount -t proc proc /proc;\n'
        umount = 'umount /proc;\n'
        cmd = '%s %s\n' % (command, args)
        return self.command("bash -c '%s'" % ''.join([mount, cmd, umount]))

    def run(self, name, command, args='', proc=False, destroylog=False,
            chroot=True, keeprunning=False):
        if not chroot and proc:
            raise InstallError, 'bad options, cannot mount proc with no_chroot'
        if proc:
            cmd = self.with_proc(command, args=args)
        else:
            cmd = self.command(command, args=args, chroot=chroot)
        runvalue = runlog(cmd, destroylog=destroylog,
                          keeprunning=keeprunning)
        return runvalue
    
class Modules(list):
    def __init__(self, path):
        list.__init__(self)
        self.path = path
        self.lines = [l.strip() for l in file(self.path).readlines()]
        self.__rebuild_modules__()
        
    def __rebuild_modules__(self):
        del self[:]
        for line in self.lines:
            if line and line[0] != '#':
                list.append(self, line)

    def append(self, module):
        if module not in self:
            self.lines.append(module)
            self.__rebuild_modules__()

    def write(self, path=None):
        if path is None:
            path = self.path
        mfile = file(path, 'w')
        mfile.write('\n'.join(self.lines) + '\n')
        mfile.close()
        
            

class BaseChrootInstaller(Installer):
    def __init__(self, conn, installer=None):
        Installer.__init__(self, conn)
        self._bootstrapped = False
        self.installer = installer
        self.debmirror = self.defenv.get('installer', 'http_mirror')
        
    def _make_target_dir(self, target):
        makepaths(target)
        
    def _check_target(self):
        if self.target is None:
            raise InstallError, 'no target specified'

    def _check_target_exists(self):
        self._check_target()
        if not isdir(self.target):
            self._make_target_dir(self.target)
        if not isdir(self.target):
            raise InstallError, 'unable to create target directory %s' % self.target
        
    def _check_installer(self):
        if self.installer is None:
            raise InstallError, 'no installer available'

    def _check_bootstrap(self):
        self._check_target_exists()
        if not self._bootstrapped:
            raise InstallError, 'target not bootstrapped'

    def _check_target_proc(self):
        if not self._proc_mounted:
            raise InstallError, 'target /proc not mounted'
        
    def _extract_base_tarball(self, suite):
        self._check_target_exists()
        runlog('echo extracting premade base tarball')
        suite_path = self.defenv.get('installer', 'suite_storage')
        basefile = join(suite_path, '%s.tar' % suite)
        runvalue = runlog('tar -C %s -xf %s' % (self.target, basefile))
        if runvalue:
            raise InstallError, 'problems extracting %s' % basefile
        else:
            self._bootstrapped = True

    def _bootstrap_target(self):
        self._check_installer()
        if self.defenv.is_it_true('installer', 'bootstrap_target'):
            mirror = self.debmirror
            suite = self.suite
            self._run_bootstrap(mirror, suite)
        else:
            suite = self.suite
            self._extract_base_tarball(suite)

    def _mount_target_proc(self):
        self._check_bootstrap()
        tproc = join(self.target, 'proc')
        cmd = 'mount --bind /proc %s' % tproc
        runvalue = runlog(cmd)
        if runvalue:
            raise InstallError, 'problem mounting target /proc at %s' % tproc
        else:
            self._proc_mounted = True

    def _umount_target_proc(self):
        self._check_target_proc()
        tproc = join(self.target, 'proc')
        cmd = 'umount %s' % tproc
        runvalue = runlog(cmd)
        if runvalue:
            raise InstallError, 'problem unmounting target /proc at %s' % tproc
        else:
            self._proc_mounted = False
            
    def _run_bootstrap(self, mirror, suite):
        self._check_target_exists()
        runvalue = runlog(debootstrap(suite, self.target, mirror))
        if runvalue:
            raise InstallError, 'bootstrapping %s on %s failed.' % (suite, self.target)
        else:
            self._bootstrapped = True
    
if __name__ == '__main__':
    from useless.db.midlevel import StatementCursor
    from useless.db.midlevel import Environment, TableDict
    c = PaellaConnection()

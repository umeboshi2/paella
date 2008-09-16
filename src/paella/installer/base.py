import os, sys
from os.path import isdir, isfile, join, basename, dirname
import subprocess
import warnings
import logging

from useless import deprecated
from useless.base import Log
from useless.base.config import Configuration
from useless.base.util import ujoin, makepaths
from useless.base.objects import Parser
from useless.base.path import path

from useless.db.midlevel import Environment

from paella.debian.base import debootstrap

from paella.base import PaellaConfig
from paella.db import PaellaConnection, DefaultEnvironment
from paella.db.base import get_traits, get_suite
from paella.db.base import SuiteCursor

from util.aptsources import make_sources_list
from util.aptsources import make_official_sources_list


def makePaellaLogger(name, filename=None, logformat='',
                 host=None, port=None, url='', method='GET', syslog=False):
    log = logging.getLogger(name)
    handler = None
    if filename is not None:
        handler = logging.FileHandler(filename)
    if syslog:
        if host is not None:
            if port is None:
                port = 514
            handler = logging.handlers.SysLogHandler((host, port))
        else:
            handler = logging.handlers.SysLogHandler()
    if handler is None:
        if host is not None:
            if port is not None:
                handler = logging.handlers.SocketHandler(host, port)
            elif url:
                handler = logging.handlers.HTTPHandler(host, url, method)
            else:
                raise RuntimeError , "unable to make handler for host %s" % host
    if handler is None:
        raise RuntimeError , "bad options, unable to make handler"
    if not logformat:
        logformat = '%(name)s - %(asctime)s - %(levelname)s: %(message)s'
    formatter = logging.Formatter(logformat)
    handler.setFormatter(formatter)
    log.addHandler(handler)
    # we should pass the level, too
    log.setLevel(logging.DEBUG)
    return log


# using StandardError temporarily now
class NoLogError(StandardError):
    pass

class RunLogError(OSError):
    pass

class InvalidSuiteError(ValueError):
    pass


class RunLogWarning(Warning):
    pass

warnings.simplefilter('always', RunLogWarning)


class MainLog(object):
    def __init__(self, filename=None, logformat='',
                 host=None, port=None, url='', method='GET', syslog=False):
        self.filename = filename
        if self.filename is not None:
            self.filename = path(self.filename)
        self.host = host
        self.port = port
        self.url = url
        self.http_method = method
        self.syslog = syslog
        self.loggers = {}
        if not logformat:
            logformat = '%(name)s - %(asctime)s - %(levelname)s: %(message)s'
        self.main_logformat = logformat

    def add_logger(self, name, logformat=''):
        if not logformat:
            logformat = self.main_logformat
        self.loggers[name] = makePaellaLogger(name, filename=self.filename,
                                              logformat=logformat, host=self.host, port=self.port,
                                              url=self.url, method=self.http_method,
                                              syslog=self.syslog)

    def info(self, name, msg):
        self.loggers[name].info(msg)

    def warn(self, name, msg):
        self.loggers[name].warn(msg)
        
        
class PaellaLogger(MainLog):
    def __init__(self, filename=None, logformat='',
                 host=None, port=None, url='', method='GET',
                 syslog=False):
        MainLog.__init__(self, filename=filename, logformat=logformat,
                         host=host, port=port, url=url, method=method,
                         syslog=syslog)
        if self.filename is not None:
            os.environ['PAELLA_LOGFILE'] = str(self.filename.abspath())
            logdir = self.filename.abspath().dirname()
            if not logdir.isdir():
                makepaths(logdir)
        self._basename = 'paella-installer'
        self.add_logger(self._basename)
        sys.paella_logger = self.loggers[self._basename]
        


    def info(self, msg, name=''):
        if not name:
            name = self._basename
        MainLog.info(self, name, msg)
        
    def warn(self, msg, name=''):
        if not name:
            name = self._basename
        MainLog.warn(self, name, msg)
        

# I've added some ugly looking warning code here
# to help clean up previously bad ideas on how to use
# this function
def runlog(cmd, logfile=None, logobject=None, failure_suppressed=False):
    kw = dict(stderr=subprocess.STDOUT, shell=True)
    # make a list of stacklevels
    # this is temporary, until we determine the best levels to
    # capture
    stacklevels = range(1,5)
    if logobject is None:
        if logfile is not None:
            output = file(logfile, 'a')
            kw['stdout'] = output
        else:
            logger = sys.paella_logger
            stream = logger.handlers[0].stream
            kw['stdout'] = stream
    else:
        kw['stdout'] = logobject.handlers[0].stream
    if type(cmd) is list:
        kw['shell'] = False
    elif type(cmd) in [str, unicode, path]:
        # Trying to keep from using the shell for the command
        # since that's a good way for malicious things to happen.
        for stacklevel in stacklevels:
            msg = "StackLevel %d: passing strings to runlog is deprecated" % stacklevel
            warnings.warn(msg, RunLogWarning, stacklevel=stacklevel)
    else:
        raise RunLogError, "unknown command type"
    retval = subprocess.call(cmd, **kw)
    if failure_suppressed:
        # we need to raise a warning about using failure_suppressed
        # we'll eventually determine all the code that passes this arg,
        # and replace them with try: runlog except: RunLogError ,
        # so we can always raise RunLogError on a non-zero return from
        # the subprocess call
        for stacklevel in stacklevels:
            msg = "StackLevel %d: failure_suppressed is true" % stacklevel
            warnings.warn(msg, RunLogWarning, stacklevel=stacklevel)
    if retval and not failure_suppressed:
        raise RunLogError, 'command %s return exit code %d' % (cmd, retval)
    return retval

        
class BaseInstallError(StandardError):
    pass

class InstallError(BaseInstallError):
    pass

class InstallSetupError(BaseInstallError):
    pass

class DefaultEnvironmentError(InstallSetupError):
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
        

# the new process based installers are below here
# --------------------------------------------------------------------

class BaseProcessor(object):
    "All the paella installers inherit from this class"
    def __init__(self):
        self._processes = []
        self._process_map = {}
        self.current = None

    def insert_process(self, index, name, function):
        if name not in self._processes:
            self._processes.insert(insert, name)
            self._process_map[name] = function
        else:
            raise ValueError, '%s is already in process list' % name
        
    def append_process(self, name, function):
        if name not in self._processes:
            self._processes.append(name)
            self._process_map[name] = function
        else:
            raise ValueError, '%s is already in process list' % name

    def run_all_processes(self):
        self.log_all_processes_started()
        for procname in self._processes:
            self.current = procname
            self.run_process(procname)
        self.log_all_processes_finished()
        self.current = None
        
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
        raise NotImplementedError, 'make_script not implemented in BaseProcessor'

    def run_process_script(self, procname, script):
        retval = runlog([script])
        if retval:
            msg = "script for process %s exited with error code %d" % (procname, retval)
            raise RunLogError, msg
        
    # below are logging methods that should be overridden in subclasses

    def log_all_processes_started(self):
        self.log.info('Starting all processes for %s' % self.__class__.__name__)
        
    def log_all_processes_finished(self):
        self.log.info('Finished all processes for %s' % self.__class__.__name__)

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

# This is the basic installer here
# It should replace the BaseChrootInstaller below

class BaseInstaller(BaseProcessor):
    def __init__(self, conn):
        BaseProcessor.__init__(self)
        self.conn = conn
        self.target = None
        self.suite = None
        self.base_suite = None
        self.defenv = DefaultEnvironment(self.conn)
        # an attribute for the child installer
        self.installer = None
        # check for default environment
        rows = self.defenv.cursor.select()
        if not len(rows):
            msg = 'There is no data in the default_environment table'
            raise DefaultEnvironmentError, msg

    def set_suite(self, suite):
        suites = self.conn.suitecursor.get_suites()
        if suite not in suites:
            raise InvalidSuiteError, "%s is an invalid suite." % suite
        self.suite = suite
        self.base_suite = self.conn.suitecursor.get_base_suite(suite)
        
    def set_target(self, target):
        self.target = path(target)
        self.paelladir = self.target / 'root/paella'
        os.environ['PAELLA_TARGET'] = self.target

    def create_target_directory(self):
        if not self.target.isdir():
            makepaths(self.target)
        if not self.target.isdir():
            raise InstallError, 'unable to create target directory %s' % self.target

    def set_logger(self, filename=None, host=None, port=None,
                   url='', method='GET', syslog=False):
        self.mainlog = PaellaLogger(filename=filename, host=host,
                                    port=port, url=url, method=method, syslog=syslog)
        name = self.__class__.__name__
        self.mainlog.add_logger(name)
        self.log = self.mainlog.loggers[name]
        
    def set_logfile(self, logfile):
        deprecated("set_logfile is deprecated, use set_logger instead")
        self.set_logger(filename=logfile)
        self.logfile = path(logfile)
        
        # the mailserver trait used to somehow erase the logfile
        # so a bkup is generated here.
        # Come to think of it, it also erased the backup file also
        # I guess the hard link wasn't sufficient to keep this from
        # happening.  This problem existed in sarge and seemed
        # to happen while installing the uw-imapd package.
        # If this happens in the future, I'll start making actual
        # copies of the log at the end of each trait (or even at
        # the end of each trait process to narrow it down further)
        # I'm leaving the comments here as a record to to the
        # the curious
        #bkup = self.logfile + '.bkup'
        #if not bkup.exists():
        #    self.logfile.link(bkup)
        
    # helper to run commands in a chroot on the target
    def chroot(self, command):
        if type(command) is list:
            return runlog(['chroot', str(self.target)] + command)
        else:
            return runlog('chroot %s %s' % (self.target, command))

if __name__ == '__main__':
    from paella.db import PaellaConnection
    c = PaellaConnection()
    #log = PaellaLogger(host='127.0.0.1', port=2345)
    bi = BaseInstaller(c)

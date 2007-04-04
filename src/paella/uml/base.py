import os, sys
from os.path import isfile, join, dirname
import subprocess
import tarfile

from useless.base.util import makepaths
from useless.base.tarball import make_tarball
from useless.base.config import Configuration, list_rcfiles
from useless.base.path import path

from paella.debian.base import RepositorySource, debootstrap
from paella.db.base import get_suite
from paella.installer.util.filesystem import mount_tmpfs

class UmlModeError(RuntimeError):
    pass

class WrongModeError(UmlModeError):
    pass

class UndefinedModeError(UmlModeError):
    pass

class UmlConfig(Configuration):
    def __init__(self, section='umlmachines',
                 files=list_rcfiles('umlmachines.conf')):
        if section is None:
            section = 'database'
        Configuration.__init__(self, section=section, files=files)

    def list_rcfiles(self):
        return list_rcfiles('umlmachines.conf')
    

    def get_umlopts(self):
        pre = 'uopt_'
        uopt_keys = [x for x in self.keys() if x[:5] == pre]
        
        #return dict([(x.split(pre)[1], self[x]) for x in uopt_keys])
        opts = {}
        for k in uopt_keys:
            optkey = k.split(pre)[1]
            if optkey.startswith('ubd') or optkey in ['python_path', 'umlconfig', 'LOGFILE']:
                value = path(self[k]).expand()
            else:
                value = self[k]
            opts[optkey] = value
        return opts

    def list_machines(self):
        sections = [s for s in self.sections() if s != 'umlmachines' ]
        return sections

    # returns a list of (option, value) items
    # that have been changed from the defaults
    def nondefault_items(self, section):
        items = self.items(section)
        default_items = self.items('DEFAULT')
        defaults = dict(default_items)
        changed = dict()
        for k, v in items:
            if not k.startswith('_'):
                if k not in defaults:
                    changed[k] = v
                else:
                    if defaults[k] != v:
                        changed[k] = v
        return changed.items()
    
    
class Option(object):
    def __init__(self, name, value):
        str.__init__(self)
        self.name = name
        self.value = value
        x = True
        y = False
        
    def __repr__(self):
        return '%s=%s' % (self.name, self.value)

    def __str__(self):
        return '%s=%s' % (self.name, self.value)

class Options(object):
    def __init__(self):
        self._dict = {}

    def __setitem__(self, key, value):
        self._dict[key] = Option(key, value)

    def __getitem__(self, key):
        return self._dict[key]

    def __repr__(self):
        return ' '.join(map(str, self._dict.values()))

    def __str__(self):
        return ' '.join(map(str, self._dict.values()))
    
    def items(self):
        return self._dict.values()

    def values(self):
        return [v.value for v in self._dict.values()]

    def keys(self):
        return self._dict.keys()

    def update(self, data):
        for key, value in data.items():
            self._dict[key] = Option(key, value)

    def clear(self):
        self._dict.clear()
    
# here is where we start requiring python 2.4
# here we make some method decorators for
# checking host/guest mode
def guest_mode(func):
    def wrapper(self, *args, **kw):
        if self.mode != 'guest':
            raise WrongModeError, 'Need to be in guest mode.'
        return func(self, *args, **kw)
    return wrapper

def host_mode(func):
    def wrapper(self, *args, **kw):
        if self.mode != 'host':
            raise WrongModeError, 'Need to be in host mode.'
    
        return func(self, *args, **kw)
    return wrapper

class Uml(object):
    def __init__(self):
        object.__init__(self)
        self.mode = 'host'
        self.options = Options()

    def command(self):
        return self._cmd_()
    
    def _cmd_(self):
        return 'linux %s' % self.options

    def __repr__(self):
        return self._cmd_()

    def __str__(self):
        return self._cmd_()

    def set_mode(self, mode):
        if mode not in ['host', 'guest']:
            raise UndefinedModeError, 'unknown mode %s' % mode
        self.mode = mode
        # if in guest mode, reset options from /proc/cmdline
        if mode == 'guest':
            # we depend on paella-init to set sys.kernopts
            kernopts = sys.kernopts
            self.options.update(kernopts)
        
    # the popen and use_pipe will probably be removed later
    # popen is now ignored use call parameter
    @host_mode
    def run_uml(self, popen=False, use_pipe=False,
                call=False, stdout=None, stderr=None):
        cmd = str(self)
        print 'cmd ->', cmd
        if call:
            print 'calling cmd'
            return subprocess.call(cmd, shell=True)
        if stderr is None:
            #stderr = subprocess.STDOUT
            pass
        if stdout is None:
            if use_pipe:
                stdout = subprocess.PIPE
        args = dict(shell=False, close_fds=True, stderr=stderr)
        # test stdout to logfile
        test_logfile = False
        if test_logfile:
            logfile = os.environ['LOGFILE']
            if os.path.exists(logfile):
                mode = 'a+'
            else:
                mode = 'w'
            debug('mode', mode)
            stdout = file(logfile, mode)
        # done testing stdout to logfile
        if stdout is not None:
            args['stdout'] = stdout
        print 'using popen', stdout
        # try to run cmd in background
        self.run_process = subprocess.Popen(cmd.split(), **args)
        return self.run_process
            
    @guest_mode
    def _init_uml_system(self):
        print 'initializing uml system'
        for target in ['/tmp', '/dev']:
            mount_tmpfs(target=target)
        # we need something better here
        os.system('mknod /dev/null c 1 3')
        os.system('mknod /dev/ubda b 98 0')
        os.system('mknod /dev/ubdb b 98 16')

if __name__ == '__main__':
    u = Uml()
    

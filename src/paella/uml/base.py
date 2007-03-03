import os
from os.path import isfile, join, dirname
import subprocess
import tarfile

from useless.base.util import makepaths
from useless.base.tarball import make_tarball
from useless.base.config import Configuration, list_rcfiles


from paella.debian.base import RepositorySource, debootstrap
from paella.db.base import get_suite
from paella.installer.util.filesystem import mount_tmpfs

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
            opts[k.split(pre)[1]] = self[k]
        return opts

    def list_machines(self):
        sections = [s for s in self.sections() if s != 'umlmachines' ]
        return sections

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
            raise RuntimeError, 'unknown mode %s' % mode
        self.mode = mode

    def check_guest(self):
        if self.mode != 'guest':
            raise RuntimeError, 'not in guest mode'

    def check_host(self):
        if self.mode != 'host':
            raise RuntimeError, 'not in host mode'
        
    # the popen and use_pipe will probably be removed later
    # popen is now ignored use call parameter
    def run_uml(self, popen=False, use_pipe=False,
                call=False, stdout=None, stderr=None):
        self.check_host()
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
        args = dict(shell=True, close_fds=True, stderr=stderr)
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
        self.run_process = subprocess.Popen(cmd, **args)
        return self.run_process
            
    def _init_uml_system(self):
        self.check_guest()
        print 'initializing uml system'
        for target in ['/tmp', '/dev']:
            mount_tmpfs(target=target)
        # we need something better here
        os.system('mknod /dev/null c 1 3')
        os.system('mknod /dev/ubd0 b 98 0')
        os.system('mknod /dev/ubd1 b 98 16')

        

if __name__ == '__main__':
    pass

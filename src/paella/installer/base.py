import os
from os.path import isdir, isfile, join, basename, dirname

from useless.base import Log
from useless.base.config import Configuration
from useless.base.util import ujoin, makepaths, runlog
from useless.base.objects import Parser

from useless.db.midlevel import Environment

from paella.debian.base import debootstrap
from paella.profile.base import get_traits, get_suite, PaellaConnection, PaellaConfig
from paella.profile.base import DefaultEnvironment
from paella.profile.trait import TraitParent, TraitPackage


class InstallerConnection(PaellaConnection):
    def __init__(self, cfg=None):
        if cfg is None:
            cfg = PaellaConfig()
        dsn = cfg.get_dsn()
        dsn['dbusername'] = 'paella'
        PaellaConnection.__init__(self, dsn)
        print 'installer connection made'


class CurrentEnvironment(Environment):
    def __init__(self, conn, hostname):
        Environment.__init__(self, conn, 'current_environment', 'hostname')
        self.set_main(hostname)
        
    

class Installer(object):
    def __init__(self, conn, cfg=None):
        object.__init__(self)
        self.conn = conn
        self.target = None
        self.cfg = cfg
        self.defenv = DefaultEnvironment(self.conn)
        #check for default environment
        rows = self.defenv.cursor.select()
        if not len(rows):
            raise Error, 'There is no data in the default_environment table'
        self.set_logfile('_unused_')

    def set_logfile(self, logfile):
        self.logfile = os.environ['LOGFILE']
        makepaths(os.path.dirname(self.logfile))
        format = '%(name)s - %(asctime)s - %(levelname)s: %(message)s'
        self.log = Log('paella-installer', self.logfile, format)
        
    def set_target(self, target):
        self.target = target
        self.paelladir = os.path.join(target, 'root/paella')
        
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
            raise Error, 'bad options, cannot mount proc with no_chroot'
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
        
            
              
if __name__ == '__main__':
    from useless.db.midlevel import StatementCursor
    from useless.db.midlevel import Environment, TableDict
    c = PaellaConnection()
    tp = TraitParent(c, 'woody')
    pp = TraitPackage(c, 'woody')
    ct = ConfigTemplate()
    path = '/tmp/spam.db'
    db = bsddb.btopen('path', 'c')
    p = Parser('var-table.csv')
    

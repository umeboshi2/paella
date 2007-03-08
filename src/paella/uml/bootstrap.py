import os
from os.path import isfile, join, dirname

from useless.base.util import makepaths

from paella.debian.base import debootstrap, Debootstrap
from paella.installer.util.misc import remove_debs

from paella.installer.util.filesystem import make_filesystem

from base import UmlConfig
from base import guest_mode
from util import create_sparse_file
from chroot import UmlChroot

class UmlBootstrapper(UmlChroot):
    def __init__(self, suite, rootimage=None, cfg=None):
        if rootimage is None:
            rootimage = suite + '.base'
        if cfg is None:
            cfg = UmlConfig()
        UmlChroot.__init__(self, cfg)
        self.set_targetimage(rootimage)
        o = self.options
        o['paellasuite'] = suite
        o['paella_action'] = 'bootstrap'

    @guest_mode
    def bootstrap(self):
        suite = self.options['paellasuite'].value
        script = ''
        if 'bootstrap_script' in self.options.keys():
            script = self.options['bootstrap_script'].value
        if 'bootstrap_mirror' in self.options.keys():
            mirror = self.options['bootstrap_mirror'].value
        else:
            mirror = self.cfg.get('umlmachines', 'bootstrap_debmirror')
        bs = Debootstrap(suite=suite, root=self.target, mirror=mirror, script=script)
        bs.exclude.append('pcmcia-cs')
        self.make_filesystem()
        self.mount_target()
        print 'mirror is', bs.mirror
        print 'command is', bs.command()
        print 'script is', bs.script
        os.system(bs.command())
        remove_debs(self.target)
        
def make_base_filesystem(suite, name, cfg=None, size=3000, mkfs='mke2fs'):
    if cfg is None:
        cfg = UmlConfig()
    path = join(cfg.get('umlmachines', 'bootstrap_basepath'), name)
    makepaths(dirname(path))
    create_sparse_file(path, size=size)
    return path

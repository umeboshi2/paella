import os
from os.path import isfile, join, dirname

from useless.base.util import makepaths
from paella.debian.base import debootstrap, Debootstrap
from paella.installer.util import remove_debs

from base import UmlConfig
from util import mkrootfs, create_sparse_file
from chroot import UmlChroot

class UmlBootstrapper(UmlChroot):
    def __init__(self, suite, rootimage=None, cfg=None):
        if rootimage is None:
            rootimage = suite + '.base'
        if cfg is None:
            cfg = PaellaConfig()
        UmlChroot.__init__(self, cfg)
        self.set_targetimage(rootimage)
        o = self.options
        o['paellasuite'] = suite
        o['paella_action'] = 'bootstrap'

    def make_filesystem(self):
        # guest mode method
        self.check_guest()
        # this function needs to be removed
        mkrootfs()
        
    def bootstrap(self):
        # guest mode method
        self.check_guest()
        suite = self.options['paellasuite'].value
        mirror = self.cfg.get('umlmachines', 'bootstrap_debmirror')
        bs = Debootstrap(suite, self.target, mirror)
        bs.exclude.append('pcmcia-cs')
        self.make_filesystem()
        self.mount_target()
        print 'mirror is', bs.mirror
        print 'command is', bs.command()
        os.system(bs.command())
        remove_debs(self.target)
        


def bootstrap_base(suite, path, cfg=None, size=3000, mkfs='mke2fs'):
    cfg = UmlConfig()
    makepaths(dirname(path))
    create_sparse_file(path, size=size)
    uml = UmlBootstrapper(suite, path, cfg=cfg)
    uml.run_uml()
    

def make_base_filesystem(suite, name, cfg=None, size=3000, mkfs='mke2fs'):
    path = join(cfg.get('umlmachines', 'bootstrap_basepath'), name)
    bootstrap_base(suite, path, cfg=cfg, size=size, mkfs=mkfs)
    
def make_base(suite, cfg=None):
    make_base_filesystem(suite, suite + '.base', cfg=cfg)
    
    
def make_bases():
    for s in ['woody', 'sarge', 'sid']:
        make_base_filesystem(s, s + '.base')


import os
from os.path import join, dirname

from umlrun import UML
from paella.base.config import Configuration
from paella.base.util import runlog
from paella.installer.base import InstallerConnection
from paella.profile.base import PaellaConfig

from base import Uml, UmlConfig
from util import create_sparse_file
from chroot import UmlChroot
from installer import UmlInstaller


class UmlRunner(Uml):
    def __init__(self, cfg=None):
        Uml.__init__(self)
        self.uml = UML()
        self.cfg = cfg
        self.options.update(self.cfg.get_umlopts())
        
    def set(self, machine):
        self.cfg.change(machine)
        self.options['umlmachine'] = machine
        self.options['umid'] = machine
        self.options.update(self.cfg.get_umlopts())
        self.options['ubd0'] = self.cfg['basefile']
        

    def run(self, oldway=True):
        if not oldway:
            self.uml.start(map(str, self.options.items()), 1, 30, False)
        else:
            os.system(str(self))
            
    def command(self, command):
        self.uml.shellcommand(command)
    
def backup(machine):
    cfg = UmlConfig(machine)
    basefile = cfg['basefile']
    backup = UmlChroot(cfg)
    backup.set_targetimage(basefile)
    backup.options['backup_target'] = machine
    backup.options['paella_action'] = 'backup'
    backup.run_uml()
    
def install(machine, backup_=False, basefile=None):
    cfg = UmlConfig(machine)
    ui = UmlInstaller(cfg=cfg)
    u = UmlRunner(cfg)
    if basefile is None:
        basefile = cfg['basefile']
    ui.install_profile(cfg['profile'], basefile)
    if backup_:
        backup(machine)
    u.set(machine)
    return u

def restore(machine, basefile=None):
    raise Error, 'need to fix me'
    cfg = PaellaConfig()
    umcfg = get_machines_config(machine)
    conn = InstallerConnection(cfg)
    ui = UmlInstaller(conn, umcfg)
    if basefile is None:
        basefile = join(umcfg['base_path'], umcfg['basefile'])
    ui.restore_profile(machine, basefile)
    
def run(machine, init=None):
    cfg = UmlConfig(machine)
    u = UmlRunner(cfg)
    u.set(machine)
    if init is not None:
        u.options['init'] = init
    u.run()

def make_diskless(machine):
    umcfg = get_machines_config(machine)
    u = UmlRunner(umcfg)
    u.set(machine)
    u.run(oldway=False)
    u.command('mount paella:%s /mnt -o nolock' %umcfg['bkuptarball_path'])
    u.command('bash -c "cat /mnt/sid.base.tar | gzip >  /home/base.tgz"')
    u.command('apt-get -d install diskless-image-simple')
    u.command('umount /mnt')
    u.uml.shutdown()
    
def build(package, machine='sbuild'):
    umcfg = get_machines_config(machine)
    u = UmlRunner(umcfg)
    u.set(machine)
    u.run(oldway=False)
    u.command('apt-get -y update')
    u.command('apt-get build-depends %s' % package)
    u.command('apt-get source %s' % package)
    u.uml.shutdown()


def extract(tarball, basefile=None, size=None):
    cfg = UmlConfig()
    u = UmlChroot(cfg)
    u.options['paella_system_tarball'] = tarball
    u.options['paella_action'] = 'extract'
    u.options['devfs'] = 'mount'
    u.set_targetimage(basefile)
    if size is None:
        size = cfg['basefile_size']
    create_sparse_file(basefile, size=size)
    u.run_uml()
    

if __name__ == '__main__':
    umcfg = Configuration(files=Configuration('umlmachines')['uml_machines_conf'])
    u = UmlRunner(umcfg)
    import sys
    if len(sys.argv) > 1:
        run(sys.argv[1])
        

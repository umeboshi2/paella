import os
from os.path import join, dirname
import subprocess

from umlrun import UML
from useless.base.config import Configuration
from useless.base.util import runlog

from paella.base import PaellaConfig
from paella.installer.base import InstallerConnection

from base import Uml, UmlConfig
from util import create_sparse_file
from chroot import UmlChroot
from installer import UmlInstaller

class MachineUnsetError(StandardError):
    pass

class UmlMachineManager(Uml):
    def __init__(self, cfg):
        Uml.__init__(self)
        self.cfg = cfg
        self.cfg.change('umlmachines')
        self.options.update(self.cfg.get_umlopts())
        self.current = None
        self.run_process = None

    def _check_current(self):
        if self.current is None:
            raise MachineUnsetError, 'Set a machine in UmlMachineManager'

    def _make_config(self, machine):
        return UmlConfig(machine)
    
    def set_machine(self, machine):
        self.cfg.change(machine)
        self.current = machine
        self.options['umlmachine'] = machine
        self.options['umid'] = machine
        self.options.update(self.cfg.get_umlopts())
        self.set_root_filesystem(self.cfg['basefile'])
        
    def set_root_filesystem(self, basefile):
        self.options['ubd0'] = basefile

    def backup_machine(self, basefile=None):
        self._check_current()
        machine = self.current
        cfg = self._make_config(machine)
        chroot = UmlChroot(cfg)
        if basefile is None:
            basefile = cfg.get(machine, 'basefile')
        chroot.set_targetimage(basefile)
        chroot.options['backup_target'] = machine
        chroot.options['paella_action'] = 'backup'
        chroot.run_uml()

    def install_machine(self, backupalso=False, basefile=None, profile=None):
        self._check_current()
        machine = self.current
        cfg = self._make_config(machine)
        installer = UmlInstaller(cfg=cfg)
        installer.options['umlmachine'] = machine
        installer.options['umid'] = machine
        runner = UmlRunner(cfg)
        if basefile is None:
            basefile = cfg.get(machine, 'basefile')
        if profile is None:
            profile = cfg.get(machine, 'profile')
        installer.install_profile(profile, basefile)
        self.run_process = installer.run_process
        print 'self.run_process', self.run_process
        if backupalso:
            self.backup_machine(basefile=basefile)
        runner.set(machine)
        return runner

    def restore_machine(self, basefile=None, archive=None):
        pass

    def run_machine(self, init=None):
        self._check_current()
        machine = self.current
        cfg = self._make_config(machine)
        runner = UmlRunner(cfg)
        runner.set(machine)
        if init is not None:
            runner.options['init'] = init
        runner.run()
        
        
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
    ui.options['umlmachine'] = machine
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
        

import os
from os.path import join

from paella.base.config import Configuration

from paella.installer.base import InstallerConnection
from paella.installer.uml import UmlInstaller
from paella.installer.uml import UmlChroot
from paella.installer.uml import Uml

class UmlRunner(Uml):
    def __init__(self, cfg=None):
        Uml.__init__(self)
        self.cfg = cfg
        self.options['eth0'] = self.cfg['eth0']
        self.options['con'] = 'pts'
        self.options['con0'] = 'xterm'
        self.options['con1'] = self.cfg['con1']
        
        
    def set(self, machine):
        self.cfg.change(machine)
        self.options['ubd0'] = join(self.cfg['base_path'], self.cfg['basefile'])

    def run(self):
        os.system(str(self))
        
def install(machine):
    cfg = Configuration('umlchroot')
    conn = InstallerConnection(cfg)
    ui = UmlInstaller(conn, cfg)
    umcfg = Configuration(files=Configuration('umlmachines')['uml_machines_conf'])
    umcfg.change(machine)
    u = UmlRunner(umcfg)
    basefile = join(umcfg['base_path'], umcfg['basefile'])
    ui.install_profile(umcfg['profile'], basefile)
    u.set(machine)
    return u

    

if __name__ == '__main__':
    umcfg = Configuration(files=Configuration('umlmachines')['uml_machines_conf'])
    u = UmlRunner(umcfg)

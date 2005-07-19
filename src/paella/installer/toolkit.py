import os

from useless.base.util import RefDict, str2list

from paella.base import PaellaConfig
from paella.db import PaellaConnection, DefaultEnvironment
from paella.db.base import get_suite
from paella.db.trait import Trait
from paella.db.trait.relations import TraitParent
from paella.db.family import Family
from paella.db.profile import Profile
from paella.db.profile.main import ProfileEnvironment

from base import Modules
from util import setup_modules
from trait import TraitInstaller

class InstallerTools(object):
    def __init__(self):
        object.__init__(self)
        self.cfg = PaellaConfig()
        self.conn = PaellaConnection()
        self.profile = os.environ['PAELLA_PROFILE']
        self.target = os.environ['PAELLA_TARGET']
        self.machine = None
        self.trait = None
        self.suite = get_suite(self.conn, self.profile)
        self.pr = Profile(self.conn)
        self.pr.set_profile(self.profile)
        self.traitlist = self.pr.make_traitlist()
        self.pe = ProfileEnvironment(self.conn, self.profile)
        self.tp = TraitParent(self.conn, self.suite)
        self.fm = Family(self.conn)
        self.tr = Trait(self.conn, self.suite)
        self.families = list(self.fm.get_related_families(self.pr.get_families()))
        self._envv = None
        self.default = DefaultEnvironment(self.conn)
        self.installer = TraitInstaller(self.conn, self.suite, self.cfg)
        if os.environ.has_key('PAELLA_MACHINE'):
            self.machine = os.environ['PAELLA_MACHINE']
        if os.environ.has_key('PAELLA_TRAIT'):
            self.set_trait(os.environ['PAELLA_TRAIT'])
            
        
    def env(self):
        env = RefDict(self.tp.Environment())
        env.update(self.pr.get_family_data())
        env.update(self.pr.get_profile_data())
        return env

    def set_trait(self, trait):
        self.trait = trait
        self.tp.set_trait(trait)
        self.tr.set_trait(trait)
        self.parents = self.tr.parents()
        self._envv = self.env()
        self.installer.set_trait(trait)
        self.packages = self.installer.traitpackage.packages()
        self.templates = self.installer.traittemplate.templates()
        
    def get(self, key):
        if self._envv is None:
            raise Error, 'need to set trait first'
        return self._envv.dereference(key)

    def install_modules(self, name):
        modules = str2list(self.get(name))
        print 'installing modules', modules, 'to %s/etc/modules' % self.target
        setup_modules(self.target, modules)

    def remove_packages(self, packages=None):
        if packages is None:
            packages = self.packages
        if len(packages):
            if hasattr(packages[0], 'package'):
                packages = [p.package for p in packages]
        package_list = ' '.join(packages)
        command = 'apt-get -y remove %s' % package_list
        self.installer.run('remove', command, proc=True)

    
    
        
if __name__ == '__main__':
    conn = PaellaConnection()
    tp = TraitParent(conn, 'gunny')

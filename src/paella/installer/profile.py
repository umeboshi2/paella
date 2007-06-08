import os
from os.path import isdir, isfile, join, basename, dirname
import logging

from useless.base import UnbornError, Log
from useless.base.util import ujoin, makepaths

from useless.db.midlevel import Environment

from paella.debian.base import RepositorySource
from paella.debian.debconf import install_debconf

from paella.base import PaellaConfig

from paella.db import PaellaConnection
from paella.db.base import get_traits, get_suite
from paella.db.trait.relations.parent import TraitParent
from paella.db.trait.relations.package import TraitPackage

from paella.db.profile import Profile
from paella.db.profile.main import ProfileTrait, ProfileEnvironment

from base import InstallerConnection, CurrentEnvironment

from base import BaseInstaller

from trait import TraitInstaller

class ProfileInstaller(BaseInstaller):
    # here parent is the chroot installer
    # The target needs to be set in the parent before
    # this class is initialized.
    def __init__(self, parent):
        BaseInstaller.__init__(self, parent.conn)
        self._parent = parent
        self.target = parent.target
        # we need this paelladir attribute for now
        # but may replace/redo this later
        self.paelladir = self.target / 'root/paella'
        self.profile = None
        self.suite = None
        self.profiletrait = ProfileTrait(self.conn)
        self._profile = Profile(self.conn)
        if False:
            # setup logfile
            if hasattr(parent, 'log'):
                self.log = parent.log
                self.log.info('profile installer initialized')
            else:
                raise RuntimeError, 'No logfile for parent defined'
        if hasattr(parent, 'mainlog'):
            self.mainlog = parent.mainlog
            name = self.__class__.__name__
            self.mainlog.add_logger(name)
            self.log = self.mainlog.loggers[name]
            
        # make empty data dicts
        self.mtypedata = {}
        self.familydata = {}
        self.profiledata = {}
        

    # this method is called within set_profile
    def _init_attributes(self):
        self.traits = self.profiletrait.trait_rows()
        self.env = ProfileEnvironment(self.conn, self.profile)
        self.familydata = self._profile.get_family_data()
        self.profiledata = self._profile.get_profile_data()
        self.suite = get_suite(self.conn, self.profile)

    # this method is called within set_profile
    # here is where the trait installer is setup
    # the data attributes need to be filled before this is called
    # this method needs to be fixed to use the new trait installer
    def _setup_installer(self, suite):
        self.installer = TraitInstaller(self)
        self.installer.familydata = self.familydata
        self.installer.profiledata = self.profiledata
        self.installer.mtypedata = self.mtypedata

    # here is where the processes are setup
    # every process is a trait and it maps to the same
    # function.  a "current_index" attribute keeps track
    # of which trait is being processed.
    def _setup_trait_processes(self, traitlist):
        self.setup_initial_paellainfo_env(traitlist)
        self._processes = traitlist
        self._process_map = {}.fromkeys(traitlist, self.process_trait)

    # setting the profile involves a lot of work
    # there are helper methods defined to help split
    # the code up into more manageable pieces.
    def set_profile(self, profile):
        self.profile = profile
        self._profile.set_profile(profile)
        os.environ['PAELLA_PROFILE'] = profile
        self.profiletrait.set_profile(profile)
        self._init_attributes()
        self._setup_installer(self.suite)
        self.traitparent = TraitParent(self.conn, self.suite)
        self.log.info('profile set to %s' % profile)
        traitlist = self.make_traitlist()
        self._setup_trait_processes(traitlist)

    # currently there is no script functionality
    # but there may be in the future.
    def make_script(self, procname):
        return None
     
    # this method needs to be checked
    def make_traitlist(self):
        listed = [x.trait for x in self.profiletrait.trait_rows()]
        log = None
        return self._profile.make_traitlist_with_traits(listed, log=log)

    def get_profile_data(self):
        return self.env.ProfileData()
    
    # this method needs to be checked
    # self.paelladir needs to be defined
    def setup_initial_paellainfo_files(self, traits):
        makepaths(self.paelladir)
        traitlist = file(join(self.paelladir, 'traitlist'), 'w')
        for trait in traits:
            traitlist.write('%s\n' % trait)
        traitlist.close()
        itraits = file(join(self.paelladir, 'installed_traits'), 'w')
        itraits.write('Installed Traits:\n')
        itraits.close()

    # initialize data in current_environment,
    # if PAELLA_MACHINE is set
    def setup_initial_paellainfo_env(self, traits):
        if os.environ.has_key('PAELLA_MACHINE'):
            machine = os.environ['PAELLA_MACHINE']
            curenv = CurrentEnvironment(self.conn, machine)
            curenv['current_profile'] = self.profile
            curenv['traitlist'] = ', '.join(traits)
            curenv['installed_traits'] = ''

            
    # this method has been rewritten to use
    # self.current_index
    # the UnbornError should never be raised
    def process_trait(self):
        trait = self._processes[self.current_index]
        self.traitparent.set_trait(trait)
        self.installer.set_trait(trait)
        parents = [r.parent for r in self.traitparent.parents()]
        for p in parents:
            if p not in self.processed:
                raise UnbornError
        self.log.info('processing trait %s' % trait)
        self.installer.run_all_processes()
        self.processed.append(trait)
        self.current_index += 1
        self.log.info('processed:  %s' % ', '.join(self.processed))
        self.append_installed_traits(trait)
        
    # this used to be called process
    def run_all_processes(self):
        traits = self.make_traitlist()
        self.setup_initial_paellainfo_files(traits)
        self.setup_initial_paellainfo_env(traits)
        self.processed = []
        self.current_index = 0
        BaseInstaller.run_all_processes(self)
        self.log.info('all traits processed for profile %s' % self.profile)
        self.log.info('------------------------------------')

    # this method needs to be checked
    def set_template_path(self, tpath):
        self.installer.set_template_path(tpath)

    # this method needs to be checked
    # target should be set upon init.
    # need to remove apt-get update command
    def set_target(self, target, update=False):
        Installer.set_target(self, target)
        self.installer.set_target(target)
        if update:
            os.system(self.command('apt-get update'))

    # this method needs to be checked
    # this method doesn't belong in the profile installer
    # this is a machine installer method
    def install_kernel(self, package):
        os.system(self.command('touch /boot/vmlinuz-fake'))
        os.system(self.command('ln -s boot/vmlinuz-fake vmlinuz'))
        os.system(self.command('apt-get -y install %s' % package))
        print 'kernel %s installed' % package

    # This helps reporting when when a trait is processed
    def append_installed_traits(self, trait):
        self._append_installed_traits_file(trait)
        self._append_installed_traits_db(trait)
        
    # this method needs to be checked
    # self.paelladir needs to be defined
    def _append_installed_traits_file(self, trait):
        itraits = file(join(self.paelladir, 'installed_traits'), 'a')
        itraits.write(trait + '\n')
        itraits.close()

    # this method needs to be checked
    def _append_installed_traits_db(self, trait):
        if os.environ.has_key('PAELLA_MACHINE'):
            machine = os.environ['PAELLA_MACHINE']
            curenv = CurrentEnvironment(self.conn, machine)
            line = curenv['installed_traits']
            traits = [t.strip() for t in line.split(',')]
            traits.append(trait)
            curenv['installed_traits'] = ', '.join(traits)
            
# ---------------------------------------------
# end new profile installer
# ---------------------------------------------

def get_profile_packages(conn, suite, profile):
    traits = get_traits(conn, profile)
    tp = TraitParent(conn, suite)
    pp = TraitPackage(conn, suite)
    packages = [p.package for p in pp.all_packages(traits, tp)]
    return packages


def parse_package_rows(packages):
    grouped = {}
    package_count = 0
    for action in actions:
        grouped[action] = [ p.package for p in packages if p.action == action]
        package_count += len(grouped[action])
    if package_count != len(packages):
        raise Error, 'SOMETHING WENT WRONG in parse_package_rows'
    return grouped




def install_packages_uml(conn, suite, profile, target):
    traits = get_traits(conn, profile)
    tp = TraitParent(conn, suite)
    pp = TraitPackage(conn, suite)
    packages = ' '.join([p.package for p in pp.all_packages(traits, tp)])
    os.system('chroot %s apt-get update' % target)
    os.system('chroot %s apt-get -y install %s' % (target, packages))
              
if __name__ == '__main__':
    from useless.db.midlevel import StatementCursor
    from useless.db.midlevel import Environment, TableDict
    from base import PaellaConnection
    c = PaellaConnection()
    cfg = PaellaConfig()
    p = ProfileInstaller(c, cfg)
    p.set_profile('bard')
    pl = p.make_traitlist()

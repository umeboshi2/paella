import os
from os.path import isdir, isfile, join, basename, dirname
import logging

from paella.base import UnbornError, Log
from paella.base.util import ujoin, makepaths

from paella.db.midlevel import Environment

from paella.debian.base import RepositorySource
from paella.debian.debconf import install_debconf

from paella.profile.base import get_traits, get_suite, PaellaConnection
from paella.profile.base import make_deplist
from paella.profile.trait import TraitParent, TraitPackage, TraitTemplate
from paella.profile.trait import TraitDebconf, TraitScript
from paella.profile.profile import ProfileTrait, ProfileEnvironment, Profile

from base import PaellaConfig, InstallerConnection, CurrentEnvironment
from base import Installer
from trait import TraitInstaller
        

class ProfileInstaller(Installer):
    def __init__(self, conn, cfg):
        os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
        Installer.__init__(self, conn, cfg)
        self.profiletrait = ProfileTrait(self.conn)
        self.profile = None
        self.installer = None
        self.cfg = cfg
        self._profile = Profile(self.conn)
        self.log.info('profile installer initialized')
        
    def set_profile(self, profile):
        self.profile = profile
        self._profile.set_profile(profile)
        os.environ['PAELLA_PROFILE'] = profile
        self.profiletrait.set_profile(profile)
        self.traits = self.profiletrait.trait_rows()
        self.env = ProfileEnvironment(self.conn, self.profile)
        self.familydata = self._profile.get_family_data()
        self.profiledata = self._profile.get_profile_data()
        self.suite = get_suite(self.conn, profile)
        self.installer = TraitInstaller(self.conn, self.suite, self.cfg)
        self.installer.log = self.log
        self.installer.familydata = self.familydata
        self.installer.profiledata = self.profiledata
        self.traitparent = TraitParent(self.conn, self.suite)
        self.log.info('profile set to %s' % profile)
                
    def get_profile_data(self):
        return self.env.ProfileData()
    
    def set_logpath(self, logpath):
        Installer.set_logpath(self, logpath)
        if hasattr(self, 'installer'):
            self.installer.set_logpath(logpath)
        
    def make_traitlist_orig(self):
        traitparent = TraitParent(self.conn, self.suite)
        profile_traits = [x.trait for x in self.profiletrait.trait_rows()]
        all_traits = list(self.traitparent.get_traitset(profile_traits))
        traitlist = []
        while len(profile_traits):
            profile_traits_prepended = False
            trait = profile_traits[0]
            traitparent.set_trait(trait)
            parents = [r.parent for r in traitparent.parents()]
            for p in parents:
                if not profile_traits_prepended and p not in traitlist:
                    profile_traits = [p] + profile_traits
                    profile_traits_prepended = True
                    self.log.info('profile_traits prepended with %s' % p)
            if not profile_traits_prepended:
                traitlist.append(trait)
                del profile_traits[0]
            self.log.info('%s %s' % (str(traitlist), profile_traits))
        return traitlist

    def make_traitlist(self):
        tp = TraitParent(self.conn, self.suite)
        listed = [x.trait for x in self.profiletrait.trait_rows()]
        all = list(self.traitparent.get_traitset(listed))
        setfun = tp.set_trait
        parfun = tp.parents
        log = self.log
        return make_deplist(listed, all, setfun, parfun, log)
        
    def process(self):
        traits = self.make_traitlist()
        self.processed = []
        for trait in traits:
            self.process_trait(trait)
            self.log.info('currently processed %s' % ','.join(self.processed))
        self.log.info('all traits processed for profile %s' % self.profile)
        self.log.info('------------------------------------')
        
    def process_trait(self, trait):
        self.traitparent.set_trait(trait)
        self.installer.set_trait(trait)
        parents = [r.parent for r in self.traitparent.parents()]
        for p in parents:
            if p not in self.processed:
                raise UnbornError
        self.log.info('processing trait %s' % trait)
        self.installer.process()
        self.processed.append(trait)
        self.log.info('processed:  %s' % ', '.join(self.processed))
        
    def set_template_path(self, path):
        self.installer.set_template_path(path)

    def set_target(self, target, update=False):
        Installer.set_target(self, target)
        self.installer.set_target(target)
        if update:
            os.system(self.command('apt-get update'))

    def install_kernel(self, package):
        os.system(self.command('touch /boot/vmlinuz-fake'))
        os.system(self.command('ln -s boot/vmlinuz-fake vmlinuz'))
        os.system(self.command('apt-get -y install %s' % package))
        print 'kernel %s installed' % package

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
    from paella.db.midlevel import StatementCursor
    from paella.db.midlevel import Environment, TableDict
    from base import PaellaConnection
    c = PaellaConnection()
    cfg = PaellaConfig()
    p = ProfileInstaller(c, cfg)
    p.set_profile('bard')
    pl = p.make_traitlist()

from os import path, link
#import os
#from os.path import join as pjoin
#from os.path import split as psplit
#from os.path import isfile, isdir, basename, dirname
#from httplib import HTTPConnection
#from md5 import md5
#import email
#import tempfile
#from copy import deepcopy as copy


#from apt_pkg import ParseTagFile

#from useless.base import debug, Error, NoFileError
#from useless.base.config import Configuration
#from useless.base.util import readfile, wget, strfile
from useless.base.util import md5sum as md5sum_base
from useless.base.util import makepaths, check_file, get_file, get_url
from useless.base.util import filecopy

from base import parse_packages, parse_sources
from base import _Srcfile, full_parse, islocaluri
#from base_stable import parse_sources_list
from base import Release, RepositorySource
from base import make_source

from repos import LocalRepos


#ARCH='i386'
#DISTS='dists'
#SUITE='sid'
#SECTIONS=['main', 'contrib', 'non-free']
#SUITES = ['woody/non-US', 'sid', 'woody']

def md5sum(afile, keepopen=False):
    result = md5sum_base(afile)
    if not keepopen:
        afile.close()
    return result



class BackupRepos(object):
    def __init__(self, localsource, arch='i386'):
        localsource = make_source(localsource)
        print dir(localsource)
        if not islocaluri(localsource.uri):
            raise Error, 'remote uri'
        self.local = LocalRepos(localsource)
        backup_src = make_source(str(localsource))
        backup_src.uri = path.join(backup_src.uri, 'backup')
        self.backup = LocalRepos(str(backup_src), arch=arch)
        self.arch = arch
        self.sections = self.backup.sections
        self.diff = {}
        self.backup.uri  = path.join(self.backup.source.uri, 'backup')
        
    def __repr__(self):
        return 'RemoteRepos %s\n%s' %(self.local.source, self.backup)
        
    def update_release(self):
        makepaths(self.backup.source.distpath)
        localpath = path.join(self.backup.source.distpath, 'Release')
        url = path.join(self.local.source.distpath, 'Release')
        release = file(url)
        if not path.isfile(localpath):
            self._write_release_(release, localpath)
        release.seek(0)
        rsum = md5sum(release, keepopen=True)
        lsum = md5sum(file(localpath))
        release.seek(0)
        if lsum != rsum:
            self._write_release_(release, localpath)
        release.seek(0)
        self.backup.parse_release()
        self.release = self.backup.release

    def _update_packagelist_(self, filename='Packages.gz'):
        self.backup.parse()
        self.local.source.sections = self.backup.sections
        rpath = path.join(self.local.source.uri, self.local.source.suite, filename)
        lpath = path.join(self.backup.source.distpath, filename)
        packagelist = get_url(rpath)
        self._write_file_(packagelist, lpath)

    def update_packagelist(self):
        self._update_packagelist_(filename='Packages.gz')
        self.check_packages('_default_', False)
        missing, corrupt = self.diff['_default_']
        for path in missing:
            lpath = path.join(self.backup.source.root, self.backup.source.suite, path)
            url = path.join(self.local.source.root, self.local.source.suite, path)
            link(url, lpath, 'missing')
        for path in corrupt:
            lpath = path.join(self.backup.source.root, self.backup.source.suite, path)
            url = path.join(self.local.source.root, self.local.source.suite, path)
            link(url, lpath, 'corrupt')



    def update_sourcelist(self):
        self._update_packagelist_(filename='Sources.gz')
        self.check_sources('_default_', False)
        missing, corrupt = self.diff['_default_']
        for path in missing:
            lpath = path.join(self.backup.source.root, self.backup.source.suite, path)
            url = path.join(self.local.source.root, self.local.source.suite, path)
            link(url, lpath, 'missing')
        for path in corrupt:
            lpath = path.join(self.backup.source.root, self.backup.source.suite, path)
            url = path.join(self.local.source.root, self.local.source.suite, path)
            link(url, lpath, 'corrupt')

    def update_flatrepos(self):
        rpath = self.release.path(section, release=release)
        localpath = path.join(self.backup.source.distpath, rpath)
        url = path.join(self.local.source.distpath, rpath)
        status = self.backup.check_section(section, release=release)
        if status == 'missing':
            makepaths(path.dirname(localpath))
            rfile = get_url(url)
            filecopy(rfile, localpath)
        elif status == 'corrupt':
            rfile = get_url(url)
            filecopy(rfile, localpath)
        else:
            print localpath, status
        
        

    def _write_file_(self, fileobj, path):
        newfile = file(path, 'w')
        fileobj.seek(0)
        newfile.write(fileobj.read())
        newfile.close()
        fileobj.seek(0)

    def _update_section_(self, section, release=False):
        rpath = self.release.path(section, release=release)
        localpath = path.join(self.backup.source.distpath, rpath)
        url = path.join(self.local.source.distpath, rpath)
        status = self.backup.check_section(section, release=release)
        if status == 'missing':
            makepaths(path.dirname(localpath))
            rfile = file(url)
            filecopy(rfile, localpath)
        elif status == 'corrupt':
            rfile = file(url)
            filecopy(rfile, localpath)
        else:
            print localpath, status
        
            
    def update_section(self, section):
        self._update_section_(section, release=True)
        self._update_section_(section)
        self.backup.sections[section] = self.backup.parse_section(section)

        
    def update_sections(self):
        for section in self.local.source.sections:
            self.update_section(section)
            
    def sync_section(self, section):
        missing, corrupt = self.diff[section]
        for a_path in missing:
            lpath = path.join(self.backup.source.root, a_path)
            url = path.join(self.local.source.root, a_path)
            if not path.isdir(path.dirname(lpath)):
                print path.dirname(lpath)
                makepaths(path.dirname(lpath))
            try:
                link(url, lpath)
            except OSError:
                print 'bad', url
        for a_path in corrupt:
            lpath = path.join(self.backup.source.root, a_path)
            url = path.join(self.local.source.root, a_path)
            if not path.isdir(path.dirname(lpath)):
                makepaths(path.dirname(lpath))
            try:
                link(url, lpath)
            except OSError:
                print 'bad', url


            
            
    def _write_release_(self, release, localpath):
        self._write_file_(release, localpath)
    

    
    def check_packages(self, section, quick=True):
        missing, corrupt = [], []
        for package in self.sections[section]:
            status, path = self.backup.check_package(package, section, quick=quick)
            if status == 'missing':
                missing.append(path)
            elif status == 'corrupt':
                corrupt.append(path)
        self.diff[section] =  (missing, corrupt)

        
    def check_sources(self, section, quick=True):
        missing, corrupt = [], []
        for package in self.sections[section]:
            m, c = self.backup.check_source(package, section, quick=quick)
            missing += m
            corrupt += c
        self.diff[section] = (missing, corrupt)
        

    def update(self, both_zips=False):
        if self.local.source.has_release():
            self.update_release()
            if both_zips:
                self.release._zip_ = 'gz'
                self.update_sections()
                self.release._zip_ = 'bz2'
                self.update_sections()
            else:
                self.update_sections()
        else:
            self.backup.parse()
            self.local.source.sections = self.backup.sections


        
    def check(self, quick=True):
        for section in self.local.source.sections:
            if self.local.source.type == 'deb':
                self.check_packages(section, quick=quick)
            elif self.local.source.type == 'deb-src':
                self.check_sources(section, quick=quick)

    def sync(self):
        for section in self.local.source.sections:
            self.sync_section(section)


if __name__ == '__main__':
    q = 'deb file:/mirrors/debian questron main contrib non-free'
    br = BackupRepos(q)

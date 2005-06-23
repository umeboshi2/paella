import os
from os.path import join as pjoin
from os.path import split as psplit
from os.path import isfile, isdir, basename, dirname
from httplib import HTTPConnection
from md5 import md5
import email
import tempfile
from copy import deepcopy as copy


from apt_pkg import ParseTagFile

from useless.base import debug, Error, NoFileError
from useless.base.util import readfile, wget, strfile
from useless.base.util import md5sum as md5sum_base
from useless.base.util import makepaths, check_file, get_file, get_url
from useless.base.util import filecopy

from base import parse_packages, parse_sources
from base import _Srcfile, full_parse, islocaluri
from base import parse_sources_list
from base import Release, RepositorySource
from base import make_source

ARCH='i386'
DISTS='dists'
SUITE='sid'
SECTIONS=['main', 'contrib', 'non-free']
SUITES = ['woody/non-US', 'sid', 'woody']



zip = {'sid' : 'bz2',
       'woody/non-US' : 'gz',
       'woody' : 'gz',
       'woody/updates' : 'gz'
       }

def md5sum(afile, keepopen=False):
    result = md5sum_base(afile)
    if not keepopen:
        afile.close()
    return result

def check_and_get_file(rpath, lpath, md5, quick):
    package = os.path.basename(lpath)
    result = check_file(lpath, md5, quick=quick)
    if result != 'ok':
        get_file(rpath, lpath, result)
    else:
        debug(result, '\t\t', package)

class LocalRepos(object):
    def __init__(self, source, arch='i386'):
        source = make_source(source)
        if islocaluri(source.uri):
            self.source = source
            self.arch = arch
            self.sections = {}
        else:
            raise Error, 'not a local source'
    
    def __repr__(self):
        return 'LocalRepos %s' %self.source
        
    def  parse_release (self):
        if self.source.has_release():
            self.release = Release(self.source, arch=self.arch)
            
    def parse_section(self, section=None):
        listfile = self._listfile_(section)
        debug(listfile)
        if not isfile(listfile):
            raise NoFileError, 'file not there'
        if self.source.type == 'deb':
            return parse_packages(listfile)
        elif self.source.type == 'deb-src':
            return parse_sources(listfile)
        else:
            raise Error, 'bad source type'

    def _check_path_(self, full_path, msum):
        if not isfile(full_path):
            status = 'missing'
        elif md5sum(file(full_path)) != msum:
            status = 'corrupt'
        else:
            status = 'ok'
        return status

    def check_section(self, section, release=False):
        rel_path = self.release.path(section, release=release)
        full_path = pjoin(self.source.distpath, rel_path)
        md5 = self.release.sum(section, release=release)
        return self._check_path_(full_path, md5)

    def parse(self):
        if self.source.has_release():
            for section in self.source.sections:
                self.sections[section] = self.parse_section(section)
        else:
            self.sections['_default_'] = self.parse_section()
        
    def full_parse(self, section=None):
        listfile = self._listfile_(section)
        return full_parse(listfile)
    
    def check_package(self, package, section, quick=True):
        path, md5 = self._get_path_md5_(section, package)
        full_path = self._fullpath_(path)
        if not isfile(full_path):
            return 'missing', path
        else:
            if not quick and md5sum(file(full_path)) != md5:
                return 'corrupt', path
            else:
                return 'ok', path

    def _listfile_(self, section=None):
        if self.source.has_release():
            return pjoin(self.source.distpath, self.release.path(section))
        else:
            return pjoin(self.source.distpath, self.source.listfile())

    def check_source(self, package, section, quick=True):
        if self.source.has_release():
            dir, files = self.sections[section][package]
        else:
            dir, files = self.sections['_default_'][package]
        missing, corrupt = [], []
        for afile in files:
            full_path = pjoin(self.source.root, dir, afile.name)
            if not isfile(full_path):
                missing.append(pjoin(dir, afile.name))
            else:
                if not quick and md5sum(file(full_path)) != afile.md5sum:
                    corrupt.append(pjoin(dir, afile.name))
        return missing, corrupt

    def _get_path_md5_(self, section, package):
        if self.source.has_release():
            path, md5 = self.sections[section][package]
        else:
            path, md5 = self.sections['_default_'][package]
        return path, md5
    
    def full_path(self, package):
        section = None
        for a_section in self.source.sections:
            if package in self.sections[a_section].keys():
                section = a_section
        if section:
            path, md5 = self._get_path_md5_(section, package)
        return self._fullpath_(path)

    def _fullpath_(self, path):
        if self.source.has_release():
            return pjoin(self.source.root, path)
        else:
            return pjoin(self.source.root, self.source.suite, path)
            
class RemoteRepos(object):
    def __init__(self, remotesource, localsource, arch='i386'):
        remotesource = make_source(remotesource)
        localsource = make_source(localsource)
        if islocaluri(remotesource.uri):
            raise Error, 'localuri'
        self.source = remotesource
        self.local = LocalRepos(localsource, arch=arch)
        self.arch = arch
        self.sections = self.local.sections
        self.diff = {}
            
    def __repr__(self):
        return 'RemoteRepos %s\n%s' %(self.source, self.local)
        
    def update_release(self):
        makepaths(self.local.source.distpath)
        localpath = pjoin(self.local.source.distpath, 'Release')
        url = pjoin(self.source.distpath, 'Release')
        release = get_url(url)
        if not isfile(localpath):
            self._write_release_(release, localpath)
        release.seek(0)
        rsum = md5sum(release, keepopen=True)
        lsum = md5sum(file(localpath))
        release.seek(0)
        if lsum != rsum:
            self._write_release_(release, localpath)
        release.seek(0)
        self.local.parse_release()
        self.release = self.local.release

    def _update_packagelist_(self, filename='Packages.gz'):
        self.local.parse()
        self.source.sections = self.local.sections
        rpath = pjoin(self.source.uri, self.source.suite, filename)
        lpath = pjoin(self.local.source.distpath, filename)
        packagelist = get_url(rpath)
        self._write_file_(packagelist, lpath)

    def update_packagelist(self):
        self._update_packagelist_(filename='Packages.gz')
        self.check_packages('_default_', False)
        missing, corrupt = self.diff['_default_']
        for path in missing:
            lpath = pjoin(self.local.source.root, self.local.source.suite, path)
            url = pjoin(self.source.root, self.source.suite, path)
            get_file(url, lpath, 'missing')
        for path in corrupt:
            lpath = pjoin(self.local.source.root, self.local.source.suite, path)
            url = pjoin(self.source.root, self.source.suite, path)
            get_file(url, lpath, 'corrupt')



    def update_sourcelist(self):
        self._update_packagelist_(filename='Sources.gz')
        self.check_sources('_default_', False)
        missing, corrupt = self.diff['_default_']
        for path in missing:
            lpath = pjoin(self.local.source.root, self.local.source.suite, path)
            url = pjoin(self.source.root, self.source.suite, path)
            get_file(url, lpath, 'missing')
        for path in corrupt:
            lpath = pjoin(self.local.source.root, self.local.source.suite, path)
            url = pjoin(self.source.root, self.source.suite, path)
            get_file(url, lpath, 'corrupt')

    def update_flatrepos(self):
        rpath = self.release.path(section, release=release)
        localpath = pjoin(self.local.source.distpath, rpath)
        url = pjoin(self.source.distpath, rpath)
        status = self.local.check_section(section, release=release)
        if status == 'missing':
            makepaths(dirname(localpath))
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
        localpath = pjoin(self.local.source.distpath, rpath)
        url = pjoin(self.source.distpath, rpath)
        status = self.local.check_section(section, release=release)
        if status == 'missing':
            makepaths(dirname(localpath))
            rfile = get_url(url)
            filecopy(rfile, localpath)
        elif status == 'corrupt':
            rfile = get_url(url)
            filecopy(rfile, localpath)
        else:
            print localpath, status
        
            
    def update_section(self, section):
        self._update_section_(section, release=True)
        self._update_section_(section)
        self.local.sections[section] = self.local.parse_section(section)

        
    def update_sections(self):
        for section in self.source.sections:
            self.update_section(section)
            
    def sync_section(self, section):
        missing, corrupt = self.diff[section]
        for path in missing:
            lpath = pjoin(self.local.source.root, path)
            url = pjoin(self.source.root, path)
            get_file(url, lpath, 'missing')
        for path in corrupt:
            lpath = pjoin(self.local.source.root, path)
            url = pjoin(self.source.root, path)
            get_file(url, lpath, 'corrupt')


            
            
    def _write_release_(self, release, localpath):
        self._write_file_(release, localpath)
    

    
    def check_packages(self, section, quick=True):
        missing, corrupt = [], []
        for package in self.sections[section]:
            status, path = self.local.check_package(package, section, quick=quick)
            if status == 'missing':
                missing.append(path)
            elif status == 'corrupt':
                corrupt.append(path)
        self.diff[section] =  (missing, corrupt)

        
    def check_sources(self, section, quick=True):
        missing, corrupt = [], []
        for package in self.sections[section]:
            m, c = self.local.check_source(package, section, quick=quick)
            missing += m
            corrupt += c
        self.diff[section] = (missing, corrupt)
        

    def update(self, both_zips=False):
        if self.source.has_release():
            self.update_release()
            if both_zips:
                self.release._zip_ = 'gz'
                self.update_sections()
                self.release._zip_ = 'bz2'
                self.update_sections()
            else:
                self.update_sections()
        else:
            self.local.parse()
            self.source.sections = self.local.sections


        
    def check(self, quick=True):
        for section in self.source.sections:
            if self.source.type == 'deb':
                self.check_packages(section, quick=quick)
            elif self.source.type == 'deb-src':
                self.check_sources(section, quick=quick)

    def sync(self):
        for section in self.source.sections:
            self.sync_section(section)


def update_repos(repos):
    repos.update()
    if repos.source.suite in ['sid']:
        repos.release._zip_ = 'gz'
        repos.update_sections()
    repos.check()
    repos.sync()

def _update_sources_(remote, local, src=False):
    rs = make_source(remote)
    ls = make_source(local)
    update_repos(RemoteRepos(rs, ls))
    if src:
        rs.type = 'deb-src'
        ls.type = 'deb-src'
        update_repos(RemoteRepos(rs, ls))
        rs.type = 'deb'
        ls.type = 'deb'

def update_suite(suite, remote=None, local=None, src=True):
    sections = 'main contrib non-free'
    if remote is None:
        remote = 'deb http://ftp.us.debian.org/debian %s %s' %(suite, sections)
    else:
        remote.type = 'deb'
        remote.suite = suite
        remote.set_path()
    if local is None:
        local = 'deb file:/mirrors/debian %s %s' %(suite, sections)
    else:
        remote.type = 'deb'
        local.suite = suite
        local.set_path()
    _update_sources_(remote, local, src=src)

def update_suites(remote=None, local=None, src=True):
    for suite in ['woody', 'sarge', 'sid']:
        update_suite(suite, remote, local, src=src)
        
def security_updates():
    for suite in ['woody', 'sarge']:
        sections = 'main contrib non-free'
        rline = 'deb http://security.debian.org/ %s/updates %s' %(suite, sections)
        lline = 'deb file:/mirrors/debian/updates %s/updates %s' %(suite, sections)
        _update_sources_(rline, lline, src=True)
    

    
if __name__ == '__main__':
    mirror = 'http://jukebox/debian'
    path = '/mirrors/share/Debian/repos/'
    sources = parse_sources_list('/etc/apt/sources.list')
    #rs = RepositorySource(sources[2])
    #ls = RepositorySource(sources[0])
    ls = sources[0]
    rs = RepositorySource('deb %s sid main contrib non-free' % mirror)
    rr = RemoteRepos(rs, ls)
    #rs = RepositorySource('deb http://developer.linuxtag.org/ knoppix/')
    #ls = RepositorySource('deb file:/mirrors/debian/local/ goofy/')
    rr = RemoteRepos(rs, ls)
    

import os, os.path
from os.path import isfile
import string, re
import email, gzip

from paella.base import Error
from paella.base.util import apply2file, md5sum
from paella.base.classes.db_result import DbBaseRow, DbRowDescription

from base import full_parse


DPKGPATH = '/var/lib/dpkg'
DPKGINFO = os.path.join(DPKGPATH, 'info')
DPKGSTATUS = os.path.join(DPKGPATH, 'status')
DPKGAVAILABLE = os.path.join(DPKGPATH, 'available')
conf_suffix = 'conffiles'
md5_suffix = 'md5sums'
list_suffix = 'list'


strippers = ['Package', 'Essential', 'Status', 'Priority', 'Section',
             'Installed-Size', 'Maintainer', 'Version', 'Replaces',
             'Provides', 'Pre-Depends', 'Conflicts', 'Source', 'Suggests',
             'Depends']

pstatus_columns = ['Package', 'Status', 'Priority', 'Section',
                   'Installed-Size', 'Maintainer', 'Version',
                   'Source']

other_fields = ['Conffiles', 'Description']

pkg_fields = strippers + other_fields

def make_pstatus_rows(pdict):
    prows =[]
    for pack in pdict.keys():
        vlist = []
        for stat_field in pstatus_columns:
            if pdict[pack].has_key(stat_field):
                vlist.append(pdict[pack][stat_field])
            else:
                vlist.append(None)
        prows.append(DbBaseRow(pstatus_columns, vlist))
    return prows

def get_packages_with_suffix(path, suffix):
    ls = os.listdir(path)
    slen = len(suffix) + 1 # for the dot
    return [x[:-slen] for x in ls if x[-slen:] == '.' + suffix]

def parse_listfile(path, package, suffix, function):
    filename = os.path.join(path, '.'.join([package, suffix]))
    return apply2file(function, filename)


def _simpleparse(afile):
    return [x.strip() for x in afile]

def _md5parse(afile):
    formed = {}
    for line in afile:
        sline = string.strip(line)
        md5 = sline[:32]
        file = '/' + string.strip(sline[32:])
        formed[file] = md5
    return formed


def parse_conffiles(path, package):
    return parse_listfile(path, package, conf_suffix, _simpleparse)
def parse_md5sums(path, package):
    return parse_listfile(path, package, md5_suffix, _md5parse)
def parse_filelist(path, package):
    return parse_listfile(path, package, list_suffix, _simpleparse)

class _foodict(dict):
    def __init__(self, suffix, parser, path=DPKGINFO):
        object.__init__(self)
        self.packs = get_packages_with_suffix(path, suffix)
        for pack in self.packs:
            self[pack] = parser(path, pack)
        

class Conffiles(_foodict):
    def __init__(self, path=DPKGINFO):
        _foodict.__init__(self, conf_suffix, parse_conffiles, path=path)
class Md5sums(_foodict):
    def __init__(self, path=DPKGINFO):
        _foodict.__init__(self, md5_suffix, parse_md5sums, path=path)
class FileList(_foodict):
    def __init__(self, path=DPKGINFO):
        _foodict.__init__(self, list_suffix, parse_filelist, path=path)



class ConfigObject(object):
    def __init__(self, root=DPKGPATH):
        spl = root.split(DPKGPATH)
        if len(spl) == 2 and spl[-1] == '':
            object.__init__(self)
            if spl[0] == '':
                self.root = '/'
            else:
                self.root = spl[0]
        else:
            raise Error, 'bad path'

    def get_files(self):
        return FileList(self._join('info'))
    def get_md5sums(self):
        return Md5sums(self._join('info'))
    def get_conffiles(self):
        return Conffiles(self._join('info'))
    def get_status(self):
        return full_parse(self._join('status'))
    def get_available(self):
        return full_parse(self._join('available'))
    def set_config(self, section):
        sections = dict([('filelist', self.get_files),
                         ('md5sums', self.get_md5sums),
                         ('conffiles', self.get_conffiles),
                         ('status', self.get_status),
                         ('available', self.get_available)
                         ])
        setattr(self, section, sections[section]())
        
    def set_every_config(self):
        print 'deprecated'
        print 'start'
        print 'filelist'
        self.filelist = self.get_files()
        print 'md5sums'
        self.md5sums = self.get_md5sums()
        print 'conffiles'
        self.conffiles = self.get_conffiles()
        print 'status'
        self.status = self.get_status()
        print 'prows'
        self.prows = make_pstatus_rows(self.status)
        print 'available'
        self.available = self.get_available()
        print 'Done'
        
    def _join(self, filename):
        return os.path.join(self.root, DPKGPATH, filename)

    def renorm(self, path):
        return os.path.join(self.root, path)

    def _conf_md5_(self, package):
        if self.conffiles.has_key(package) and self.md5sums.has_key(package):
            psums = self.md5sums[package].items()
            return dict([(p,s) for p,s in psums if p in self.conffiles[p]])
        else:
            raise Error, "no way dude"
        
    def _md5check_(self, package):
        ndict, cdict = {}, {}
        for a_file, a_sum in self.md5sums[package].items():
            ndict[a_file] = md5sum(self.renorm(a_file))
            if ndict[a_file] != a_sum:
                cdict[a_file] = (a_sum, ndict[a_file])
        return ndict, cdict
    

    def _confirm_package(self, package):
        if package in self.md5sums:
            return self._md5check_(package)
        else:
            raise Error, 'no package'
        
if __name__ == '__main__':
    co = ConfigObject()
    #p = parse_dpackage_status(DPKGSTATUS)
    #pd = PackageDict(DPKGSTATUS)
    pass

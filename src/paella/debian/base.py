from os.path import join, dirname, basename, split
from gzip import GzipFile
import tempfile
import email

from apt_pkg import ParseTagFile


from useless.base import debug, Error
from useless.base.util import gunzip, bunzip
from useless.base.util import readfile

SRCPATH = 'source'

def dotjoin(*args):
    return '.'.join(args)

def _binpath(arch):
    return 'binary-%s' %arch


class _Srcfile(list):
    def __init__(self, md5sum, size, name):
        list.__init__(self, [md5sum, size, name])
        self.md5sum = md5sum
        self.size = size
        self.name = name


class RepositorySource(object):
    default_line = ['deb file:/mirrors/debian sid main contrib non-free']
    def __init__(self, line=default_line[0]):
        object.__init__(self)
        self.set_source(line)
        self._zip_ = 'gz'

    def listfile(self):
        if not self.has_release():
            if self.type == 'deb-src':
                return dotjoin('Sources', self._zip_)
            else:
                return dotjoin('Packages', self._zip_)
        else:
            raise Error, 'this shouldnt have been called'
        
    def set_source(self, line):
        debug(line)
        line = line.strip().split()
        debug('split', line)
        self.type, self.uri, self.suite = line[:3]
        self.sections = line[3:]
        self.set_path()

    def set_path(self):
        if islocaluri(self.uri):
            self.root = self.uri.split(':')[1]
        else:
            self.root = self.uri
        if not self.has_release():
            self.distpath = join(self.root, self.suite)
        else:
            self.distpath = join(self.root, 'dists', self.suite)

    def has_release(self):
        return not self.suite[-1] == '/'
    
    def __repr__(self):
        line = ' '.join([self.type, self.uri, self.suite] + self.sections)
        return 'Source: %s' % line

    def __str__(self):
        line = ' '.join([self.type, self.uri, self.suite] + self.sections)
        return line


        


class ReleaseSums(object):
    def __init__(self, type='binary', sections='SECTIONS',
                 arch='i386'):
        object.__init__(self)
        self.type = type
        self.sections = sections
        self.arch = arch

    def parse_path(self, path):
        sectype, filename = split(path)
        section, atype = split(sectype)
        type = atype.split('-')[0]
        return section, type, filename



class Release(object):
    def __init__(self, source, arch='i386'):
        object.__init__(self)
        self.source = source
        self.arch = arch
        self.parse()
        self._zip_ = 'gz'
        if self.source.suite in ['sid']:
            self._zip_ = 'bz2'

    def __repr__(self):
        sums = ['%s: -> %s' %(s.name, s.md5sum) for s in self.sums.values()]
        return '\n'.join(sums)
    
    def _parse_md5sums(self, body):
        sums = [_Srcfile(*x.split()) for x in body.split('\n')[1:]]
        midpath = self.midpath(arch=self.arch)
        sumdict = dict([(x.name, x) for x in sums if _2up(x.name) == midpath])
        return sumdict

    def parse(self):
        filename = join(self.source.distpath, 'Release')
        self.fields = email.message_from_string(readfile(filename))
        self.sums = self._parse_md5sums(self.fields['md5sum'])
        
    def path(self, section, release=False):
        midpath = self.midpath(arch=self.arch)
        file = self.listfile(release=release)
        return join(section, midpath, file)
        
    def listfile(self, release=False):
        if self.source.type == 'deb-src' and not release:
            return dotjoin('Sources', self._zip_)
        elif release:
            return 'Release'
        else:
            return dotjoin('Packages', self._zip_)

    def midpath(self, arch='i386'):
        if self.source.type == 'deb-src':
            midpath = SRCPATH
        else:
            midpath = _binpath(arch)
        return midpath

    def sum(self, section, release=False):
        key = self.path(section, release=release)
        return self.sums[key].md5sum
    

def islocaluri(uri):
    return uri.split(':')[0] == 'file'

        
#returns [[md5sum, size, filename] . . ] for x in filelist
def split_filelist(filelist):
    return [_Srcfile(*x.split()) for x in filelist.split('\n')]

def _parse_tagfile(filename, function):
    pdict = {}
    if filename[-3:] == '.gz':
        tagfile = gunzip(filename)
    elif filename[-4:] == '.bz2':
        tagfile = bunzip(filename)
    else:
        tagfile = file(filename)
    parser = ParseTagFile(tagfile)
    while parser.Step():
        k,v = function(parser.Section)
        pdict[k] = v
    return pdict

def make_pkg_item(section):
    pkg = section['package']
    path = section['filename']
    md5 = section['md5sum']
    return pkg, (path, md5)

def make_src_item(section):
    pkg = section['package']
    dir = section['directory']
    files = split_filelist(section['files'])
    return pkg, (dir, files)

def make_section(section):
    pkg = section['package']
    sdict = {}
    for k in section.keys():
        sdict[k.lower()] = section[k]
    return pkg, sdict

def parse_sources(filename):
    return _parse_tagfile(filename, make_src_item)

def parse_packages(filename):
    return _parse_tagfile(filename, make_pkg_item)

def full_parse(filename):
    return _parse_tagfile(filename, make_section)

def parse_sources_list(filename):
    listfile = file(filename)
    lines = [line for line in listfile if line.strip() and line[0] != '#']
    listfile.close()
    return [RepositorySource(line) for line in lines]



def _2up(path):
    return basename(dirname(path))

def make_dist_dirs(suite, sections, path, arch='i386'):
    distpath = join(path, DISTS, suite)
    makepaths(distpath)
    for section in sections:
        bpath = join(distpath, section, _binpath(arch))
        spath = join(distpath, section, SRCPATH)
        makepaths(bpath, spath)
    

def parse_release_md5sums(astring, arch='i386', sources=False):
    paths = [_binpath(arch)]
    if sources:
        paths.append(SRCPATH)
    msums = [_Srcfile(*x.split()) for x in astring.split('\n')[1:]]
    mysums = dict([(x.name, x) for x in msums if _2up(x.name) in paths])
    return mysums

def parse_release(suite, path):
    filename = pjoin(path, DISTS, suite, 'Release')
    release = email.message_from_string(readfile(filename))
    return release, parse_release_md5sums(release['md5sum'])


def make_source(source):
    if type(source) is str:
        source = RepositorySource(source)
    return source





def debootstrap(suite, root, mirror=None, script=''):
    cmd = 'debootstrap --arch i386'
    if mirror is None:
        mirror = 'file:/mirrors/debian'
    return ' '.join([cmd, suite, root, mirror, script])


class Debootstrap(object):
    def __init__(self, suite='woody', root='base',
                 mirror='file:/mirrors/debian', script=''):
        self.arch = 'i386'
        self.include = []
        self.exclude = []
        self.suite = suite
        self.root = root
        self.mirror = mirror
        self.script = script

    def _set_opts_(self):
        opts = ''
        if self.arch:
            opts += '--arch %s' % self.arch
        if len(self.include):
            opts += ' --include=%s' % ','.join(self.include)
        if len(self.exclude):
            opts += ' --exclude=%s' % ','.join(self.exclude)
        return opts

    def command(self):
        cmd = 'debootstrap'
        opts = self._set_opts_()
        args = '%s %s %s %s' % (self.suite, self.root, self.mirror, self.script)
        return '%s %s %s' % (cmd, opts, args)
    
            

if __name__ == '__main__':
    fname = '/mirrors/debian/dists/sid/main/binary-i386/Packages.gz'
    fp = full_parse(fname)
    

import os, sys
from os.path import isfile, isdir, join
from gzip import GzipFile
from StringIO import StringIO
from md5 import md5

import pycurl

from paella.base import debug, Error

from defaults import BLOCK_SIZE

class strfile(StringIO):
    def __init__(self, string=''):
        StringIO.__init__(self, string)

class Pkdictrows(dict):
    def __init__(self, rows, keyfield):
        dict.__init__(self, [(x[keyfield], x) for x in rows])

class Mount(dict):
    def __init__(self, device, mtpnt, fstype, opts, dump, pass_):
        dict.__init__(self, device=device, mtpnt=mtpnt, fstype=fstype,
                      opts=opts, dump=dump)
        self['pass'] = pass_

    def __repr__(self):
        fields = ['device', 'mtpnt', 'fstype', 'opts', 'dump', 'pass']
        values = [self[field] for field in fields]
        return 'Mount:  %s'  % ' '.join(values)

    def isnfs(self):
        return self['fstype'] == 'nfs'

    def istmpfs(self):
        return self['fstype'] == 'tmpfs'

    def isrootfs(self):
        return self['fstype'] == 'rootfs'

    def isproc(self):
        return self['fstype'] == 'proc'
    
class RefDict(dict):
    def dereference(self, key):
        value = self[key]
        if value[0] == '$':
            key = value[1:]
            if key[0] == '$':
                return key
            else:
                return self.dereference(key)
        else:
            return value
        

    


def makepaths(*paths):
    for path in paths:
        if not isdir(path):
            os.makedirs(path)

def blank_values(count, value=None):
    for x in range(count):
        yield value

def blank_list(length, value=None):
    return list(blank_values(length, value))


def diff_dict(adict, bdict):
    diffdict = {}
    for key in adict.keys():
        diffdict[key] = bool(adict[key] == bdict[key])
    return diffdict

def apply2file(function, path, *args):
    f = file(path)
    result = function(f, *args)
    f.close()
    return result

def wget(url, path='.'):
    here = os.getcwd()
    if path == '.':
        path = here
    os.chdir(os.path.dirname(path))
    cmd = 'wget %s' % url
    os.system(cmd)
    os.chdir(here)

def md5sum(afile):
    m = md5()
    block = afile.read(BLOCK_SIZE)
    while block:
        m.update(block)
        block = afile.read(BLOCK_SIZE)
    return m.hexdigest()

def gunzip(path):
    return os.popen2('gzip -cd %s' %path)[1]

def bunzip(path):
    return os.popen2('bzip2 -cd %s' %path)[1]

def check_file(path, md5_, quick=False):
    package = os.path.basename(path)
    if isfile(path):
        if not quick:
            debug('checking ', package)
            if md5sum(path) == md5_:
                return 'ok'
            else:
                print package, md5_, md5sum(path)
                return 'corrupt'
        else:
            return 'ok'
    else:
        return 'gone'

def get_file(rpath, lpath, result='gone'):
    dir, package = os.path.split(lpath)
    if result == 'corrupt':
        while isfile(lpath):
            os.remove(lpath)
        wget(rpath, lpath)
        print package, ' was corrupt, got it'
    else:
        print package, ' not there'
        makepaths(dir)
        wget(rpath, lpath)


def ujoin(*args):
    return '_'.join(args)

def oneliner(path, line):
    f = file(path, 'w')
    f.write(line + '\n')
    f.close()
    

def export_vars(out, variables):
    lines = ['export %s=%s\n' %(k,v) for k,v in variables.items()]
    out.write(lines)
def parse_vars(path):
    f = file(path)
    lines = [x.strip() for x in f.readlines()]
    items = [(x[0],x[1].strip()) for x in lines if x and x[0] !='#']
    return dict(items)

def parse_vars_eq(path):
    f = file(path)
    lines = [x.strip() for x in f.readlines()]
    items = [x.split('=') for x in lines if x and x[0] !='#']
    return dict(items)

def writefile(path, string):
    f = file(path, 'w')
    f.write(string)
    f.close()

def readfile(filename):
    f = file(filename)
    s = f.read()
    f.close()
    return s

def get_url(url):
    string = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, string.write)
    c.setopt(c.MAXREDIRS, 5)
    c.perform()
    c.close()
    string.seek(0)
    return string

def filecopy(afile, path):
    newfile = file(path, 'w')
    if afile.tell() != 0:
        afile.seek(0)
    block = afile.read(1024)
    while block:
        newfile.write(block)
        block = afile.read(1024)
    newfile.close()

def backuptree(directory, backup):
    input, output = os.popen2('find %s -type d' %directory)
    dir = output.readline().strip()
    while dir:
        makepaths(join(backup, dir))
        dir = output.readline().strip()
    input, output = os.popen2('find %s -type f' %directory)
    file = output.readline().strip()
    while file:
        os.link(file, join(backup, file))
        file = output.readline().strip()
        
def has_extension(filename, extension, dot=True):
    if extension[0] != '.' and dot:
        extension = '.' + extension
    return filename[-len(extension):] == extension

def indexed_items(items):
    return dict([(v[0], k) for k,v in enumerate(items)])

def get_sub_path(fullpath, rootpath):
    if fullpath[:len(rootpath)] != rootpath:
        raise Error, 'fullpath not in rootpath\n%s\n%s' %(fullpath, rootpath)
    if rootpath[-1] != '/':
        rootpath += '/'
    tpath = fullpath.split(rootpath)[1]
    return tpath

def parse_proc_cmdline():
    _opts = file('/proc/cmdline').read().strip().split()
    return dict([o.split('=') for o in _opts if o.find('=') >= 0])

def parse_proc_mounts():
    mounts = [Mount(*x.strip().split()) for x in file('/proc/mounts').readlines()]
    return mounts

def ismounted(mtpnt):
    mounts = parse_proc_mounts()
    mounted = False
    for m in mounts:
        if m['mtpnt'] == mtpnt:
            mounted = True
    return mounted

def runlog(command, destroylog=False,
           keeprunning=False, logvar='LOGFILE'):
    logfile = os.environ[logvar]
    if isfile(logfile) and destroylog:
        os.remove(logfile)
    sysstream = dict(in_=sys.stdin, out=sys.stdout, err=sys.stderr)
    newstream = dict(in_=file('/dev/null'),
                     out=file(logfile, 'a'),
                     err=file(logfile, 'a+', 0))
    backup = {}
    for stream  in sysstream:
        backup[stream] = [os.dup(sysstream[stream].fileno()),
                          sysstream[stream].fileno()]
    for stream  in sysstream:
        os.dup2(newstream[stream].fileno(), backup[stream][1])
    run = os.system(command)
    if run and not keeprunning:
        raise Error, 'error in command %s , check %s' % (command, logfile)
    for stream in sysstream:
        os.dup2(backup[stream][0], backup[stream][1])
    for stream in newstream:
        newstream[stream].close()
    for stream in backup:
        os.close(backup[stream][0])
    return run

def echo(message, logvar='LOGFILE'):
    runlog('echo %s' % message, logvar=logvar)
    
def str2list(data, delim=','):
    return [x.strip() for x in data.split(delim)]

if __name__ == '__main__':
    print 'hello'
    

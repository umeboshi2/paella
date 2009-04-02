import sys
import os
import stat
import errno
import logging

import fuse
from fuse import Fuse

from useless.base.path import path

from paella.db import PaellaConnection
from paella.db.main import PaellaExporter
from paella.db.trait import Trait
from paella.db.trait.base import Traits

fuse.fuse_python_api = (0, 2)

#logging.basicConfig(level=logging.DEBUG,
#                    format='%(asctime)s %(levelname)s %(message)s',
#                    filename='/tmp/myapp.log',
#                    filemode='w')
#logging.debug('A debug message')
#logging.info('Some information')
#logging.warning('A shot across the bows')

logging.basicConfig(level=logging.DEBUG,
                    filename='flog', filemode='a')



class MyStat(fuse.Stat):
    def __init__(self):
        self.st_mode = stat.S_IFDIR | 0755
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

class PaellaPath(path):
    def splitparts(self):
        parts = self.split('/')
        return parts
    
    def depth(self):
        if self == '/':
            return 0
        else:
            return self.count('/')

def pathinfo(fspath):
    depth = fspath.count('/')
    parts = fspath.split('/')[1:]
    logging.info('pathinfo: depth %d, parts %s' % (depth, parts))
    pathlist = ['suite', 'trait', 'ftype', 'fname']
    data = dict()
    for index in range(len(parts)):
        data[pathlist[index]] = parts[index]
    return data

class PaellaFile(object):
    def __init__(self, conn, fspath, flags, *mode):
        logging.info('PaellaFile.__init__ start')
        self.conn = conn
        self.fileobj = None
        self.info = pathinfo(fspath)
        #logging.info('info %s' % self.info)
        #logging.info('conn %s' % self.conn)
        self.fspath = fspath
        self.traitdb = Trait(self.conn, self.info['suite'])
        #logging.info('traitdb %s' % self.traitdb)
        #logging.info('set trait to %s' % self.info['trait'])
        self.traitdb.set_trait(self.info['trait'])
        logging.info('traitdb.current_trait %s' % self.traitdb.current_trait)

        #logging.info('PaellaFile.__init__ info: %s' % self.info)
        fname = self.info['fname']
        ftype = self.info['ftype']
        if ftype == 'scripts':
            self. fileobj = self.traitdb._scripts.scriptfile(fname)
        else:
            logging.warn('Unable to handle ftype of %s' % ftype)
        logging.info('PaellaFile initialized with %s, %s' % (ftype, fname))
            
            

    def read(self, length, offset):
        logging.info('PaellaFile.read(%d, %d)' % (length, offset))
        self.fileobj.seek(offset)
        data = self.fileobj.read(length)
        #logging.info('read data %s' % data)
        return data

    def fgetattr(self):
        logging.info('PaellaFile.fgetattr called')
        st = MyStat()
        st.st_mode = stat.S_IFREG | 0644
        st.st_uid = os.getuid()
        st.st_gid = os.getgid()
        st.st_size = self.fileobj.len
        return st

    def release(self, flags):
        self.fileobj.close()

    def test__getattr__(self, attribute, *args, **kw):
        if hasattr(self, attribute):
            return getattr(self, attribute, *args, **kw)
        else:
            logging.warn('%s called in PaellaFile' % attribute)
            raise AttributeError , "PaellaFile instance has no attribute '%s'" % attribute
        
        
class TestFS(Fuse):
    def __init__(self, *args, **kw):
        print "args:", args
        print "kw:", kw
        Fuse.__init__(self, *args, **kw)
        self.conn = PaellaConnection()
        self.db = PaellaExporter(self.conn)
        print "Init complete"

    def getattr(self, fspath, fh=None):
        st = MyStat()
        pp = PaellaPath(fspath)
        info = pathinfo(fspath)
        #if pp.depth() > 3:
        #    logging.info('pp depth %d' % pp.depth())
        #    logging.info('parts %s' % pp.splitparts())
        #    st.st_mode = stat.S_IFREG | 0644
        #    st.st_uid = os.getuid()
        #    st.st_gid = os.getgid()
        if fh is not None:
            self.log.info('in fs.getattr, fh is %s' % fh)
        if info.has_key('fname'):
            logging.info('%s is a file' % fspath)
            st.st_mode = stat.S_IFREG | 0644
            st.st_uid = os.getuid()
            st.st_gid = os.getgid()
            fileobj = PaellaFile(self.conn, fspath, 0)
            st.st_size = fileobj.fileobj.len
        return st

    def readdir(self, fspath, offset):
        dirents = ['.', '..']
        if fspath == '/':
            dirents.extend(self.db.suitecursor.get_suites())
        else:
            logging.warn("Need to handle %s" % fspath)
            depth = fspath.count('/')
            logging.warn('depth is %d' % depth)
            if depth == 1:
                suite = os.path.basename(fspath)
                logging.info('fspath is %s' % fspath)
                logging.info('suite is %s' % suite)
                traitdb = Trait(self.conn, suite)
                traits = traitdb.get_trait_list()
                dirents.extend(traits)
            elif depth == 2:
                trait = os.path.basename(fspath)
                dirname = os.path.dirname(fspath)
                suite = os.path.basename(dirname)
                logging.info('depth 2, suite %s, trait %s' % (suite, trait))
                dirents.extend(['scripts', 'templates'])
            elif depth == 3:
                ignore, suite, trait, ftype = fspath.split('/')
                logging.info('ftype is %s' % ftype)
                logging.info('suite is %s' % suite)
                logging.info('trait is %s' % trait)
                traitdb = Trait(self.conn, suite)
                traitdb.set_trait(trait)
                if ftype == 'scripts':
                    scripts = traitdb._scripts.scripts(trait=trait)
                    scripts = [row.script for row in scripts]
                    dirents.extend(scripts)
                else:
                    logging.warn('unable to handle ftype %s' % ftype)
            else:
                logging.warn('unable to handle depth of %d' % depth)
        for ent in dirents:
            yield fuse.Direntry(ent)
            
    def open(self, fspath, flags):
        logging.info('In open, %s, flags %s' % (fspath, flags))
        return PaellaFile(self.conn, fspath, flags)
        

    def read(self, fspath, length, offset, fh=None):
        #info = 'fspath %s, length %s, offset %s, fh %s' % (fspath, length, offset, fh)
        #logging.info('In read, %s' % info)
        data = fh.read(length, offset)
        #logging.info('if fs.read -> data is %s' % data)
        return data

    def fgetattr(self, fspath, fh=None):
        return fh.fgetattr()
    
        
        
        
    
if __name__ == '__main__':
    fs = TestFS()
    fs.parse()
    fs.main()

    

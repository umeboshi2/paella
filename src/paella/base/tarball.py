import os
from os.path import join, isdir, basename
import tempfile
from tarfile import TarFile, open

from util import makepaths

def make_tarball(target, tarball_path, name):
    makepaths(tarball_path)
    tarball = open(join(tarball_path, name + '.tar'), 'w:')
    tarball.add(target, './')
    tarball.close()

    
class RootTarball(TarFile):
    def __init__(self, name=None, fileobj=None):
        TarFile.__init__(self, name=name, mode='r', fileobj=fileobj)
        self.tmpdir = None
        
    def fake_extract(self):
        self.tmpdir = tempfile.mkdtemp(basename(self.name), '_fakeroot')
        makepaths(self.tmpdir)
        here = os.getcwd()
        os.chdir(self.tmpdir)
        for info in self:
            ipath = info.name
            if info.isdir():
                if not isdir(ipath):                
                    makepaths(ipath)
            elif info.isreg():
                file(ipath, 'w')
        os.chdir(here)

    def _fixpath(self, path):
        while path[0] == '/':
            path = path[1:]
        return path

    def get_info(self, path):
        path = self._fixpath(path)
        return self.getmember(path)

    def get_info_and_file(self, path):
        info = self.get_info(path)
        return info, self.extractfile(info)
        
    def get_file(self, path):
        return self.extractfile(self.get_info(path))
    
    def __del__(self):
        if self.tmpdir is not None:
            os.system('rm %s -fr' % self.tmpdir)

    
if __name__ == '__main__':
    r = RootTarball('/mirrors/bkups/sid.base.tar')

    

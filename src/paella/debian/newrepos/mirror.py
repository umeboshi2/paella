import os
from os.path import join, split, isfile
from os.path import isdir, basename, dirname
from xmlrpclib import ServerProxy, SafeTransport

from paella.base.config import Configuration
from paella.base.util import makepaths
from paella.db.lowlevel import LocalConnection
from paella.db.midlevel import StatementCursor



from base import RepositorySource, make_source
from repos import LocalRepository, RepositoryConnection
from dpkgdeb import DpkgDeb

default_source = 'deb file:/mirrors/debian sid main contrib non-free'



class DebRepos(object):
    def __init__(self):
        object.__init__(self)
        self.cfg = Configuration('repos')
        cfg = self.cfg
        uri = 'http://%s:%s' % (cfg['repos_server'], cfg['repos_server_port'])
        print uri
        self.repos = ServerProxy(uri, None, None, 0, allow_none=True)
        self.dpkg = DpkgDeb()
        self.current_suite = None
        
    def extract_packages(self, packages, path):
        makepaths(path)
        os.system('rm %s/* -fr' %path)
        print 'extracting ', ', '.join(packages)
        print 'current_suite', self.current_suite
        for package in packages:
            tmp_path = join(path, package)
            makepaths(tmp_path)
            package_path = self.repos.full_path(self.current_suite, package)
            self.dpkg.extract(package_path, tmp_path)
            self.dpkg.control(package_path, tmp_path)
            
    def set_suite(self, suite):
        self.current_suite = suite

if __name__ == '__main__':
    #d = DebRepos()
    #d.set_source('deb file:/mirrors/debian sid main contrib non-free')
    #d.extract_packages(['bash', 'frotz', 'apache'], 'righthere')
    #m = DebMirror()
    #m.connect('http://localhost:8000')
    conn = LocalConnection('repos_db')
    c = StatementCursor(conn)
    

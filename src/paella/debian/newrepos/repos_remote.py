from os.path import dirname, isfile, join

from paella.base.config import Configuration
from paella.base.util import makepaths, filecopy, md5sum
from paella.base.util import get_file, get_url

from base import Release
from repos_base import Repository
from repos_local import LocalRepository

class RemoteRepository(Repository):
    def __init__(self, conn, name, type):
        print 'RemoteRepository', name, type
        Repository.__init__(self, conn, name, type)
        self.set_source(name, type)
        self.diff = {}

        
    def set_source(self, name, type):
        Repository.set_source(self, name, type)
        self.local_src = self.manager.make_source(name, type)
        self.local = LocalRepository(self.conn, name, type)
        self.remote_src = self.manager.get_remote(name, type, remote=True)
        

    def update_release(self, update=False):
        release_file = self.get_remote_release()
        if not self.check_release_file(release_file):
            localpath = join(self.local_src.distpath, 'Release')
            print 'release bad'
            self._write_release_(release_file, localpath)
            release_file.seek(0)
            self.update_release_file(release_file, update=update)
        if not len(self.release.select()):
            release_file.seek(0)
            self.update_release_file(release_file, update=True)
            
    def get_remote_release(self):
        url = join(self.remote_src.distpath, 'Release')
        release_file = get_url(url)
        release_file.seek(0)
        return release_file
    

    def check_release_file(self, release_file):
        release_file.seek(0)
        makepaths(self.local_src.distpath)
        localpath = join(self.local_src.distpath, 'Release')
        if isfile(localpath):
            rsum = md5sum(release_file, keepopen=True)
            lsum = md5sum(file(localpath))
            release_file.seek(0)
            return rsum == lsum
        else:
            return False

    def check_local_release_file(self):
        return self.local.check_release_file_exists()
    
    def make_release(self, release_file):
        release = Release((release_file, self.local_src))
        print release
        
    def _write_release_(self, release_file, localpath):
        local_release = file(localpath, 'w')
        release_file.seek(0)
        local_release.write(release_file.read())
        local_release.close()
        release_file.seek(0)

    def _retrieve_files_(self, filelist, status):
        for path in filelist:
            lpath = join(self.local_src.root, path)
            url = join(self.remote_src.root, path)
            get_file(url, lpath, status)

    def retrieve_missing(self, missing):
        self._retrieve_files_(missing, 'missing')
        
    def retrieve_corrupt(self, corrupt):
        self._retrieve_files_(corrupt, 'corrupt')


    def _update_section_(self, section, release=False):
        
        rpath = self.release.path(section, release=release)
        localpath = join(self.local_src.distpath, rpath)
        url = join(self.remote_src.distpath, rpath)
        status = self.local.check_dist_section(section, release=release)
        please_insert = False
        if not self.local._section_.count_rows(section) and not release:
                please_insert = True
        while status in ['missing', 'corrupt']:
            if status == 'missing':
                makepaths(dirname(localpath))
            rfile = get_url(url)
            filecopy(rfile, localpath)
            print localpath, status
            status = self.local.check_dist_section(section, release=release)
        print localpath, status
        if please_insert:
            self.insert_section_data(section)
        elif status == 'corrupt':
            self.insert_section_data(section)
        

    def update_section(self, section):
        self._update_section_(section, release=True)
        self._update_section_(section)

    def update_sections(self):
        for section in self.manager.get_sections(self.current.name):
            self.update_section(section)

    def __repr__(self):
        return 'RemoteRepository %s\n%s' %(self.remote_src, self.local_src)

    def update_source(self, name, type):
        self.set_source(name, type)
        self.update_release()
        self.update_sections()
    
    def fullpath(self, path):
        return join(self.remote_src.root, path)

    def fulldistpath(self, path):
        return join(self.remote_src.distpath, path)


        
def quick_init(rrepos):
    from base import RepositorySource
    if len(rr.repos.tables()) == 4 and len(rr.sources.select()) == 0:
        local_uri = 'file:/mirrors/debian'
        remote_uri = 'http://ftp.us.debian.org/debian'
        
        source = RepositorySource('deb %s woody main contrib non-free' % local_uri)
        for suite in ['woody', 'sarge', 'sid']:
            source.suite = suite
            for type in ['deb', 'deb-src']:
                source.type = type
                rrepos.add_source(suite, source)
                source.uri = remote_uri
                rrepos.add_source(suite, source)
                source.uri = local_uri
                rrepos.set_source(suite, type)
                rrepos.update_release()
                rrepos.update_sections()







if __name__ == '__main__':
    cfg = Configuration()
    #conn = LocalConnection(cfg['repos_db'])
    from paella.db.lowlevel import QuickConn
    #conn = QuickConn(cfg)
    conn = RepositoryConnection()
    mirror = 'http://10.0.0.2/debian'
    path = '/mirrors/share/Debian/repos/'

    sources = parse_sources_list('/etc/apt/sources.list')

    ls = sources[0]
    rs = sources[2]

    #rp = LocalRepos(ls)
    r = Repository(conn)
    rr = RemoteRepository(conn)

    def dtables():
        for t in rr.repos.tables():
            rr.repos.execute('drop table %s'%t)
        
    s = make_source('deb file:/mirrors/debian sid main non-free contrib')

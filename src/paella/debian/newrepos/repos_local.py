from os.path import join, isfile, dirname

from paella.base import debug, Error, NoFileError
from paella.base.util import md5sum, makepaths
from paella.base.objects import DbBaseRow

from repos_base import Repository
from repos_base import NameType

class StatusRow(DbBaseRow):
    def __init__(self, package, section, status, path, full_path):
        keys = ['section', 'package', 'path', 'status', 'full_path']
        vals = [section, package, path, status, full_path]
        DbBaseRow.__init__(self, keys, vals)

        
class LocalRepository(Repository):
    def __init__(self, conn, name, type):
        Repository.__init__(self, conn, name, type)
        
    def set_source(self, name, type): 
        self.current = NameType(name, type)
        self.release.set_source(name, type)
        self._section_.set_source(name, type)
        self.cur_src = self.make_source()
        
    def get_release_file(self):
        source = self.cur_src
        localpath = join(source.distpath, 'Release')
        if isfile(localpath):
            return file(localpath)
        else:
            raise NoFileError, 'file not found'

    def update_release_file(self, release_file=None):
        if release_file is None:
            release_file = self.get_release_file()
        c = self.current
        Repository.update_release_file(self, c.name, c.type, release_file)
        
    def _check_path_(self, full_path, msum, quick=False):
        if not isfile(full_path):
            status = 'missing'
        elif not quick and md5sum(file(full_path)) != msum:
            status = 'corrupt'
        else:
            status = 'ok'
        return status

    def check_release_file_exists(self):
        source = self.cur_src
        path = join(source.distpath, 'Release')
        return isfile(path)

    def _check_dist_section(self, source, section, release=False):
        rel_path = self.release.path(section, release=release)
        full_path = join(source.distpath, rel_path)
        md5 = self.release.sum(rel_path).md5sum
        status = self._check_path_(full_path, md5)
        return StatusRow(rel_path, section, status, rel_path, full_path)
    
        
    def check_all_dist_sections(self):
        source = self.cur_src
        status_rows = []
        for section in self.manager.get_sections(self.current.name):
            status_rows.append(self._check_dist_section(source, section))
            status_rows.append(self._check_dist_section(source, section, release=True))
        return status_rows

    def check_dist_section(self, section, release=False):
        source = self.cur_src
        return self._check_dist_section(source, section, release)

    def check_section(self, section, quick=True):
        if self.current.type == 'deb':
            return self.check_packages(section, quick)
        else:
            return self.check_sources(section, quick)

    def check_all_sections(self, quick=True):
        status_rows = []
        for section in self.manager.get_sections(self.current.name):
            status_rows += self.check_section(section, quick)
        return status_rows
    
    def make_source(self):
        current = self.current
        return self.manager.make_source(current.name, current.type)

    def __check_row_(self, row, quick, path_function):
        path = path_function(row)
        return self._check_path_(self._fullpath_(path), row.md5sum, quick), path

    def __path_from_plst(self, row):
        return row.filename

    def __path_from_slst(self, row):
        return join(row.directory, row.filename)
    
    def __check_rows_(self, fields, section, quick, path_function):
        status_rows = []
        if type(section) is list:
            rows = section
        else:
            rows = self._section_.all_irows(fields, section)
        for row in rows:
            status, path = self.__check_row_(row, quick, path_function)
            srow = [row.package, section, status, path, self._fullpath_(path)]
            status_rows.append(StatusRow(*srow))
        return status_rows

    def check_packages(self, section, quick=True):
        fields = ['package', 'filename', 'md5sum']
        return self.__check_rows_(fields, section, quick, self.__path_from_plst)

    def check_sources(self, section, quick=True):
        fields = ['package', 'directory', 'filename']
        return self.__check_rows_(fields, section, quick, self.__path_from_slst)

    def check_source(self, package, section, quick=True):
        bad = False
        status_data = dict(missing=[], corrupt=[])
        sources = self._section_.source_package(section, package)
        return self.__check_rows_(sources, quick, self.__path_from_slst)
        
    def check_package(self, package, section, quick=True):
        status_data = dict(missing=[], corrupt=[])
        row = self._section_.package(section, package)
        status, path = self.__check_row_(row, quick, self.__path_from_plst)
        if status != 'ok':
            status_data[status].append(path)
            return status_data
        else:
            return status
        
    def find_path(self, package, section=None):
        if not section:
            section = self._find_section(package)
        path, md5 = self._section_.package_path_md5(section, package)
        self._section_.clear()
        return self._fullpath_(path)
    
    def _find_section(self, package):
        for a_section in self.get_sections(self.current.name):
            self._section_.set_section(a_section)
            if self._section_.has_package(package):
                section = a_section
        if not section:
            raise Error, 'package %s not in %s' % (package, self.current)
        return section


    def __repr__(self):
        if self.current:
            return 'LocalRepository %s' % self.make_source()
        else:
            return 'LocalRepository <unset>'
        
    def _fullpath_(self, path):
        source = self.cur_src
        return join(source.root, path)

    def insert_section(self, section):
        c = self.current
        self.insert_section_data(c.name, c.type, section)

    def insert_sections(self):
        c = self.current
        for section in self.get_sections(c.name):
            self.insert_section_data(c.name, c.type, section)
            
    
        


if __name__ == '__main__':
    from repos_base import RepositoryConnection
    #conn = LocalConnection(cfg['repos_db'])
    #conn = QuickConn(cfg)
    conn = RepositoryConnection()
    mirror = 'http://10.0.0.2/debian'
    path = '/mirrors/share/Debian/repos/'



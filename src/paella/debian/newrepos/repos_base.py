from os.path import join, isfile

from paella.base import debug, Error, NoFileError, ExistsError
from paella.base.config import Configuration
from paella.sqlgen.clause import Eq
from paella.db.lowlevel import QuickConn
from paella.db.midlevel import StatementCursor, Environment


from base import parse_packages, parse_sources
from base import parse_sources_list, full_parse, islocaluri
from base import Release, RepositorySource
from base import make_source, dotjoin
from repos_schema import primary_tables
from repos_schema import FullParseTable, ListTable
from repos_schema import fullparse_tablename, list_tablename

_plist_table = ListTable('woody', 'deb', 'main')
package_columns = [col.name for col in _plist_table.columns]

class RepositoryConnection(QuickConn):
    def __init__(self, cfg=Configuration('repos')):
        QuickConn.__init__(self, cfg)
        

class NameType(object):
    def __init__(self, name, type):
        object.__init__(self)
        self.name = name
        self.type = type
        
    def clause(self):
        return Eq('name', self.name) & Eq('type', self.type)

    def __repr__(self):
        return '%s %s' % (self.name, self.type)


class HasNameType(object):
    def set_source(self, name, type):
        self.current = NameType(name, type)

class RepositoryCursor(StatementCursor, HasNameType):
    pass

    
class ReleaseCursor(RepositoryCursor):
    def __init__(self, conn, arch='i386'):
        StatementCursor.__init__(self, conn)
        self.set_table('release')
        self.arch = arch
        self._zip_ = 'gz'
        
    def set_source(self, name, type):
        RepositoryCursor.set_source(self, name, type)
        self.stmt.clause = self.current.clause()
        
    def paths(self):
        if self.current:
            return [x.path for x in self.select()]
        else:
            raise Error, 'set current first'

    def sum(self, path):
        if not self.current:
            raise Error, 'set current first'
        clause = self.current.clause() & Eq('path', path)
        return self.select_row(clause=clause)


    def path(self, section, release=False):
        midpath = self.midpath(arch=self.arch)
        file = self.listfile(release=release)
        return join(section, midpath, file)
        
    def listfile(self, release=False):
        zip = self._zip_
        if self.current.name == 'sid':
            zip = 'bz2'
        if self.current.type == 'deb-src' and not release:
            return dotjoin('Sources', zip)
        elif release:
            return 'Release'
        else:
            return dotjoin('Packages', zip)

    def midpath(self, arch='i386'):
        if self.current.type == 'deb-src':
            midpath = 'source'
        else:
            midpath = 'binary-%s' % arch
        return midpath

    def parse_path(self, path):
        section = path.split('/')[0]
        release = path.split('/')[-1] == 'Release'
        return section, release

class PackageListCursor(RepositoryCursor):
    def __init__(self, conn):
        RepositoryCursor.__init__(self, conn)

    def set_section(self, section):
        self.set_table(self._tablename(section))
        self.current.section = section

    def _tablename(self, section, name=None, type=None):
        if name is None:
            name = self.current.name
        if type is None:
            type = self.current.type
        return list_tablename(name, type, section)
        
    def _package_rows(self, section, package):
        table = self._tablename(section)
        clause = Eq('package', package)
        return self.select_row(table=table, clause=clause)
        
    def source_package(self, section, package):
        return self._package_rows(section, package)

    def package(self, section, package):
        return self._package_rows(section, package)        

    def has_package(self, package):
        clause = Eq('package', package)
        return self.count('package', self.stmt.table, clause=clause)[0][0]

    def all_rows(self, section):
        return self.select(table=self._tablename(section))

    def all_irows(self, fields, section):
        return self.iselect(fields=fields, table=self._tablename(section))

    def count_rows(self, section):
        return self.select(fields=['count(package)'], table=self._tablename(section))[0][0]
    
    

class FullParseCursor(Environment, HasNameType):
    def __init__(self, conn, table):
        Environment.__init__(self, conn, table, 'package')

    def set_section(self, section):
        self.set_table(self._tablename(section))
        self.current.section = section

    def set_package(self, package):
        self.set_main(package)


class RepositoryManager(object):
    def __init__(self, conn):
        self.conn = conn
        self.main = StatementCursor(self.conn, 'RepositoryMain')
        self.repos = StatementCursor(self.conn, 'Repository')
        self.repos.set_table('repository')
        self.sources = StatementCursor(self.conn, 'Sources')
        self.sources.set_table('sources')
        self.release = ReleaseCursor(self.conn)
        self.repsections = StatementCursor(self.conn, 'repos_section')
        self.repsections.set_table('repos_section')
        self.__init_db__()
        
    def __init_db__(self):
        if not len(self.main.tables()):
            map(self.main.create_table, primary_tables())

    def drop_source(self, name, type):
        nameclause = Eq('name', name)
        clause = nameclause & Eq('type', type)
        for section in self.get_sections(name):
            self.main.drop(list_tablename(name, type, section))
        self.sources.delete(clause=clause)
        sources = self.sources.select(clause=clause)
        if not len(sources):
            self.repsections.delete(clause=nameclause)
            self.repos.delete(clause=nameclause)
            
    def add_source(self, name, source):
        source = make_source(source)
        if name not in [x.name for x in self.repos.select()]:
            self.repos.insert(data=dict(name=name))
        clause = Eq('name', name) & Eq('type', source.type)
        count = int(self.sources.select(fields=['count(name)'], clause=clause)[0][0])
        if count == 0:
            if islocaluri(source.uri):
                data = dict(name=name, type=source.type, uri=source.uri,
                            suite=source.suite)
                self.sources.insert(data=data)
                current_sections = self.get_sections(name)
                sdata = dict(name=name, section=None)
                for section in source.sections:
                    if section not in current_sections:
                        sdata['section'] = section
                        self.repsections.insert(data=sdata)
                    fullparse = FullParseTable(name, source.type, section)
                    if fullparse.name not in self.main.tables():
                        self.main.create_table(fullparse)
                    listtable = ListTable(name, source.type, section)
                    if listtable.name not in self.main.tables():
                        self.main.create_table(listtable)
            else:
                raise Error, 'local uris first'
        else:
            if not islocaluri(source.uri):
                data = dict(remote=source.uri)
                self.sources.update(data=data, clause=clause)
            else:
                raise ExistsError, 'already there'

    def get_sections(self, name):
        clause = Eq('name', name)
        return [x.section for x in self.repsections.iselect(fields=['section'], clause=clause)]

    def make_source_line(self, name, type, remote=False):
        repsrc = self.make_source(name, type, remote)
        return str(repsrc)

    def make_source(self, name, type, remote=False):
        clause = Eq('name', name) & Eq('type', type)
        source = self.sources.select_row(clause=clause)
        repsrc = RepositorySource()
        repsrc.type = source.type
        if remote:
            repsrc.uri = source.remote
        else:
            repsrc.uri = source.uri
        repsrc.suite = source.suite
        repsrc.sections = self.get_sections(name)
        repsrc.set_path()
        return repsrc

    def listfile(self, name, type, section=None):
        source = self.make_source(name, type)
        release = Release(source)
        print 'Need to pull from database!!!'
        if source.has_release():
            return join(source.distpath, release.path(section))
        else:
            return join(source.distpath, source.listfile())
    def get_remote(self, name, type, remote=True):
        return self.make_source(name, type, remote=True)

    def parse_section(self, name, type, section=None):
        listfile = self.listfile(name, type, section)
        debug(listfile)
        if not isfile(listfile):
            raise NoFileError, 'file not there'
        if type == 'deb':
            return full_parse(listfile)
        elif type == 'deb-src':
            return parse_sources(listfile)
        else:
            raise Error, 'bad source type'

    def add_repository(self, name):
        self.repos.insert(data=dict(name=name))

    
class Repository(HasNameType):
    def __init__(self, conn, name, type):
        self.conn = conn
        self.manager = RepositoryManager(self.conn)
        self.sources = StatementCursor(self.conn, 'Sources')
        self.sources.set_table('sources')
        self.release = ReleaseCursor(self.conn)
        self._section_ = PackageListCursor(self.conn)
        self.set_source(name, type)
        
    def set_source(self, name, type):
        HasNameType.set_source(self, name, type)
        self.release.set_source(name, type)
        self._section_.set_source(name, type)

    def update_release_file(self, release_file, update=False):
        c = self.current
        current_files = [x.path for x in self.release.select(clause=c.clause())]
        source = self.manager.make_source(c.name, c.type)
        r = Release((release_file, source))
        for sum in r.sums.values():
            row = dict(name=c.name, type=c.type, md5sum=sum.md5sum,
                       size=sum.size, path=sum.name)
            if sum.name not in current_files:
                self.release.insert(data=row)
            else:
                clause = c.clause() & Eq('path', sum.name)
                self.release.update(data=row, clause=clause)

    def insert_section_data(self, section):
        c = self.current
        print 'in insert_section_data current is', c
        self._section_.set_section(section)
        self._section_.delete()
        parsed = self.manager.parse_section(c.name, c.type, section)
        if c.type == 'deb':
            self.insert_packages(parsed)
        elif c.type == 'deb-src':
            self.insert_sources(parsed)
        else:
            raise Error, 'bad source type'

    def get_remote(self):
        current = self.current
        return self.make_repos_source(current.name, current.type, remote=True)
        
    def insert_full_parse(self, section):
        c = self.current
        listfile = self.manager.listfile(c.name, c.type, section)
        if not isfile(listfile):
            raise NoFileError, 'file not there'
        table = fullparse_tablename(c.name, c.type, section)
        fptable = FullParseCursor(self.conn, table)
        for package, data in full_parse(listfile).items():
            fptable.set_package(package)
            fptable.update(data)
            
    def insert_packages(self, parsed):
        for package, data in parsed.items():
            insert_data = {}.fromkeys(package_columns)
            for field in package_columns:
                try:
                    insert_data[field] = data[field]
                except KeyError:
                    if field == 'installedsize':
                        insert_data[field] = data['installed-size']
                    else:
                        raise KeyError, 'bad key %s' % field
            self._section_.insert(data=insert_data)

            

    def insert_sources(self, parsed):
        for package, (dir, files) in parsed.items():
            data = dict(package=package, directory=dir)
            for afile in files:
                data.update(dict(zip(['md5sum', 'size', 'filename'], afile)))
                self._section_.insert(data=data)

        



def quick_init(rrepos):
    if len(rrepos.repos.tables()) == 4 and len(rrepos.sources.select()) == 0:
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
    conn = RepositoryConnection()

    sources = parse_sources_list('/etc/apt/sources.list')

    def dtables():
        for t in c.tables():
            c.execute('drop table %s'%t)
        
    s = make_source('deb file:/mirrors/debian sid main non-free contrib')

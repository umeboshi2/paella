from paella.base import Error, debug
from paella.base.util import ujoin
from paella.sqlgen.classes import Table
from paella.sqlgen.defaults import Text
from paella.sqlgen.defaults import PkBigname, Bigname, Name, Num, PkName



LISTPREFIX = {'deb' : 'plst', 'deb-src' : 'slst'}

def fullparse_tablename(name, type, section):
    type = type.replace('-', '')
    section = section.replace('-', '')
    return ujoin('fparse', name, type, section)

def list_tablename(name, type, section):
    section = section.replace('-', '')
    print 'type is ', type
    return ujoin(LISTPREFIX[type], name, section)

class RepositoryTable(Table):
    def __init__(self):
        Table.__init__(self, 'repository', [PkName('name')])

class SourceTable(Table):
    def __init__(self):
        source_columns = [
            PkName('name'),
            PkName('type'),
            Bigname('uri'),
            Name('suite'),
            Bigname('remote'),
            Bigname('srcline')]
        Table.__init__(self, 'sources', source_columns)

class ReposSection(Table):
    def __init__(self):
        section_columns = [
            PkName('name'),
            PkName('section')]
        Table.__init__(self, 'repos_section', section_columns)
        
class ReleaseTable(Table):
    def __init__(self):
        release_columns = [
            PkName('name'),
            PkName('type'),
            PkBigname('path'),
            Num('size'),
            Name('md5sum')]
        Table.__init__(self, 'release', release_columns)

class FullParseTable(Table):
    def __init__(self, name, type, section):
        fullparse_columns = [
            PkBigname('package'),
            PkBigname('name'),
            Text('value')]
        type = type.replace('-', '')
        section = section.replace('-', '')
        tablename = fullparse_tablename(name, type, section)
        Table.__init__(self, tablename, fullparse_columns)

class PackageListTable(Table):
    def __init__(self, name, section='__default__'):
        packagelist_columns = [
            PkBigname('package'),
            Name('priority'),
            Name('section'),
            Num('installedsize'),
            Bigname('maintainer'),
            Name('architecture'),
            Name('version'),
            Bigname('filename'),
            Num('size'),
            Name('md5sum'),
            Text('description')]
        section = section.replace('-', '')
        tablename = list_tablename(name, 'deb', section)
        Table.__init__(self, tablename, packagelist_columns)
        
class SourceListTable(Table):
    def __init__(self, name, section='__default__'):
        sourcelist_columns = [
            PkBigname('package'),
            PkBigname('directory'),
            Name('md5sum'),
            Num('size'),
            PkBigname('filename')]
        section = section.replace('-', '')
        tablename = list_tablename(name, 'deb-src', section)
        Table.__init__(self, tablename, sourcelist_columns)

def ListTable(name, type, section):
    if type == 'deb':
        return PackageListTable(name, section)
    elif type == 'deb-src':
        return SourceListTable(name, section)

def primary_tables():
    repos = RepositoryTable()
    source = SourceTable()
    release = ReleaseTable()
    sections = ReposSection()
    return [repos, source, release, sections]

    
          

if __name__ == '__main__':
    from paella.db.lowlevel import LocalConnection
    from paella.db.midlevel import StatementCursor
    conn = LocalConnection('repos_db')
    c = StatementCursor(conn)
    def dtable():
        cmd.execute('drop table ptable')

    def dtables():
        for t in cmd.tables():
            if t != 'footable':
                cmd.execute('drop table %s' %t)
    st = SourceTable()

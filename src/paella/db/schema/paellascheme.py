import os

from useless.base import Error, debug
from useless.base.util import ujoin, makepaths
from useless.base.util import readfile, wget, strfile

from paella.debian.base import RepositorySource
from paella.debian.repos import LocalRepos
from paella.debian.repos import RemoteRepos

from useless.sqlgen.classes import Column, Table
from useless.sqlgen.defaults import Text, DefaultNamed, Bool
from useless.sqlgen.defaults import PkBigname, Bigname, Name, Num
from useless.sqlgen.defaults import PkBignameTable, PkNameTable, PkName

from useless.sqlgen.statement import Statement
from useless.sqlgen.admin import grant_public
from useless.sqlgen.clause import Eq

from useless.db.lowlevel import OperationalError
from useless.db.midlevel import StatementCursor
from useless.db.plsql import pgsql_delete

from paella_tables import suite_tables, primary_tables, primary_sequences
from paella_tables import packages_columns, SCRIPTS
from paella_tables import MTSCRIPTS

PRIORITIES = ['first', 'high', 'pertinent', 'none', 'postinstall', 'last']
SUITES = ['sid', 'woody'] 




plpgsql_delete_trait = """create or replace function delete_trait(varchar, varchar) returns integer as '
	begin
	execute ''delete from '' || $1 || ''_scripts where trait = '' || quote_literal($2) ;
	execute ''delete from '' || $1 || ''_templates where trait = ''|| quote_literal($2) ;
	execute ''delete from '' || $1 || ''_trait_package where trait = ''|| quote_literal($2) ;
	execute ''delete from '' || $1 || ''_trait_parent where trait = ''|| quote_literal($2) ;
	execute ''delete from '' || $1 || ''_debconf where trait = ''|| quote_literal($2) ;
	execute ''delete from '' || $1 || ''_variables where trait = ''|| quote_literal($2) ;
	execute ''delete from '' || $1 || ''_traits where trait = ''|| quote_literal($2) ;
	return 0 ;
	end ;
' language 'plpgsql';
"""
def pgsql_delete_family():
    tables = ['family_environment', 'family_parent', 'families']
    return pgsql_delete('delete_family', tables, 'family')

def pgsql_delete_profile():
    tables = ['profile_variables', 'profile_family', 'profile_trait', 'profiles']
    return pgsql_delete('delete_profile', tables, 'profile')

def pgsql_delete_disk():
    tables = ['partitions', 'disk']
    return pgsql_delete('delete_disk', tables, 'diskname')

def pgsql_delete_mtype():
    tables = ['machine_disks', 'machine_modules', 'machine_types']
    return pgsql_delete('delete_mtype', tables, 'machine_type')

def pgsql_delete_filesystem():
    tables = ['filesystem_mounts', 'filesystems']
    return pgsql_delete('delete_filesystem', tables, 'filesystem')


    
    


def getcolumn(name, columns):
    ncols = [column for column in columns if column.name == name]
    if len(ncols) == 1:
        return ncols[0]
    else:
        raise Error, 'key not found'

def insert_list(cursor, table, field, list):
    for value in list:
        cursor.insert(table=table, data={field : value})

def isnonus(suite):
    if suite[-6:] == 'non-US':
        return True
    else:
        return False


def package_to_row(packagedict, section='main'):
    pcolumns = packages_columns()
    newdict = {}.fromkeys([col.name for col in pcolumns])
    for f in ['package', 'priority', 'filename', 'md5sum',
              'version', 'description', 'size', 'maintainer']:
        try:
            newdict[f] = packagedict[f]
        except KeyError:
            newdict[f] = 'Not Applicable'
    newdict['installedsize'] = packagedict['installed-size']
    if section != 'main':
        newdict['section'] = '/'.join(section, packagedict['section'])
    else:
        newdict['section'] = packagedict['section']
    return newdict


def package_to_row_quick(packagedict, section='main'):
    #newdict = {}.fromkeys([col.name for col in packages_columns()])
    fields = ['package', 'priority', 'version', 'size', 'maintainer']
    newdict = {}.fromkeys(fields)
    for f in fields:
        newdict[f] = packagedict[f]
    for f in ['filename', 'md5sum', 'description']:
        newdict[f] = '_get_rid_of_me_'
    newdict['installedsize'] = packagedict['installed-size']
    if section != 'main':
        newdict['section'] = '/'.join(section, packagedict['section'])
    else:
        newdict['section'] = packagedict['section']
    return newdict

def _insert_some_more_packages(cursor, table, packages, quick=False):
    prow = package_to_row
    if quick:
        prow = package_to_row_quick
    for package in packages:
        try:
            cursor.insert(table, prow(package))
        except OperationalError:
            pass
    
def insert_more_packages(cursor, repos, suite=None, quick=False):
    repos.source.set_path()
    repos.parse_release()
    table = ujoin(suite, 'packages')
    packages = repos.full_parse().values()
    _insert_some_more_packages(cursor, table, packages, quick=quick)
        
def insert_suite_packages(cursor, repos, quick=False):
    prow = package_to_row
    if quick:
        prow = package_to_row_quick
    suite = repos.source.suite
    if isnonus(suite):
        suite = suite.split('/')[0]
    table = ujoin(suite, 'packages')
    for section in repos.source.sections:
        for package in repos.full_parse(section).values():
            cursor.insert(table, prow(package))


def make_suite(cursor, suite):
    tables = suite_tables(suite)
    map(cursor.create_table, tables)
    cursor.execute(grant_public([x.name for x in tables]))

def update_uri(source, ext):
        source.uri = os.path.join(source.uri, ext)

def update_remote_uri(repos, ext):
    update_uri(repos.source, ext)
    update_uri(repos.local.source, ext)
    
def update_local_packagelist(repos, localdist, localsuite):
    repos.source.sections = []
    repos.local.source.sections = []
    update_remote_uri(repos, localdist)
    repos.source.suite = localsuite
    repos.local.source.suite = localsuite
    rurl = os.path.join(repos.source.uri, repos.source.suite, 'Packages.gz')
    lpath = os.path.join(repos.local.source.uri, repos.local.source.suite, 'Packages.gz')[5:]
    makepaths(os.path.dirname(lpath))
    if not os.path.isfile(lpath):
        print rurl, lpath, 'rurl, lpath'
        wget(rurl, lpath)


class SuiteHandler(object):
    def __init__(self, conn, cfg):
        self.conn = conn
        self.cfg = cfg
        self.cursor = StatementCursor(self.conn)
        self.http_mirror = 'http://%s' % self.cfg.get('debrepos', 'repos_host')
        self.local_mirror = 'file:/tmp/paellamirror'
        self.suite = None
        self.sources_rows = []

    def set_suite(self, suite):
        self.suite = suite
        self.sources_rows = self.get_sources_rows(self.suite)

    def make_suite(self):
        if self.suite is None:
            raise Error, 'the suite needs to be set first'
        self._make_suite_tables()
        self.update_packagelists()
        for row in self.sources_rows:
            self._insert_packages(row)
            
    def _make_suite_tables(self):
        tables = suite_tables(self.suite)
        map(self.cursor.create_table, tables)
        self.cursor.execute(grant_public([x.name for x in tables]))
        
    def update_packagelists(self):
        self._update_suite_packages(self.suite)
        
    def get_sources_rows(self, suite):
        table = 'apt_sources natural join suite_apt_sources'
        rows = self.cursor.select(table=table, clause=Eq('suite', suite), order=['ord'])
        return rows

    def _insert_some_packages(self, table, packages):
        for package in packages:
            try:
                self.cursor.insert(table, data=package_to_row(package))
            except OperationalError:
                pass
            
    def _insert_packages(self, src_row):
        table = '%s_packages' % self.suite
        repos = self._row2repos(src_row)
        prow = package_to_row
        local = repos.local
        if local.source.sections:
            repos.update()
            local.parse_release()
            for section in local.source.sections:
                packages = local.full_parse(section).values()
                self._insert_some_packages(table, packages)
        else:
            packages = local.full_parse().values()
            self._insert_some_packages(table, packages)
            
            
        
    def _row2repsource(self, row, http_mirror):
        lp = row.local_path
        while lp[0] == '/':
            lp = lp[1:]
        uri = os.path.join(http_mirror, lp)
        suite = row.dist
        src = 'deb %s %s' % (uri, suite)
        if not suite.endswith('/'):
            src = '%s %s' % (src, row.sections)
        r = RepositorySource(src)
        return r

    def _row2repos(self, row):
        rsource = self._row2repsource(row, self.http_mirror)
        lsource = self._row2repsource(row, self.local_mirror)
        return RemoteRepos(rsource, lsource)
                
    def _get_packages_file(self, repos):
        if repos.source.has_release():
            repos.update()
        else:
            rpath = os.path.join(repos.source.uri, repos.source.suite, 'Packages.gz')
            # the [5:] slice is to remove file: from local uri
            lpath = os.path.join(repos.local.source.uri, repos.source.suite, 'Packages.gz')[5:]
            if not os.path.isfile(lpath):
                print 'lpath is --->', lpath
                makepaths(os.path.dirname(lpath))
                print rpath, lpath, 'getting now'
                wget(rpath, lpath)
            
    def _update_suite_packages(self, suite):
        rows = self.get_sources_rows(suite)
        for row in rows:
            repos = self._row2repos(row)
            self._get_packages_file(repos)

# new functions for apt sources schema
def get_apt_sources_rows(cursor, suite):
    table = 'apt_sources natural join suite_apt_sources'
    rows = cursor.select(table=table, clause=Eq('suite', suite), order=['ord'])
    return rows





def insert_packagesNew(cfg, cursor, suite, quick=False):
    table = 'apt_sources natural join suite_apt_sources'
    rows = cursor.select(table=table, clause=Eq('suite', suite), order=['ord'])
    http_mirror = cfg.get('debrepos', 'http_mirror')
    for r in rows:
        print _row2repsource(r, http_mirror)
        

    
def insert_packages(cfg, cursor, suite, quick=False):
    source = 'deb %s %s main contrib non-free' % (cfg.get('debrepos', 'http_mirror'), suite)
    lsource = 'deb file:/tmp/paellamirror %s main contrib non-free' % suite
    #source = 'deb file:/mirrors/debian %s main contrib non-free' %suite
    rp = RemoteRepos(source, lsource)
    rp.update()
    rp.local.parse_release()
    insert_suite_packages(cursor, rp.local)
    suites = cursor.as_dict('suites', 'suite')
    if suites[suite]['nonus'] == True:
        rp.source.suite += "/non-US"
        rp.local.source.suite += "/non-US"
        rp.source.set_path()
        rp.local.source.set_path()
        rp.update()
        rp.local.parse_release()
        insert_suite_packages(cursor, rp.local, quick=quick)
    if suites[suite]['local'] == True:
        rp = RemoteRepos(source, lsource)
        update_local_packagelist(rp, 'local', '%s/' % suite)
        insert_more_packages(cursor, rp.local, suite=suite, quick=quick)
    if suites[suite]['common'] == True:
        rp = RemoteRepos(source, lsource)
        update_local_packagelist(rp, 'local', 'common/')
        insert_more_packages(cursor, rp.local, suite=suite, quick=quick)

def start_schema(conn):
    cursor = StatementCursor(conn, 'start_schema')
    map(cursor.create_sequence, primary_sequences())
    tables, mapping = primary_tables()
    map(cursor.create_table, tables)
    priorities_table = mapping['priorities']
    insert_list(cursor, priorities_table.name, 'priority', PRIORITIES)
    insert_list(cursor, 'scriptnames', 'script', SCRIPTS)
    newscripts = [s for s in MTSCRIPTS if s not in SCRIPTS]
    insert_list(cursor, 'scriptnames', 'script', newscripts)
    cursor.execute(grant_public([x.name for x in tables]))
    cursor.execute(grant_public(['current_environment'], 'ALL'))
    cursor.execute(grant_public(['partition_workspace'], 'ALL'))
    cursor.execute(plpgsql_delete_trait)
    cursor.execute(pgsql_delete_profile())
    cursor.execute(pgsql_delete_family())
    cursor.execute(pgsql_delete_disk())
    cursor.execute(pgsql_delete_mtype())
    cursor.execute(pgsql_delete_filesystem())
    
def create_database(cfg, default_traits):
    dsn = cfg.get_dsn()
    dsn['dbname'] = 'mishmash'
    conn = QuickConn(dsn)
    cmd = StatementCursor(conn, 'create_database')
    for table in cmd.tables():
        cmd.execute('drop table %s' %table)
    start_schema(conn, default_traits)
    make_suites(conn)
    cmd.execute(grant_public(cmd.tables()))
    cmd.execute(grant_public(['current_environment'], 'ALL'))
    
    
    
def doall(conn, filename):
    start_schema(conn, filename)
    parse_xmldb(conn, filename)


if __name__ == '__main__':
    from useless.db.lowlevel import QuickConn
    from useless.db.midlevel import StatementCursor
    from paella.debian.base import parse_packages, full_parse
    #cmd = CommandCursor(c, 'dsfsdf')
    def dtable():
        cmd.execute('drop table ptable')

    def dtables():
        for t in cmd.tables():
            if t != 'footable':
                cmd.execute('drop table %s' %t)


    #start_schema(cmd, traits)
    #rp = Repos('/mirrors/debian')
    #ps = rp.parse('contrib')
    #prows = [package_to_row(p) for p in ps.values()]
    from paella.profile.base import PaellaConnection
    from pyPgSQL.PgSQL import Connection, Cursor, PgLargeObject
    conn = PaellaConnection()
    cursor = StatementCursor(conn)


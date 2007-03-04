import os

from useless.base import debug
from useless.base.util import makepaths
from useless.base.util import wget

from paella.debian.base import RepositorySource
from paella.debian.repos import RemoteRepos

from useless.sqlgen.admin import grant_public
from useless.sqlgen.clause import Eq, In

from useless.db.lowlevel import OperationalError

from schema.paella_tables import suite_tables
from schema.paella_tables import packages_columns

from schema.util import insert_packages

class SuiteHandler(object):
    def __init__(self, conn, cfg):
        self.conn = conn
        self.cfg = cfg
        self.cursor = self.conn.cursor(statement=True)
        self.http_mirror = 'http://%s' % self.cfg.get('debrepos', 'repos_host')
        self.local_mirror = 'file:/tmp/paellamirror'
        self.suite = None
        self.sources_rows = []

    def set_suite(self, suite):
        self.suite = suite
        self.sources_rows = self.get_sources_rows(self.suite)

    def _check_suite(self):
        if self.suite is None:
            raise RuntimeError, 'the suite needs to be set first'

    def _get_apt_ids(self):
        return [row.apt_id for row in self.sources_rows]

    def make_suite(self):
        self._check_suite()
        debug("in make_suite ->", self.suite)
        self._make_suite_tables()
        
        #self.update_packagelists()
        #for row in self.sources_rows:
        #    self._insert_packages(row)
        apt_ids = self._get_apt_ids()
        clause = In('apt_id', apt_ids)
        select = str(self.cursor.stmt.select(table='apt_source_packages' ,
                                  fields=['distinct package'], clause=clause))
        table = '%s_packages' % self.suite
        insert = 'insert into %s %s' % (table, select)
        self.cursor.execute(insert)
        #print 'inserting %d packages for suite %s' % (len(rows), self.suite)
        #for row in rows:
        #    self.cursor.insert(table=table, data=dict(package=row.package))
            
    def _make_suite_tables(self):
        # make a new Statement
        stmt = self.cursor.stmt.__class__()
        table = 'apt_source_packages'
        fields = [col.name for col in packages_columns()]
        apt_ids = self._get_apt_ids()
        clause = In('apt_id', apt_ids)
        order = ['apt_id', 'package']
        select = stmt.select(fields=fields, table=table, clause=clause, order=order)
        suite_packages = '%s_packages' % self.suite
        create_view = 'create view %s as %s' % (suite_packages, select)
        #self.cursor.execute(create_view)
        tables = suite_tables(self.suite)
        #tables = tables[1:]
        map(self.cursor.create_table, tables)
        self.cursor.execute(grant_public([x.name for x in tables]))
        
    def update_packagelists(self):
        self._update_suite_packages(self.suite)
        
    def get_sources_rows(self, suite):
        table = 'apt_sources natural join suite_apt_sources'
        rows = self.cursor.select(table=table, clause=Eq('suite', suite), order=['ord'])
        return rows

    def _insert_some_packages(self, table, packages):
        duplicates = insert_packages(self.conn, table, packages)
        if duplicates:
            debug('These duplicates were ignored', ' '.join(duplicates))
            
    def _insert_packages(self, src_row):
        table = '%s_packages' % self.suite
        repos = self._row2repos(src_row)
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
                debug('lpath is --->', lpath)
                makepaths(os.path.dirname(lpath))
                debug(rpath, lpath, 'getting now')
                wget(rpath, lpath)
            
    def _update_suite_packages(self, suite):
        rows = self.get_sources_rows(suite)
        for row in rows:
            debug('_update_suite_packages', row)
            repos = self._row2repos(row)
            debug('repos is', repos)
            self._get_packages_file(repos)

if __name__ == '__main__':
    pass



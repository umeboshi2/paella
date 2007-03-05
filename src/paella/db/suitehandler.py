import os

from useless.base import debug
from useless.base.util import makepaths
from useless.base.util import wget

from paella.debian.base import RepositorySource
from paella.debian.repos import RemoteRepos

from useless.sqlgen.clause import Eq, In

from useless.db.lowlevel import OperationalError

from base import SuiteCursor

class SuiteHandler(object):
    def __init__(self, conn, cfg):
        self.conn = conn
        self.cfg = cfg
        self.cursor = SuiteCursor(self.conn)
        self.http_mirror = 'http://%s' % self.cfg.get('debrepos', 'repos_host')
        self.local_mirror = 'file:/tmp/paellamirror'
        self.suite = None
        self.sources_rows = []

    def get_suites(self):
        return self.cursor.get_suites()
    
    def set_suite(self, suite):
        self.suite = suite
        self.cursor.set_suite(suite)
        self.sources_rows = self.cursor.get_apt_rows()
        
    def get_apt_rows(self):
        return self.cursor.get_apt_rows()
    
    def _check_suite(self):
        if self.suite is None:
            raise RuntimeError, 'the suite needs to be set first'

    def _get_apt_ids(self):
        return [row.apt_id for row in self.sources_rows]

    # this is some code i want to keep for a little while
    # in case I want to make a view out of the packages table
    def _create_package_view(self):
        from schema.tables import packages_columns
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
        
if __name__ == '__main__':
    pass



import os

from useless.base import debug
from useless.base.util import makepaths
from useless.base.util import wget

from paella.debian.base import RepositorySource
from paella.debian.repos import RemoteRepos

from useless.sqlgen.admin import grant_public
from useless.sqlgen.clause import Eq

from useless.db.lowlevel import OperationalError

from paella_tables import suite_tables

#from paella_tables import packages_columns, SCRIPTS
#from paella_tables import MTSCRIPTS
from paella_tables import packages_columns

#from paella import deprecated

# used in suite handler
# package_to_row


PRIORITIES = ['first', 'high', 'pertinent', 'none', 'postinstall', 'last']
SUITES = ['sid', 'woody'] 




    
def getcolumn(name, columns):
    ncols = [column for column in columns if column.name == name]
    if len(ncols) == 1:
        return ncols[0]
    else:
        raise Error, 'key not found'

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
            #newdict[f] = packagedict[f].encode('utf-8', 'ignore')
            # decode to utf-8 ignoring errors seems to work here
            # then re-encode to utf-8
            # not sure if any information is lost here, I probably couln't
            # read it anyway.
            newdict[f] = packagedict[f].decode('utf-8', 'ignore').encode('utf-8')
        except KeyError:
            newdict[f] = 'Not Applicable'
    newdict['installedsize'] = packagedict['installed-size']
    if section != 'main':
        newdict['section'] = '/'.join(section, packagedict['section'])
    else:
        newdict['section'] = packagedict['section']
    return newdict

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

    def make_suite(self):
        if self.suite is None:
            raise RuntimeError, 'the suite needs to be set first'
        debug("in make_suite ->", self.suite)
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
        duplicates = []
        for package in packages:
            try:
                # normal package info
                data = package_to_row(package)
                # just the package names now
                #data = dict(package=package['package'])
                self.cursor.insert(table, data=data)
            except OperationalError, inst:
                if inst.args[0].startswith('ERROR:  duplicate key violates unique constraint'):
                    duplicates.append(package['package'])
                    pass
                else:
                    print 'OperationalError occured:',
                    print 'number of arguements', len(inst.args)
                    count = 1
                    for arg in inst.args:
                        print 'arg%d' % count, arg
                    raise inst
        if duplicates:
            debug('These duplicates were ignored', ' '.join(duplicates))
            
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



import os

from useless.base import debug
from useless.base.util import wget
from useless.base.util import makepaths
from useless.sqlgen.clause import Eq

from paella.base.util import get_architecture
from paella.debian.base import RepositorySource
from paella.debian.repos import RemoteRepos

from schema.util import convert_package_data


class AptSourceHandler(object):
    def __init__(self, conn):
        self.conn = conn
        self.cursor = self.conn.cursor(statement=True)
        self.local_mirror = 'file:/tmp/paellamirror'

    def get_apt_rows(self):
        return self.cursor.select(table='apt_sources', order=['apt_id'])
    
    def get_apt_row(self, apt_id):
        clause = Eq('apt_id', apt_id)
        return self.cursor.select_row(table='apt_sources', clause=clause)
    
    def insert_packages(self, apt_id, uri=None):
        repos = self._make_repository(apt_id, uri)
        self._get_packages_file(repos)
        packages = self._get_packages_from_repository(repos)
        self._insert_packages(apt_id, packages)

    def insert_apt_source_row(self, apt_id, uri, dist, sections, local_path):
        data = dict(apt_id=apt_id, uri=uri, dist=dist,
                    sections=sections, local_path=local_path)
        table = 'apt_sources'
        self.cursor.insert(table=table, data=data)
        
    def _insert_packages(self, apt_id, packages):
        table = 'apt_source_packages'
        extra = dict(apt_id=apt_id)
        self.report_total_packages(len(packages))
        for package in packages:
            data = convert_package_data(package)
            data.update(extra)
            self.cursor.insert(table=table, data=data)
            self.report_package_inserted(package['package'])

    def _get_packages_from_repository(self, repos):
        local = repos.local
        if local.source.sections:
            repos.update()
            local.parse_release()
            packages = []
            for section in local.source.sections:
                packages += local.full_parse(section).values()
        else:
            packages = local.full_parse().values()
        return packages
    
    def report_package_inserted(self, package):
        debug('package %s inserted' % package)

    def report_total_packages(self, total):
        print "%s packages" % total
        

    def _make_repository_source(self, apt_id, uri=None):
        row = self.cursor.select_row(table='apt_sources', clause=Eq('apt_id', apt_id))
        if uri is None:
            uri = row.uri
        src = 'deb %s %s' % (uri, row.dist)
        if not row.dist.endswith('/'):
            src = '%s %s' % (src, row.sections)
        r = RepositorySource(src)
        return r

    def _make_repository(self, apt_id, uri=None):
        rsource = self._make_repository_source(apt_id, uri=uri)
        lsource = self._make_repository_source(apt_id, uri=self.local_mirror)
        arch = get_architecture()
        return RemoteRepos(rsource, lsource, arch=arch)
    
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

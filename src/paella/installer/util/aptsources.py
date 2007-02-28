import os
import urlparse

from os.path import join
import tempfile
import commands
from time import sleep

from useless.base import Error
from useless.base.util import makepaths, runlog, echo

from paella import deprecated
from paella.debian.base import RepositorySource

from paella.db import DefaultEnvironment
from paella.db.base import SuiteCursor



def _is_option_true(cfg, section, option):
    return cfg.has_option(section, option) and cfg.get(section, option) == 'true'

def _make_source_line(parts):
    return ' '.join(parts) + '\n'

def urlunparse(protocol, host, local_path):
    return urlparse.urlunparse((protocol, host, local_path, '', '', ''))


# here uri is protocol://host/local_path
def make_sources_list_lines(apt_rows, uri=None):
    lines = []
    for row in apt_rows:
        if uri is None:
            main_uri = row.uri
        else:
            main_uri = uri
        parsed = urlparse.urlparse(main_uri)
        protocol = parsed[0]
        host = parsed[1]
        source = RepositorySource()
        source.uri = urlunparse(protocol, host, row.local_path)
        if row.sections == '/' and row.dist.endswith('/'):
            source.sections = []
        else:
            source.sections = [s.strip() for s in row.sections.split()]
        source.suite = row.dist
        lines.append(str(source))
        # will probably make this optional later
        if True:
            source.type = 'deb-src'
            lines.append(str(source))
    return lines

def make_sources_list_common(conn, target, suite, installer=False):
    defenv = DefaultEnvironment(conn)
    suitecursor = SuiteCursor(conn)
    apt_rows = suitecursor.get_apt_rows(suite)
    if installer:
        # while installing use sources from local mirror
        uri = defenv.get('installer', 'http_mirror')
    else:
        # otherwise use official sources list
        uri = None
    apt_lines = make_sources_list_lines(apt_rows, uri=uri)
    aptdir = os.path.join(target, 'etc', 'apt')
    makepaths(aptdir)
    sources_list = file(os.path.join(aptdir, 'sources.list'), 'w')
    for line in apt_lines:
        sources_list.write('%s\n' % line)
    sources_list.write('\n')
    sources_list.close()

def make_sources_list(conn, target, suite):
    make_sources_list_common(conn, target, suite, installer=True)

def make_official_sources_list(conn, target, suite):
    make_sources_list_common(conn, target, suite)

if __name__ == '__main__':
    from paella.db import PaellaConnection
    conn = PaellaConnection()
    cursor = SuiteCursor(conn)
    rows = cursor.get_apt_rows('desksarge')
    msll = make_sources_list_lines
    

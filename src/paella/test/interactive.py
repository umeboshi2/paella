from os.path import join
from paella.base import debug, Error
from paella.base.util import ujoin

from paella.sqlgen.clause import Eq, In, NotIn, Like

from paella.base.config import Configuration
from paella.db.lowlevel import QuickConn
from paella.db.midlevel import StatementCursor

from paella.gtk import dialogs
from paella.gtk.windows import MenuWindow

#from paella.admin.repos_client import RepositoryBrowserWindow as rbw
from paella.admin.template import TemplateManager
from paella.admin.interactive import Select
#s = Select(conn)

from paella.gtk.utils import DownloadPoolBox as dpb
from paella.admin.management import Manager, SuiteManager
from paella.admin.debconf import DebconfEditorWin, DebconfBrowser

cfg = Configuration()

m = Manager()
m.set_usize(200, 300)
m.set_uposition(1050, 730)

#mirror = 'http://ftp.us.debian.org/debian/dists/'
mirror = 'http://paella/debian/dists.orig/'
m.dbconnect(cfg['dbname'])
#tm = TemplateManager(m.conn, 'woody')
#dc.debconf.set_config('/var/cache/debconf/config.dat')
#db = DebconfBrowser(m.conn, 'sid', 'default')

from paella.profile.trait import TraitDebconf
from paella.profile.profile import ProfileEnvironment
pe = ProfileEnvironment(m.conn, 'paella')
pe.set_trait('base')

td = TraitDebconf(m.conn, 'sid')

w = SuiteManager(m.conn, 'woody')
s = SuiteManager(m.conn, 'sid')

w.set_uposition(600, 20)
s.set_uposition(600, 60)

import os
from qt import SLOT, SIGNAL, Qt

from kdecore import KApplication, KIconLoader
from kdecore import KStandardDirs
from kdecore import KLockFile

from kdeui import KMainWindow, KSystemTray
from kdeui import KPopupMenu

from kdeui import KListView, KListViewItem

from paella.profile.base import PaellaConfig
from paella.profile.base import PaellaConnection
from paella.db.midlevel import StatementCursor
from paella.kde.base import MainWindow
from paella.kde.trait import TraitMainWindow
from paella.kde.profile import ProfileMainWindow
from paella.kde.family import FamilyMainWindow

class PaellaMainApplication(KApplication):
    def __init__(self, *args):
        KApplication.__init__(self)
        self.cfg = PaellaConfig()
        self.conn = PaellaConnection(self.cfg)
        dirs = KStandardDirs()
        self.tmpdir = str(dirs.findResourceDir('tmp', '/'))
        self.datadir = str(dirs.findResourceDir('data', '/'))
        self.socketdir = str(dirs.findResourceDir('socket', '/'))
        dsn = {}
        

class PaellaMainWindow(KMainWindow):
    def __init__(self, app, *args):
        KMainWindow.__init__(self, *args)
        self.app = app
        self.icons = KIconLoader()
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.conn = app.conn
        self.cfg = app.cfg
        self.cursor = StatementCursor(self.conn)
        self.listView = KListView(self)
        self.listView.setRootIsDecorated(True)
        self.listView.addColumn('widget')
        self.setCentralWidget(self.listView)
        self.refreshListView()
        self.connect(self.listView,
                     SIGNAL('selectionChanged()'), self.selectionChanged)

    def initActions(self):
        collection = self.actionCollection()
        
    def initMenus(self):
        mainMenu = KPopupMenu(self)
        menus = [mainMenu]
        self.menuBar().insertItem('&Main', mainMenu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))

    def initToolbar(self):
        toolbar = self.toolBar()
        
    def refreshListView(self):
        suite_folder = KListViewItem(self.listView, 'suites')
        for row in self.cursor.select(table='suites'):
            item = KListViewItem(suite_folder, row.suite)
            item.suite = row.suite
        profile_folder = KListViewItem(self.listView, 'profiles')
        profile_folder.profiles = True
        family_folder = KListViewItem(self.listView, 'families')
        family_folder.families = True
        
    def selectionChanged(self):
        current = self.listView.currentItem()
        if hasattr(current, 'suite'):
            print 'suite is', current.suite
            TraitMainWindow(self.app, self, current.suite)
        elif hasattr(current, 'profiles'):
            ProfileMainWindow(self.app, self)
        elif hasattr(current, 'families'):
            print 'running families'
            FamilyMainWindow(self.app, self)

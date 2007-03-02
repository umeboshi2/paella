import os
from qt import SLOT, SIGNAL, Qt
from qt import PYSIGNAL

from kdecore import KApplication, KIconLoader
from kdecore import KStandardDirs
from kdecore import KLockFile

from kdeui import KMainWindow, KSystemTray
from kdeui import KPopupMenu, KStdAction

from kdeui import KListView, KListViewItem

from paella.base import PaellaConfig
from paella.db import PaellaConnection

from useless.db.midlevel import StatementCursor
from useless.kbase.gui import MainWindow
from useless.kdb import BaseDatabase

from paella.kde.base.actions import ManageFamilies
from paella.kde.base.actions import EditTemplateAction
from paella.kde.base.actions import ManageSuiteAction
from paella.kde.trait import TraitMainWindow
from paella.kde.profile import ProfileMainWindow
from paella.kde.family import FamilyMainWindow
from paella.kde.machine import MachineMainWindow
from paella.kde.differ import DifferWin
from paella.kde.environ import DefEnvWin
from paella.kde.installer import InstallerMainWin

class PaellaMainApplication(KApplication):
    def __init__(self):
        KApplication.__init__(self)
        self.cfg = PaellaConfig()
        self.conn = PaellaConnection(self.cfg)
        self.db = BaseDatabase(self.conn, 'paelladb', None)
        dirs = KStandardDirs()
        self.tmpdir = str(dirs.findResourceDir('tmp', '/'))
        self.datadir = str(dirs.findResourceDir('data', '/'))
        self.socketdir = str(dirs.findResourceDir('socket', '/'))
        #print self.tmpdir, self.datadir, self.socketdir
        dsn = {}
        

class PaellaMainWindow(KMainWindow):
    def __init__(self, parent=None, name='PaellaMainWindow'):
        KMainWindow.__init__(self, parent, name)
        # setup app pointer
        self.app = KApplication.kApplication()
        # I don't know why the KIconLoader is called
        self.icons = KIconLoader()
        
        self._environ_types = ['default', 'current']
        self._differ_types = ['trait', 'family']

        # setup convenient pointers to connection and config objects
        self.conn = self.app.conn
        self.cfg = self.app.cfg
        # make a cursor
        self.cursor = StatementCursor(self.conn)
        self._suites = [x.suite for x in self.cursor.select(table='suites')]

        # setup actions, menus, and toolbar
        self.initActions()
        self.initMenus()
        self.initToolbar()

        # we use a listview instead of a regular menu
        # to call other parts of the application
        self.listView = KListView(self)
        self.listView.setRootIsDecorated(True)
        self.listView.addColumn('widget')
        self.setCentralWidget(self.listView)
        self.refreshListView()
        self.setCaption('Main Menu')
        self.connect(self.listView,
                     SIGNAL('selectionChanged()'), self.selectionChanged)

    def initActions(self):
        collection = self.actionCollection()
        self.manageFamiliesAction = ManageFamilies(self.slotManageFamilies, collection)
        self.editTemplatesAction = EditTemplateAction(self.slotEditTemplates, collection)
        self.quitAction = KStdAction.quit(self.app.quit, collection)
        self.suiteActions = {}
        for suite in self._suites:
            self.suiteActions[suite] = ManageSuiteAction(suite, self.slotManageSuite, collection)
        self.environActions = {}
        self.differActions = {}
        
    def initMenus(self):
        mainMenu = KPopupMenu(self)
        actions = self.suiteActions.values()
        actions += [self.manageFamiliesAction,
                   self.editTemplatesAction,
                   self.quitAction]
        self.menuBar().insertItem('&Main', mainMenu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))
        for action in actions:
            action.plug(mainMenu)
            
    def initToolbar(self):
        toolbar = self.toolBar()
        actions = [self.manageFamiliesAction,
                   self.editTemplatesAction,
                   self.quitAction]
        for action in actions:
            action.plug(toolbar)
            
    def refreshListView(self):
        suite_folder = KListViewItem(self.listView, 'suites')
        for row in self.cursor.select(table='suites'):
            item = KListViewItem(suite_folder, row.suite)
            item.suite = row.suite
        profile_folder = KListViewItem(self.listView, 'profiles')
        profile_folder.profiles = True
        family_folder = KListViewItem(self.listView, 'families')
        family_folder.families = True
        machine_folder = KListViewItem(self.listView, 'machines')
        machine_folder.machines = True
        differ_folder = KListViewItem(self.listView, 'differs')
        differ_folder.differs = True
        for dtype in ['trait', 'family']:
            item = KListViewItem(differ_folder, dtype)
            item.dtype = dtype
        environ_folder = KListViewItem(self.listView, 'environ')
        environ_folder.environ = True
        for etype in ['default', 'current']:
            item = KListViewItem(environ_folder, etype)
            item.etype = etype
        installer_folder = KListViewItem(self.listView, 'installer')
        installer_folder.installer = True
        
    def selectionChanged(self):
        current = self.listView.currentItem()
        if hasattr(current, 'suite'):
            print 'suite is', current.suite
            TraitMainWindow(self.app, self, current.suite)
        elif hasattr(current, 'profiles'):
            ProfileMainWindow(self.app, self)
        elif hasattr(current, 'families'):
            self.slotManageFamilies()
        elif hasattr(current, 'machines'):
            MachineMainWindow(self.app, self)
        elif hasattr(current, 'dtype'):
            print 'differ', current.dtype
            DifferWin(self.app, self, current.dtype)
        elif hasattr(current, 'etype'):
            DefEnvWin(self.app, self, current.etype)
        elif hasattr(current, 'installer'):
            InstallerMainWin(self.app, self)

    def slotManageFamilies(self):
        print 'running families'
        FamilyMainWindow(self.app, self)
            
    def slotEditTemplates(self):
        print 'edit templates'

    def slotEditEnvironment(self, etype):
        print 'in slotEditEnvironment etype is', etype, type(etype)
        DefEnvWin(self.app, self, etype)

    def slotManageSuite(self, wid=-1):
        print 'in slotManageSuite suite is', wid
        TraitMainWindow(self.app, self, current.suite)
        

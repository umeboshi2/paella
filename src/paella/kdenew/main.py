from qt import SIGNAL

from kdecore import KApplication
from kdecore import KStandardDirs

from kdeui import KPopupMenu
from kdeui import KStdAction
from kdeui import KMessageBox
from kdeui import KListView, KListViewItem

from useless.kdebase.mainwin import BaseMainWindow

from paella.base import PaellaConfig
from paella.db import PaellaConnection

# import actions
from paella.kdenew.base.actions import ManageFamilies
from paella.kdenew.base.actions import EditTemplateAction
from paella.kdenew.base.actions import ManageSuiteAction

from paella.kdenew.base.mainwin import BasePaellaWindow

# import child windows
from paella.kdenew.trait import TraitMainWindow
from paella.kdenew.differ import DifferWindow

class PaellaMainApplication(KApplication):
    def __init__(self):
        KApplication.__init__(self)
        self.cfg = PaellaConfig()
        self.conn = PaellaConnection(self.cfg)
        dirs = KStandardDirs()
        self.tmpdir = str(dirs.findResourceDir('tmp', '/'))
        self.datadir = str(dirs.findResourceDir('data', '/'))
        # I probably don't need the socket dir
        self.socketdir = str(dirs.findResourceDir('socket', '/'))

class BasePaellaMainWindow(BasePaellaWindow):
    def __init__(self, parent=None, name='BasePaellaMainWindow'):
        BasePaellaWindow.__init__(self, None, name)
        self.initPaellaCommon()
        # make a cursor
        self.cursor = self.conn.cursor(statement=True)
        # figure out what suites are available
        self._suites = [row.suite for row in self.cursor.select(table='suites')]
        # setup actions, menus, and toolbar
        self.initActions()
        self.initMenus()
        self.initToolbar()

    def initActions(self):
        collection = self.actionCollection()
        self.manageFamiliesAction = ManageFamilies(self.slotManageFamilies,
                                                   collection)
        self.editTemplatesAction = EditTemplateAction(self.slotEditTemplates,
                                                      collection)
        # in the main window assign quit to app.quit
        self.quitAction = KStdAction.quit(self.app.quit, collection)
        self.suiteActions = {}
        for suite in self._suites:
            self.suiteActions[suite] = ManageSuiteAction(suite,
                                                         self.slotManageSuite, collection)
        # these will be similar to suiteActions
        # where the key is the context
        self.environActions = {}
        self.differActions = {}

    def initMenus(self):
        mainmenu = KPopupMenu(self)
        suitemenu = KPopupMenu(self)
        suite_actions = self.suiteActions.values()
        main_actions = [self.manageFamiliesAction,
                        self.editTemplatesAction,
                        self.quitAction]
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)
        menubar.insertItem('&Suite', suitemenu)
        menubar.insertItem('&Help', self.helpMenu(''))
        for action in main_actions:
            action.plug(mainmenu)
        for action in suite_actions:
            action.plug(suitemenu)
        
    def initToolbar(self):
        toolbar = self.toolBar()
        actions = [self.manageFamiliesAction,
                   self.editTemplatesAction,
                   self.quitAction]
        for action in actions:
            action.plug(toolbar)
            

# This is the old way to select what you want to do
# It probably breaks some HIG's, but it may be preferable.
class PaellaMainWindowSmall(BasePaellaMainWindow):
    def __init__(self, parent=None, name='PaellaMainWindowSmall'):
        print 'using window', name
        BasePaellaMainWindow.__init__(self, parent, name)
        # In this window, we use a listbox to select the other
        # parts of the application
        self.listView = KListView(self)
        self.listView.setRootIsDecorated(True)
        self.listView.addColumn('widget')
        self.setCentralWidget(self.listView)
        self.refreshListView()
        self.setCaption('Main Menu')
        self.connect(self.listView,
                     SIGNAL('selectionChanged()'),
                     self.selectionChanged)
        
    def refreshListView(self):
        suite_folder = KListViewItem(self.listView, 'suites')
        suite_folder.folder = True
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
        differ_folder.folder = True
        for dtype in ['trait', 'family']:
            item = KListViewItem(differ_folder, dtype)
            item.dtype = dtype
        environ_folder = KListViewItem(self.listView, 'environ')
        environ_folder.environ = True
        environ_folder.folder = True
        for etype in ['default', 'current']:
            item = KListViewItem(environ_folder, etype)
            item.etype = etype
        installer_folder = KListViewItem(self.listView, 'installer')
        installer_folder.installer = True
        
    def selectionChanged(self):
        current = self.listView.currentItem()
        win = None
        if hasattr(current, 'suite'):
            print 'suite is', current.suite
            win = TraitMainWindow(self, current.suite)
        elif hasattr(current, 'profiles'):
            win = ProfileMainWindow(self)
        elif hasattr(current, 'families'):
            self.slotManageFamilies()
        elif hasattr(current, 'machines'):
            win = MachineMainWindow(self)
        elif hasattr(current, 'dtype'):
            print 'differ', current.dtype
            win = DifferWindow(self, current.dtype)
        elif hasattr(current, 'etype'):
            win = DefEnvWin(self, current.etype)
        elif hasattr(current, 'installer'):
            win = InstallerMainWin(self)
        elif hasattr(current, 'folder'):
            # nothing important selected, do nothing
            pass
        else:
            KMessageBox.error(self, 'something bad happened in the list selection')
        if win is not None:
            win.show()
        
    def slotManageFamilies(self):
        print 'running families'
        #FamilyMainWindow(self.app, self)
        KMessageBox.error(self, 'Managing families unimplemented')
        
    def slotEditTemplates(self):
        print 'edit templates'
        KMessageBox.error(self, 'Edit Templates unimplemented')
        
    def slotEditEnvironment(self, etype):
        print 'in slotEditEnvironment etype is', etype, type(etype)
        #DefEnvWin(self.app, self, etype)
        KMessageBox.error(self, 'Edit Environment is unimplemented')
        
    def slotManageSuite(self, wid=-1):
        print 'in slotManageSuite suite is', wid
        #TraitMainWindow(self.app, self, current.suite)
        KMessageBox.error(self, 'Managing suites unimplemented')
        
        
    
class PaellaMainWindow(BasePaellaMainWindow):
    pass

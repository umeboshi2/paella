from qt import SIGNAL

from kdecore import KApplication
from kdecore import KStandardDirs

from kdeui import KPopupMenu
from kdeui import KStdAction
from kdeui import KMessageBox
from kdeui import KListView, KListViewItem

from kfile import KDirSelectDialog

from useless.kdebase.mainwin import BaseMainWindow

from paella.base import PaellaConfig
from paella.db import PaellaConnection

# database manager
from paella.db.main import DatabaseManager

# import actions
from paella.kdenew.base.actions import ManageFamilies
from paella.kdenew.base.actions import EditTemplateAction
from paella.kdenew.base.actions import ManageSuiteAction
from paella.kdenew.base.actions import ImportDatabaseAction
from paella.kdenew.base.actions import ExportDatabaseAction


from paella.kdenew.base.mainwin import BasePaellaWindow

# import child windows
from paella.kdenew.trait import TraitMainWindow
from paella.kdenew.differ import DifferWindow
from paella.kdenew.profile import ProfileMainWindow
from paella.kdenew.environ import EnvironmentWindow
from paella.kdenew.family import FamilyMainWindow
from paella.kdenew.machine.main import MachineMainWindow
from paella.kdenew.clients import ClientsMainWindow

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
        if 'suites' in self.cursor.tables():
            self._suites = [row.suite for row in self.cursor.select(table='suites')]
        else:
            self._suites = []
        # setup actions, menus, and toolbar
        self.initActions()
        self.initMenus()
        self.initToolbar()

        # setup dialog pointers
        self._import_export_dirsel_dialog = None
        
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
        self.dbactions = {}
        self.dbactions['import'] = ImportDatabaseAction(self.slotImportDatabase, collection)
        self.dbactions['export'] = ExportDatabaseAction(self.slotExportDatabase, collection)
        
        # these will be similar to suiteActions
        # where the key is the context
        self.environActions = {}
        self.differActions = {}

    def initMenus(self):
        mainmenu = KPopupMenu(self)
        dbmenu = KPopupMenu(self)
        suitemenu = KPopupMenu(self)
        suite_actions = self.suiteActions.values()
        main_actions = [self.manageFamiliesAction,
                        self.editTemplatesAction,
                        self.quitAction]
        dbactions = [self.dbactions[action] for action in ('import', 'export')]
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)
        menubar.insertItem('&Database', dbmenu)
        menubar.insertItem('&Suite', suitemenu)
        menubar.insertItem('&Help', self.helpMenu(''))
        for action in main_actions:
            action.plug(mainmenu)
        for action in dbactions:
            action.plug(dbmenu)
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
        tables = self.cursor.tables()
        print 'tables', tables
        if not tables:
            msg = 'There are no tables in the database.\n'
            msg += 'Please import a database.'
            KMessageBox.error(self, msg)
        
    def refreshListView(self):
        suite_folder = KListViewItem(self.listView, 'suites')
        suite_folder.folder = True
        for suite in self._suites:
            item = KListViewItem(suite_folder, suite)
            item.suite = suite
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
        clients_folder = KListViewItem(self.listView, 'clients')
        clients_folder.clients = True
        
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
            win = EnvironmentWindow(self, current.etype)
        elif hasattr(current, 'installer'):
            win = InstallerMainWin(self)
        elif hasattr(current, 'clients'):
            win = ClientsMainWindow(self)
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
        #KMessageBox.error(self, 'Managing families unimplemented')
        win = FamilyMainWindow(self)
        win.show()
        
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
        
        
    def slotImportDatabase(self):
        print 'slotImportDatabase called'
        self._select_import_export_directory('import')

    def slotExportDatabase(self):
        print 'slotExportDatabase called'
        self._select_import_export_directory('export')

    # here action is either 'import' or 'export'
    def _select_import_export_directory(self, action):
        if self._import_export_dirsel_dialog is None:
            default_db_path = self.app.cfg.get('database', 'import_path')
            dlg = KDirSelectDialog(default_db_path, False , self)
            dlg.connect(dlg, SIGNAL('okClicked()'), self._import_export_directory_selected)
            dlg.db_action = action
            dlg.show()
            self._import_export_dirsel_dialog = dlg
        else:
            KMessageBox.error('This dialog is already open, or bug in code.')
            
    def _import_export_directory_selected(self):
        dlg = self._import_export_dirsel_dialog
        if dlg is None:
            raise RuntimeError, 'There is no import export dialog'
        url = dlg.url()
        fullpath = str(url.path())
        action = dlg.db_action
        print 'selected fullpath', fullpath
        print 'action is', dlg.db_action
        dbm = DatabaseManager(self.conn)
        if action == 'import':
            dbm.restore(fullpath)
        elif action == 'export':
            dbm.backup(fullpath)
        else:
            KMessageBox.error(self, 'action %s not supported' % action)
    
class PaellaMainWindow(BasePaellaMainWindow):
    pass

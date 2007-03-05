from qt import SIGNAL
from qt import PYSIGNAL
from kdeui import KPopupMenu
from kdeui import KStdAction
from kdeui import KMessageBox
from kdeui import KListView, KListViewItem

from kfile import KDirSelectDialog

from useless.kdebase.mainwin import BaseMainWindow

# database manager
from paella.db.main import DatabaseManager

# import actions
from paella.kde.base.actions import ManageFamilies
from paella.kde.base.actions import EditTemplateAction
from paella.kde.base.actions import ManageSuiteAction
#from paella.kde.base.actions import ImportDatabaseAction
#from paella.kde.base.actions import ExportDatabaseAction
#from paella.kde.base.actions import ConnectDatabaseAction
#from paella.kde.base.actions import DisconnectDatabaseAction
from paella.kde.base.actions import dbactions
from paella.kde.base.actions import ManageAptSourcesAction
from paella.kde.base.actions import OpenSuiteManagerAction

from paella.kde.base.mainwin import BasePaellaWindow
from paella.kde.base.dialogs import PaellaConnectionDialog
from paella.kde.base.dialogs import ExportDbProgressDialog

# import child windows
from paella.kde.trait.main import TraitMainWindow
from paella.kde.differ import DifferWindow
from paella.kde.profile import ProfileMainWindow
from paella.kde.environ import EnvironmentWindow
from paella.kde.family import FamilyMainWindow
from paella.kde.machine.main import MachineMainWindow
from paella.kde.clients import ClientsMainWindow
from paella.kde.aptsrc.main import AptSourceMainWindow
from paella.kde.suites.main import SuiteManagerWindow

class BasePaellaMainWindow(BasePaellaWindow):
    def __init__(self, parent=None, name='BasePaellaMainWindow'):
        BasePaellaWindow.__init__(self, None, name)
        self.initPaellaCommon()
        self._suites = []
        # make a cursor
        if self.conn is not None:
            self.cursor = self.conn.cursor(statement=True)
            # figure out what suites are available
            if 'suites' in self.cursor.tables():
                self._suites = [row.suite for row in self.cursor.select(table='suites')]
        # setup actions, menus, and toolbar
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.statusbar = self.statusBar()
        self.statusbar.message('Disconnected')
        
        # setup dialog pointers
        self._import_export_dirsel_dialog = None
        
    def initActions(self):
        collection = self.actionCollection()
        self.manageFamiliesAction = \
                                  ManageFamilies(self.slotManageFamilies,
                                                 collection)
        self.editTemplatesAction = \
                                 EditTemplateAction(self.slotEditTemplates,
                                                    collection)
        self.manageAptSourcesAction = \
                                    ManageAptSourcesAction(self.slotManageAptSources,
                                                           collection)
        self.openSuiteManagerAction = OpenSuiteManagerAction(
            self.slotOpenSuiteManager, collection)
        
        # in the main window assign quit to app.quit
        self.quitAction = KStdAction.quit(self.app.quit, collection)
        self.suiteActions = {}
        for suite in self._suites:
            self.suiteActions[suite] = ManageSuiteAction(suite,
                                                         self.slotManageSuite, collection)
        # define database action slots
        self._dbactionslots = dict(export=self.slotExportDatabase,
                                   connect=self.slotConnectDatabase,
                                   disconnect=self.slotDisconnectDatabase)
        # don't collide with keyword
        self._dbactionslots['import'] = self.slotImportDatabase
        self.dbactions = dict()
        for action in dbactions.keys():
            self.dbactions[action] = dbactions[action](self._dbactionslots[action], collection)
        # these will be similar to suiteActions
        # where the key is the context
        self.environActions = {}
        self.differActions = {}

    def initMenus(self):
        mainmenu = KPopupMenu(self)
        dbmenu = KPopupMenu(self)
        self.suitemenu = KPopupMenu(self)
        suite_actions = self.suiteActions.values()
        main_actions = [self.manageAptSourcesAction,
                        self.openSuiteManagerAction,
                        self.quitAction]
        actions = ['connect', 'disconnect', 'import', 'export']
        dbactions = [self.dbactions[action] for action in actions]
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)
        menubar.insertItem('&Database', dbmenu)
        menubar.insertItem('&Suite', self.suitemenu)
        menubar.insertItem('&Help', self.helpMenu(''))
        for action in main_actions:
            action.plug(mainmenu)
        for action in dbactions:
            action.plug(dbmenu)
        for action in suite_actions:
            action.plug(self.suitemenu)
        
    def initToolbar(self):
        toolbar = self.toolBar()
        actions = [self.dbactions['connect'],
                   self.dbactions['disconnect'],
                   self.manageAptSourcesAction,
                   self.openSuiteManagerAction,
                   self.quitAction]
        for action in actions:
            action.plug(toolbar)
            

    def slotConnectDatabase(self):
        win = PaellaConnectionDialog(self)
        dsn = self.cfg.get_dsn()
        fields = ['dbhost', 'dbname', 'dbusername']
        data = dict([(f, dsn[f]) for f in fields])
        win.setRecordData(data)
        win.connect(win, SIGNAL('okClicked()'), win.slotConnectDatabase)
        win.connect(win, PYSIGNAL('dbconnected(data)'), self.slotDbConnected)
        win.show()

    def slotDisconnectDatabase(self):
        self.app.disconnect_database()
        self.statusbar.message('Disconnected')
        
    def slotDbConnected(self, dsn):
        print dsn
        print 'slotDbConnected'
        for action in self.suiteActions.values():
            action.unplug(self.suitemenu)
        self.suite_actions = {}
        self.cursor = self.app.conn.cursor(statement=True)
        if 'suites' in self.cursor.tables():
            self._suites = [row.suite for row in self.cursor.select(table='suites')]
        collection = self.actionCollection()
        for suite in self._suites:
            self.suiteActions[suite] = ManageSuiteAction(suite,
                                                         self.slotManageSuite, collection)
        for action in self.suiteActions.values():
            action.plug(self.suitemenu)
        self.statusbar.message('Connected to %s on host %s' % (dsn['dbname'], dsn['dbhost']))
        if not self.cursor.tables():
            yesno = KMessageBox.questionYesNo(self, 'create primary tables?')
            if yesno == KMessageBox.Yes:
                dbm = DatabaseManager(self.app.conn)
                dbm.importer.start_schema()
            print yesno == KMessageBox.Yes
            
    def slotManageAptSources(self):
        win = AptSourceMainWindow(self)
        win.show()
        
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
        if self.app.conn is not None:
            self.refreshListView()
        self.setCaption('Main Menu')
        self.connect(self.listView,
                     SIGNAL('selectionChanged()'),
                     self.selectionChanged)

    def refreshListView(self):
        self.listView.clear()
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

    def slotOpenSuiteManager(self):
        win = SuiteManagerWindow(self)
        win.show()

    def _destroy_dialog(self):
        self._dialog = None
        self._import_export_dirsel_dialog = None
        
    def _connect_destroy_dialog(self, dialog):
        dialog.connect(dialog, SIGNAL('cancelClicked()'), self._destroy_dialog)
        dialog.connect(dialog, SIGNAL('closeClicked()'), self._destroy_dialog)
        
    # here action is either 'import' or 'export'
    def _select_import_export_directory(self, action):
        if self._import_export_dirsel_dialog is None:
            default_db_path = self.app.cfg.get('database', 'default_path')
            win = KDirSelectDialog(default_db_path, False , self)
            win.connect(win, SIGNAL('okClicked()'), self._import_export_directory_selected)
            self._connect_destroy_dialog(win)
            win.db_action = action
            win.show()
            self._import_export_dirsel_dialog = win
        else:
            KMessageBox.error(self, 'This dialog is already open, or bug in code.')
            
    def _import_export_directory_selected(self):
        win = self._import_export_dirsel_dialog
        if win is None:
            raise RuntimeError, 'There is no import export dialog'
        url = win.url()
        fullpath = str(url.path())
        action = win.db_action
        print 'selected fullpath', fullpath
        print 'action is', win.db_action
        dbm = DatabaseManager(self.app.conn)
        if action == 'import':
            dbm.restore(fullpath)
        elif action == 'export':
            #dbm.backup(fullpath)
            win = ExportDbProgressDialog(self)

            exporter = dbm.exporter
            exporter.report_total_suites = win.suite_progess.setTotalSteps
            exporter.report_suite_exported = win.suite_progess.step_progress
            exporter.report_total_traits = win.trait_progress.setTotalSteps
            exporter.report_trait_exported = win.trait_progress.step_progress
            #exporter.report_all_traits_exported = win.trait_progress.progressbar.reset
            exporter.report_start_exporting_traits = win.trait_progress.progressbar.reset
            
            profiles = exporter.profiles
            family = exporter.family
            profiles.report_total_profiles = win.profile_progress.setTotalSteps
            profiles.report_profile_exported = win.profile_progress.step_progress
            family.report_total_families = win.family_progress.setTotalSteps
            family.report_family_exported = win.family_progress.step_progress

                        
            win.show()
            self.app.processEvents()
            dbm.export_all(fullpath)
        else:
            KMessageBox.error(self, 'action %s not supported' % action)

    def slotDbConnected(self, dsn):
        BasePaellaMainWindow.slotDbConnected(self, dsn)
        self.conn = self.app.conn
        self.refreshListView()

    def slotDisconnectDatabase(self):
        BasePaellaMainWindow.slotDisconnectDatabase(self)
        self.conn = None
        self.listView.clear()
    
class PaellaMainWindow(BasePaellaMainWindow):
    pass

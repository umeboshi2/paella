from qt import SIGNAL
from qt import PYSIGNAL
from kdeui import KPopupMenu
from kdeui import KStdAction
from kdeui import KMessageBox
from kdeui import KListView, KListViewItem

from kfile import KDirSelectDialog

from useless.base.path import path
from useless.kdebase.mainwin import BaseMainWindow

# database manager
from paella.db.main import DatabaseManager

from paella.kde.base.widgets import BasePaellaWidget

# import actions
from paella.kde.base.actions import BaseItem, BaseAction
from paella.kde.base.actions import dbactions
from paella.kde.base.actions import ManageFamilies
from paella.kde.base.actions import EditTemplateAction
from paella.kde.base.actions import ManageAptSourcesAction
from paella.kde.base.actions import OpenSuiteManagerAction
from paella.kde.base.actions import ManageAptKeysAction

from paella.kde.base.mainwin import BasePaellaWindow

# import dialogs
from paella.kde.base.dialogs import PaellaConnectionDialog
from paella.kde.base.dialogs import ExportDbProgressDialog
from paella.kde.base.dialogs import ImportDbProgressDialog

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
from paella.kde.aptkey import AptKeyWindow

from application import NotConnectedError

class ManageTraitsItem(BaseItem):
    def __init__(self, suite):
        msg = 'manage %s traits' % suite
        BaseItem.__init__(self, msg, 'colors', msg, msg)
                          
class ManageTraitsAction(BaseAction, BasePaellaWidget):
    def __init__(self, suite, slot, parent):
        BaseAction.__init__(self, ManageTraitsItem(suite), 'ManageTraits%s' % suite,
                            slot, parent)
        self.initPaellaCommon()
        self.suite = suite
        self.connect(self, SIGNAL('activated()'), self._activate)
        self._winparent = None
        
    def _activate(self):
        print 'activating %s action' % self.suite
        #BaseAction.activate(self)
        win = TraitMainWindow(self._winparent, self.suite)
        self._winparent._all_my_children.append(win)
        win.show()

    def set_winparent(self, parent):
        self._winparent = parent

class BasePaellaMainWindow(BasePaellaWindow):
    def __init__(self, parent=None, name='BasePaellaMainWindow'):
        BasePaellaWindow.__init__(self, None, name)
        self.initPaellaCommon()
        self._suites = []
        # make a cursor
        if self.conn is not None:
            self.cursor = self.conn.cursor(statement=True)
            # figure out what suites are available
            self._refresh_suites()
        # setup actions, menus, and toolbar
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.statusbar = self.statusBar()
        self.statusbar.message('Disconnected')
        
        # setup dialog pointers
        self._import_export_dirsel_dialog = None

        self._all_my_children = []

    def _refresh_suites(self):
        if 'suites' in self.cursor.tables():
            self._suites = [row.suite for row in self.cursor.select(table='suites')]
        
        
        
    def _initTraitsActions(self, suites):
        collection = self.actionCollection()
        for suite in suites:
            action = ManageTraitsAction(suite,
                                        self.slotManageTraits, collection)
            action.set_winparent(self)
            self.manageTraitsActions[suite] = action
                                              
        
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

        self.manageAptKeysAction = \
                                 ManageAptKeysAction(self.slotManageAptKeys,
                                                     collection)
        
        # in the main window assign quit to app.quit
        self.quitAction = KStdAction.quit(self.app.quit, collection)
        self.suiteActions = {}
        self.manageTraitsActions = {}

        self._initTraitsActions(self._suites)
        # define database action slots
        self._dbactionslots = dict(export=self.slotExportDatabase,
                                   connect=self.slotConnectDatabase,
                                   disconnect=self.slotDisconnectDatabase)
        # don't collide with python keyword
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
        #suite_actions = self.suiteActions.values()
        suite_actions = self.manageTraitsActions.values()
        main_actions = [self.manageAptSourcesAction,
                        self.openSuiteManagerAction,
                        self.manageAptKeysAction,
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
            

    def _already_connected_dialog(self):
        KMessageBox.information(self, 'Already connected to a database, disconnect first.')

    def _connect_first_dialog(self):
        KMessageBox.information(self, 'Please connect to a database before trying this.')
        
    def slotConnectDatabase(self):
        if self.app.conn is None:
            win = PaellaConnectionDialog(self)
            dsn = self.cfg.get_dsn()
            fields = ['dbhost', 'dbname', 'dbusername']
            data = dict([(f, dsn[f]) for f in fields])
            win.setRecordData(data)
            win.connect(win, SIGNAL('okClicked()'), win.slotConnectDatabase)
            win.connect(win, PYSIGNAL('dbconnected(data)'), self.slotDbConnected)
            win.show()
        else:
            self._already_connected_dialog()

    def slotDisconnectDatabase(self):
        self.app.disconnect_database()
        self.statusbar.message('Disconnected')
        
    def slotDbConnected(self, dsn):
        #print dsn
        #print 'slotDbConnected'
        for action in self.suiteActions.values():
            action.unplug(self.suitemenu)
        self.suite_actions = {}
        self.cursor = self.app.conn.cursor(statement=True)
        if 'suites' in self.cursor.tables():
            self._suites = [row.suite for row in self.cursor.select(table='suites')]
            self._initTraitsActions(self._suites)
        for action in self.manageTraitsActions.values():
            action.plug(self.suitemenu)
        self.statusbar.message('Connected to %s on host %s' % (dsn['dbname'], dsn['dbhost']))
        if not self.cursor.tables():
            yesno = KMessageBox.questionYesNo(self, 'create primary tables?')
            if yesno == KMessageBox.Yes:
                dbm = DatabaseManager(self.app.conn)
                dbm.importer.start_schema()
            #print yesno == KMessageBox.Yes
            
    def slotManageAptSources(self):
        if self.app.conn is not None:
            win = AptSourceMainWindow(self)
            win.show()
            self._all_my_children.append(win)
        else:
            self._connect_first_dialog()

    def slotManageAptKeys(self):
        if self.app.conn is not None:
            win = AptKeyWindow(self)
            win.show()
            self._all_my_children.append(win)
        else:
            self._connect_first_dialog()
            
    def slotImportDatabase(self):
        print 'slotImportDatabase called'
        self._select_import_export_directory('import')

    def slotExportDatabase(self):
        print 'slotExportDatabase called'
        self._select_import_export_directory('export')

    def slotOpenSuiteManager(self):
        if self.app.conn is not None:
            win = SuiteManagerWindow(self)
            win.show()
            self._all_my_children.append(win)
        else:
            self._connect_first_dialog()
            
    def _destroy_dialog(self):
        self._dialog = None
        self._import_export_dirsel_dialog = None
        
    def _connect_destroy_dialog(self, dialog):
        dialog.connect(dialog, SIGNAL('cancelClicked()'), self._destroy_dialog)
        dialog.connect(dialog, SIGNAL('closeClicked()'), self._destroy_dialog)
        
    # here action is either 'import' or 'export'
    def _select_import_export_directory(self, action):
        if self._import_export_dirsel_dialog is None:
            default_db_path = path(self.app.cfg.get('database', 'default_path')).expand()
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
        self._import_export_dirsel_dialog = None
        url = win.url()
        fullpath = str(url.path())
        action = win.db_action
        print 'selected fullpath', fullpath
        print 'action is', win.db_action
        win.close()
        #self.app.processEvents()
        dbm = DatabaseManager(self.app.conn)
        if action == 'import':
            #dbm.restore(fullpath)
            win = ImportDbProgressDialog(self)

            importer = dbm.importer
            importer.report_total_apt_sources = win.aptsrc_progress.setTotalSteps
            #importer.report_aptsrc_imported = win.aptsrc_progress.step_progress
            importer.report_importing_aptsrc = win.aptsrc_progress.start_step
            importer.report_aptsrc_imported = win.aptsrc_progress.finish_step
            
            aptsrc = importer.aptsrc
            aptsrc.report_total_packages = win.package_progress.setTotalSteps
            aptsrc.report_package_inserted = win.package_progress.step_progress

            importer.report_total_suites = win.suite_progess.setTotalSteps
            importer.report_importing_suite = win.suite_progess.start_step
            importer.report_suite_imported = win.suite_progess.finish_step
            
            #importer.report_total_traits = win.trait_progress.setTotalSteps
            importer.report_total_traits = win.report_total_traits
            importer.report_trait_imported = win.trait_progress.step_progress
            
            importer.report_total_families = win.family_progress.setTotalSteps
            importer.report_family_imported = win.family_progress.step_progress
            importer.report_total_profiles = win.profile_progress.setTotalSteps
            importer.report_profile_imported = win.profile_progress.step_progress
            
            
            win.show()
            dbm.import_all(fullpath)
            self.app.processEvents()
            win.close()
            KMessageBox.information(self, 'Database Imported')
            
        elif action == 'export':
            #dbm.backup(fullpath)
            win = ExportDbProgressDialog(self)

            exporter = dbm.exporter
            exporter.report_total_suites = win.suite_progess.setTotalSteps
            exporter.report_exporting_suite = win.suite_progess.start_step
            exporter.report_suite_exported = win.suite_progess.finish_step
            exporter.report_total_traits = win.trait_progress.setTotalSteps
            exporter.report_trait_exported = win.trait_progress.step_progress
            #exporter.report_all_traits_exported = win.trait_progress.progressbar.reset
            exporter.report_start_exporting_traits = win.trait_progress.progressbar.reset
            exporter.report_total_profiles = win.profile_progress.setTotalSteps
            exporter.report_profile_exported = win.profile_progress.step_progress

            family = exporter.family
            family.report_total_families = win.family_progress.setTotalSteps
            family.report_family_exported = win.family_progress.step_progress

                        
            win.show()
            self.app.processEvents()
            dbm.export_all(fullpath)
            self.app.processEvents()
            win.close()
        else:
            KMessageBox.error(self, 'action %s not supported' % action)

    # this slot does nothing, the work is done in the action
    def slotManageTraits(self, *args):
        pass
    
        
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

    def _import_export_directory_selected(self):
        BasePaellaMainWindow._import_export_directory_selected(self)
        self.refreshListView()
        
    def refreshListView(self):
        self.listView.clear()
        self._refresh_suites()
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
            if  not self._suites:
                KMessageBox.information(self, "No suites are present.")
            else:
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
            #win = InstallerMainWin(self)
            KMessageBox.information(self, 'Not Implemented')
        elif hasattr(current, 'clients'):
            win = ClientsMainWindow(self)
        elif hasattr(current, 'folder'):
            # nothing important selected, do nothing
            pass
        else:
            KMessageBox.error(self, 'something bad happened in the list selection')
        if win is not None:
            win.show()
            self._all_my_children.append(win)
            
    def slotManageFamilies(self):
        print 'running families'
        #FamilyMainWindow(self.app, self)
        #KMessageBox.error(self, 'Managing families unimplemented')
        win = FamilyMainWindow(self)
        win.show()
        self._all_my_children.append(win)
        
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
        
        
    def slotDbConnected(self, dsn):
        BasePaellaMainWindow.slotDbConnected(self, dsn)
        self.conn = self.app.conn
        self.refreshListView()

    def slotDisconnectDatabase(self):
        try:
            BasePaellaMainWindow.slotDisconnectDatabase(self)
        except NotConnectedError:
            pass
        self.conn = None
        self.listView.clear()
        while self._all_my_children:
            child = self._all_my_children.pop()
            try:
                child.close()
            except RuntimeError, inst:
                if inst.args[0] != 'underlying C/C++ object has been deleted':
                    raise inst

class PaellaMainWindow(BasePaellaMainWindow):
    pass

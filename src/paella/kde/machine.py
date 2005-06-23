import os
from qt import SLOT, SIGNAL, Qt
from kdecore import KIconLoader
from kdeui import KMainWindow
from kdeui import KPopupMenu, KStdAction
from kdeui import KMessageBox, KTextEdit
from kdeui import KListView, KListViewItem

from paella.profile.base import PaellaConfig
from paella.profile.base import PaellaConnection
from paella.profile.trait import Trait
from paella.machines.machine import MachineHandler

from useless.db.midlevel import StatementCursor
from useless.kbase.gui import MainWindow, SimpleSplitWindow
from useless.kbase.gui import ViewWindow
from useless.kdb.gui import RecordSelector, ViewBrowser

from paella.kde.base import RecordSelectorWindow
from paella.kde.base.actions import ManageMachinesAction
from paella.kde.base.actions import ManageMachineTypesAction
from paella.kde.base.actions import ManageFilesystemsAction
from paella.kde.base.actions import ManageDisksAction
from paella.kde.base.actions import ManageMountsAction
from paella.kde.base.actions import ManageKernelsAction

from paella.kde.xmlgen import MachineDoc

ManageActions = {
    'machine' : ManageMachinesAction,
    'machine_type' : ManageMachineTypesAction,
    'filesystem' : ManageFilesystemsAction,
    'disk' : ManageDisksAction,
    'mount' : ManageMountsAction,
    'kernels' : ManageKernelsAction
    }

class SimpleEdit(KTextEdit):
    def __init__(self, app, parent):
        KTextEdit.__init__(self, parent)
        self.app = app
        
class MachineSelector(RecordSelector):
    def __init__(self, app, parent):
        table = 'machines'
        fields = ['machine', 'machine_type', 'kernel', 'profile', 'filesystem']
        idcol = 'machine'
        groupfields = ['machine_type', 'kernel', 'profile', 'filesystem']
        view = MachineView
        RecordSelector.__init__(self, app, parent, table, fields,
                                idcol, groupfields, view, 'MachineSelector')
        

class MachineView(ViewBrowser):
    def __init__(self, app, parent):
        ViewBrowser.__init__(self, app, parent, MachineDoc)

    def set_machine(self, machine):
        self.doc.set_machine(machine)
        self.setText(self.doc.toxml())

    def setSource(self, url):
        KMessageBox.information(self, 'called %s' % url)


class MachineMainWindowOrig(RecordSelectorWindow):
    def __init__(self, app, parent):
        RecordSelectorWindow.__init__(self, app, parent,
                                      MachineSelector, 'MachineMainWindow')

    def selectionChanged(self):
        current = self.listView.currentItem()
        self.view.set_machine(current.machine)

class MachineMainWindow(KMainWindow):
    def __init__(self, app, parent):
        KMainWindow.__init__(self, parent)
        self.app = app
        self.icons = KIconLoader()
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.conn = app.conn
        self.cfg = app.cfg
        self.cursor = StatementCursor(self.conn)
        #self.listView = KListView(self)
        #self.listView.setRootIsDecorated(True)
        #self.listView.addColumn('widget')
        #self.setCentralWidget(self.listView)
        #self.refreshListView()
        #self.connect(self.listView,
        #             SIGNAL('selectionChanged()'), self.selectionChanged)
        self.show()

    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.app.quit, collection)
        self._manage_actions = {}
        for k,v in ManageActions.items():
            self._manage_actions[k] = v(self.slotManageSomething, collection)
            
    def initMenus(self):
        mainMenu = KPopupMenu(self)
        actions = self._manage_actions.values()
        actions += [self.quitAction]
        self.menuBar().insertItem('&Main', mainMenu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))
        for action in actions:
            action.plug(mainMenu)
            
    def initToolbar(self):
        toolbar = self.toolBar()
        actions = self._manage_actions.values()
        actions += [self.quitAction]
        for action in actions:
            action.plug(toolbar)
            
    def refreshListView(self):
        machine_folder = KListViewItem(self.listView, 'machines')
                    
    def selectionChanged(self):
        current = self.listView.currentItem()
        print current, dir(current)
            
    def slotManageFamilies(self):
        print 'running families'
        FamilyMainWindow(self.app, self)
            
    def slotEditTemplates(self):
        print 'edit templates'

    def slotManageSomething(self):
        print 'manage something'
        
if __name__ == '__main__':
    cfg = PaellaConfig()
    conn = PaellaConnection(cfg)
    t = Trait(conn, suite='kudzu')

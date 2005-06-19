import os
from qt import SLOT, SIGNAL, Qt
from kdeui import KMainWindow
from kdeui import KPopupMenu
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

from paella.kde.xmlgen import MachineDoc

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

class MachineMainWindowOrig(SimpleSplitWindow):
    def __init__(self, app, parent):
        SimpleSplitWindow.__init__(self, app, parent, MachineView, 'MachineMainWindow')
        self.app = app
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.conn = app.conn
        self.cfg = app.cfg
        self.machine = MachineHandler(self.conn)
        self.cursor = StatementCursor(self.conn)
        self.refreshListView()
        self.resize(600, 800)
        self.setCaption('paella machines')
        
    def initActions(self):
        collection = self.actionCollection()
        
    def initMenus(self):
        mainMenu = KPopupMenu(self)
        menus = [mainMenu]
        self.menuBar().insertItem('&Main', mainMenu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))

    def initToolbar(self):
        toolbar = self.toolBar()

    def initlistView(self):
        self.listView.setRootIsDecorated(True)
        self.listView.addColumn('group')
        
    def refreshListView(self):
        mrows = self.machine.mtypes.select(fields=['machine'], table='machines', order='machine')
        for row in mrows:
            item = KListViewItem(self.listView, row.machine)
            item.machine = row.machine

    def selectionChanged(self):
        current = self.listView.currentItem()
        self.view.set_machine(current.machine)

class MachineMainWindow(RecordSelectorWindow):
    def __init__(self, app, parent):
        RecordSelectorWindow.__init__(self, app, parent, MachineSelector, 'MachineMainWindow')

    def selectionChanged(self):
        current = self.listView.currentItem()
        self.view.set_machine(current.machine)
        
if __name__ == '__main__':
    cfg = PaellaConfig()
    conn = PaellaConnection(cfg)
    t = Trait(conn, suite='kudzu')

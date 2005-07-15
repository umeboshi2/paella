import os
from qt import SLOT, SIGNAL, Qt
from qt import QSplitter, QString

from kdecore import KIconLoader
from kdeui import KMainWindow
from kdeui import KPopupMenu, KStdAction
from kdeui import KMessageBox, KTextEdit
from kdeui import KListView, KListViewItem
from kdeui import KStatusBar

from paella.profile.base import PaellaConfig
from paella.profile.base import PaellaConnection
from paella.profile.trait import Trait
from paella.machines.machine import MachineHandler

from useless.db.midlevel import StatementCursor
from useless.kbase.gui import MainWindow, SimpleSplitWindow
from useless.kbase.gui import ViewWindow, MainWindow
from useless.kdb.gui import RecordSelector, ViewBrowser

from paella.kde.base import RecordSelectorWindow
from paella.kde.base.actions import ManageMachinesAction
from paella.kde.base.actions import ManageMachineTypesAction
from paella.kde.base.actions import ManageFilesystemsAction
from paella.kde.base.actions import ManageDisksAction
from paella.kde.base.actions import ManageMountsAction
from paella.kde.base.actions import ManageKernelsAction

from paella.kde.xmlgen import MachineDoc
from paella.kde.xmlgen import MachineTypeDoc
from paella.kde.xmlgen import FilesystemDoc

ManageActions = {
    'machine' : ManageMachinesAction,
    'machine_type' : ManageMachineTypesAction,
    'filesystem' : ManageFilesystemsAction,
    'disk' : ManageDisksAction,
    'mount' : ManageMountsAction,
    'kernels' : ManageKernelsAction
    }


class MachineView(ViewBrowser):
    def __init__(self, app, parent):
        ViewBrowser.__init__(self, app, parent, MachineDoc)

    def set_machine(self, machine):
        self.doc.set_machine(machine)
        self.setText(self.doc.toxml())

    def setSource(self, url):
        KMessageBox.information(self, 'called %s' % url)

class MachineTypeView(ViewBrowser):
    def __init__(self, app, parent):
        ViewBrowser.__init__(self, app, parent, MachineTypeDoc)

    def set_machine_type(self, machine_type):
        self.doc.set_machine_type(machine_type)
        self.setText(self.doc.toxml())

    def setSource(self, url):
        KMessageBox.information(self, 'called %s' % url)
        
class FilesystemView(ViewBrowser):
    def __init__(self, app, parent):
        ViewBrowser.__init__(self, app, parent, FilesystemDoc)

    def set_filesystem(self, filesystem):
        self.doc.set_filesystem(filesystem)
        self.setText(self.doc.toxml())

    def setSource(self, url):
        KMessageBox.information(self, 'called %s' % url)
        
class BaseManagerWidget(QSplitter):
    def __init__(self, app, parent, view, name):
        QSplitter.__init__(self, parent, name)
        self.app = app
        self.listView = KListView(self)
        self.view = view(self.app, self)
        self.initlistView()
        self.connect(self.listView,
                     SIGNAL('selectionChanged()'), self.selectionChanged)
        self.show()

    def selectionChanged(self):
        KMessageBox.information('selectionChanged Needs to be Overridden')
        
class MachineManager(BaseManagerWidget):
    def __init__(self, app, parent):
        view = MachineView
        BaseManagerWidget.__init__(self, app, parent, view, 'MachineTypeManager')
                
    def initlistView(self):
        self.cursor = StatementCursor(self.app.conn)
        table='machines'
        rows = self.cursor.select(table='machines')
        self.listView.addColumn('machine')
        for row in rows:
            KListViewItem(self.listView, row.machine)
  
    def selectionChanged(self):
        current = self.listView.currentItem().text(0)
        print str(current)
        self.view.set_machine(str(current))
        
class MachineTypeManager(BaseManagerWidget):
    def __init__(self, app, parent):
        view = MachineTypeView
        BaseManagerWidget.__init__(self, app, parent, view, 'MachineTypeManager')
                
    def initlistView(self):
        self.cursor = StatementCursor(self.app.conn)
        table='machines'
        rows = self.cursor.select(table='machine_types')
        self.listView.addColumn('machine_type')
        for row in rows:
            KListViewItem(self.listView, row.machine_type)
  
    def selectionChanged(self):
        current = self.listView.currentItem().text(0)
        print str(current)
        self.view.set_machine_type(str(current))


class FilesystemManager(BaseManagerWidget):
    def __init__(self, app, parent):
        view = FilesystemView
        BaseManagerWidget.__init__(self, app, parent, view, 'FilesystemManager')

    def initlistView(self):
        self.cursor = StatementCursor(self.app.conn)
        table='filesystems'
        rows = self.cursor.select(table=table)
        self.listView.addColumn('filesystem')
        for row in rows:
            KListViewItem(self.listView, row.filesystem)
        
    def selectionChanged(self):
        current = self.listView.currentItem().text(0)
        print str(current)
        self.view.set_filesystem(str(current))

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
        self.mainView = None
        self.resize(400, 300)
        self.show()

    def _killmainView(self):
        if self.mainView is not None:
            print 'need to kill mainView here'
            del self.mainView
            self.mainView = None
            
    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.app.quit, collection)
        self._manage_actions = {}
        for k,v in ManageActions.items():
            att = 'slotManage%s' % k
            self._manage_actions[k] = v(getattr(self, att), collection)
            
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
            
    def slotManagemachine(self):
        self._killmainView()
        self._managing = 'machines'
        table='machines'
        rows = self.cursor.select(table='machines')
        columns = ['machine', 'machine_type', 'kernel', 'profile', 'filesystem']
        self.mainView = MachineManager(self.app, self)
        self.setCentralWidget(self.mainView)
        self.connect(self.mainView.listView,
                     SIGNAL('rightButtonClicked(QListViewItem *, const QPoint &, int )'),
                     self.slotMouseIsPressed)
        self.mainView.show()
        print 'manage machines'
        print '%d machines' % len(rows)

    def slotManagemachine_type(self):
        self._killmainView()
        self._managing = 'machine_types'
        self.mainView = MachineTypeManager(self.app, self)
        self.setCentralWidget(self.mainView)
        self.connect(self.mainView.listView,
                     SIGNAL('rightButtonClicked(QListViewItem *, const QPoint &, int )'),
                     self.slotMouseIsPressed)
        self.mainView.show()
        print 'manage machine_types'

    def slotManagefilesystem(self):
        self._killmainView()
        self._managing = 'filesystems'
        self.mainView = FilesystemManager(self.app, self)
        self.setCentralWidget(self.mainView)
        self.mainView.show()
        print 'manage filesystems'

    def slotManagekernels(self):
        self._killmainView()
        self._managing = 'kernels'
        table = 'kernels'
        rows = self.cursor.select(table='kernels')
        self.mainView = KListView(self)
        self.mainView.setRootIsDecorated(True)
        self.setCentralWidget(self.mainView)
        self.mainView.addColumn('kernel')
        self.connect(self.mainView,
                     SIGNAL('rightButtonClicked(QListViewItem *, const QPoint &, int )'),
                     self.slotMouseIsPressed)
        for row in rows:
            KListViewItem(self.mainView, row.kernel)
        self.mainView.show()
        

    def slotManagedisk(self):
        self._killmainView()
        print 'manage disks'

    def slotManagemount(self):
        self._killmainView()
        print 'manage mounts'

    def slotMouseIsPressed(self):
        print 'mouse press'
        KMessageBox.information(self, 'Managing %s' % self._managing)
        
if __name__ == '__main__':
    cfg = PaellaConfig()
    conn = PaellaConnection(cfg)
    t = Trait(conn, suite='kudzu')

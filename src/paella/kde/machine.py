import os
from qt import SLOT, SIGNAL, Qt
from qt import QSplitter, QString

from kdecore import KIconLoader
from kdeui import KMainWindow
from kdeui import KPopupMenu, KStdAction
from kdeui import KMessageBox, KTextEdit
from kdeui import KListView, KListViewItem
from kdeui import KStatusBar

from paella.base import PaellaConfig
from paella.db import PaellaConnection
from paella.db.trait import Trait
from paella.db.machine import MachineHandler
from paella.db.machine.mtype import MachineTypeHandler
from paella.db.schema.paella_tables import MTSCRIPTS

from useless.base.util import strfile
from useless.db.midlevel import StatementCursor
from useless.kbase.gui import MainWindow, SimpleSplitWindow
from useless.kbase.gui import ViewWindow, MainWindow
from useless.kbase.gui import SimpleRecordDialog
from useless.kbase.gui import MyCombo, VboxDialog
from useless.kdb.gui import RecordSelector, ViewBrowser

from paella.kde.base import RecordSelectorWindow
from paella.kde.base import split_url
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

class MTScriptCombo(MyCombo):
    def __init__(self, parent):
        MyCombo.__init__(self, parent, 'MTScriptCombo')
        self.fill(MTSCRIPTS)

class NewMTScriptDialog(VboxDialog):
    def __init__(self, parent):
        VboxDialog.__init__(self, parent, 'NewMTScriptDialog')
        self.scriptnameBox = MTScriptCombo(self.page)
        self.scriptdataBox = KTextEdit(self.page)
        self.vbox.addWidget(self.scriptnameBox)
        self.vbox.addWidget(self.scriptdataBox)
        self.show()

    def getRecordData(self):
        name = str(self.scriptnameBox.currentText())
        data = str(self.scriptdataBox.text())
        return dict(name=name, data=data)
    
class NewMachineDialog(VboxDialog):
    def __init__(self, parent, handler):
        VboxDialog.__init__(self, parent, 'NewMachineDialog')
        self.conn = handler.conn
        self.handler = handler
        self.mtypeBox = MyCombo(self.page)
        self.mtypeBox.fill(self.handler.list_all_machine_types())
        self.profileBox = MyCombo(self.page)
        self.profileBox.fill(['hello'])
        self.kernelBox = MyCombo(self.page)
        self.kernelBox.fill(self.handler.list_all_kernels())
        self.fsBox = MyCombo(self.page)
        self.fsBox.fill(self.handler.list_all_filesystems())
        boxes = [self.mtypeBox, self.profileBox, self.kernelBox,
                 self.fsBox]
        map(self.vbox.addWidget, boxes)
        self.show()
        
class MachineView(ViewBrowser):
    def __init__(self, app, parent):
        ViewBrowser.__init__(self, app, parent, MachineDoc)

    def set_machine(self, machine):
        self.doc.set_machine(machine)
        self.setText(self.doc.toxml())

    def setSource(self, url):
        action, context, id_ = split_url(url)
        if action == 'new':
            if context == 'machine':
                handler = self.doc.machine
                dialog = NewMachineDialog(self, handler)
            else:
                self._info('make new <url> %s' % url)
        else:
            self._info('%s not supported yet' % url)

    def _info(self, message, parent=None):
        if parent is None:
            parent = self
        KMessageBox.information(parent, message)
        
class MachineTypeView(ViewBrowser):
    def __init__(self, app, parent):
        ViewBrowser.__init__(self, app, parent, MachineTypeDoc)
        self._dialog = None

    def _info(self, message, parent=None):
        if parent is None:
            parent = self
        KMessageBox.information(parent, message)
        
    def set_machine_type(self, machine_type):
        self.doc.set_machine_type(machine_type)
        self.setText(self.doc.toxml())

    def resetView(self):
        self.set_machine_type(self.doc.mtype.current)

    def setSource(self, url):
        action, context, id_ = split_url(url)
        fields = []
        if context == 'Disks':
            fields = ['diskname', 'device']
        elif context == 'Families':
            fields = ['family']
        elif context == 'Variables':
            fields = ['trait', 'name', 'value']
        if action == 'new':
            if context == 'Scripts':
                dialog = NewMTScriptDialog(self)
                dialog.connect(dialog, SIGNAL('okClicked()'), self.insertNewScript)
                self._dialog = dialog
            elif fields:
                dialog = SimpleRecordDialog(self, fields)
                dialog.context = context
                dialog.connect(dialog, SIGNAL('okClicked()'), self.insertNewRecord)
                self._dialog = dialog
            else:
                self._info('problem with %s' % url)
        elif action == 'edit':
            if context == 'Variables':
                self.doc.mtype.edit_variables()
            elif context == 'Scripts':
                self.doc.mtype.edit_script(id_)
            else:
                self._info('need to edit %s, %s' % (context, id_))
        elif action == 'delete':
            if context == 'Families':
                self.doc.mtype.delete_family(id_)
            elif context == 'Variables':
                self._info('use edit to delete variables')
            elif context == 'Scripts':
                self.doc.mtype.delete_script(id_)
            elif context == 'Modules':
                self._info('Deleting modules not supported')
            else:
                self._info('need to delete something in context %s, %s' % (context, id_))
        else:
            KMessageBox.information(self, 'called %s' % url)
        self.resetView()
        
    def insertNewRecord(self):
        dialog = self._dialog
        context = dialog.context
        data = dialog.getRecordData()
        if context == 'Disks':
            self.doc.mtype.add_disk(data['diskname'], data['device'])
        elif context == 'Families':
            self.doc.mtype.append_family(data['family'])
        elif context == 'Variables':
            self.doc.mtype.append_variable(data['trait'], data['name'],
                                           data['value'])
        else:
            KMessageBox.information(self, 'called something')
        self.resetView()

    def updateRecord(self):
        KMessageBox.information('called updateRecord')

    def insertNewScript(self):
        dialog = self._dialog
        data = dialog.getRecordData()
        mtype = self.doc.mtype
        mtype.insert_script(data['name'], strfile(data['data']))
        self.resetView()
        
        
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
        self.quitAction = KStdAction.quit(self.close, collection)
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

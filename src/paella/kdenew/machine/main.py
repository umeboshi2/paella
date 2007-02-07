from kdeui import KListViewItem
from kdeui import KStdAction
from kdeui import KPopupMenu

from useless.kdebase import get_application_pointer

from paella.kdenew.base.widgets import PaellaManagerWidget
from paella.kdenew.base.mainwin import BasePaellaWindow

from viewbrowser import MachineView
from viewbrowser import MachineTypeView
from viewbrowser import FilesystemView

#from actions import ManageMachinesAction
#from actions import ManageMachineTypesAction
#from actions import ManageFilesystemsAction
#from actions import ManageDisksAction
#from actions import ManageMountsAction
#from actions import ManageKernelsAction
from actions import ManageActions, ManageActionsOrder


class MachineManager(PaellaManagerWidget):
    def __init__(self, parent):
        mainview = MachineView
        PaellaManagerWidget.__init__(self, parent, mainview, name='MachineManager')
        self.initlistView()
        
    def initlistView(self):
        self.cursor = self.conn.cursor(statement=True)
        self.listView.addColumn('machine')
        rows = self.cursor.select(table='machines')
        for row in rows:
            KListViewItem(self.listView, row.machine)

    def selectionChanged(self):
        item = self.listView.currentItem()
        self.mainView.set_machine(str(item.text(0)))

class MachineTypeManager(PaellaManagerWidget):
    def __init__(self, parent):
        mainview = MachineTypeView
        PaellaManagerWidget.__init__(self, parent, mainview, name='MachineTypeManager')
        self.initlistView()
        
    def initlistView(self):
        self.cursor = self.conn.cursor(statement=True)
        self.listView.addColumn('machine_type')
        rows = self.cursor.select(table='machine_types')
        for row in rows:
            KListViewItem(self.listView, row.machine_type)

    def selectionChanged(self):
        item = self.listView.currentItem()
        self.mainView.set_machine_type(str(item.text(0)))

class FilesystemManager(PaellaManagerWidget):
    def __init__(self, parent):
        mainview = FilesystemView
        PaellaManagerWidget.__init__(self, parent, mainview, name='FilesystemManager')

    def initlistView(self):
        self.cursor = self.conn.cursor(statement=True)
        rows = self.cursor.select(table='filesystem')
        for row in rows:
            KListViewItem(self.listView, row.filesystem)

    def selectionChanged(self):
        item = self.listView.currentItem()
        self.mainView.set_filesystem(str(item.text(0)))

class MachineMainWindow(BasePaellaWindow):
    def __init__(self, parent):
        BasePaellaWindow.__init__(self, parent, name='MachineMainWindow')
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.mainView = None
        self.resize(400, 300)
        self.setCaption('Machine Manager')

    def _killmainView(self):
        if self.mainView is not None:
            del self.mainView
            self.mainView = None

    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)
        self._manage_action_objects = {}
        for action_name in ManageActionsOrder:
            slotname = 'slotManage%s' % action_name
            slot = getattr(self, slotname)
            action_object = ManageActions[action_name](slot, collection)
            self._manage_action_objects[action_name] = action_object
            
    def initMenus(self):
        mainmenu = KPopupMenu(self)
        actions = [self._manage_action_objects[name] for name in ManageActionsOrder]
        actions.append(self.quitAction)
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)
        menubar.insertItem('&Help', self.helpMenu(''))
        for action in actions:
            action.plug(mainmenu)

    def initToolbar(self):
        toolbar = self.toolBar()
        actions = [self._manage_action_objects[name] for name in ManageActionsOrder]
        actions.append(self.quitAction)
        for action in actions:
            action.plug(toolbar)
            
    def slotManagemachine(self):
        self._killmainView()
        manager = MachineManager(self)
        self.setCentralWidget(manager)
        manager.show()
        self.mainView = manager
        
    def slotManagemachine_type(self):
        self._killmainView()
        manager = MachineTypeManager(self)
        self.setCentralWidget(manager)
        manager.show()
        self.mainView = manager


    def slotManagefilesystem(self):
        raise NotImplementedError, 'slotManagefilesystem not implemented'

    def slotManagekernels(self):
        raise NotImplementedError, 'slotManagekernels not implemented'

    def slotManagedisk(self):
        raise NotImplementedError, 'slotManagedisk not implemented'

    def slotManagemount(self):
        raise NotImplementedError, 'slotManagemount not implemented'
    

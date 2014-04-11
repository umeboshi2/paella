from kdeui import KListView
from kdeui import KListViewItem
from kdeui import KStdAction
from kdeui import KPopupMenu
from kdeui import KMessageBox

from useless.kdebase import get_application_pointer

from paella.kde.base.widgets import PaellaManagerWidget
from paella.kde.base.mainwin import BasePaellaWindow

from viewbrowser import MachineView
from viewbrowser import DiskConfigView
from viewbrowser import KernelView


from actions import ManageActions, ManageActionsOrder

from actions import ManageMachinesAction, ManageDiskConfigAction
from actions import ManageKernelsAction


class MachineManager(PaellaManagerWidget):
    def __init__(self, parent):
        mainview = MachineView
        PaellaManagerWidget.__init__(self, parent, mainview, name='MachineManager')
        self.initlistView()
        
    def initlistView(self):
        self.cursor = self.conn.cursor(statement=True)
        self.listView.addColumn('machine')
        self.refreshListView()

    def refreshListView(self):
        self.listView.clear()
        rows = self.cursor.select(table='machines', order='machine')
        for row in rows:
            KListViewItem(self.listView, row.machine)
        
    def selectionChanged(self):
        item = self.listView.currentItem()
        self.mainView.set_machine(str(item.text(0)))

class DiskConfigManager(PaellaManagerWidget):
    def __init__(self, parent):
        mainview = DiskConfigView
        PaellaManagerWidget.__init__(self, parent, mainview, name='DiskConfigManager')
        self.cursor = self.conn.cursor(statement=True)
        self.initlistView()
        
    def initlistView(self):
        self.listView.addColumn('diskconfig')
        self.refreshListView()
        
    def refreshListView(self):
        self.listView.clear()
        rows = self.cursor.select(fields=['name'], table='diskconfig')
        for row in rows:
            KListViewItem(self.listView, row.name)

    def selectionChanged(self):
        item = self.listView.currentItem()
        self.mainView.set_diskconfig(str(item.text(0)))

    def resetView(self):
        item = self.listView.currentItem()
        diskconfig = str(item.text(0))
        self.refreshListView()
        #self.selectionChanged()
        self.mainView.set_diskconfig(diskconfig)
        
        
class MachineMainWindow(BasePaellaWindow):
    def __init__(self, parent):
        BasePaellaWindow.__init__(self, parent, name='MachineMainWindow')
        self.initPaellaCommon()
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.mainView = None
        self.resize(500, 600)
        self.setCaption('Machine Manager')
        self.statusbar = self.statusBar()
        self._managing = None
        
    def _killmainView(self):
        if self.mainView is not None:
            del self.mainView
            self.mainView = None
            self._managing = None
            
    def _setMainView(self, managerclass):
        self._killmainView()
        manager = managerclass(self)
        self.setCentralWidget(manager)
        manager.show()
        self.mainView = manager
        if hasattr(self.mainView, 'setSizes'):
            self.mainView.setSizes([75, 425])
        
    def initActions(self):
        collection = self.actionCollection()
        self.newAction = KStdAction.openNew(self.slotNewObject, collection)
        self.quitAction = KStdAction.quit(self.close, collection)
        self._manage_action_objects = {}
        ao = self._manage_action_objects
        ao['machine'] = ManageMachinesAction(self.slotManagemachine, collection)
        ao['diskconfig'] = ManageDiskConfigAction(self.slotManagediskconfig, collection)
        ao['kernels'] = ManageKernelsAction(self.slotManagekernels, collection)
        #for action_name in ManageActionsOrder:
        #    slotname = 'slotManage%s' % action_name
        #    slot = getattr(self, slotname)
        #    action_object = ManageActions[action_name](slot, collection)
        #    self._manage_action_objects[action_name] = action_object
            
    def initMenus(self):
        mainmenu = KPopupMenu(self)
        actions = [self.newAction]
        actions += [self._manage_action_objects[name] for name in ManageActionsOrder]
        actions.append(self.quitAction)
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)
        menubar.insertItem('&Help', self.helpMenu(''))
        for action in actions:
            action.plug(mainmenu)

    def initToolbar(self):
        toolbar = self.toolBar()
        actions = [self.newAction]
        actions += [self._manage_action_objects[name] for name in ManageActionsOrder]
        actions.append(self.quitAction)
        for action in actions:
            action.plug(toolbar)
            
    def slotManagemachine(self):
        self._setMainView(MachineManager)
        self.statusbar.message('Manage Machines')
        self._managing = 'machine'
        
    def slotManagediskconfig(self):
        self._setMainView(DiskConfigManager)
        self.statusbar.message('Manage diskconfig')
        self._managing = 'diskconfig'

    def slotManagekernels(self):
        self._setMainView(KernelView)
        self.mainView.refresh_view()
        self.statusbar.message('Manage kernels')
        self._managing = 'kernel'
        
    def slotNewObject(self):
        if self._managing is None:
            KMessageBox.information(self, 'Select something to manage first.')
        elif self._managing == 'machine':
            self.mainView.mainView.setSource('new.machine.foo')
        elif self._managing == 'diskconfig':
            self.mainView.mainView.setSource('new.diskconfig.foo')
        elif self._managing == 'kernel':
            # kernel url's use '||' since the package names
            # have "."'s in them
            self.mainView.setSource('new||kernel||foo')
        else:
            KMessageBox.information(self, '%s not supported yet' % self._managing)
            

import os

from qt import SIGNAL

from kdecore import KApplication
from kdecore import KStandardDirs

from kdeui import KPopupMenu
from kdeui import KStdAction
from kdeui import KMessageBox
from kdeui import KListView, KListViewItem

from useless.kdebase.mainwin import BaseMainWindow
from useless.kdebase import get_application_pointer
from useless.kdebase.manager_widget import BaseManagerWidget

from paella.base import PaellaConfig
from paella.db import PaellaConnection

from paella.uml.base import UmlConfig

from paella.kdenew.base.viewbrowser import ViewBrowser


# import actions
from actions import BootstrapMachine
from actions import BackupMachine
from actions import InstallMachine
from actions import RestoreMachine
from actions import LaunchMachine
from actions import EditConfigFile

#from paella.kdenew.base.actions import ManageFamilies
#from paella.kdenew.base.actions import EditTemplateAction
#from paella.kdenew.base.actions import ManageSuiteAction

from docgen import UmlMachineDoc



class UmlManagerApplication(KApplication):
    def __init__(self):
        KApplication.__init__(self)
        self.umlcfg = UmlConfig()
        self.update_config()
        
    def update_config(self):
        self.umlcfg.clear_all()
        self.umlcfg.read(self.umlcfg.list_rcfiles())
        
class BaseUmlManagerMainWindow(BaseMainWindow):
    def __init__(self, parent=None, name='BaseUmlManagerMainWindow'):
        BaseMainWindow.__init__(self, parent, name)
        self.app = get_application_pointer()
        
class UmlManagerMainWindow(BaseUmlManagerMainWindow):
    def __init__(self, parent=None, name='UmlManagerMainWindow'):
        BaseUmlManagerMainWindow.__init__(self, parent=parent, name=name)
        self.initActions()
        self.initMenus()
        self.initToolbar()

        self.mainView = MainUmlManagerWidget(self)
        self.setCentralWidget(self.mainView)
        
    def initActions(self):
        collection = self.actionCollection()

        # in the main window assign quit to app.quit
        self.quitAction = KStdAction.quit(self.app.quit, collection)
        self.bootstrapMachineAction = BootstrapMachine(self.slotBootstrapMachine,
                                                       collection)
        self.installMachineAction = InstallMachine(self.slotInstallMachine,
                                                   collection)
        self.backupMachineAction = BackupMachine(self.slotBackupMachine,
                                                 collection)
        self.editConfigFileAction = EditConfigFile(self.slotEditConfigFile,
                                                   collection)
        

    def initMenus(self):
        mainmenu = KPopupMenu(self)
        main_actions = [self.bootstrapMachineAction,
                        self.installMachineAction,
                        self.backupMachineAction,
                        self.editConfigFileAction,
                        self.quitAction]
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)
        menubar.insertItem('&Help', self.helpMenu(''))
        for action in main_actions:
            action.plug(mainmenu)
        
    def initToolbar(self):
        toolbar = self.toolBar()
        actions = [self.quitAction]                   
        for action in actions:
            action.plug(toolbar)
            
    def slotBootstrapMachine(self):
        print 'bootstrap machine'

    def slotBackupMachine(self):
        print 'backup machine'

    def slotInstallMachine(self):
        print 'install machine'

    def slotEditConfigFile(self):
        filename = os.path.expanduser('~/.umlmachines.conf')
        os.system('$EDITOR %s' % filename)
        self.app.update_config()
        self.mainView.refreshListView()
        
        
class BaseUmlManagerWidget(BaseManagerWidget):
    def __init__(self, parent, mainview, listview=None, name='UmlManagerWidget'):
        BaseManagerWidget.__init__(self, parent, mainview, listview=listview,
                                   name=name)
        self.app = get_application_pointer()

class MainUmlManagerWidget(BaseUmlManagerWidget):
    def __init__(self, parent, name='MainUmlManagerWidget'):
        mainview = UmlMachineView
        BaseUmlManagerWidget.__init__(self, parent, mainview,
                                      name='MainUmlManagerWidget')
        self.initListView()
        
    def initListView(self):
        self.listView.addColumn('uml machine')
        self.refreshListView()
        
    def refreshListView(self):
        self.listView.clear()
        machines = self.app.umlcfg.list_machines()
        for machine in machines:
            KListViewItem(self.listView, machine)

    def selectionChanged(self):
        item = self.listView.currentItem()
        self.mainView.set_machine(str(item.text(0)))
        
        
class UmlMachineView(ViewBrowser):
    def __init__(self, parent):
        ViewBrowser.__init__(self, parent, UmlMachineDoc)

    def set_machine(self, machine):
        self.doc.set_machine(machine)
        self.setText(self.doc.output())

    def setSource(self, url):
        print url, 'clicked'
        
    

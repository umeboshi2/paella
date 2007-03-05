#from qt import SIGNAL
from qt import QListBoxText

from kdeui import KStdAction
from kdeui import KListViewItem

from useless.kdebase.mainwin import BaseSplitWindow
from useless.kdebase.dialogs import BaseAssigner

from paella.db.suitehandler import SuiteHandler

from paella.kde.base.mainwin import BasePaellaWindow
from paella.kde.base.viewbrowser import ViewBrowser

from docgen import SuiteManagerDoc

class SuiteAptAssigner(BaseAssigner):
    def __init__(self, parent, name='SuiteAptAssigner'):
        pass
    
class SuiteManagerView(ViewBrowser):
    def __init__(self, parent):
        ViewBrowser.__init__(self, parent, SuiteManagerDoc)
        self._dialog = None
        self.suite = None
        
    def set_suite(self, suite):
        self.suite = suite
        self.doc.set_suite(suite)
        self.setText(self.doc.output())

    def resetView(self):
        self.set_suite(self.suite)
        
class SuiteManagerWindow(BaseSplitWindow, BasePaellaWindow):
    def __init__(self, parent, name='SuiteManagerWindow'):
        BaseSplitWindow.__init__(self, parent, SuiteManagerView, name=name)
        self.initPaellaCommon()
        self.handler = SuiteHandler(self.conn, self.cfg)
        self.refreshListView()
        self.initActions()
        self.initMenus()
        self.initToolbar()
        

    def initActions(self):
        collection = self.actionCollection()
        self.newAction = KStdAction.openNew(self.slotNew, collection)
        self.quitAction = KStdAction.quit(self.close, collection)

    def initMenus(self):
        pass

    def initToolbar(self):
        toolbar = self.toolBar()
        self.newAction.plug(toolbar)
        self.quitAction.plug(toolbar)
        

    def initlistView(self):
        self.listView.addColumn('suite')

    def refreshListView(self):
        self.listView.clear()
        for suite in self.handler.get_suites():
            item = KListViewItem(self.listView, suite)
            item.suite = suite
            
        
    def selectionChanged(self):
        item = self.listView.currentItem()
        self.mainView.set_suite(item.suite)

    def slotNew(self):
        print 'new suite'

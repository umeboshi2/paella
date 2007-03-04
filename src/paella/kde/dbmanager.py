from qt import SIGNAL

from kdeui import KStdAction
from kdeui import KListViewItem

from useless.kdebase.mainwin import BaseSplitWindow

from paella.db.base import SuiteCursor
from paella.db.suitehandler import SuiteHandler
from paella.db.aptsrc import AptSourceHandler

from paella.kde.base.mainwin import BasePaellaWindow
from paella.kde.base.viewbrowser import ViewBrowser
from paella.kde.base.dialogs import PaellaConnectionDialog

from paella.kde.docgen.aptsrc import AptSourceDoc

class BaseManager(object):
    def __init__(self):
        pass

    
class MainDbWindow(BasePaellaWindow):
    def __init__(self, parent, name='MainDbWindow'):
        pass

class AptSourceView(ViewBrowser):
    def __init__(self, parent):
        ViewBrowser.__init__(self, parent, AptSourceDoc)
        self._dialog = None
        
    def set_apt_source(self, apt_id=None):
        self.doc.set_apt_source(apt_id)
        self.setText(self.doc.output())

    def resetView(self):
        self.set_apt_source()
        
    

class AptSourceMainWindow(BaseSplitWindow, BasePaellaWindow):
    def __init__(self, parent, name='AptSourceMainWindow'):
        BaseSplitWindow.__init__(self, parent, AptSourceView,
                                 name=name)
        self.initPaellaCommon()
        self.aptsrc = AptSourceHandler(self.conn)
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.setCaption('Apt Sources Manager')
        self.resize(500, 300)
        self.splitter.setSizes([100, 400])
        self.refreshListView()
        self.mainView.resetView()
        
    def initlistView(self):
        self.listView.addColumn('apt_id')

    def refreshListView(self):
        self.listView.clear()
        for row in self.aptsrc.get_apt_rows():
            item = KListViewItem(self.listView, row.apt_id)
            item.apt_id = row.apt_id
            
    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)
        self.newAction = KStdAction.openNew(self.slotNew, collection)

    def initMenus(self):
        pass

    def initToolbar(self):
        toolbar = self.toolBar()
        self.newAction.plug(toolbar)
        self.quitAction.plug(toolbar)

    def slotNew(self):
        print 'slotNew'

    def selectionChanged(self):
        item = self.listView.currentItem()
        self.mainView.set_apt_source(item.apt_id)


class SuiteManagerWindow(BasePaellaWindow):
    def __init__(self, parent, name='SuiteManagerWindow'):
        BasePaellaWindow.__init__(self, parent, name=name)
        self.initPaellaCommon()

    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)

    def initMenus(self):
        pass

    def initToolbar(self):
        pass
    

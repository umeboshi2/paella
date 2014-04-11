from qt import SIGNAL
from qt import QListBoxText

from kdeui import KStdAction
from kdeui import KListViewItem
from kdeui import KMessageBox

from useless.kdebase.mainwin import BaseSplitWindow
from useless.kdebase.dialogs import BaseAssigner
from useless.kdebase.dialogs import BaseRecordDialog

from paella.db.base import SuiteCursor

from paella.kde.base.mainwin import BasePaellaWindow
from paella.kde.base.viewbrowser import ViewBrowser
from paella.kde.base.widgets import BasePaellaWidget

from docgen import SuiteManagerDoc

class SuiteAptAssigner(BaseAssigner, BasePaellaWidget):
    def __init__(self, parent, suite, name='SuiteAptAssigner'):
        self.suite = suite
        self.initPaellaCommon()
        self.suitecursor = SuiteCursor(self.conn)
        BaseAssigner.__init__(self, parent, name=name,
                              udbuttons=True)
        self.connect(self, SIGNAL('okClicked()'), self.slotAssignAptSrcs)
        

    def initView(self):
        abox = self.listBox.availableListBox()
        apt_ids = [r.apt_id for r in self.suitecursor.get_apt_sources()]
        for apt_id in apt_ids:
            QListBoxText(abox, apt_id)
            
        
        
    def slotAssignAptSrcs(self):
        sbox = self.listBox.selectedListBox()
        apt_ids = [str(sbox.item(n).text()) for n in range(sbox.numRows())]
        
        suite = self.suite
        self.suitecursor.make_suite(suite, apt_ids)
        
            
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
        self.suitecursor = SuiteCursor(self.conn)
        self.refreshListView()
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.resize(800, 300)
        self.splitter.setSizes([100, 700])

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
        for suite in self.suitecursor.get_suites():
            item = KListViewItem(self.listView, suite)
            item.suite = suite
            
        
    def selectionChanged(self):
        item = self.listView.currentItem()
        self.mainView.set_suite(item.suite)

    def slotNew(self):
        win = BaseRecordDialog(self, ['name'])
        win.connect(win, SIGNAL('okClicked()'), self.slotNewSuiteNamed)
        self._dialog = win
        win.show()
        
    def slotNewSuiteNamed(self):
        win = self._dialog
        suite = win.getRecordData()['name']
        suite = suite.strip()
        if not suite:
            raise RuntimeError , 'no suite in slotNewSuiteNamed'
        win = SuiteAptAssigner(self, suite)
        win.show()
    
    def _destroy_dialog(self):
        self._dialog = None

    def _connect_dialog_destroy(self, dialog):
        pass
    

from qt import SIGNAL
from qt import QListBoxText

from kdeui import KStdAction
from kdeui import KListViewItem

from useless.kdebase.mainwin import BaseSplitWindow
from useless.kdebase.dialogs import BaseAssigner
from paella.db.base import SuiteCursor
from paella.db.suitehandler import SuiteHandler
from paella.db.aptsrc import AptSourceHandler

from paella.kde.base.mainwin import BasePaellaWindow
from paella.kde.base.viewbrowser import ViewBrowser
from paella.kde.base.dialogs import PaellaConnectionDialog
from paella.kde.base.dialogs import BasePaellaRecordDialog
from paella.kde.base.dialogs import VBoxDialog
from paella.kde.base.progress import LabeledProgress

from paella.kde.docgen.aptsrc import AptSourceDoc
from paella.kde.docgen.aptsrc import SuiteManagerDoc

class BaseManager(object):
    def __init__(self):
        pass

class SuiteAptAssigner(BaseAssigner):
    def __init__(self, parent, name='SuiteAptAssigner'):
        pass
    
class AptSrcDialog(BasePaellaRecordDialog):
    def __init__(self, parent, record=None, name='AptSrcDialog'):
        fields = ['apt_id', 'uri', 'dist', 'sections', 'local_path']
        BasePaellaRecordDialog.__init__(self, parent, fields,
                                        record=record, name=name)
        

class AptSrcProgressDialog(VBoxDialog):
    def __init__(self, parent, name='AptSrcProgressDialog'):
        VBoxDialog.__init__(self, parent, name=name)
        self.main_progress = LabeledProgress(self.vbox, 'apt source progress')
        self.package_progress = LabeledProgress(self.vbox, 'inserting packages')
        
        
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

    def _destroy_dialog(self):
        self._dialog = None
        
    def slotNew(self):
        win = AptSrcDialog(self)
        win.connect(win, SIGNAL('okClicked()'), self.newAptSrcSelected)
        apt_id = self.mainView.doc.apt_id
        if True:
            record = dict(apt_id='etch_base', uri='http://ftp.us.debian.org/debian',
                          dist='etch', sections='main contrib non-free',
                          local_path='/debian')
            win.setRecordData(record)
        if apt_id is not None:
            record = self.aptsrc.get_apt_row(apt_id)
            win.setRecordData(record)
        win.show()
        self._dialog = win
        
    def newAptSrcSelected(self):
        win = self._dialog
        record = win.getRecordData()
        apt_id = record['apt_id']
        parameters = [record[field] for field in win.frame.fields]
        self.aptsrc.insert_apt_source_row(*parameters)
        self._destroy_dialog()
        win = AptSrcProgressDialog(self)
        self.aptsrc.report_total_packages = win.package_progress.setTotalSteps
        self.aptsrc.report_package_inserted = win.package_progress.step_progress
        win.show()
        self.app.processEvents()
        self.aptsrc.insert_packages(apt_id)
        self.refreshListView()
        
        
        
    def selectionChanged(self):
        item = self.listView.currentItem()
        self.mainView.set_apt_source(item.apt_id)


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

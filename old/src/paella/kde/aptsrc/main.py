from qt import SIGNAL


from kdeui import KStdAction
from kdeui import KListViewItem

from useless.kdebase.mainwin import BaseSplitWindow

from paella.db.aptsrc import AptSourceHandler

from paella.kde.base.mainwin import BasePaellaWindow
from paella.kde.base.viewbrowser import ViewBrowser

from paella.kde.base.dialogs import BasePaellaRecordDialog
from paella.kde.base.dialogs import VBoxDialog
from paella.kde.base.progress import LabeledProgress

from docgen import AptSourceDoc

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


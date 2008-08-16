from qt import SIGNAL
from qt import QLabel

from kdeui import KStdAction
from kdeui import KListViewItem
from kdeui import KTextEdit, KLineEdit

from useless.kdebase.mainwin import BaseSplitWindow

from paella.db.aptkey import AptKeyHandler

from paella.kde.base.mainwin import BasePaellaWindow
from paella.kde.base.viewbrowser import ViewBrowser

from paella.kde.base.dialogs import BasePaellaRecordDialog
from paella.kde.base.dialogs import VBoxDialog
from paella.kde.base.progress import LabeledProgress


#from docgen import AptSourceDoc

class NewAptKeyDialog(VBoxDialog):
    def __init__(self, parent, name='NewAptKeyDialog'):
        VBoxDialog.__init__(self, parent, name=name)
        self.name_label = QLabel('name', self.vbox)
        self.name_entry = KLineEdit(self.vbox)
        self.data_lable = QLabel('data', self.vbox)
        self.data_entry = KTextEdit(self.vbox)
        self.resize(300, 500)
        self.setCaption('Enter new key')
        

class AptKeyDoc(object):
    def __init__(self, app):
        self.app = app
        self.data = ''

    def set_key(self, data):
        self.data = data

    def output(self):
        return '<pre>%s</pre>' % self.data
    

#class AptSrcDialog(BasePaellaRecordDialog):
#    def __init__(self, parent, record=None, name='AptSrcDialog'):
#        fields = ['apt_id', 'uri', 'dist', 'sections', 'local_path']
#        BasePaellaRecordDialog.__init__(self, parent, fields,
#                                        record=record, name=name)
        
class AptKeyView(ViewBrowser):
    def __init__(self, parent):
        ViewBrowser.__init__(self, parent, AptKeyDoc)
        self._dialog = None

    def set_key(self, data):
        self.doc.set_key(data)
        self.setText(self.doc.output())

    def resetView(self):
        self.set_key('')
        
class AptKeyWindow(BaseSplitWindow, BasePaellaWindow):
    def __init__(self, parent, name='AptKeyWindow'):
        BaseSplitWindow.__init__(self, parent, AptKeyView, name=name)
        self.initPaellaCommon()
        self.db = AptKeyHandler(self.conn)
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.setCaption('Apt Key Manager')
        #self.resize(500, 300)
        #self.splitter.setSizes([100, 400])
        #self.refreshListView()
        #self.mainView.resetView()
        self.refreshListView()

    def initlistView(self):
        self.listView.addColumn('name')

    def refreshListView(self):
        self.listView.clear()
        for row in self.db.get_keys():
            item = KListViewItem(self.listView, row.name)
            item.keyname = row.name
            item.keydata = row.data
            
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
        win = NewAptKeyDialog(self)
        win.connect(win, SIGNAL('okClicked()'), self.newKeySelected)
        win.show()
        self._dialog = win

    def newKeySelected(self):
        win = self._dialog
        if win is None:
            raise RuntimeError, "No dialog present"
        name = str(win.name_entry.text())
        data = str(win.data_entry.text())
        self.db.insert_key(name, data)
        self._destroy_dialog()
        self.refreshListView()
        
        

    def selectionChanged(self):
        item = self.listView.currentItem()
        self.mainView.set_key(item.keydata)
        



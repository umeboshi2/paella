from qt import QSplitter, QPixmap, QGridLayout
from qt import QLabel, QFrame, QString
from qt import SIGNAL, SLOT, Qt
from qt import QMimeSourceFactory

from kdeui import KMainWindow, KEdit
from kdeui import KMessageBox, KAboutDialog
from kdeui import KConfigDialog, KListView
from kdeui import KDialogBase, KLineEdit
from kdeui import KTextBrowser
from kdecore import KConfigDialogManager

class MimeSources(QMimeSourceFactory):
    def __init__(self):
        QMimeSourceFactory.__init__(self)
        self.addFilePath('/usr/share/wallpapers')
        

class AboutDialog(KAboutDialog):
    def __init__(self, parent, *args):
        KAboutDialog.__init__(self, parent, *args)
        self.setTitle('Paella Configuration Management Database')
        self.setAuthor('Joseph Rawson')
        self.show()

class MainWindow(KMainWindow):
    def __init__(self, parent, name='MainWindow'):
        #KMainWindow.__init__(self, parent, name, Qt.WType_Dialog)
        KMainWindow.__init__(self, parent, name)
        
        
class SimpleRecord(QGridLayout):
    def __init__(self, parent, fields, text=None, name='SimpleRecord'):
        if text is None:
            text = '<b>insert a simple record</b>'
        QGridLayout.__init__(self, parent, len(fields) + 1, 2, 1, -1, name)
        self.fields = fields
        self.entries = {}
        self._setupfields(parent)
        self.setSpacing(7)
        self.setMargin(10)
        self.addMultiCellWidget(QLabel(text, parent), 0, 0, 0, 1)

    def _setupfields(self, parent):
        for f in range(len(self.fields)):
            entry = KLineEdit('', parent)
            self.entries[self.fields[f]] = entry
            self.addWidget(entry, f + 1, 1)
            label = QLabel(entry, self.fields[f], parent, self.fields[f])
            self.addWidget(label, f + 1, 0)
        
class SimpleRecordDialog(KDialogBase):
    def __init__(self, parent, fields, name='SimpleRecordDialog'):
        KDialogBase.__init__(self, parent, name)
        self.page = QFrame(self)
        self.setMainWidget(self.page)
        text = 'this is a <em>simple</em> record dialog'
        self.grid = SimpleRecord(self.page, fields, text, name=name)
        self.showButtonApply(False)
        self.setButtonOKText('insert', 'insert')
        self.show()

class SimpleSplitWindow(KMainWindow):
    def __init__(self, app, parent, view, name):
        KMainWindow.__init__(self, parent, name)
        self.app = app
        self.conn = app.conn
        self.mainView = QSplitter(self, 'mainView')
        self.listView = KListView(self.mainView)
        self.listView.setRootIsDecorated(True)
        self.view = view(self.app, self.mainView)
        self.setCentralWidget(self.mainView)
        if hasattr(self, 'initlistView'):
            self.initlistView()
        self.connect(self.listView,
                     SIGNAL('selectionChanged()'), self.selectionChanged)
        self.show()

class ViewBrowser(KTextBrowser):
    def __init__(self, app, parent, doc):
        KTextBrowser.__init__(self, parent)
        self.setMimeSourceFactory(MimeSources())
        self.app = app
        self.doc = doc(self.app)
        self.setNotifyClick(True)
        

    def setMimeSourceFactory(self, factory=None):
        if factory is None:
            self.mimes = QMimeSourceFactory()
            self.mimes.addFilePath('/usr/share/wallpapers')
        else:
            self.mimes = factory
        KTextBrowser.setMimeSourceFactory(self, self.mimes)

    def set_clause(self, clause):
        self.doc.set_clause(clause)
        self.setText(self.doc.toxml())

class ViewWindow(KMainWindow):
    def __init__(self, app, parent, view, name):
        KMainWindow.__init__(self, parent, name)
        self.app = app
        self.conn = app.conn
        self.view = view(self.app, self)
        self.setCentralWidget(self.view)
        self.show()
        

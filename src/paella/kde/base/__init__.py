from qt import QSplitter, QPixmap, QGridLayout
from qt import QLabel, QFrame, QString
from qt import SIGNAL, SLOT, Qt
from qt import QMimeSourceFactory

from kdeui import KMainWindow, KEdit
from kdeui import KMessageBox, KAboutDialog
from kdeui import KConfigDialog, KListView
from kdeui import KDialogBase, KLineEdit
from kdeui import KTextBrowser
from kdeui import KPushButton, KListViewItem
from kdecore import KConfigDialogManager

from paella.db.midlevel import StatementCursor
from paella.sqlgen.clause import Eq

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

class RecordSelectorWindow(KMainWindow):
    def __init__(self, app, parent, recselector, name):
        KMainWindow.__init__(self, parent, name)
        self.app = app
        self.conn = app.conn
        self.mainView = recselector(self.app, self)
        self.setCentralWidget(self.mainView)
        self.show()
        

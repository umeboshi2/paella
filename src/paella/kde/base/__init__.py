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

class currentobject(object):
    def __init__(self):
      self.group = None
      self.id = None
      

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

class RecordSelectorWindow(KMainWindow):
    def __init__(self, app, parent, recselector, name):
        KMainWindow.__init__(self, parent, name)
        self.app = app
        self.conn = app.conn
        self.mainView = recselector(self.app, self)
        self.setCentralWidget(self.mainView)
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

class EditableRecord(QGridLayout):
    def __init__(self, parent, fields, text=None, name='EditableRecord'):
        QGridLayout.__init__(self, parent, len(fields) + 2, 2, 1, -1, name)
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
        self.insButton = KPushButton('insert/new', parent)
        self.updButton = KPushButton('update', parent)
        self.addWidget(self.insButton, len(self.fields), 0)
        self.addWidget(self.updButton, len(self.fields), 1)
        
    def get_data(self):
        return dict([(k, v.text()) for k,v in self.entries.items()])

        
class RecordSelector(QSplitter):
    def __init__(self, app, parent, table, fields, idcol, groupfields, view, name='RecordSelector'):
        QSplitter.__init__(self, parent, name)
        self.current = currentobject()
        self.app = app
        self.conn = app.conn
        self.mcursor = StatementCursor(self.conn)
        self.table = table
        self.fields = fields
        self.idcol = idcol
        self.groupfields = groupfields
        self.listView = KListView(self)
        self.vsplit = QSplitter(self)
        self.vsplit.setOrientation(Qt.Vertical)
        self.recView = view(self.app, self.vsplit)
        frame = QFrame(self.vsplit)
        self.recForm = EditableRecord(frame, fields)
        self.connect(self.listView, SIGNAL('selectionChanged()'), self.groupChanged)
        self.connect(self.recForm.insButton, SIGNAL('clicked()'), self.insertRecord)
        self.connect(self.recForm.updButton, SIGNAL('clicked()'), self.updateRecord)
        self.initlistView()
        self.setSource(self.handleURL)
    
    def initlistView(self):
        self.listView.addColumn('group')
        self.listView.setRootIsDecorated(True)
        all = KListViewItem(self.listView, 'all')
        groups = [KListViewItem(self.listView, g) for g in self.groupfields]
        for g, parent in zip(self.groupfields, groups):
            fields = ['distinct %s' % g]
            rows = self.mcursor.select(fields=fields, table=self.table, order=g)
            for row in rows:
                item = KListViewItem(parent, row[g])
                item.groupfield = g
                

    def groupChanged(self):
        item = self.listView.currentItem()
        self.current.group = item.text(0)
        if hasattr(item, 'groupfield'):
            clause = Eq(item.groupfield, self.current.group)
            self.recView.set_clause(clause)
        elif self.current.group == 'all':
            self.recView.set_clause(None)
        else:
            self.recView.set_clause('NULL')

    def handleURL(self, url):
        action, obj, ident = str(url).split('.')
        row = self.mcursor.select_row(fields=self.fields,
                                      table=self.table, clause=Eq(self.idcol, ident))
        entries = self.recForm.entries
        for field in entries:
            entries[field].setText(row[field])
        self.current.id = ident
        

    def setSource(self, handler):
        self.recView.setSource = handler

    def insertRecord(self):
        data = self.recForm.get_data()
        self.db.insertData(self.idcol, self.table, data)
        self.groupChanged()

    def updateRecord(self):
        if self.current.id is not None:
            data = self.recForm.get_data()
            clause = Eq(self.idcol, self.current.id)
            row = self.mcursor.select_row(table=self.table, clause=clause)
            updict = {}
            for k, v in data.items():
                if str(row[k]) != str(v) and str(v):
                    print v
                    updict[k] = v
            print updict
        if updict:
            self.mcursor.update(table=self.table, data=updict, clause=clause)
            self.groupChanged()
            
    
        

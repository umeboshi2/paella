from qt import QSplitter
from qt import QFrame
from qt import QGridLayout
from qt import QLabel

from kdeui import KListView, KListViewItem
from kdeui import KLineEdit
from kdeui import KPushButton

from useless.kdebase import get_application_pointer
from useless.kdebase.manager_widget import BaseManagerWidget

class BasePaellaWidget(object):
    def initPaellaCommon(self):
        self.app = get_application_pointer()
        self.conn = self.app.conn
        self.cfg = self.app.cfg
        
        
class PaellaManagerWidget(BaseManagerWidget, BasePaellaWidget):
    def __init__(self, parent, mainview, listview=None, name='PaellaManagerWidget'):
        BaseManagerWidget.__init__(self, parent, mainview, listview=listview,
                                   name=name)
        BasePaellaWidget.initPaellaCommon(self)

class EditableRecordFrame(QFrame):
    def __init__(self, parent, fields, text=None, name='EditableRecordFrame'):
        QFrame.__init__(self, parent, name)
        numrows = len(fields) +2
        numcols = 2
        self.grid = QGridLayout(self, numrows, numcols, 1, -1, name)
        self.fields = fields
        self.entries = {}
        self._setupfields()
        self.grid.setSpacing(7)
        self.grid.setMargin(10)
        self.text_label = QLabel(text, self)
        self.grid.addMultiCellWidget(self.text_label, 0, 0, 0, 1)
        
    def _setupfields(self):
        numfields = len(self.fields)
        for fnum in range(numfields):
            fname = self.fields[fnum]
            entry = KLineEdit('', self)
            self.entries[fname] = entry
            self.grid.addWidget(entry, fnum + 1, 1)
            label = QLabel(entry, fname, self, fname)
            self.grid.addWidget(label, fnum + 1, 0)
        self.insButton = KPushButton('insert/new', self)
        self.updButton = KPushButton('update', self)
        self.grid.addWidget(self.insButton, numfields, 0)
        self.grid.addWidget(self.updButton, numfields, 1)

    def get_data(self):
        data = {}
        for field in self.entries:
            data[field] = str(self.entries[field].text())
        return data
    
        

# helper object for PaellaRecordSelector
class currentobject(object):
    def __init__(self):
        self.group = None
        self.id = None

# this a sort-of ugly class        
class PaellaRecordSelector(QSplitter, BasePaellaWidget):
    def __init__(self, parent, table, fields, idcol, groupfields,
                 mainview, name='PaellaRecordSelector'):
        #PaellaManagerWidget.__init__(self, parent, mainview, name=name)
        QSplitter.__init__(self, parent, name)
        BasePaellaWidget.initPaellaCommon(self)
        self.current = currentobject()
        self.table = table
        self.fields = fields
        self.idcol = idcol
        self.groupfields = groupfields
        self.listView = KListView(self)
        self.vsplit = QSplitter(self)
        self.vsplit.setOrientation(self.Vertical)
        self.mainView = mainview(self.vsplit)
        self.recordForm = EditableRecordFrame(self, fields)
        self.connect(self.listView, SIGNAL('selectionChanged()'),
                     self.groupChanged)
        self.connect(self.recordForm.insButton, SIGNAL('clicked()'),
                     self.insertRecord)
        self.connect(self.recordForm.updButton, SIGNAL('clicked()'),
                     self.updateRecord)
        self.initlistView()
        self.setSource(self.handleURL)
        
    def initlistView(self):
        self.listView.addColumn('group')
        self.listView.setRootIsDecorated(True)
        

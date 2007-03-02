from qt import SIGNAL
from qt import QWidget
from qt import QGridLayout
from qt import QLabel
from qt import QGridView

from kdeui import KLineEdit

from widgets import BasePaellaWidget

class TraitVariableLineEdit(KLineEdit):
    def __init__(self, parent, name='TraitVariableLineEdit'):
        KLineEdit.__init__(self, parent, name)

    def createPopupMenu(self, pos=None):
        menu = KLineEdit.createPopupMenu(self)
        menu.insertItem('Hello There Dude!')
        return menu
    
        
class BaseVariablesEditor(QWidget, BasePaellaWidget):
    def __init__(self, parent, fields=[], data={}, name='VariablesEditor'):
        QWidget.__init__(self, parent, name)
        self.initPaellaCommon()
        self.grid = QGridLayout(self, len(fields), 2, 1, -1, 'VariablesEditorLayout')
        self.fields = fields
        self.fields.sort()
        self._data = data
        self.entries = {}
        self._labels = {}
        if fields:
            self._setup_grid()
        self.grid.setSpacing(7)
        self.grid.setMargin(10)
        
    def _clear_grid(self):
        print 'clearing grid'
        self.grid.deleteAllItems()
        for entry in self.entries.values():
            entry.close(True)
        for label in self._labels.values():
            label.close(True)

    def _set_data(self):
        self._data.clear()
        for field in self.fields:
            value = str(self.entries[field].text())
            self._data[field] = value
        
    def _setup_grid(self):
        self._clear_grid()
        numfields = len(self.fields)
        for fnum in range(numfields):
            fname = self.fields[fnum]
            data = ''
            if self._data.has_key(fname):
                data = self._data[fname]
            #entry = KLineEdit(data, self)
            entry = TraitVariableLineEdit(data, self)
            entry.show()
            self.entries[fname] = entry
            label = QLabel(entry, fname, self, fname)
            label.show()
            self._labels[fname] = label
            self.grid.addWidget(label, fnum, 0)
            self.grid.addWidget(entry, fnum, 1)

    def set_fields(self, fields, data={}):
        self.fields = fields
        self._data = data
        self._setup_grid()
        
    def add_field(self, field, value=''):
        if field not in self.fields:
            self._set_data()
            self.fields.append(field)
            self.fields.sort()
            if value:
                self._data[field] = value
            self._setup_grid()

    def get_data(self):
        self._set_data()
        return dict(self._data.items())
    
            

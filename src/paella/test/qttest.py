import sys
from qt import QLabel, QApplication
from qt import QListView, QListViewItem
from qt import QToolBox, QHBox, QHBoxLayout
from qt import QTabBar, QSplitter

from paella.base import Error
from paella.db.midlevel import StatementCursor
from paella.profile.base import PaellaConfig, PaellaConnection

class Listbox(QListView):
    def __init__(self, parent=None, rows=[], name='ListBox', columns=[]):
        self.__clist_rows__ = rows
        if len(self.__clist_rows__):
            test_row = self.__clist_rows__[0]
            if not (hasattr(test_row, '_keylist_') or hasattr(test_row, '_desc_')):
                if columns:
                    if len(columns) == 1:
                        nrows = [[x] for x in self.__clist_rows__]
                        self.__clist_rows__ = nrows
                    dbrows = [DbBaseRow(columns, x) for x in self.__clist_rows__]
                    self.__clist_rows__ = dbrows
                    self.__clist_row_desc = self.__clist_rows__[0]._keylist_
                    self.__col_titles__ = self.__clist_row_desc
                    
                else:
                    self.__clist_row_desc = None
                    self.__col_titles__ = ['nothing']
            else:
                if hasattr(test_row, '_desc_'):
                    self.__clist_row_desc = [x[0] for x in test_row._desc_]
                else:
                    self.__clist_row_desc = test_row._keylist_
                self.__col_titles__ = self.__clist_row_desc
        else:
            self.__col_titles__ = ['nothing']
            self.__clist_rows__ = []
        QListView.__init__(self, None)
        self.__setup_listbox()
        self.show()
        self.append_rows()
        
    def __setup_listbox(self):
        for col in self.__col_titles__:
            self.addColumn(col)

    def append_rows(self):
        for row in self.__clist_rows__:
            lvrow = QListViewItem(self, *map(str, row))
            #for col in self.__col_titles__:
            #    print row[col]
            #    lvrow.insertItem(QListViewItem(lvrow, str(row[col])))
            self.insertItem(lvrow)
            self.sort()

class Toolbar(QToolBox):
    pass


class ListNotebook(QSplitter):
    def __init__(self, parent=None):
        QSplitter.__init__(self, parent, 'hsplit')
        self.setOrientation(QSplitter.Horizontal)
        self.listbox = QListView(self)
        #self.insertWidget(self.listbox)
        self.notebook = QTabBar(self)
        #self.addWidget(self.notebook)
        

cfg = PaellaConfig('database')
conn = PaellaConnection()
cursor = StatementCursor(conn)
app = QApplication(sys.argv)
#lv = QListView(None)
#lv.addColumn('section')
#for s in cursor.tables():
#    lv.insertItem(QListViewItem(lv, s))
#lv.show()
hello = QLabel('<font color=blue>%s <i>Qt!</i></font>' % str(cfg.section), None)
#lb = Listbox(None, cursor.select(table='gunny_templates'))
ln = ListNotebook()
ln.show()
ln.listbox.addColumn('table')
for t in cursor.tables():
    ln.listbox.insertItem(QListViewItem(ln.listbox, t))

app.setMainWidget(ln)

hello.show()
hello.setText(str(cfg.sections()))
app.exec_loop()

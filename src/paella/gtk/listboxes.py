from gtk import CList
from gtk import TRUE
from gtk import DEST_DEFAULT_MOTION
from gtk import DEST_DEFAULT_HIGHLIGHT
from gtk import DEST_DEFAULT_DROP
from gtk.gdk import ACTION_COPY, ACTION_MOVE

from paella.base.objects import DbRowDescription, DbBaseRow


def listbox_rightclick_select(*args):
        print 'args %s' %str(args)
        listbox, event = args
        if (event.type) == 3:
                selection= listbox.get_selection_info(event.x,event.y)
                listbox.select_row(selection[0], selection[1])

    
class ListBox(CList):
    def __init__(self, rows=[], name='ListBox', columns=[]):
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
        CList.__init__(self, len(self.__col_titles__), self.__col_titles__)
        self.set_name(name)
        self.__setup_listbox()
        self.show()
        self.append_rows()
        
    def __setup_listbox(self):
        self.set_auto_sort(0)
        self.column_titles_active()
        self.column_titles_show()
        self.set_reorderable(1)
        self.connect('click_column', self.sort_column)
        for column_no in xrange(len(self.__col_titles__)):
            self.set_column_resizeable(column_no, TRUE)

    def set_row_select(self, select_fun):
        self.__select_row_func__ = select_fun
        self.connect('select_row', self.__select_row__)

    def __select_row__(self, *args):
        prev, ltst = 'the_previous_selection', 'the_latest_selection'
        self.set_data(prev, self.get_data(ltst))
        self.set_data(ltst, [sel for sel in self.selection])
        return self.__select_row_func__(*args)

    def sort_column(self, *args):
        listbox = args[0]
        column_no = args[1]
        rows = self.__clist_rows__
        if len(rows):
            tst = self.get_row_data(0)[column_no]
            if isinstance(tst, (int, long, float)):
                f = int
                if isinstance(tst, float):
                    f = float
                def cmpfunc(x, y):
                    return cmp(f(x[column_no]), f(y[column_no]))
                listbox.clear()
                rows.sort(cmpfunc)
                listbox.freeze()
                self.append_rows()
                listbox.thaw()
            else:
                self.set_sort_column(column_no)
                listbox.sort()

    def append_rows(self):
        self.__row_data__ = []
        index = 0
        for row in self.__clist_rows__:
            self.append(map(str, row.values()))
            self.set_row_data(index, row)
            self.__row_data__.append(row)
            index += 1
        self.columns_autosize()
        self._col_titles = self.__col_titles__
    def get_selected_data(self):
        rows = []
        if len(self.selection):
            for row in self.selection:
                rows.append(self.get_row_data(row))
        return rows
            

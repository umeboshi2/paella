from paella.gtk.dialogs import CList

from gtk import mainloop, mainquit

from paella.db.lowlevel import QuickConn()
from paella.db.midlevel import StatementCursor
from paella.sqlgen.statement import Statement

class TableBrowser(CList):
    def __init__(self, conn):
        self.cmd = StatementCursor(conn, name='TableBrowser')
        CList.__init__(self, 'Tables', name='TableBrowser')
        self.set_rows(self.cmd.tables(), ['table'])
        self.set_row_select(self.__hello__)
        self.statement = Statement('select')
    def __hello__(self, listbox, row, column, event):
        self.statement.table = listbox.get_selected_data()[0]['table']
        table = self.statement.table
        tb = CList(table, name=table)
        rows = self.cmd.getall('*', table)
        cols = []
        if len(rows):
            cols = rows[0].keys()
        tb.set_rows(rows, cols)
        tb.set_usize(400,200)
        
        
        
if __name__ == '__main__':
    c = QuickConn()
    win = TableBrowser(c)
    win.connect('destroy', mainquit)
    
    
    def dtable():
        cmd.execute('drop table themebase')
    def dtables():
        for t in cmd.tables():
            if t not in  ['footable']:
                cmd.execute('drop table %s' %t)
    #dtables()
    mainloop()
    

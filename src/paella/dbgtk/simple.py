from pyPgSQL.libpq import IntegrityError, OperationalError
from paella.db.pg_special import get_pkey_info, get_attributes
from paella.db.lowlevel import BaseConnection
from paella.db.midlevel import StatementCursor
from paella.sqlgen.clause import Eq, SimpleClause
from paella.gtk.middle import ListNoteBook, ScrollCList
from paella.gtk.windows import CommandBoxWindow
from paella.gtk.helpers import HasDialogs, make_menu, HasListbox
from paella.gtk import dialogs
from paella.gtk.dialog_helpers import get_single_row
from gtk import ScrolledWindow

class RelationalBrowser(ListNoteBook, HasDialogs):
    def __init__(self, conn, maintable, reltable, pkey, fields):
        self.menu = make_menu(['insert', 'update', 'done'], self.pkey_command)
        ListNoteBook.__init__(self)
        self.conn = conn
        self.main = StatementCursor(self.conn)
        self.main.set_table(maintable)
        self.rel = StatementCursor(self.conn)
        self.rel.set_table(reltable)
        self.pkey = pkey
        self._fields = fields
        self.fields = [self.pkey] + self._fields
        self.reset_rows()
        self.dialogs = {}.fromkeys(['insert', 'update', 'delete'])
        self.relmenu = make_menu(['insert', 'update', 'delete'], self.relmenu_command)
        
        
    def reset_rows(self):
        self.set_rows(self.main.select(order=self.pkey))
        self.set_row_select(self.pkey_selected)
        
    def pkey_selected(self, listbox, row, column, event):
        value = listbox.get_selected_data()[0][0]
        self.current_value = value
        if value not in self.pages:
            rows  = self.rel.select(clause=Eq(self.pkey, value), order=self.pkey)
            rtable = ScrollCList(rcmenu=self.relmenu)
            rtable.set_rows(rows)
            self.append_page(rtable, value)
        self.set_current_page(value)

    def pkey_command(self, menuitem, command):
        if command == 'insert':
            if self.dialogs['insert'] is None:
                dialog = dialogs.Entry('insert a %s' % self.pkey, name='insert')
                dialog.set_ok(self.pkey_insert_ok)
                dialog.set_cancel(self.destroy_dialog)
                self.dialogs['insert'] = dialog
        elif command == 'update':
            dialogs.Message('need to set update to cascade in db')
        elif command == 'done':
            value = None
            try:
                value = self.listbox.get_selected_data()[0][0]
            except IndexError:
                dialogs.Message('need to select %s first' % self.pkey)
            if value is not None:
                self.remove_page(value)
                

    def pkey_insert_ok(self, *args):
        dialog = self.dialogs['insert'] 
        value = dialog.get()
        print value
        try:
            self.main.insert(data={self.pkey : value})
            inserted = True
        except OperationalError:
            dialogs.Message('bad query\n%s is not allowed' % value)
        if inserted:
            self.destroy_dialog(dialog)
            self.reset_rows()
            
    def relmenu_command(self, menuitem, command):
        print command
        if command in ['insert', 'update', 'delete']:
            if self.dialogs[command] is None:
                clause = Eq(self.pkey, self.current_value)
                try:
                    row = self.rel.select(clause=clause)[0]
                except IndexError:
                    row = dict.fromkeys(self.fields)
                row[self.pkey] = self.current_value
                if command in ['insert', 'delete']:
                    fields = self.fields
                    clause = None
                else:
                    fields = self._fields
                    clause = Eq(self.pkey, self.current_value)
                make_record_dialog(self, command, row,
                                   self.relmenu_command_selected,
                                   self.pkey, fields, {command:command})
            print self.dialogs.items()
    

    def relmenu_command_selected(self, button, *data):
        command = button.get_name()
        dialog = self.dialogs[command]
        items = dialog.items()
        if command == 'insert':
            self.rel.insert(data=dict(items))
        elif command == 'delete':
            print 'delete delete delete delete'
            clause = SimpleClause(items, '=', 'and')
            dialogs.Message(self.rel.stmt.delete(clause=clause))
            
        if False:
            dialog = self.dialogs['insert']
            print dialog
            items = dialog.items()
            print items
            self.rel.insert(data=dict(items))
            self.destroy_dialog(dialog)
            self.reset_rows()
        

if __name__ == '__main__':
    from paella.base.config import Configuration
    from paella.db.lowlevel import QuickConn
    from gtk import mainloop, mainquit
    from paella.profile.base import PaellaConnection
    conn = PaellaConnection()
    te = TableEditor(conn, 'suites')
    te.connect('destroy', mainquit)
    mainloop()
    
        

from pyPgSQL.libpq import IntegrityError, OperationalError
from paella.base import Error
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

def make_record_dialog(parent, name, row, okfun, pkey, fields, cdata):
    items = [(x, row[x]) for x in fields]
    print 'items are', items
    dialog = dialogs.RecordEntry(cdata[name], items, name=name)
    dialog.set_ok(okfun)
    dialog.set_cancel(parent.destroy_dialog)
    dialog.pkey = pkey
    if parent is not None:
        parent.dialogs[name] = dialog
    else:
        return dialog
    

class ListWin(CommandBoxWindow, HasDialogs, HasListbox):
    def __init__(self):
        CommandBoxWindow.__init__(self)
        self.scroll = ScrolledWindow()
        self.vbox.add(self.scroll)
        self.scroll.show()
        if hasattr(self, 'menu'):
            HasListbox.__init__(self, self.scroll, rcmenu=self.menu)
        else:
            HasListbox.__init__(self, self.scroll)

class BaseRelationalBrowser(ListNoteBook, HasDialogs):
    def __init__(self, conn, maintable, pkey):
        self.menu = make_menu(['insert', 'update', 'done'], self.pkey_command)
        ListNoteBook.__init__(self)
        self.conn = conn
        self.main = StatementCursor(self.conn)
        self.main.set_table(maintable)
        self.pkey = pkey
        self.dialogs = {}.fromkeys(['insert', 'update', 'delete'])
        self.relations = {}
        
    def reset_rows(self):
        self.set_rows(self.main.select(order=self.pkey))
        self.set_row_select(self.pkey_selected)

    def pkey_selected(self, listbox, row, column, event):
        print listbox.get_selected_data()[0][0]
        
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
                dialogs.Message('ok, i am done.')

    def append_relation(self, table, fields=[], fkeyname=None):
        if table not in self.relations:
            if not fields:
                if fkeyname is None:
                    fkeyname = self.pkey
                fields = [f for f in self.main.fields(table) if f != fkeyname]
            if fkeyname is None:
                fkeyname = self.pkey
            self.relations[table] = fkeyname, fields
        else:
            raise Error, "relation already exists %s" % table
    
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
        
            
            

class TableEditor(ListWin):
    def __init__(self, conn, table, pkey=None, fields=[],
                 command_data=dict(new='new entry', edit='edit entry')):
        ListWin.__init__(self)
        self.conn = conn
        self.cursor = StatementCursor(self.conn)
        self.cursor.set_table(table)
        self._cdata = command_data
        self.tbar.add_button('new', self._cdata['new'], self.toolbar_button_pressed)
        self.tbar.add_button('edit', self._cdata['edit'], self.toolbar_button_pressed)
        if pkey is None:
            print get_pkey_info(StatementCursor(conn), table)
        self._pkey = pkey
        self.reset_rows()
        self._fields = fields
        self.fields = [pkey] + self._fields
        self.dialogs = {}.fromkeys(self._cdata.keys())

    def reset_rows(self):
        self.set_rows(self.cursor.select(order=self._pkey))

    def toolbar_button_pressed(self, button, data):
        row = None
        if data == 'new':
            if self.dialogs['new'] is None:
                row = self.cursor.select()[0]
                self._make_dialog('new', row, self.add_new_record)
        elif data == 'edit':
            if self.dialogs['edit'] is None:
                row = get_single_row(self.listbox, self._pkey)
                if row is not None:
                    self._make_dialog('edit', row, self.edit_record, row[self._pkey])
            
                
                
    def _make_dialog(self, name, row, okfun, pkey=None):
        if name == 'edit':
            fields = self._fields
        else:
            fields = self.fields
        make_record_dialog(self, name, row, okfun, pkey, fields, self._cdata)
        
    def add_new_record(self, *args):
        dialog = self.dialogs['new']
        self.cursor.insert(data=dict(dialog.items()))
        self.destroy_dialog(dialog)
        self.reset_rows()

    def edit_record(self, *args):
        dialog = self.dialogs['edit']
        clause = Eq(self._pkey, dialog.pkey)
        data = dict(dialog.items())
        self.cursor.update(data=data, clause=clause)
        self.destroy_dialog(dialog)
        self.reset_rows()

class DatabaseManager(ListNoteBook):
    def __init__(self, dbhost, dbuser, passwd=None):
        self.menu = make_menu(['connect', 'disconnect'], self.db_command)
        ListNoteBook.__init__(self)
        self.conn = BaseConnection(user=dbuser, host=dbhost,
                                   dbname='template1', passwd=passwd)
        self.dialogs = {}.fromkeys(['database'])
        self.dbname = 'template1'
        self.reset_rows()
        self.connections = {}
        self._dbuser = dbuser
        self._dbhost = dbhost
        self._dbpasswd = passwd
        self.table_edit_menu = make_menu(['edit'], self.table_edit_menu_command)
        
    def _connect(self, dbname):
        if self.connections.has_key(dbname):
            dialogs.Message('connection already exists for %s' % dbname)
        else:
            conn = BaseConnection(user=self._dbuser, host=self._dbhost,
                                  dbname=dbname, passwd=self._dbpasswd)
            self.connections[dbname] = conn
            cursor = StatementCursor(self.connections[dbname])
            rows = cursor.tables()
            tables = ScrollCList(rcmenu=self.table_edit_menu)
            tables.set_rows(rows, columns=['table'])
            self.append_page(tables, dbname)
            self.set_current_page(dbname)
            
    def reset_rows(self, *args):
        cursor = StatementCursor(self.conn)
        self.set_rows(cursor.select(fields='datname', table='pg_database'))
        self.set_row_select(self.db_selected)

    def db_selected(self, *args):
        print args
        dbname = self.listbox.get_selected_data()[0][0]
        if dbname in self.connections:
            self.set_current_page(dbname)

    def db_command(self, menuitem, command):
        row = get_single_row(self.listbox, 'a database')
        if row is not None:
            if command == 'connect':
                dbname = row[0]
                self._connect(dbname)

    def table_edit_menu_command(self, menuitem, command):
        print command
        print self.pages
        print self.current_page()
        
                
                            
class BrowserWin(CommandBoxWindow):
    def __init__(self, conn, browser):
        CommandBoxWindow.__init__(self)
        self.conn = conn
        self.browser = browser
        self.vbox.add(self.browser)

if __name__ == '__main__':
    from paella.base.config import Configuration
    from paella.db.lowlevel import QuickConn
    from gtk import mainloop, mainquit
    from paella.profile.base import PaellaConnection
    conn = PaellaConnection()
    te = TableEditor(conn, 'suites')
    te.connect('destroy', mainquit)
    mainloop()
    
        

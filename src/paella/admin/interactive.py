from paella.base.config import Configuration
from paella.db.lowlevel import QuickConn
from paella.db.midlevel import StatementCursor

from paella.gtk import dialogs
from paella.gtk.simple import SimpleMenu
from paella.gtk.middle import ScrollCList
from paella.gtk.windows import MenuWindow


#statement_atts = ['select', 'update', 'insert', 'tables',

class Select(object):
    def __init__(self, conn):
        self.conn = conn
        self.win = MenuWindow()
        self.scroll = ScrollCList()
        self.win.vbox.add(self.scroll)
        self.s = StatementCursor(self.conn)

    def select(self, *args, **kw):
        rows = self.s.select(*args, **kw)
        self.scroll.set_rows(rows)


#conn = QuickConn()
#s = StatementCursor(conn)
#s = Select(conn)

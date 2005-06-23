from useless.base.config import Configuration
from useless.db.lowlevel import QuickConn
from useless.db.midlevel import StatementCursor

from useless.gtk import dialogs
from useless.gtk.simple import SimpleMenu
from useless.gtk.middle import ScrollCList
from useless.gtk.windows import MenuWindow


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

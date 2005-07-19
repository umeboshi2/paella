from kdeui import KDialogBase
from kdeui import KListView, KListViewItem

from paella.db.base import Suites

def dbwidget(widget, app):
    widget.app = app
    widget.conn = app.conn
    widget.db = app.db
    
class SuiteSelector(KDialogBase):
    def __init__(self, app, parent):
        KDialogBase.__init__(self, parent, 'SuiteSelector')
        dbwidget(self, app)
        self.suites = Suites(self.conn)
        self.listView = KListView(self)
        self.listView.addColumn('suite')
        self.setMainWidget(self.listView)
        self.refreshlistView()
        self.show()
        
    def refreshlistView(self):
        self.listView.clear()
        for suite in self.suites.list():
            item = KListViewItem(self.listView, suite)
            item.suite = suite
            

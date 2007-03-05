#from forgetHTML import UnorderedList, ListItem
from forgetHTML import Table, TableRow, TableCell
#from forgetHTML import Anchor
#from forgetHTML import Paragraph
from paella.db.aptsrc import AptSourceHandler
from paella.db.suitehandler import SuiteHandler

from base import BaseDocument
from base import Bold

class AptSourceTable(Table):
    def __init__(self, **atts):
        Table.__init__(self, **atts)
        
    def set_apt_source(self, row):
        self._content = []
        fields = ['apt_id', 'uri', 'dist', 'sections', 'local_path']
        for field in fields:
            fieldrow = TableRow()
            fieldrow.append(TableCell(Bold(field)))
            fieldrow.append(TableCell(row[field]))
            self.append(fieldrow)


class AptSourceDoc(BaseDocument):
    def __init__(self, app, **atts):
        BaseDocument.__init__(self, app, **atts)
        self.aptsrc = AptSourceHandler(self.conn)
        self.apt_table = AptSourceTable()
        self.apt_id = None
        
    def set_apt_source(self, apt_id=None):
        self.clear_body()
        self.apt_id = apt_id
        if apt_id is None:
            self.body.append('Hello There')
        else:
            self.body.append(self.apt_table)
            self.apt_table.set_apt_source(self.aptsrc.get_apt_row(apt_id))
        

class SuiteManagerDoc(BaseDocument):
    def __init__(self, app, **atts):
        BaseDocument.__init__(self, app, **atts)
        self.handler = SuiteHandler(self.conn, self.app.cfg)
        

    def set_suite(self, suite):
        self.suite = suite
        self.handler.set_suite(suite)
        self.clear_body()
        self.body.append('Suite:  %s' % suite)

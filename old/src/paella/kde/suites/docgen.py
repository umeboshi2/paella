#from useless.base.forgethtml import UnorderedList, ListItem
from useless.base.forgethtml import Table, TableRow, TableCell
#from useless.base.forgethtml import Anchor
#from useless.base.forgethtml import Paragraph

from paella.kde.docgen.base import BaseDocument
from paella.kde.docgen.base import Bold
from paella.kde.docgen.base import SimpleTitleElement

from paella.db.base import SuiteCursor

class SuiteAptSrcTable(Table):
    def __init__(self, **atts):
        Table.__init__(self, **atts)

    def set_suite(self, suite, apt_ids):
        self._content = []
        
        headrow = TableRow(TableCell('Suite: %s' % suite))
        self.append(headrow)
        aptsrc_row = TableRow(TableCell('Apt Sources'))
        
class SuiteManagerDoc(BaseDocument):
    def __init__(self, app, **atts):
        BaseDocument.__init__(self, app, **atts)
        self.cursor = SuiteCursor(self.conn)
        
        

    def set_suite(self, suite):
        self.suite = suite
        self.cursor.set_suite(suite)
        self.clear_body()
        attributes = dict(bgcolor='IndianRed', width='100%')
        title = SimpleTitleElement('Suite:  %s' % suite, **attributes)
        title.cell.attributes['align'] = 'center'
        self.body.append(title)
        apt_rows = self.cursor.get_apt_rows()
        if len(apt_rows):
            aptsrc_table = Table(bgcolor='khaki')
            self.body.append(aptsrc_table)
            fields = ['apt_id', 'uri', 'dist', 'sections', 'local_path']
            headrow = TableRow()
            for field in fields:
                headrow.append(TableCell(Bold(field)))
            for row in apt_rows:
                tblrow = TableRow()
                aptsrc_table.append(tblrow)
                for field in fields:
                    tblrow.append(TableCell(row[field]))
            

    

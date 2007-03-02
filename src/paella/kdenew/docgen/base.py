from forgetHTML import Element
from forgetHTML import Link, Inline
from forgetHTML import Table, TableRow, TableCell
from forgetHTML import TableHeader
from forgetHTML import SimpleDocument
from forgetHTML import Header

# some elements not in forgetHTML
# these classes taken from useless.webframe.forgethtml
class Favicon(Link):
    def __init__(self, href='/favicon.ico', type='image/x-icon'):
        Link.__init__(self, rel='shortcut icon',
                      type=type,
                      href=href)
        
class Bold(Inline):
    tag = 'b'

class Font(Inline):
    tag = 'font'
    
# hacky way to set the color on the header row of a table
# this should be done in a class somewhere
def color_header(table, color='cornsilk3'):
    table.header['bgcolor'] = color

# This is analogous to RecordElement in xmlgen.base
class RecordTable(Table):
    def __init__(self, fields, idcol, action, record, **atts):
        Table.__init__(self, **atts)
        self.record = record
        refdata = None
        if hasattr(record, '_refdata'):
            refdata = record._refdata
        for field in fields:
            # make url first if action
            if action:
                stringlist = map(str, [action, field, record[idcol]])
                url = '.'.join(stringlist)
            row = TableRow()
            keycell = TableCell(bgcolor='DarkSeaGreen')
            keycell.set(Bold(field))
            row.append(keycell)
            valcell = TableCell()
            # the following code needs more comments
            # this should be a private method called _make_valcell
            if refdata is not None and field in refdata.cols:
                ridcol = refdata.cols[field]
                refrec = refrec.data[field][record[ridcol]]
                node = refdata.object[field](refrec)
                if action:
                    valcell.set(Anchor(node, href=url))
                else:
                    valcell.set(node)
            elif action:
                valcell.set(Anchor(record[field], href=url))
            else:
                valcell.set(record[field])
            row.append(valcell)
            self.val = valcell
            self.key = keycell
            self.append(row)
            

# This is analogous to SimpleTitleElement in useless.xmlgen.base
class SimpleTitleElement(Table):
    def __init__(self, title, **attributes):
        Table.__init__(self, **attributes)
        self.row = TableRow()
        self.cell = TableCell()
        self.set(self.row)
        self.row.set(self.cell)
        self.h1 = Header(level=1)
        self._font = Font(color='gold')
        self.cell.set(self.h1)
        self.h1.set(self._font)
        self.set_title(title)

    def set_font(self, **attributes):
        self._font.attributes.clear()
        self._font.attributes.update(attributes)

    def set_title(self, title):
        self._title = title
        self._font.set(self._title)

    # use this to make action links to the right of the title
    def create_rightside_table(self):
        self._rstable = Table(border=0)
        self.row.append(TableCell(self._rstable, align='right'))

    def append_rightside_anchor(self, anchor):
        row = TableRow()
        self._rstable.append(row)
        cell = TableCell(align='right', rowspan=1)
        row.set(cell)
        font = Font(color='gold')
        cell.set(font)
        font.set(anchor)
        
# all of the above classes need to be put in either useless
# or forgetHTML upstream

class BaseDocument(SimpleDocument):
    def __init__(self, app, title='BaseDocument', **atts):
        SimpleDocument.__init__(self, title=title)
        if atts:
            print atts
            print 'Warning attributes are unimplemented in BaseDocument'
        self.app = app
        self.conn = app.conn

    def clear_body(self):
        # need to request Element.clear method in forgetHTML
        self.body._content = []

class TxtTD(TableCell):
    def __init__(self, text):
        print "Warning, TxtTD is deprecated"
        TableCell.__init__(self, text)
        
class TraitEnvTable(RecordTable):
    def __init__(self, trait, env, **atts):
        fields = env.keys()
        fields.sort()
        RecordTable.__init__(self, fields, 'trait', None, env, **atts)

class SectionTitle(SimpleTitleElement):
    def __init__(self, text, **atts):
        attributes = dict(bgcolor='IndianRed', width='100%')
        attributes.update(atts)
        SimpleTitleElement.__init__(self, text, **attributes)

class BaseFieldTable(Table):
    def __init__(self, fields, row, **atts):
        Table.__init__(self, **atts)
        for field in fields:
            row = TableRow()
            field_cell = TableCell(field)
            row.append(field_cell)
            value_cell = TableCell(row[field])
            row.append(value_cell)
            self.append(row)

class PVarTable(Table):
    def __init__(self, rows, **atts):
        Table.__init__(self, **atts)
        headrow = TableRow(bgcolor='MistyRose3')
        headrow.append(TableHeader('Trait'))
        headrow.append(TableHeader('Name'))
        headrow.append(TableHeader('Value'))
        self.set(headrow)
        for row in rows:
            tablerow = TableRow()
            tablerow.append(TableCell(row.trait))
            tablerow.append(TableCell(row.name))
            tablerow.append(TableCell(row.value))
            self.append(tablerow)

class TraitTable(Table):
    def __init__(self, rows, **atts):
        Table.__init__(self, **atts)
        headrow = TableRow()
        headrow.append(TableCell(Bold('Trait')))
        headrow.append(TableCell(Bold('Order')))
        self.set(headrow)
        for row in rows:
            tablerow = TableRow()
            tablerow.append(TableCell(row.trait))
            tablerow.append(TableCell(row.ord))
            self.append(tablerow)

# first draft completed

from xml.dom.minidom import Text

#Efrom useless.sqlgen.clause import Eq
from useless.xmlgen.base import BaseElement, TextElement
from useless.xmlgen.base import Anchor, Html, Body
#from useless.xmlgen.base import ListItem, UnorderedList
from useless.xmlgen.base import BR, HR, Bold, TR, TD, Paragraph
from useless.xmlgen.base import SimpleTitleElement

#from useless.db.midlevel import StatementCursor
#from paella.db.trait import Trait
#from paella.db.profile import Profile
#from paella.db.family import Family
#from paella.db.machine import MachineHandler
#from paella.db.machine.mtype import MachineTypeHandler

def color_header(table, color='cornsilk3'):
    table.header.firstChild.setAttribute('bgcolor', color)
    
class RecordElement(BaseElement):
    def __init__(self, fields, idcol, action, record, **atts):
        BaseElement.__init__(self, 'table', **atts)
        self.record = record
        refdata = None
        if hasattr(record, '_refdata'):
            refdata = record._refdata
        for field in fields:
            row = BaseElement('tr')
            key = TD(bgcolor='DarkSeaGreen')
            key.appendChild(Bold(field))
            row.appendChild(key)
            val = TD()
            if refdata is not None and field in refdata.cols:
                ridcol = refdata.cols[field]
                refrec =  refdata.data[field][record[ridcol]]
                node = refdata.object[field](refrec)
                if action:
                    url = '.'.join(map(str, [action, field, record[idcol]]))
                    val.appendChild(Anchor(url, node))
                else:
                    val.appendChild(node)
            elif action:
                url = '.'.join(map(str, [action, field, record[idcol]]))
                val.appendChild(Anchor(url, record[field]))
            else:
                node = Text()
                node.data = record[field]
                val.appendChild(node)
            row.appendChild(val)
            self.val = val
            self.key = key
            self.appendChild(row)

class BaseDocument(BaseElement):
    def __init__(self, app, **atts):
        BaseElement.__init__(self, 'html', **atts)
        self.app = app
        self.conn = app.conn
        self.body = Body()
        self.appendChild(self.body)

    def clear_body(self):
        while self.body.hasChildNodes():
            del self.body.childNodes[0]

class TxtTD(TextElement):
    def __init__(self, text):
        TextElement.__init__(self, 'td', text)
        
class TraitEnvTable(RecordElement):
    def __init__(self, trait, env, **atts):
        fields = env.keys()
        fields.sort()
        RecordElement.__init__(self, fields, 'trait', None, env, **atts)
        
class SectionTitle(SimpleTitleElement):
    def __init__(self, text, **atts):
        atts['width'] = '75%'
        atts['bgcolor'] = 'IndianRed'
        SimpleTitleElement.__init__(self, text, **atts)

class BaseFieldTable(BaseElement):
    def __init__(self, fields, row, **atts):
        BaseElement.__init__(self, 'table', **atts)
        for field in fields:
            trow = TR()
            p = TxtTD(field)
            trow.appendChild(p)
            a = TxtTD(row[field])
            trow.appendChild(a)
            self.appendChild(trow)
        
class PVarTable(BaseElement):
    def __init__(self, rows, **atts):
        BaseElement.__init__(self, 'table', **atts)
        hrow = TR(bgcolor='MistyRose3')
        hrow.appendChild(TxtTD('Trait'))
        hrow.appendChild(TxtTD('Name'))
        hrow.appendChild(TxtTD('Value'))
        self.appendChild(hrow)
        for row in rows:
            trow = TR()
            trow.appendChild(TxtTD(row.trait))
            trow.appendChild(TxtTD(row.name))
            trow.appendChild(TxtTD(row.value))
            self.appendChild(trow)
            
class TraitTable(BaseElement):
    def __init__(self, rows, **atts):
        BaseElement.__init__(self, 'table', **atts)
        hrow = TR()
        hrow.appendChild(TxtTD(Bold('Trait')))
        hrow.appendChild(TxtTD(Bold('Order')))
        self.appendChild(hrow)
        for row in rows:
            trow = TR()
            trow.appendChild(TxtTD(row.trait))
            trow.appendChild(TxtTD(row.ord))
            self.appendChild(trow)


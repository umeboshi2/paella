#from xml.dom.minidom import Text

from useless.sqlgen.clause import Eq
from useless.xmlgen.base import BaseElement, TextElement
from useless.xmlgen.base import Anchor, Html, Body
from useless.xmlgen.base import ListItem, UnorderedList
from useless.xmlgen.base import BR, HR, Bold, TR, TD, Paragraph
from useless.xmlgen.base import SimpleTitleElement

from useless.db.midlevel import StatementCursor
#from paella.db.trait import Trait
#from paella.db.profile import Profile
#from paella.db.family import Family
from paella.db.machine import MachineHandler
from paella.db.machine.mtype import MachineTypeHandler

from base import color_header
from base import BaseDocument
from base import TxtTD


class _MachineBaseDocument(BaseDocument):
    def __init__(self, app, **atts):
        BaseDocument.__init__(self, app, **atts)
        self.cursor = StatementCursor(self.conn)
    
    def _add_table_row(self, table, fields, row):
        trow = TR()
        for field in fields:
            trow.appendChild(TxtTD(row[field]))
        table.appendChild(trow)

    def _add_table_header(self, table, fields, **atts):
        th = BaseElement('th', **atts)
        trow = TR()
        th.appendChild(trow)
        for field in fields:
            trow.appendChild(TxtTD(Bold(field)))
        table.appendChild(th)
        table.header = th

    def _make_table(self, fields, rows, **atts):
        table = BaseElement('table', **atts)
        self._add_table_header(table, fields)
        for row in rows:
            self._add_table_row(table, fields, row)
        return table

    def _make_footer_anchors(self, name, value):
        newanchor = Anchor('new.%s.foo' % name, 'new')
        editanchor = Anchor('edit.%s.%s' % (name, value), 'edit')
        deleteanchor = Anchor('delete.%s.%s' % (name, value), 'delete')
        self.body.appendChild(HR())
        self.body.appendChild(editanchor)
        self.body.appendChild(BR())
        self.body.appendChild(deleteanchor)
        self.body.appendChild(BR())
        self.body.appendChild(newanchor)
    
class MachineDoc(BaseDocument):
    def __init__(self, app, **atts):
        BaseDocument.__init__(self, app, **atts)
        self.machine = MachineHandler(self.conn)

    def set_machine(self, machine):
        self.machine.set_machine(machine)
        self.clear_body()
        title = SimpleTitleElement('Machine:  %s' % machine, bgcolor='IndianRed',
                                   width='100%')
        self.body.appendChild(title)
        mtable = BaseElement('table')
        for k,v in self.machine.current.items():
            trow = TR()
            trow.appendChild(TxtTD(Bold(k)))
            trow.appendChild(TxtTD(v))
            mtable.appendChild(trow)
        self.body.appendChild(mtable)
        newanchor = Anchor('new.machine.foo', 'new')
        editanchor = Anchor('edit.machine.%s' % machine, 'edit')
        self.body.appendChild(HR())
        self.body.appendChild(editanchor)
        self.body.appendChild(BR())
        self.body.appendChild(newanchor)
        
    def set_clause(self, clause):
        print 'clause---->', clause, type(clause)
        #self.machine.cursor.clause = clause
        self.clear_body()
        title = SimpleTitleElement('Machines', bgcolor='IndianRed', width='100%')
        self.body.appendChild(title)
        for row in self.machine.cursor.select(clause=clause):
            self.body.appendChild(MachineFieldTable(row, bgcolor='MistyRose3'))
            self.body.appendChild(HR())

class MachineTypeDoc(_MachineBaseDocument):
    def __init__(self, app, **atts):
        _MachineBaseDocument.__init__(self, app, **atts)
        self.mtype = MachineTypeHandler(self.conn)
        self.body.setAttribute('bgcolor', 'Salmon')

    def set_machine_type(self, machine_type):
        clause = Eq('machine_type', machine_type)
        self.clear_body()
        self.mtype.set_machine_type(machine_type)
        title = SimpleTitleElement('MachineType:  %s' % machine_type,
                                   bgcolor='IndianRed', width='100%')
        self.body.appendChild(title)

        rows = self.cursor.select(table='machine_disks', clause=clause)
        self._setup_section('Disks', ['diskname', 'device'], rows)
        modrows =  self.cursor.select(table='machine_modules', clause=clause,
                                      order=['ord'])
        self._setup_section('Modules', ['module', 'ord'], modrows)
        famrows = self.cursor.select(table='machine_type_family', clause=clause,
                                     order='family')
        self._setup_section('Families', ['family'], famrows)
        scripts = self.cursor.select(table='machine_type_scripts', clause=clause,
                                     order='script')
        self._setup_section('Scripts', ['script'], scripts)
        vars_ = self.cursor.select(table='machine_type_variables', clause=clause,
                                   order=['trait', 'name'])
        self._setup_section('Variables', ['trait', 'name', 'value'], vars_)
        self._make_footer_anchors('machine_type', machine_type)

    def _setup_section(self, name, fields, rows):
        title = SimpleTitleElement(name)
        title.set_font(color='DarkViolet')
        td = TD()
        anchor = Anchor('new.%s.mtype' % name, 'new')
        td.appendChild(anchor)
        title.row.appendChild(td)
        self.body.appendChild(title)
        if len(rows):
            table = self._make_table(name, fields, rows, border=1, cellspacing=1)
            color_header(table, 'MediumOrchid2')
            self.body.appendChild(table)
            
    def _make_table(self, context, fields, rows, **atts):
        table = BaseElement('table', bgcolor='MediumOrchid3', **atts)
        table.context = context
        self._add_table_header(table, fields + ['command'])
        for row in rows:
            self._add_table_row(table, fields, row)
        return table

    def _add_table_row(self, table, fields, row):
        trow = TR()
        for field in fields:
            val = row[field]
            trow.appendChild(TxtTD(val))
        durl = 'delete.%s.%s' % (table.context, row[fields[0]])
        eurl = 'edit.%s.%s' % (table.context, row[fields[0]])
        delanchor = Anchor(durl, 'delete')
        editanchor = Anchor(eurl, 'edit')
        td = TD()
        td.appendChild(editanchor)
        td.appendChild(BR())
        td.appendChild(delanchor)
        trow.appendChild(td)
        #trow.appendChild(TxtTD(delanchor))
        table.appendChild(trow)

class FilesystemDoc(_MachineBaseDocument):
    def set_filesystem(self, filesystem):
        clause = Eq('filesystem', filesystem)
        self.clear_body()
        title = SimpleTitleElement('Filesystem:  %s' % filesystem,
                                   bgcolor='IndianRed', width='100%')
        self.body.appendChild(title)
        self.body.appendChild(TextElement('h2', 'Filesystem Mounts'))
        rows = self.cursor.select(table='filesystem_mounts', clause=clause,
                                  order=['ord'])
        fields = ['mnt_name', 'partition', 'ord']
        mounttable = self._make_table(fields, rows, bgcolor='DarkSeaGreen')
        self.body.appendChild(mounttable)
        self._make_footer_anchors('filesystem', filesystem)

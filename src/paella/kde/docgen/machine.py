from forgetHTML import Table, TableRow, TableCell
from forgetHTML import TableHeader
from forgetHTML import Anchor, Ruler, Break
from forgetHTML import Header

from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq

from paella.db.machine import MachineHandler
from paella.db.machine.mtype import MachineTypeHandler

from base import color_header
from base import BaseDocument
from base import Bold
from base import SectionTitle
from base import BaseFieldTable

class _MachineBaseDocument(BaseDocument):
    def __init__(self, app, **atts):
        BaseDocument.__init__(self, app, **atts)
        self.cursor = StatementCursor(self.conn)
    
    def _add_table_row(self, table, fields, row):
        tablerow = TableRow()
        for field in fields:
            tablerow.append(TableCell(row[field]))
        table.append(tablerow)

    # this has been changed from the xmlgen version
    # the th elements are cells
    #we don't append th to tr here
    def _add_table_header(self, table, fields, **atts):
        if atts:
            print 'Warning, use of atts here is questionable', atts
            print 'in _MachineBaseDocument._add_table_header'
        tablerow = TableRow(**atts)
        table.append(tablerow)
        for field in fields:
            tablerow.append(TableHeader(Bold(field)))
        # we should check if we need the header attribute here
        table.header = tablerow

    def _make_table(self, fields, rows, **atts):
        table = Table(**atts)
        self._add_table_header(table, fields)
        for row in rows:
            self._add_table_row(table, fields, row)
        return table
    
    def _make_footer_anchors(self, name, value):
        newanchor = Anchor('new', href='new.%s.foo' % name)
        editanchor = Anchor('edit', href='edit.%s.%s' % (name, value))
        deleteanchor = Anchor('delete', href='delete.%s.%s' % (name, value))
        self.body.append(Ruler())
        self.body.append(editanchor)
        self.body.append(Break())
        self.body.append(deleteanchor)
        self.body.append(Break())
        self.body.append(newanchor)
    
class MachineDoc(BaseDocument):
    def __init__(self, app, **atts):
        BaseDocument.__init__(self, app, **atts)
        self.machine = MachineHandler(self.conn)

    def set_machine(self, machine):
        self.machine.set_machine(machine)
        self.clear_body()
        title = SectionTitle('Machine:  %s' % machine)
        title['bgcolor'] = 'IndianRed'
        title['width'] = '100%'
        self.body.append(title)
        mtable = Table()
        for k,v in self.machine.current.items():
            tablerow = TableRow()
            tablerow.append(TableCell(Bold(k)))
            tablerow.append(TableCell(v))
            mtable.append(tablerow)
        self.body.append(mtable)
        newanchor = Anchor('new', href='new.machine.foo')
        editanchor = Anchor('edit', href='edit.machine.%s' % machine)
        self.body.append(Ruler())
        self.body.append(editanchor)
        self.body.append(Break())
        self.body.append(newanchor)
        
    def set_clause(self, clause):
        print 'clause---->', clause, type(clause)
        self.clear_body()
        title = SectionTitle('Machines')
        title['bgcolor'] = 'IndianRed'
        title['width'] = '100%'
        self.body.append(title)
        for row in self.machine.cursor.select(clause=clause):
            self.body.append(MachineFieldTable(row, bgcolor='MistyRose3'))
            self.body.append(Ruler())

class MachineTypeDoc(_MachineBaseDocument):
    def __init__(self, app, **atts):
        _MachineBaseDocument.__init__(self, app, **atts)
        self.mtype = MachineTypeHandler(self.conn)
        self.body['bgcolor'] = 'Salmon'

    def set_machine_type(self, machine_type):
        clause = Eq('machine_type', machine_type)
        self.clear_body()
        self.mtype.set_machine_type(machine_type)
        title = SectionTitle('Machine Type:  %s' % machine_type)
        title['bgcolor'] = 'IndianRed'
        title['width'] = '100%'
        self.body.append(title)

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
        title = SectionTitle(name)
        title.set_font(color='DarkViolet')
        anchor = Anchor('new', href='new.%s.mtype' % name)
        title.row.append(TableCell(anchor))
        self.body.append(title)
        if len(rows):
            table = self._make_table(name, fields, rows, border=1, cellspacing=1)
            color_header(table, 'MediumOrchid2')
            self.body.append(table)
            
    def _make_table(self, context, fields, rows, **atts):
        table = Table(bgcolor='MediumOrchid3', **atts)
        table.context = context
        self._add_table_header(table, fields + ['command'])
        for row in rows:
            self._add_table_row(table, fields, row)
        return table

    def _add_table_row(self, table, fields, row):
        tablerow = TableRow()
        for field in fields:
            tablerow.append(TableCell(row[field]))
        durl = 'delete.%s.%s' % (table.context, row[fields[0]])
        eurl = 'edit.%s.%s' % (table.context, row[fields[0]])
        delanchor = Anchor('delete', href=durl)
        editanchor = Anchor('edit', href=eurl)
        cell = TableCell(editanchor)
        cell.append(Break())
        cell.append(delanchor)
        tablerow.append(cell)
        table.append(tablerow)

class FilesystemDoc(_MachineBaseDocument):
    def set_filesystem(self, filesystem):
        clause = Eq('filesystem', filesystem)
        self.clear_body()
        title = SectionTitle('Filesystem:  %s' % filesystem)
        title['bgcolor'] = 'IndianRed'
        title['width'] = '100%'
        self.body.append(title)
        self.body.append(Header('Filesystem Mounts', level=2))
        rows = self.cursor.select(table='filesystem_mounts', clause=clause,
                                  order=['ord'])
        fields = ['mnt_name', 'partition', 'ord']
        mounttable = self._make_table(fields, rows, bgcolor='DarkSeaGreen')
        self.body.append(mounttable)
        self._make_footer_anchors('filesystem', filesystem)


class MachineFieldTable(BaseFieldTable):
    def __init__(self, row, **atts):
        fields = ['machine', 'machine_type', 'kernel', 'profile', 'filesystem']
        BaseFieldTable.__init__(self, fields, row, **atts)


# first draft completed

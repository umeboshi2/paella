from useless.base.forgethtml import Table, TableRow, TableCell
from useless.base.forgethtml import TableHeader
from useless.base.forgethtml import Anchor, Ruler, Break
from useless.base.forgethtml import Header
from useless.base.forgethtml import Pre, Paragraph

from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq

from paella.db.machine import MachineHandler
from paella.db.machine.base import DiskConfigHandler
from paella.db.machine.relations import AttributeUnsetInAncestryError

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
            tablerow.append(TableCell(str(row[field])))
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

class DiskConfigDoc(BaseDocument):
    def __init__(self, app, **atts):
        BaseDocument.__init__(self, app, **atts)
        self.diskconfig = DiskConfigHandler(self.conn)
        

    def set_diskconfig(self, diskconfig):
        row = self.diskconfig.get(diskconfig)
        self.clear_body()
        title = SectionTitle('DiskConfig: %s' % row.name)
        self.body.append(title)
        content = row.content
        if content is None:
            content = ''
        pre = Pre(content)
        self.body.append(pre)
        self.body.append(Ruler())
        editanchor = Anchor('edit', href='edit.diskconfig.%s' % row.name)
        self.body.append(editanchor)
        self.body.append(Ruler())
        deleteanchor = Anchor('delete', href='delete.diskconfig.%s' % row.name)
        self.body.append(deleteanchor)
        
    
        
class MachineDoc(_MachineBaseDocument):
    def __init__(self, app, **atts):
        _MachineBaseDocument.__init__(self, app, **atts)
        self.machine = MachineHandler(self.conn)
        self._bgcolor_body = 'Salmon'
        self._bgcolor_section = 'IndianRed'
        self._other_section_font_color = 'DarkViolet'
        self._bgcolor_thead = 'MediumOrchid2'
        self._bgcolor_table = 'MediumOrchid3'
        self.body['bgcolor'] = self._bgcolor_body

    def set_machine(self, machine):
        self.machine.set_machine(machine)
        self.clear_body()
        title = SectionTitle('Machine:  %s' % machine)
        title['bgcolor'] = self._bgcolor_section
        title['width'] = '100%'
        self.body.append(title)
        #mtable = Table()
        self._setup_parent_table()
        self._setup_main_attributes()
        self._setup_relation_sections()
        self._make_footer_anchors('machine', machine)
        return

    def _setup_parent_table(self):
        machine = self.machine.current_machine
        parent_table = Table(bgcolor=self._bgcolor_table, border=1)
        parent = self.machine.parent
        if parent is None:
            parent = '(No Parent Set)'
        headrow = TableRow(bgcolor=self._bgcolor_thead)
        for col in ['parent', 'command']:
            headrow.append(TableHeader(col))
        parent_table.append(headrow)
        mainrow = TableRow()
        parent_cell = TableCell(parent)
        mainrow.append(parent_cell)
        select_anchor = Anchor('select', href='select.parent.%s' % machine)
        delete_anchor = Anchor('delete', href='delete.parent.%s' % machine)
        command_cell = TableCell()
        command_cell.append(select_anchor)
        if self.machine.parent is not None:
            #command_cell.append(Break())
            command_cell.append('|=====|')
            command_cell.append(delete_anchor)
        mainrow.append(command_cell)
        parent_table.append(mainrow)
        self.body.append(parent_table)
        
    def _setup_main_attributes(self):
        machine = self.machine.current_machine
        attribute_table = Table(bgcolor=self._bgcolor_table, border=1)
        headrow = TableRow(bgcolor=self._bgcolor_thead)
        for col in ['Attribute', 'Value', 'Inherited From', 'Command']:
            headrow.append(TableHeader(col))
        attribute_table.append(headrow)
        for attribute in ['kernel', 'profile', 'diskconfig']:
            errormsg = ''
            try:
                value, inherited_from = self.machine.get_attribute(attribute)
            except AttributeUnsetInAncestryError:
                errormsg = "WARNING: not set anywhere"
                value, inherited_from = errormsg, errormsg
            tablerow = TableRow()
            href = 'select.attribute||%s.%s' % (attribute, machine)
            anchor = Anchor(attribute, href=href)
            cell = TableCell(Bold(anchor, ':'))
            tablerow.append(cell)
            cell = TableCell(value)
            tablerow.append(value)
            cell = TableCell()
            if inherited_from is not None:
                if errormsg:
                    anchor = Bold(errormsg)
                else:
                    anchor = Anchor(inherited_from, href='select.machine.%s' % inherited_from)
                cell.append(anchor)
            else:
                cell.append('(set here)')
            tablerow.append(cell)
            cell = TableCell()
            anchor = Anchor('clear', href='delete.attribute||%s.%s' % (attribute, machine))
            if inherited_from is None:
                cell.set(anchor)
            tablerow.append(cell)
            attribute_table.append(tablerow)
        self.body.append(attribute_table)
        
    def _setup_relation_sections(self):
        machine = self.machine.current_machine
        clause = Eq('machine', machine)
        cursor = self.conn.cursor(statement=True)
        famrows = cursor.select(table='machine_family', clause=clause,
                                     order='family')
        self._setup_section('Families', ['family'], famrows)
        self._setup_script_section()
        vars_ = cursor.select(table='machine_variables', clause=clause,
                                   order=['name'])
        #self._setup_section('Variables', ['trait', 'name', 'value'], vars_)
        self._setup_variables_section(vars_)
        
    def _setup_script_section(self):
        machine = self.machine.current_machine
        relation = self.machine.relation
        scriptnames = relation.scripts.scriptnames
        scripts = []
        for scriptname in scriptnames:
            result = relation.get_script(scriptname, show_inheritance=True)
            if result is not None:
                # if result is not None, then result is a tuple
                # that is (fileobj, parent)
                # but we need scriptname, parent
                scripts.append((scriptname, result[1]))
        # make the section
        title = SectionTitle('Scripts', bgcolor=self._bgcolor_section)
        title.set_font(color=self._other_section_font_color)
        anchor = Anchor('new', href='new.%s.machine' % 'Scripts')
        title.row.append(TableCell(anchor))
        self.body.append(title)
        if len(scripts):
            table = self._make_script_table(scripts, border=1, cellspacing=1)
            color_header(table, self._bgcolor_thead)
            self.body.append(table)

    def _make_script_table(self, scripts, **atts):
        table = Table(bgcolor=self._bgcolor_table, **atts)
        table.context = 'Scripts'
        fields= ['script', 'inherited', 'command']
        self._add_table_header(table, fields)
        for scriptname, parent in scripts:
            self._add_script_table_row(table, scriptname, parent)
        return table
    
    def _add_script_table_row(self, table, scriptname, parent):
        tablerow = TableRow()
        # scriptname cell
        scriptname_cell = TableCell(scriptname)
        
        # command cell (we use
        # an empty cell as default)
        command_cell = TableCell()

        # parent cell
        if parent is None:
            parent = '(defined here)'
            # if script is defined here, instead of inherited
            # we make the command anchors.
            durl = 'delete.%s.%s' % (table.context, scriptname)
            eurl = 'edit.%s.%s' % (table.context, scriptname)
            delanchor = Anchor('delete', href=durl)
            editanchor = Anchor('edit', href=eurl)
            command_cell = TableCell(editanchor)
            command_cell.append(Break())
            command_cell.append(delanchor)
        parent_cell = TableCell(parent)

        # append the cells to the rows
        tablerow.append(scriptname_cell)
        tablerow.append(parent_cell)
        tablerow.append(command_cell)
        table.append(tablerow)

    def _setup_variables_section(self, rows):
        section = 'Variables'
        machine = self.machine.current_machine
        relation = self.machine.relation
        # make the section
        title = SectionTitle(section, bgcolor=self._bgcolor_section)
        title.set_font(color=self._other_section_font_color)
        anchor = Anchor('new', href='new.%s.machine' % section)
        title.row.append(TableCell(anchor))
        self.body.append(title)
        if len(rows):
            table = self._make_variables_table(rows, border=1, cellspacing=1)
            color_header(table, self._bgcolor_thead)
            self.body.append(table)

    def _make_variables_table(self, rows, **atts):
        table = Table(bgcolor=self._bgcolor_table, **atts)
        table.context = 'Variables'
        fields = ['trait', 'name', 'value']
        self._add_table_header(table, fields + ['command'])
        for row in rows:
            self._add_variables_table_row(table, fields, row)
        return table

    def _add_variables_table_row(self, table, fields, row):
        tablerow = TableRow()
        for field in fields:
            tablerow.append(TableCell(str(row[field])))
        ident = '%s||%s' % (row['trait'], row['name'])
        durl = 'delete.%s.%s' % (table.context, ident)
        eurl = 'edit.%s.%s' % (table.context, ident)
        delanchor = Anchor('delete', href=durl)
        editanchor = Anchor('edit', href=eurl)
        cell = TableCell(editanchor)
        cell.append(Break())
        cell.append(delanchor)
        tablerow.append(cell)
        table.append(tablerow)

    def _setup_section(self, name, fields, rows):
        title = SectionTitle(name, bgcolor=self._bgcolor_section)
        title.set_font(color=self._other_section_font_color)
        anchor = Anchor('new', href='new.%s.machine' % name)
        title.row.append(TableCell(anchor))
        self.body.append(title)
        if len(rows):
            table = self._make_table(name, fields, rows, border=1, cellspacing=1)
            color_header(table, self._bgcolor_thead)
            self.body.append(table)
            
    def _make_table(self, context, fields, rows, **atts):
        table = Table(bgcolor=self._bgcolor_table, **atts)
        table.context = context
        self._add_table_header(table, fields + ['command'])
        for row in rows:
            self._add_table_row(table, fields, row)
        return table

    def _add_table_row(self, table, fields, row):
        tablerow = TableRow()
        for field in fields:
            tablerow.append(TableCell(str(row[field])))
        durl = 'delete.%s.%s' % (table.context, row[fields[0]])
        eurl = 'edit.%s.%s' % (table.context, row[fields[0]])
        delanchor = Anchor('delete', href=durl)
        editanchor = Anchor('edit', href=eurl)
        cell = TableCell(editanchor)
        cell.append(Break())
        cell.append(delanchor)
        tablerow.append(cell)
        table.append(tablerow)

    def _make_footer_anchors(self, name, value):
        newanchor = Anchor('new', href='new.%s.foo' % name)
        deleteanchor = Anchor('delete', href='delete.%s.%s' % (name, value))
        self.body.append(Ruler())
        self.body.append(Break())
        self.body.append(deleteanchor)
        self.body.append(Break())
        self.body.append(newanchor)



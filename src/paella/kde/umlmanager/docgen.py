from forgetHTML import Table, TableRow, TableCell
from forgetHTML import TableHeader
from forgetHTML import Anchor, Ruler, Break
from forgetHTML import Header

from forgetHTML import SimpleDocument

class OptionsTable(Table):
    def set_options(self, items):
        hrow = TableRow()
        self.set(hrow)
        hrow.append(TableHeader('Option'))
        hrow.append(TableHeader('Value'))
        for k, v in items:
            row = TableRow()
            self.append(row)
            row.append(TableCell(k))
            row.append(TableCell(v))

class UmlMachineDoc(SimpleDocument):
    def __init__(self, app):
        SimpleDocument.__init__(self, title='Uml Machines')
        self.app = app
        self.umlcfg = self.app.umlcfg
        self.opttable = OptionsTable()
        
    def set_machine(self, machine):
        msg = 'Uml Machine is %s\n' % machine
        self.body.set(msg)
        
        self.body.append(self.opttable)
        items = self.umlcfg.nondefault_items(machine)
        self.opttable.set_options(items)
        self.umlcfg.change(machine)
        umlopts = self.umlcfg.get_umlopts()
        umlopttable = OptionsTable()
        umlopttable.set_options(umlopts.items())
        self.body.append(umlopttable)

import os
from os.path import join

from useless.gtk.simple import MyCombo
from useless.gtk import dialogs
from useless.gtk.middle import ListNoteBook, ScrollCList
from useless.gtk.middle import TwinScrollCList

from useless.gtk.windows import CommandBoxWindow
from useless.gtk.helpers import make_menu, right_click_menu, HasDialogs

from gtk import HBox, VBox, Button

from useless.base import Error
from useless.base.util import makepaths, strfile
from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq

from paella.base.objects import Differ

#these need to be encapsulated in Trait object
from paella.db.trait.relations import TraitTemplate, TraitScript

from paella.db.family import Family, FamilyVariablesConfig

class SuiteBar(HBox):
    def __init__(self, suites, name='SuiteBar'):
        HBox.__init__(self)
        self.set_name(name)
        self.lcombo = MyCombo(suites)
        self.lcombo.set(suites[0])
        self.rcombo = MyCombo(suites)
        self.rcombo.set(suites[0])
        self.ubutton = Button('update')
        self.dbutton = Button('diff')
        self.pack_start(self.lcombo, 0, 0, 0)
        self.pack_end(self.rcombo, 0, 0, 0)
        self.add(self.ubutton)
        self.add(self.dbutton)
        self.ubutton.show()
        self.dbutton.show()
        self.show()

class TraitBar(HBox):
    def __init__(self, name='TraitBar'):
        HBox.__init__(self)
        self.set_name(name)
        self.lcombo = MyCombo()
        self.rcombo = MyCombo()
        self.lcombo.set('')
        self.rcombo.set('')
        self.cbutton = Button('clear')
        self.cbutton.show()
        self.pack_start(self.lcombo, 0, 0, 0)
        self.pack_end(self.rcombo, 0, 0, 0)
        self.add(self.cbutton)
        self.show()

class UDBar(HBox):
    def __init__(self, name='UDBar'):
        HBox.__init__(self)
        self.set_name(name)
        self.ubutton = Button('update')
        self.dbutton = Button('diff')
        self.pack_start(self.ubutton, 0, 0, 0)
        self.pack_end(self.dbutton, 0, 0, 0)
        self.ubutton.show()
        self.dbutton.show()
        self.show()
        
class BaseDiffer(VBox):
    def __init__(self, conn, name='BaseDiffer'):
        VBox.__init__(self)
        self.set_name(name)
        self.conn = conn
        self.view = TwinScrollCList(name=name)
        self.cursor = StatementCursor(self.conn)
        suites = [r.suite for r in self.cursor.select(table='suites', order='suite')]
        self.suite_bar = SuiteBar(suites, name=name)
        self.trait_bar = TraitBar(name=name)
        self.pack_end(self.suite_bar, 0, 0, 0)
        self.pack_end(self.trait_bar, 0, 0, 0)
        self.add(self.view)
        self.suite_bar.show()
        self.show()

    def update_lists(self, fields, suffix):
        self.lsuite = self.suite_bar.lcombo.get()
        self.rsuite = self.suite_bar.rcombo.get()
        self.cursor.set_fields(fields)
        clause = None
        ltrait = self.trait_bar.lcombo.get()
        if ltrait:
            clause = Eq('trait', ltrait)
        table = '%s_%s' % (self.lsuite, suffix)
        rows = self.cursor.select(table=table, clause=clause, order=fields)
        self.view.lbox.set_rows(rows)
        clause = None
        rtrait = self.trait_bar.rcombo.get()
        if rtrait:
            clause = Eq('trait', rtrait)
        table = '%s_%s' % (self.rsuite, suffix)
        rows = self.cursor.select(table=table, clause=clause, order=fields)
        self.view.rbox.set_rows(rows)
        fields = ['trait']
        self.cursor.set_fields(fields)
        rows = self.cursor.select(table='%s_traits' % self.lsuite, order=fields)
        ltraits = [r.trait for r in rows]
        rows = self.cursor.select(table='%s_traits' % self.rsuite, order=fields)
        rtraits = [r.trait for r in rows]
        self.trait_bar.lcombo.fill(ltraits)
        self.trait_bar.rcombo.fill(rtraits)
        if ltrait and ltrait in ltraits:
            self.trait_bar.lcombo.set(ltrait)
        else:
            self.trait_bar.lcombo.set('')
        if rtrait and rtrait in rtraits:
            self.trait_bar.rcombo.set(rtrait)
        else:
            self.trait_bar.rcombo.set('')
        
class TemplateDiffer(BaseDiffer):
    def __init__(self, conn, name='TemplateDiffer'):
        BaseDiffer.__init__(self, conn, name=name)
        self.suite_bar.ubutton.connect('clicked', self.update_pressed)
        self.suite_bar.dbutton.connect('clicked', self.diff_selection)

    def update_pressed(self, button):
        fields = ['trait', 'template', 'package', 'templatefile']
        self.update_lists(fields, 'templates')
        
    def diff_selection(self, *args):
        lrow = self.view.lbox.get_selected_data()[0]
        rrow = self.view.rbox.get_selected_data()[0]
        ltemplate = TraitTemplate(self.conn, self.lsuite)
        rtemplate = TraitTemplate(self.conn, self.rsuite)
        ltemplate.set_trait(lrow.trait)
        rtemplate.set_trait(rrow.trait)
        ldata = ltemplate.templatedata(lrow.package, lrow.template)
        rdata = rtemplate.templatedata(rrow.package, rrow.template)
        differ = Differ(ldata, rdata)
        differ.diff()
        if differ.isdifferent('left', ldata):
            newdata = differ.get_data('left')
            ltemplate.update_templatedata(lrow.package, lrow.template, newdata)
        if differ.isdifferent('right', rdata):
            newdata = differ.get_data('right')
            rtemplate.update_templatedata(rrow.package, rrow.template, newdata)
            
        

class ScriptDiffer(BaseDiffer):
    def __init__(self, conn, name='ScriptDiffer'):
        BaseDiffer.__init__(self, conn, name=name)
        self.suite_bar.ubutton.connect('clicked', self.update_pressed)
        self.suite_bar.dbutton.connect('clicked', self.diff_selection)

    def update_pressed(self, button):
        fields = ['trait', 'script', 'scriptfile']
        self.update_lists(fields, 'scripts')

    def diff_selection(self, *args):
        lrow = self.view.lbox.get_selected_data()[0]
        rrow = self.view.rbox.get_selected_data()[0]
        lscript = TraitScript(self.conn, self.lsuite)
        rscript = TraitScript(self.conn, self.rsuite)
        lscript.set_trait(lrow.trait)
        rscript.set_trait(rrow.trait)
        ldata = lscript.scriptdata(lrow.script)
        rdata = rscript.scriptdata(rrow.script)
        differ = Differ(ldata, rdata)
        differ.diff()
        if differ.isdifferent('left', ldata):
            newdata = differ.get_data('left')
            lscript.update_scriptdata(lrow.script, newdata)
        if differ.isdifferent('right', rdata):
            newdata = differ.get_data('right')
            rscript.update_scriptdata(rrow.script, newdata)

        
class FamilyDiffer(VBox):
    def __init__(self, conn, name='FamilyDiffer'):
        VBox.__init__(self)
        self.set_name(name)
        self.conn = conn
        self.view = TwinScrollCList(name=name)
        self.cursor = StatementCursor(self.conn)
        self.lfamily = Family(self.conn)
        self.rfamily = Family(self.conn)
        self.add(self.view)
        self.udbar = UDBar()
        self.pack_end(self.udbar, 0, 0, 0)
        self.show()
        self.udbar.ubutton.connect('clicked', self.update_pressed)
        self.udbar.dbutton.connect('clicked', self.diff_selection)

    def update_pressed(self, button):
        self.update_lists()

    def update_lists(self):
        rows = self.lfamily.family_rows()
        self.view.lbox.set_rows(rows)
        self.view.rbox.set_rows(rows)

    def diff_selection(self, *args):
        lrow = self.view.lbox.get_selected_data()[0]
        rrow = self.view.rbox.get_selected_data()[0]
        lfam, rfam = lrow.family, rrow.family
        lcfg = FamilyVariablesConfig(self.conn, lfam)
        rcfg = FamilyVariablesConfig(self.conn, rfam)
        lcfg.diff(rcfg)
        
        
class DifferWin(CommandBoxWindow, HasDialogs):
    def __init__(self, conn, type, name='DifferWin'):
        CommandBoxWindow.__init__(self, name=name)
        self.conn = conn
        self.set_title(name)
        if type == 'template':
            self.browser = TemplateDiffer(self.conn)
        elif type == 'family':
            self.browser = FamilyDiffer(self.conn)
        else:
            self.browser = ScriptDiffer(self.conn)
        self.vbox.add(self.browser)
        
if __name__ == '__main__':
    from paella.profile.base import PaellaConnection
    from gtk import mainloop, mainquit
    c = PaellaConnection()
    twin = DifferWin(c, 'template')
    twin.connect('destroy', mainquit)
    swin = DifferWin(c, 'script')
    swin.connect('destroy', mainquit)
    
    
    def dtable():
        cmd.execute('drop table themebase')
    def dtables():
        for t in cmd.tables():
            if t not in  ['footable']:
                cmd.execute('drop table %s' %t)
    #dtables()
    mainloop()
    

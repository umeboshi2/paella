import os
#from os.path import join
from operator import and_
from sets import Set

from useless.gtk.base import right_click_pressed, FlavoredTargets
from useless.gtk.base import rowpacker, set_receive_targets
from useless.gtk.simple import SimpleMenu, SimpleMenuBar
from useless.gtk import dialogs
from useless.gtk.middle import ListNoteBook, ScrollCList
from useless.gtk.windows import CommandBoxWindow
from useless.gtk.helpers import make_menu, right_click_menu, HasDialogs

from useless.base import debug, Error
from useless.sqlgen.clause import Eq
from paella.profile.family import Family, FamilyVariablesConfig

from traitgen import DragListWindow

def substring(field, substr):
    return 'substring(%s from 1 for %s)' %(field, len(substr))
def substring_clause(section):
    return "%s = '%s'" %(substring('section', section), section)

TARGETS = FlavoredTargets(40, ['family', 'variable'], ['flavor'])
print TARGETS

def doublepacker(key1, key2, rows):
    return '^&^'.join(['%s<=>%s' % (rows[key1], r[key2]) for r in rows])

def triplepacker(key1, key2, key3, rows):
    return '^&^'.join(['%s<=>%s<=>%s' % (r[key1], r[key2], r[key3]) for r in rows])

class FamiliesWindow(DragListWindow):
    def __init__(self, rows):
        packer = lambda x : rowpacker('family', x)
        DragListWindow.__init__(self, 'families', packer, rows,
                                TARGETS.get('family', 'flavor'))

class VariablesWindow(DragListWindow):
    def __init__(self, rows):
        packer = lambda x : triplepacker('trait', 'name', 'value', x)
        DragListWindow.__init__(self, 'variables', packer, rows,
                                TARGETS.get('variable', 'flavor'))
        
class FamilyBrowser(ListNoteBook):
    def __init__(self, conn):
        self.menu = make_menu(['delete'], self.modify_family)
        ListNoteBook.__init__(self)
        self.conn = conn
        self.family = Family(self.conn)
        self.var_menu = make_menu(['edit', 'nothing', 'nothing', 'drop'],
                              self.var_menu_selected)
        self.parent_menu = make_menu(['drop'], self.modify_parent)
        self.reset_rows()
        self.append_page(ScrollCList(rcmenu=self.var_menu), 'environment')
        self.append_page(ScrollCList(rcmenu=self.parent_menu), 'parents')
        self.set_size_request(400, 300)

    def modify_parent(self, menuitem, action):
        if action == 'drop':
            parents = self._get_listbox_col_('parents', 'family')
            self.trait.delete_parents(parents)
            self.__set_pages(self.current_family)

    def modify_family(self, menuitem, action):
        if action == 'delete':
            trait = self.listbox.get_selected_data()[0].family
            self.trait.delete_family(family)
            self.reset_rows()
            
    def reset_rows(self):
        self.set_rows(self.family.family_rows())
        self.set_row_select(self.family_selected)

    def __set_droptargets__(self, pages):
        set_receive_targets(pages['environment'].listbox,
                            self.drop_variable, TARGETS.get('variable', 'flavor'))
        set_receive_targets(pages['parents'].listbox,
                            self.drop_family, TARGETS.get('family', 'flavor'))

    def set_package(self, menu_item, action):
        packages = self._get_listbox_col_('packages', 'package')
        trait = self.current_family
        self.trait.set_action(action, packages)
        self.__set_pages(self.current_trait)

    def var_menu_selected(self, menu_item, action):
        if action == 'edit':
            config = FamilyVariablesConfig(self.conn, self.current_family)
            newconfig = config.edit()
            config.update(newconfig)
            self.select_family(self.current_family)
        elif action == 'drop':
            pages = dict(self.pages)
            listbox = pages['environment'].listbox
            rows = listbox.get_selected_data()
            data = dict(family=self.current_family)
            for row in rows:
                data['trait'] = row.trait
                data['name'] = row.name
                clause = reduce(and_, [Eq(k, v) for k,v in data.items()])
                self.family.env.cursor.delete(clause=clause)
    

    def pop_mymenu(self, widget, event, menu):
        if right_click_pressed(event):
            menu.popup(None, None, None, event.button, event.time)

    def family_selected(self, listbox, row, column, event):
        family = listbox.get_selected_data()[0].family
        self.select_family(family)
        
    def select_family(self, family):
        self.current_family = family
        self.family.set_family(family)
        self.__set_pages(self.current_family)

    def __set_pages(self, family):
        pages = dict(self.pages)
        pages['environment'].set_rows(self.family.environment_rows())
        pages['environment'].set_select_mode('multi')
        pages['parents'].set_rows(self.family.parents(), ['family'])
        pages['parents'].set_select_mode('multi')
        self.__set_droptargets__(pages)

    def drop_family(self, listbox, context, x, y, selection, targettype, time):
        families = Set(selection.data.split('^&^'))
        self.family.insert_parents(families)
        self.__set_pages(self.current_family)

    def drop_variable(self, listbox, context, x, y, selection, targettype, time):
        table = 'family_environment'
        trips = [x.split('<=>') for x in selection.data.split('^&^')]
        rows = [dict(trait=x[0], name=x[1], value=x[2]) for x in trips]
        print rows
        for r in trips:
            clause = Eq('family', self.current_family)
            clause &= Eq('trait', r[0]) & Eq('name', r[1]) 
            trows = self.family.cursor.select(table=table, clause=clause)
            print 'trows', trows
            if len(trows) == 0:
                data = dict(trait=r[0], name=r[1], value=r[2])
                data['family'] = self.current_family
                print 'data', data
                self.family.cursor.insert(table=table, data=data)        
        self.__set_pages(self.current_family)

    def _get_listbox_col_(self, page, field):
        pages = dict(self.pages)
        return [row[field] for row in pages[page].listbox.get_selected_data()]

    def make_families_window(self):
        rows = self.family.family_rows()
        FamiliesWindow(rows)

    def make_variables_window(self):
        rows = self.family.get_all_defaults()
        VariablesWindow(rows)
        
            
class FamilyWin(CommandBoxWindow, HasDialogs):
    def __init__(self, conn, name='FamilyWin'):
        if name is None:
            name = '.'.join([suite, 'traits'])
        CommandBoxWindow.__init__(self, name=name)
        self.conn = conn
        self.set_title(name)
        self.browser = FamilyBrowser(self.conn)
        self.__make_menus__()
        self.vbox.pack_start(self.menu_bar, 0, 0, 0)
        self.vbox.add(self.browser)
        self.dialogs = {}.fromkeys(['create'])


    def __make_menus__(self):
        self.menu_bar = SimpleMenuBar()
        self.main_menu = SimpleMenu()
        self.tbar.add_button('create', 'create family', self.ask_dialog)
        self.tbar.add_button('variables', 'show all variables', self.create_list_dialog)
        self.tbar.add_button('families', 'show all families', self.create_list_dialog)
        #self.main_menu.add('create', self.ask_dialog)
        #self.main_menu.add('packages', self.create_package_list)
        #self.main_menu.add('traits', self.create_package_list)
        #self.menu_bar.append(self.main_menu, 'main')
        
    def ask_dialog(self, button, data):
        if not self.dialogs[data]:
            if data == 'create':
                self.dialogs[data] = dialogs.Entry('create family', name='create')
                self.dialogs[data].set_ok(self.create_family)
            self.dialogs[data].set_cancel(self.destroy_dialog)

    def create_family(self, button):
        name = button.get_name()
        if name == 'create':
            family = self.dialogs[name].get()
            try:
                self.browser.family.create_family(family)
            except ExistsError:
                dialogs.Message('family %s already exists' % family)
            self.destroy_dialog(self.dialogs['create'])
            self.browser.reset_rows()

    def create_list_dialog(self, button, data):
        if data == 'variables':
            self.browser.make_variables_window()
        elif data == 'families':
            self.browser.make_families_window()

    def make_suite_menu(self):
        self.suite_menu = SimpleMenu()
        suites = self.cmd.as_dict('suites', 'suite')
        for suite in suites:
            self.suite_menu.add(suite, self.browser.change_suite)
        self.menu_bar.append(self.suite_menu, 'suite')
        self.suite = suite
        
if __name__ == '__main__':
    c = PaellaConnection()
    win = TraitGenWin(c, 'woody')
    win.connect('destroy', mainquit)
    
    
    def dtable():
        cmd.execute('drop table themebase')
    def dtables():
        for t in cmd.tables():
            if t not in  ['footable']:
                cmd.execute('drop table %s' %t)
    #dtables()
    mainloop()
    

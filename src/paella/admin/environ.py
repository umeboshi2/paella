from useless.base import Error, debug

from useless.base.util import ujoin
from useless.base.defaults import DELIMITERS

from useless.gtk.base import right_click_pressed
from useless.gtk.simple import SimpleMenu
from useless.gtk.middle import ListNoteBook, FieldEntryVbox
from useless.gtk.middle import RecordBox
from useless.gtk.windows import MenuWindow
from useless.gtk.helpers import populate_menu, make_menu
from useless.gtk import dialogs

from useless.db.midlevel import StatementCursor, Environment

from paella.db import PaellaConfig, PaellaConnection
from paella.db.base import get_suite
from paella.db.trait import Trait
from paella.db.trait.relations import TraitParent, TraitEnvironment

from gtk import TRUE, FALSE, mainquit, mainloop

config = PaellaConfig()
class _EnvironmentEditor(ListNoteBook):
    def __init__(self, conn, name='_EnvironmentEditor'):
        ListNoteBook.__init__(self, name=name)
        self.conn = conn
        self.main = StatementCursor(self.conn, name=name)
        self.append_page(RecordBox({}), 'Environment')
        self.menu = SimpleMenu()
        self.delimiters = DELIMITERS['out-arrows']
        self.dialogs = {}.fromkeys(['create', 'remove'])
        
    def box_pressed(self, widget, event=None):
        if right_click_pressed(event):
            self.menu.popup(None, None, None, event.button, event.time)
        
    def populate_menu(self, widget, mainmenu, itementry, tmenu):
        self.current_entry = itementry
        self._current_entry_widget_ = widget
        populate_menu(mainmenu, '_define_', ['_create_', '_remove_'], self.make_new_tag)
        for section, vars in self.sections.items():
            populate_menu(mainmenu, section, vars, self.make_tag)


    def make_new_tag(self, menuitem, name, pmenu):
        if name == '_create_':
            self.ask_new_entry()
        elif name == '_remove_':
            self.ask_remove_key()

    def ask_new_entry(self):
        if self.dialogs['create'] is None:
            data = dict(name='', value='')
            self.dialogs['create'] = dialogs.RecordEntry('enter a new variable',
                                                         data, 'create')
            self.dialogs['create'].set_cancel(self.destroy_dialog)
            self.dialogs['create'].set_ok(self.make_new_variable)

    def ask_remove_key(self):
        if self.dialogs['remove'] is None:
            self.dialogs['remove'] = dialogs.CList('remove which item', name='remove')
            d = self.dialogs['remove']
            d.set_rows(self.record.keys(), ['name'])
            self.dialogs['remove'].set_cancel(self.destroy_dialog)
            self.dialogs['remove'].set_ok(self.remove_item)

    def make_tag(self, menuitem, name, parent):
        trait = parent.get_name()
        print trait, name
        self.pages['Environment']
        self._current_entry_widget_.set_text('$' + trait + '_' + name)
            

class EnvironmentEditor(_EnvironmentEditor):
    def __init__(self, conn, suite, name='EnvironmentEditor'):
        self.menu = make_menu(['update', 'create'], self.env_command)
        _EnvironmentEditor.__init__(self, conn, name=name)
        self.suite = suite
        self.traitparent = TraitParent(self.conn, self.suite)
        self.current_trait = None
        self.reset_rows()
        w, h = map(int, config.get_list('env_editor_size', section='management_gui'))
        self.set_size_request(w, h)
        
    def reset_rows(self):
        rows = self.main.select(fields=['trait'], table=ujoin(self.suite, 'traits'))
        self.set_rows(rows)
        self.set_row_select(self.trait_selected)

    def trait_selected(self, listbox, row, column, event):
        trait = listbox.get_selected_data()[0].trait
        self.select_trait(trait)
        
    def select_trait(self, trait):
        self.current_trait = trait
        environ = TraitEnvironment(self.conn, self.suite, trait)
        self.environ = self.traitparent.get_environment([self.current_trait])
        self.sections = dict([(k, v.keys()) for k,v in self.environ])
        self.remove_page('Environment')
        self.record = RecordBox(environ, name=self.current_trait)
        self.append_page(self.record, 'Environment')
        self.pages['Environment'].connect('button_press_event', self.box_pressed)
        #self.menu.connect('populate', self.populate_menu, self.menu)
        self.record.connect_entries('populate-popup', self.populate_menu, self.menu)
        

    def make_new_variable(self, *args):
        d = self.dialogs['create']
        environ = TraitEnvironment(self.conn, self.suite, self.current_trait)
        environ.update(dict([(d['name'], d['value'])]))

    def remove_item(self, *args):
        d = self.dialogs['remove']
        name = d.get_selected_data()[0].name
        environ = TraitEnvironment(self.conn, self.suite, self.current_trait)
        del environ[name]
        dialogs.Message('%s deleted' %name)
        self.destroy_dialog(d)
        
    def update_environment(self):
        environ = TraitEnvironment(self.conn, self.suite, self.current_trait)
        environ.update(self.record)

    def env_command(self, menuitem, command):
        if command == 'update':
            dialogs.Message('updating %s' % self.current_trait)
            self.update_environment()
        elif command == 'create':
            self.ask_new_entry()
        else:
            dialogs.Message('ack')
            
class ProfileEnvironmentEditor(_EnvironmentEditor):
    def __init__(self, conn, profile, name='ProfileEnvironmentEditor'):
        self.menu = make_menu(['update', 'create'], self.env_command)
        _EnvironmentEditor.__init__(self, conn, name=name)
        self.profile = profile
        self.suite = get_suite(self.conn, self.profile)
        self.main.set_table('profile_variables')
        
    def reset_rows(self):
        pass
        
class EnvironmentEditorWin(MenuWindow):
    def __init__(self, conn, suite, name='EnvironmentEditorWin'):
        MenuWindow.__init__(self)
        self.conn = conn
        self.editor = EnvironmentEditor(self.conn, suite)
        self.vbox.add(self.editor)
        self.add_menu(['update', 'revert'], 'sync', self.db_commands)

    def db_commands(self, menuitem, name):
        if name == 'update':
            self.editor.update_environment()
            self.editor.select_trait(self.editor.current_trait)
        elif name == 'revert':
            self.editor.select_trait(self.editor.current_trait)
        

                
if __name__ == '__main__':
    conn = PaellaConnection()
    win = MenuWindow()
    ee = EnvironmentEditor(conn, 'sid')
    win.vbox.add(ee)
    win.show()
    win.connect('destroy', mainquit)
    mainloop()
    



#if __name__ == '__main__':

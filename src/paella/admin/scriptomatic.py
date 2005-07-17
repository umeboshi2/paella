import os
import tempfile

from useless.base import Error, debug
from useless.base.util import makepaths, ujoin, strfile

from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq

from useless.gtk.helpers import make_menu, populate_menu
from useless.gtk.simple import TextScroll, SimpleMenu
from useless.gtk.middle import ListNoteBook, MyNotebook
from useless.gtk.windows import MenuWindow
from useless.gtk import dialogs

from paella.db.base import Traits
from paella.db.schema.paella_tables import SCRIPTS
from paella.db.trait.relations import TraitScript

class AllScriptsDialog(dialogs.CList):
    def __init__(self, message, conn, suite, name='AllScriptsDialog'):
        dialogs.CList.__init__(self, message, name=name)
        self.script = TraitScript(conn, suite)
        rows = self.script.cmd.select()
        self.set_rows(rows)

class ScriptText(TextScroll):
    def __init__(self, conn, suite, trait, script):
        self.conn = conn
        self.suite = suite
        self.trait = trait
        self.script = TraitScript(self.conn, self.suite)
        self.script.set_trait(trait)
        self.current_script = script
        text = self.script.read_script(self.current_script)
        TextScroll.__init__(self, text)
        

    def populate_menu(self, widget, mainmenu, tmenu):
        menuitem = widget.get_name()
        populate_menu(mainmenu, self.trait, [menuitem], self.edit_script)

    def edit_script(self, menuitem, name, parent):
        sfile = self.script.get(name)
        tmp, path = tempfile.mkstemp('paella', 'script')
        print path, tmp
        script = sfile.read()
        sfile.close()
        tmp = file(path, 'w')
        tmp.write(script)
        tmp.close()
        os.system('$EDITOR %s' %path)
        tmp = file(path, 'r')
        mod = tmp.read()
        tmp.seek(0)
        if mod != script:
            print 'script modified'
            self.script.save_script(name, tmp)
            self.set_text(name, mod)
        os.remove(path)
        
    def new_script(self, name):
        if self.script.get(name) is not None:
            dialogs.Message('script exists')
            raise Error, 'script exists'
        tmp = strfile()
        self.script.insert_script(name, tmp)
        self.append_script(name)
        tmp.close()
        self.edit_script(None, name, None)

    def append_script(self, name, text=''):
        page = TextScroll(text, name=name)
        page.tview.connect('populate-popup', self.populate_menu, self.menu)
        self.append_page(page, name)
        
        
class ScriptNotebook(MyNotebook):
    def __init__(self, conn, suite, trait):
        MyNotebook.__init__(self)
        self.conn = conn
        self.suite = suite
        self.trait = trait
        self.script = TraitScript(self.conn, self.suite)
        self.script.set_trait(trait)
        self.menu = SimpleMenu()
        for row in self.script.scripts():
            name = row.script
            sfile = self.script.scriptfile(name)
            self.append_script(name, sfile.read())
            sfile.close()

    def populate_menu(self, widget, mainmenu, tmenu):
        menuitem = widget.get_name()
        populate_menu(mainmenu, self.trait, [menuitem], self.edit_script)

    def edit_script(self, menuitem, name, parent):
        sfile = self.script.get(name)
        tmp, path = tempfile.mkstemp('paella', 'script')
        script = sfile.read()
        sfile.close()
        tmp = file(path, 'w')
        tmp.write(script)
        tmp.close()
        os.system('$EDITOR %s' %path)
        tmp = file(path, 'r')
        mod = tmp.read()
        tmp.seek(0)
        if mod != script:
            print 'script modified'
            self.script.save_script(name, tmp)
            self.set_text(name, mod)
        os.remove(path)
        
    def new_script(self, name):
        if self.script.get(name) is not None:
            dialogs.Message('script exists')
            raise Error, 'script exists'
        tmp = strfile()
        self.script.insert_script(name, tmp)
        self.append_script(name)
        tmp.close()
        self.edit_script(None, name, None)

    def append_script(self, name, text=''):
        page = TextScroll(text, name=name)
        page.tview.connect('populate-popup', self.populate_menu, self.menu)
        self.append_page(page, name)
        
        

    def set_text(self, name, text):
        self.pages[name].set_text(text)

class ScriptBrowser(ListNoteBook):
    def __init__(self, conn, suite, trait):
        self.conn = conn
        self.suite = suite
        self.trait = trait
        self.cursor = StatementCursor(self.conn)
        self.cursor.set_table('%s_scripts' % self.suite)
        self.edit_menu = make_menu(SCRIPTS, self.modify_trait, name='edit')
        self.diff_menu = make_menu(SCRIPTS, self.modify_trait, name='diff')
        self.menu = make_menu(['edit', 'diff'], self.modify_trait)
        self.menu['edit'].set_submenu(self.edit_menu)
        self.menu['diff'].set_submenu(self.diff_menu)
        self.menu.set_name('main')
        ListNoteBook.__init__(self)
        self.reset_rows()

    def reset_rows(self):
        rows = self.cursor.select(fields=['script'], clause=self._trait_clause())
        self.set_rows(rows)
        self.set_row_select(self.script_selected)

    def modify_trait(self, menuitem, action):
        parent = menuitem.get_parent().get_name()
        if parent == '_none_':
            print 'ack ack ack'
        elif parent != 'main':
            print parent, action

    def _trait_clause(self):
        return Eq('trait', self.trait)

    def script_selected(self, listbox, row, column, event):
        script = listbox.get_selected_data()[0].script
        self.select_script(script)

    def select_script(self, script):
        if script not in self.pages:
            newpage = ScriptText(self.conn, self.suite, self.trait, script)
            self.append_page(newpage, script)
        self.set_current_page(script)



   

class TraitScriptBrowser(ListNoteBook):
    def __init__(self, conn, suite):
        self.conn = conn
        self.suite = suite
        self.traits = Traits(self.conn, self.suite)
        self.edit_menu = make_menu(SCRIPTS, self.modify_trait, name='edit')
        self.diff_menu = make_menu(SCRIPTS, self.modify_trait, name='diff')
        self.menu = make_menu(['edit', 'diff'], self.edit_menu)
        self.menu['edit'].set_submenu(self.edit_menu)
        self.menu['diff'].set_submenu(self.diff_menu)
        ListNoteBook.__init__(self)
        self.reset_rows()

    def modify_trait(self, menuitem, action):
        parent = menuitem.get_parent()
        command = parent.get_name()
        rows = self.get_selected_data()
        if len(rows):
            trait = rows[0].trait
            print action, trait
            if command == 'edit':
                if action not in self.pages[trait].pages:
                    self.pages[trait].new_script(action)
                else:
                    self.pages[trait].edit_script(None, action, None)
            elif command == 'diff':
                print 'diff', action
                AllScriptsDialog('which script?', self.conn, self.suite)
            
        else:
            dialogs.Message('select a trait first')

    def reset_rows(self):
        rows = self.traits.select(fields=['trait'])
        self.set_rows(rows)
        self.set_row_select(self.trait_selected)

    def trait_selected(self, listbox, row, column, event):
        trait = listbox.get_selected_data()[0].trait
        self.select_trait(trait)

    def select_trait(self, trait):
        if trait not in self.pages:
            newpage = ScriptNotebook(self.conn, self.suite, trait)
            self.append_page(newpage, trait)
        self.set_current_page(trait)

    


class ScriptManager(MenuWindow):
    def __init__(self, conn, suite, name='ScriptManager'):
        MenuWindow.__init__(self, name=name)
        self.set_title('%s script manager' % suite)
        self.conn = conn
        self.suite = suite
        self.browser  = TraitScriptBrowser(self.conn, self.suite)
        self.vbox.add(self.browser)
        self.set_size_request(600, 400)
        

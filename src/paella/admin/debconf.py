import os
import tempfile
from paella.base import Error, debug

from paella.base.util import ujoin
from paella.base.defaults import DELIMITERS

from paella.gtk.base import right_click_pressed, select_a_file
from paella.gtk.simple import SimpleMenu, TextScroll
from paella.gtk.middle import ListNoteBook, FieldEntryVbox
from paella.gtk.middle import RecordBox, ScrollCList
from paella.gtk.windows import MenuWindow, CommandBoxWindow
from paella.gtk.helpers import populate_menu, make_menu
from paella.gtk import dialogs

from paella.debian.debconf import parse_debconf
from paella.debian.debconf import parse_debconf_template

from paella.db.midlevel import StatementCursor, Environment

from paella.profile.base import PaellaConnection, TraitEnvironment, Traits
from paella.profile.trait import TraitDebconf


from gtk import TRUE, FALSE, mainquit, mainloop

from base import select_from_tarfile


class _DebconfEditor(ListNoteBook):
    def __init__(self, name='_DebconfEditor'):
        ListNoteBook.__init__(self)
        self.set_name(name)
        self._debconf = {}
        self.reset_rows()
        self.append_page(TextScroll(''), 'data')

    def reset_rows(self):
        self.set_rows(self._debconf.keys(), ['name'])
        self.set_row_select(self.confrow_selected)
        print 'reset_rows'

    def set_config(self, path):
        self._debconf = parse_debconf(path)
        self.reset_rows()

    def set_template(self, path):
        self._debconf = parse_debconf_template(path)
        self.reset_rows()

    def confrow_selected(self, listbox, row, column, event):
        row = listbox.get_selected_data()[0]
        self.select_confrow(row.name)

    def select_confrow(self, name):
        items = ['%s:  %s' % (k,v) for k,v in self._debconf[name].items()]
        self.pages['data'].set_text('\n'.join(items))
        


class _DebconfData(_DebconfEditor):
    def __init__(self, name='_DebconfData'):
        _DebconfEditor.__init__(self, name=name)
        
        

class DebconfEditor(_DebconfEditor):
    def __init__(self, conn, suite, trait, name='DebconfEditor'):
        self.menu = make_menu(['update', 'insert'], self.main_command)
        _DebconfEditor.__init__(self, name=name)
        self.conn = conn
        self.suite = suite
        self.dc = TraitDebconf(self.conn, self.suite)
        self.dialogs = dict.fromkeys(['setconf', 'settemplate'])
        self.trait = trait
        self.dc.set_trait(trait)
        
    def _get_debconf(self, data=True):
        rows = self.get_selected_data()
        if not len(rows):
            raise dialogs.Message('need to select something')
        name = rows[0].name
        if data:
            return self._get_debconf_data(name)
        else:
            return name

    def _get_debconf_data(self, name):
        data = {}.fromkeys(['name', 'template', 'owners', 'value'])
        for key in data:
            data[key] = self._debconf[name][key]
        return data
    
    def main_command(self, menuitem, command):
        if command == 'update':
            data = self._get_debconf()
            self.dc.update(data, self.trait)
        elif command == 'insert':
            data = self._get_debconf()
            self.dc.insert(data, self.trait)
                

    def filesel_ok(self, button, filesel):
        path = filesel.get_filename()
        action = filesel.get_data('action')
        if action == 'setconf':
            self.set_config(path)
        else:
            self.set_template(path)
        filesel.destroy()
    

class DebconfEditorWin(MenuWindow):
    def __init__(self, conn, suite, trait, name='DebconfEditorWin'):
        MenuWindow.__init__(self)
        self.set_name(name)
        self.debconf = DebconfEditor(conn, suite, trait, name=name)
        self.vbox.add(self.debconf)

    def set_config(self, path):
        self.debconf.set_config(path)

dcmenu_cmds = ['getconfig', 'getfromtar', 'update', 'delete']
class TraitDebconfBrowser(ListNoteBook):
    def __init__(self, conn, suite, name='TraitDebconfBrowser'):
        self.menu = make_menu(dcmenu_cmds, self.modify_trait)
        ListNoteBook.__init__(self)
        self.conn = conn
        self.suite = suite
        self.dc = TraitDebconf(self.conn, self.suite)
        self.traits = Traits(self.conn, self.suite)
        self.reset_rows()

    def reset_rows(self):
        rows = self.traits.select(fields=['trait'])
        self.set_rows(rows)
        self.set_row_select(self.trait_selected)

    def trait_selected(self, listbox, row, column, event):
        trait = listbox.get_selected_data()[0].trait
        self.select_trait(trait)
        
    def select_trait(self, trait):
        self.trait = trait
        self.dc.set_trait(trait)
        if trait not in self.pages:
            newpage = ScrollCList()
            self.append_page(newpage, trait)
        self.set_current_page(trait)
        self.pages[trait].set_rows(self.dc.cmd.select())

    def modify_trait(self, menuitem, action):
        try:
            trait = self.listbox.get_selected_data()[0].trait
        except IndexError:
            dialogs.Message('no trait selected')
            raise IndexError
        if action == 'getconfig':
            self.select_configdat(action='getconfig')
        elif action == 'getfromtar':
            self.select_configdat(action='getfromtar')
        elif action == 'update':
            print 'update'
        elif action == 'delete':
            print 'delete'
        

    def select_configdat(self, button=None, data=None, action='getconfig'):
        select_a_file(action, '/', self.filesel_ok)
        

    def pull_from_tar(self, button, fileselect):
        info, tfile = fileselect.extract_file()
        print tfile.name
        conffile, cfpath = tempfile.mkstemp('paella', 'debconf')
        conffile = file(cfpath, 'w')
        conffile.write(tfile.read())
        conffile.close()
        self.editor = DebconfEditorWin(self.conn, self.suite, self.trait)
        self.editor.set_config(cfpath)
        fileselect.destroy()
        os.remove(cfpath)
    
        
    def filesel_ok(self, button, filesel):
        path = filesel.get_filename()
        action = filesel.get_data('action')
        if action == 'getconfig':
            self.editor = DebconfEditorWin(self.conn, self.suite, self.trait)
            self.editor.set_config(path)
        elif action == 'getfromtar':
            select_from_tarfile('getfromtar', path, self.pull_from_tar)
        filesel.destroy()

         
class DebconfBrowser(CommandBoxWindow):
    def __init__(self, conn, suite, name='DebconfBrowser'):
        CommandBoxWindow.__init__(self, name=name)
        self.tdcbox = TraitDebconfBrowser(conn, suite, name=name)
        self.vbox.add(self.tdcbox)
        self.conn = conn
        self.suite = suite
        self.dc = TraitDebconf(self.conn, self.suite)
        self.tbar.add_button('update', 'update', self.reset_rows)
        self.tbar.add_button('delete', 'delete', self.delete_row)
        self.reset_rows()
        
    def reset_rows(self, *args):
        self.dcbox.set_rows(self.dc.cmd.select())


    def delete_row(self, button, data):
        rows = self.dcbox.get_selected_data()
        if len(rows) != 1:
            dialogs.Message('need to select something')
        else:
            r = rows[0]
            self.dc.delete(r.name, r.trait)
            
                
if __name__ == '__main__':
    conn = PaellaConnection()
    win = MenuWindow()
    dc = DebconfEditor(conn, 'sid', 'base')
    win.vbox.add(dc)
    win.show()
    win.connect('destroy', mainquit)
    mainloop()
    



#if __name__ == '__main__':

from paella.profile.base import Suites
from paella.profile.trait import Trait
from useless.gtk.middle import ScrollCList
from useless.gtk.middle import ListNoteBook
from useless.gtk.windows import CommandBoxWindow
from useless.gtk.helpers import HasDialogs, make_menu
from useless.gtk import dialogs

from paella.admin.template import TemplateBrowser
from paella.admin.scriptomatic import ScriptBrowser
from paella.admin.traitgen import TraitBrowser

TRAITCMDS = ['import', 'export']

class TraitManagerBrowser(ListNoteBook):
    def __init__(self, conn, suite=None):
        self.menu = make_menu(TRAITCMDS, self.trait_command)
        ListNoteBook.__init__(self)
        self.conn = conn
        self.suite = suite
        self.reset_rows()
        for page in ['parents', 'packages', 'templates', 'scripts']:
            self.append_page(ScrollCList(), page)

    def set_suite(self, suite):
        self.suite = suite
        self.reset_rows()
        
    def trait_command(self, *args):
        print args

    def reset_rows(self):
        if self.suite is None:
            self.traits = None
            self.set_rows([])
        else:
            self.traits = Trait(self.conn, self.suite)
            self.set_rows(self.traits.get_traits())
        self.set_row_select(self.trait_selected)

    def trait_selected(self, listbox, row, column, event):
        trait = listbox.get_selected_data()[0][0]
        self.select_trait(trait)
        
    def select_trait(self, trait):
        for page in ['parents', 'packages', 'templates', 'scripts']:
            if page in self.pages:
                self.remove_page(page)
        self.append_page(TraitBrowser(self.conn, self.suite), 'parents')
        self.pages['parents'].select_trait(trait)
        self.append_page(TemplateBrowser(self.conn, self.suite, trait), 'templates')
        self.append_page(ScriptBrowser(self.conn, self.suite, trait), 'scripts')
                
            

class TraitManagerWin(CommandBoxWindow, HasDialogs):
    def __init__(self, conn):
        CommandBoxWindow.__init__(self)
        self.conn = conn
        self.suites = Suites(self.conn)
        self.add_menu(['all', 'profile'], 'selection', self.set_trait_selection)
        self.tbar.add_button('suite', 'select suite', self.suite_selection)
        self.dialogs = {}.fromkeys(['select suite'])
        self.browser = TraitManagerBrowser(self.conn)
        self.vbox.add(self.browser)
        

    def set_trait_selection(self, menuitem, command):
        print menuitem, command

    def suite_selection(self, button, data):
        print button, data
        dialog = dialogs.CList('select a suite', 'select suite')
        dialog.set_rows(self.suites.select(fields=['suite']))
        dialog.set_ok(self.suite_dialog_selected)
        dialog.set_cancel(self.destroy_dialog)
        self.dialogs['select suite'] = dialog
        
    def suite_dialog_selected(self, *args):
        print args
        suite = self.dialogs['select suite'].get_selected_data()[0][0]
        self.destroy_dialog(self.dialogs['select suite'])
        self.suites.set(suite)
        self.browser.set_suite(suite)
        self.browser.reset_rows()
        self.set_title('Managing %s traits' % suite)
        

if __name__ == '__main__':
    from gtk import mainloop, mainquit
    from useless.profile.base import PaellaConfig, PaellaConnection
    cfg = PaellaConfig()
    conn = PaellaConnection(cfg)
    win = TraitManagerWin(conn)
    win.connect('destroy', mainquit)
    mainloop()
    
        

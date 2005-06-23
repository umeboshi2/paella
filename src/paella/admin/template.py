import os
from os.path import join, dirname, isfile, isdir
from xmlrpclib import ServerProxy, SafeTransport
import tempfile

from useless.base import Error, debug, NoExistError, UnbornError
from useless.base.util import ujoin, readfile, makepaths
from useless.base.util import get_sub_path, writefile, strfile
from useless.db.lowlevel import OperationalError
from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq

from useless.gtk.base import select_a_file
from useless.gtk.simple import SimpleMenu
from useless.gtk.middle import ListNoteBook, ScrollCList, MyNotebook
from useless.gtk.helpers import get_buffer_text, populate_menu, make_menu
from useless.gtk.template import TemplateEditor
from useless.gtk.windows import MenuWindow
from useless.gtk import dialogs

from gtk import MenuItem, FileSelection, ScrolledWindow
from gtk import TRUE, FALSE, mainquit, mainloop

from paella.profile.base import Traits, PaellaConfig
from paella.profile.trait import TraitParent, TraitTemplate
from paella.profile.trait import TraitPackage
from paella.profile.trait import TraitElement, backup_trait
from paella.profile.trait import Trait, TraitTarFile

from base import SystemTarWindow, select_from_tarfile
from traitgen import TraitGenWin
from debconf import DebconfBrowser

def get_file_path(path, conf_path):
    tpath = get_sub_path(path, conf_path)
    package = tpath.split('/')[0]
    return tpath[len(package):][1:], package


TEMPL_CMDS = ['new', 'save', 'done', 'drop', 'root', 'edit']
TRAIT_TEMPL_CMDS = ['select trait', 'extract trait packages',
                    'trait manager']

class _CommonTemplate(object):
    def template_filename(self, template):
        tpath = join(self.template_path, self.suite, self.trait)
        return join(tpath, template + '.template')

    def suite_template_path(self, filesel=False):
        path = join(self.template_path, self.suite)
        if filesel:
            path += '/'
        return path

    def trait_temp_path(self, filesel=False):
        path = join(self._tmp_path, self.suite, self.trait)
        if filesel:
            path += '/'
        return path

    def set_suite(self, suite):
        self.suite = suite



class TemplateEnvironment(ScrolledWindow):
    def __init__(self, conn):
        ScrolledWindow.__init__(self)
        self.conn = conn
        self.editor = TemplateEditor()
        self.menu = SimpleMenu()
        self.editor.connect('populate-popup', self.populate_menu, self.menu)
        self.add_with_viewport(self.editor)
        self.show()
        
    def set_suite(self, suite):
        self.suite = suite
        self.__set_suitecursors__()

    def __set_suitecursors__(self):
        self.traitparent = TraitParent(self.conn, self.suite)
        self.traittemplate = TraitTemplate(self.conn, self.suite)
        self.traitpackage = TraitPackage(self.conn, self.suite)
        
    def set_trait(self, trait):
        self.trait = trait
        self.traitparent.set_trait(trait)
        self.traittemplate.set_trait(trait)
        self.traitpackage.set_trait(trait)
        self.__set_environment__()

    def __set_environment__(self):
        self.environ = dict(self.traitparent.get_environment([self.trait]))
        self.sections = dict([(k, v.keys()) for k,v in self.environ.items()])

    def populate_menu(self, widget, mainmenu, tmenu):
        self.__set_environment__()
        populate_menu(mainmenu, '_define_', ['_create_'], self.make_new_tag)
        for section, vars in self.sections.items():
            populate_menu(mainmenu, section, vars, self.make_tag)

    def make_tag(self, menuitem, name, parent):
        parentname = parent.get_name()
        tagname = ujoin(parentname, name)
        self.editor.make_tag(tagname)

    def make_new_tag(self, menuitem, name, parent):
        parentname = parent.get_name()
        if (parentname, name) == ('_define_', '_create_'):
            self.editor.create_new_tag(self.create_entry)
            
    def create_entry(self, *args):
        var = dict(self.editor.dialogs['create'].items())
        debug('var is %s' % var)
        self.environ[self.trait][var['name']] = var['value']
        tagname = ujoin(self.trait, var['name'])
        self.editor.make_tag(tagname)
        self.editor.destroy_dialog(self.editor.dialogs['create'])

    def preview(self, *args):
        subs = self.traitparent.get_superdict(self.environ.keys())
        self.editor.buffer.set_subs(subs)
        self.editor.preview(*args)

    def set_text(self, text):
        self.editor.buffer.set_text(text)

    def get_text(self):
        return self.editor.get_text()

class TemplateNotebook(MyNotebook):
    def __init__(self, conn, cfg, suite, trait, package, template, extracted=None):
        MyNotebook.__init__(self)
        self.conn = conn
        self.cmd = TraitTemplate(self.conn, suite)
        self.cfg = cfg
        self.trait = trait
        self._tmp_path = '/nowhere'
        self.template_path = '/nowhere'
        self.workspace = TemplateEnvironment(self.conn)
        self.template_view = TemplateEnvironment(self.conn)
        self.original_view = TemplateEnvironment(self.conn)
        self.set_suite(suite)
        self.workspace.set_trait(trait)
        self.template_view.set_trait(trait)
        self.original_view.set_trait(trait)
        self.template_view.editor.set_editable(False)
        self.original_view.editor.set_editable(False)
        self.append_page(self.workspace, 'workspace')
        self.append_page(self.template_view, 'template')
        self.append_page(self.original_view, 'original')
        self.extracted = extracted
        self.set_template(package, template)
        
        
    def set_template(self, package, template):
        self.package = package
        self.template = template
        path = self.template_filename(package, template)
        print self.trait, 'self.trait'
        clause = Eq('trait', self.trait) & Eq('package', package) & Eq('template', template)
        print 'clause', clause
        template_text = self.traittemplate.templatedata(package, template)
        self.workspace.set_text(template_text)
        self.template_view.set_text(template_text)
        if self.extracted:
            path = join(self.trait_temp_path(), package, template)
            try:
                self.original_view.set_text(readfile(path))
            except NoExistError:
                pass
            except IOError:
                pass
            

    def set_suite(self, suite):
        self.suite = suite
        self.workspace.set_suite(suite)
        self.template_view.set_suite(suite)
        self.original_view.set_suite(suite)
        self.traittemplate = self.workspace.traittemplate
        self.traitpackage = self.workspace.traitpackage
        self.tmp_path = join(self._tmp_path, self.suite)

    def template_filename(self, package, template):
        tpath = join(self.template_path, self.suite, self.trait)
        return join(tpath, package, template + '.template')

    def suite_template_path(self, filesel=False):
        path = join(self.template_path, self.suite)
        if filesel:
            path += '/'
        return path

    def trait_temp_path(self, filesel=False):
        path = join(self._tmp_path, self.suite, self.trait)
        if filesel:
            path += '/'
        return path

    def save_template(self):
        template_path = 'in database'
        package, template = self.package, self.template
        data = strfile(self.workspace.get_text())
        self.traittemplate.save_template(package, template, data)
        dialogs.Message('saved %s in\n%s' % (template, template_path))        

    def edit_template(self):
        package, template = self.package, self.template
        data = self.template_view.get_text()
        tmp, path = tempfile.mkstemp('paella', 'template')
        tmp = file(path, 'w')
        tmp.write(data)
        tmp.close()
        os.system('$EDITOR %s' %path)
        tmp = file(path, 'r')
        mod = tmp.read()
        tmp.seek(0)
        if mod != data:
            print 'template modified'
            self.workspace.set_text(mod)
            self.template_view.set_text(mod)
            self.save_template()
        os.remove(path)
        
            

    def _diff(self, template, path):
        current_template = self.template_filename(template)
        os.popen2('meld %s %s' %(current_template, path))

    def fileselect_ok(self, button, filesel):
        path = filesel.get_filename()
        action = filesel.get_data('action')
        filesel.destroy()
        if action == 'new':
            template, package = get_file_path(path, self.trait_temp_path())
            if template not in self.templates:
                self.insert_new_template(package, template, path)
            else:
                dialogs.Message('template already exists')
        elif action == 'diff':
            pass
        elif action == 'load':
            self.load_template(path)

class TemplateBrowser(ListNoteBook):
    def __init__(self, conn, suite, trait):
        self.menu = make_menu(TEMPL_CMDS, self.template_command)
        self.conn = conn
        self.current_trait = trait
        self.traittemplate = TraitTemplate(self.conn, suite)
        self.traittemplate.set_trait(self.current_trait)
        self.traitpackage = TraitPackage(self.conn, suite)
        self.traitpackage.set_trait(self.current_trait)
        self.current_template = None
        self.cfg = PaellaConfig()
        self.template_path = '/nowhere'
        self._tmp_path = '/nowhere'
        self.tarball_path = self.cfg.get('management_gui', 'bkuptarball_path')
        ListNoteBook.__init__(self)
        self.set_suite(suite)
        self.extracted = None
        self.reset_rows()
        self.dialogs = {}.fromkeys(['attach', 'rootsel'])
        
    def reset_rows(self):
        rows = self.traittemplate.templates(fields=['template', 'package'])
        self.set_rows(rows)
        self.set_row_select(self.template_selected)
        self.templates = [r.template for r in rows]
            
    def template_selected(self, listbox, row, column, event):
        row = listbox.get_selected_data()[0]
        self.set_template(row.package, row.template)
    
    def set_template(self, package, template):
        self.current_package = package
        self.current_template = template
        if template not in self.pages:
            trait = self.current_trait
            nbook = TemplateNotebook(self.conn, self.cfg, self.suite, trait,
                                     package, template, self.extracted)
            self.append_page(nbook, template)
        else:
            self.set_current_page(template)
            
    def template_filename(self, package, template):
        tpath = join(self.template_path, self.suite, self.current_trait)
        return join(tpath, package, template + '.template')
        

    def suite_template_path(self, filesel=False):
        path = join(self.template_path, self.suite)
        if filesel:
            path += '/'
        return path

    def trait_temp_path(self, filesel=False):
        path = join(self._tmp_path, self.suite, self.current_trait)
        if filesel:
            path += '/'
        return path
       
    def set_suite(self, suite):
        self.suite = suite

    def save_template(self):
        try:
            template = self.get_selected_data()[0].template
            self.pages[template].save_template()
        except IndexError:
            dialogs.Message('a template must be selected')
            

    def edit_template(self):
        try:
            template = self.get_selected_data()[0].template
            self.pages[template].edit_template()
        except IndexError:
            dialogs.Message('a template must be selected')
            
        
        
    def template_command(self, meuitem, command):
        if command in ['new']:
            path = self.trait_temp_path(filesel=True)
            select_a_file('new', path, self.fileselect_ok)
        elif command == 'diff':
            path = self.suite_template_path(filesel=True)
            select_a_file('load', path, self.fileselect_ok)
        elif command == 'save':
            self.save_template()
        elif command == 'load':
            path = self.suite_template_path(filesel=True)
            select_a_file('load', path, self.fileselect_ok)
        elif command == 'done':
            try:
                template = self.get_selected_data()[0].template
                self.remove_page(template)
            except IndexError:
                pass
        elif command == 'drop':
            print 'need to drop template'
            rows = self.get_selected_data()
            if len(rows):
                row = rows[0]
                self.traittemplate.drop_template(row.package, row.template)
                self.remove_page(row.template)
                self.reset_rows()
            else:
                dialogs.Message('a template must be selected')
        elif command == 'root':
            if self.dialogs['rootsel'] is None:
                path = self.tarball_path + '/'
                select_a_file('root', path, self.tarball_selected)
        elif command == 'edit':
            self.edit_template()
            
            


    def tarball_selected(self, button, fileselect):
        path = fileselect.get_filename()
        fileselect.destroy()
        self.dialogs['rootsel'] = select_from_tarfile('heydude', path, self.pull_from_tar)
        
    def pull_from_tar(self, button, fileselect):
        info, tfile = fileselect.extract_file()
        template = tfile.name
        action = 'attach'
        if self.dialogs[action] is None:
            msg = 'attach to which package?'
            self.dialogs[action] = dialogs.CList(msg, name=action)
            lbox = self.dialogs[action]
            lbox.set_rows(self.traitpackage.packages())
            lbox.set_ok(self.insert_new_template_from_tar)
            lbox.set_cancel(self.destroy_dialog)
            lbox.set_data('tarmember', (info, tfile))
            
    def insert_new_template_from_tar(self, button):
        lbox = self.dialogs['attach']
        rows = lbox.get_selected_data()
        if len(rows) == 1:
            package = rows[0].package
            info, tfile = lbox.get_data('tarmember')
            self.destroy_dialog(lbox)
            self._insert_new_template(package, info.name, tfile, info)
            
        
    def _insert_new_template(self, package, template, fileobj, info):
        fileobj.seek(0)
        filename = self.template_filename(package, template)
        data = dict(owner=info.uname, grp_owner=info.gname,
                    mode=oct(info.mode), package=package,
                    template=template)
        self.traittemplate.insert_template(data, fileobj)
        self.set_template(package, template)
        self.reset_rows()
        
        
            
    def insert_new_template(self, package, template, path):
        newfile = readfile(path)
        filename = self.template_filename(package, template)
        makepaths(dirname(filename))
        writefile(filename, newfile)
        try:
            self.traittemplate.insert_template(dict(package=package, template=template),
                                               file(path))
        except OperationalError:
            dialogs.Message('template already exists')
        self.set_template(package, template)
        self.reset_rows()

    def load_template(self, path):
        template, package = get_file_path(path, self.suite_template_path())
        if template[-9:] == '.template':
            template = template[:-9]
            if template not in self.templates:
                try:
                    orig = self.find_original(template)
                    self.insert_new_template(package, template, path)
                except NoExistError:
                    dialogs.Message('%s not in extracted packages' %template)


    def _diff(self, template, path):
        current_template = self.template_filename(template)
        os.popen2('meld %s %s' %(current_template, path))

    def fileselect_ok(self, button, filesel):
        path = filesel.get_filename()
        action = filesel.get_data('action')
        filesel.destroy()
        if action == 'new':
            template, package = get_file_path(path, self.trait_temp_path())
            if template not in self.templates:
                self.insert_new_template(package, template, path)
            else:
                dialogs.Message('template already exists')
        elif action == 'diff':
            pass
        elif action == 'load':
            self.load_template(path)

    def set_extracted(self, extracted):
        self.extracted = extracted
        for page in self.pages.values():
            page.extracted = extracted

    def _extract_packages(self):
        dialogs.Message('deprecated(for now)')
        if False:
            if self.extracted is None:
                packages = [p.package for p in self.traitpackage.packages()]
                path = self.trait_temp_path()
                self.set_extracted(True)
                packs = ',\n'.join(packages)
                message = 'extracted packages:\n %s into:\n%s'%(packs, path)
                dialogs.Message(message)
            else:
                dialogs.Message('already extracted')

    def extract_packages(self):
        self._extract_packages()

_MODTRAIT  = ['extract', 'import', 'export', 'update', 'updatedir', 'exportdir']
_MODTRAIT += ['importdir']

class TraitTemplateBrowser(ListNoteBook):
    def __init__(self, conn, suite):
        self.menu = make_menu(_MODTRAIT, self.modify_trait)
        ListNoteBook.__init__(self)
        self.conn = conn
        self.traits = Traits(self.conn, suite)
        self.trait_selection = '_all_traits_'
        self.reset_rows()
        self.cfg = PaellaConfig()
        self._parents = TraitParent(self.conn, suite)
        self.cursor = StatementCursor(self.conn)
        self.template_path = '/nowhere'
        self.tarball_path = self.cfg.get('management_gui', 'bkuptarball_path')
        self.suite = suite

    def modify_trait(self, menuitem, action):
        if action == 'hello':
            dialogs.Message('hello')
        elif action in ['import', 'update']:
            filesel = select_a_file(action, self.tarball_path + '/', self.select_trait_tarball)
        elif action in ['updatedir', 'exportdir', 'importdir']:
            filesel = select_a_file(action, self.tarball_path + '/', self.select_traitdir)
        elif action == 'export':
            try:
                trait = self.listbox.get_selected_data()[0].trait
                #self.pages[trait].extract_packages()
                self.select_export_path(trait)
            except IndexError:
                dialogs.Message('no trait selected')
            
        elif action == 'extract':
            try:
                trait = self.listbox.get_selected_data()[0].trait
                self.pages[trait].extract_packages()
            except IndexError:
                dialogs.Message('no trait selected')
        
    def reset_rows(self):
        if self.trait_selection == '_all_traits_':
            rows = self.traits.select(fields=['trait'])
            self.set_rows(rows)
        else:
            clause = Eq('profile', self.trait_selection)
            rows = self.cursor.select(fields=['trait'],
                                      table='profile_trait',
                                      clause=clause)
            ptraits = [x.trait for x in rows]
            traits = self._parents.get_traitset(ptraits)
            self.set_rows(list(traits), [self.trait_selection])
        self.set_row_select(self.trait_selected)

    def trait_selected(self, listbox, row, column, event):
        trait = listbox.get_selected_data()[0][0]
        self.select_trait(trait)
        
    def select_trait(self, trait):
        if trait not in self.pages:
            newpage = TemplateBrowser(self.conn, self.traits.suite, trait)
            self.append_page(newpage, trait)
        self.set_current_page(trait)
            
    def set_suite(self, suite):
        self.suite = suite
        self.traits.set_suite(suite)
        for page in self.pages:
            self.remove_page(page)
        self.reset_rows()

    def select_traitdir(self, button, filesel):
        path = filesel.get_filename()
        action = filesel.get_data('action')
        filesel.destroy()
        if not isdir(path):
            path = dirname(path)
        if not isdir(path):
            raise Error, '%s not found' % path
        if action in ['updatedir', 'importdir']:
            if action == 'updatedir':
                tcmd = 'update'
            elif action == 'importdir':
                tcmd = 'import'
            traits = [t.trait for t in self.traits.select()]
            if tcmd == 'update':
                ls = [f for f in os.listdir(path) if f[-4:] == '.tar' and f[:-4] in traits]
                for f in ls:
                    self.importupdate(join(path, f), tcmd)
            elif tcmd == 'import':
                ls = [f for f in os.listdir(path) if f[-4:] == '.tar']
                traits = [t[:-4] for t in ls]
                while len(traits):
                    trait = traits[0]
                    try:
                        self.importupdate(join(path, trait + '.tar'), tcmd)
                    except UnbornError:
                        traits.append(trait)
                    del traits[0]
                    print 'processed', trait
                    
        elif action == 'exportdir':
            self.select_export_path('_all_traits_')
            
    def select_trait_tarball(self, button, filesel):
        path = filesel.get_filename()
        action = filesel.get_data('action')
        filesel.destroy()
        self.importupdate(path, action)
        
    def importupdate(self, path, action):
        tarball = TraitTarFile(path)
        trait = tarball.get_trait()
        traitdb = Trait(self.conn, self.suite)
        if action == 'import':
            traitdb.insert_trait(path, suite=self.suite)
        for info in tarball:
            if info.name[:10] == 'templates/':
                #tarball.extract(info, template_path)
                pass
        self.reset_rows()

    def select_export_path(self, trait):
        filesel = select_a_file(trait, self.tarball_path + '/', self.export_path_selected)
        
    def export_path_selected(self, button, filesel):
        trait = filesel.get_data('action')
        path = dirname(filesel.get_filename())
        filesel.destroy()
        if trait == '_all_traits_':
            traits = [t.trait for t in self.traits.select()]
            for t in traits:
                self.export_trait(t, path)
        else:
            self.export_trait(trait, path)
        
        
    def export_trait(self, trait, path=None):
        if path is None:
            path = self.tarball_path
        tt = TraitTemplate(self.conn, self.suite)
        tt.set_trait(trait)
        backup_trait(self.conn, self.suite, trait, path)
        dialogs.Message('%s exported to %s' % (trait, path))
        
class TemplateManager(MenuWindow):
    def __init__(self, conn, suite):
        MenuWindow.__init__(self)
        self.set_title('%s template manager' % suite)
        self.conn = conn
        self.suite = suite
        self.main = StatementCursor(self.conn)
        self.browser = TraitTemplateBrowser(self.conn, suite)
        self.vbox.add(self.browser)
        self.add_menu(['all', 'profile'], 'selection', self.set_trait_selection)
        self.add_menu(TEMPL_CMDS, 'template', self.template_command)
        tc = TRAIT_TEMPL_CMDS
        self.add_menu(tc, 'trait', self.trait_command)
        self.set_size_request(600,400)
        self.dialogs = {}.fromkeys(['select trait', 'select profile'])
        self.browser.set_suite(suite)


    def template_command(self, menuitem, command):
        if self.browser.extracted is None and command in ['new', 'diff', 'load']:
            dialogs.Message('packages not yet extracted')
        else:
            self.browser.template_command(command)
            
    def trait_command(self, menuitem, command):
        tc = TRAIT_TEMPL_CMDS
        if command == tc[0]:
            if self.dialogs[command] is None:
                self._trait_select_dialog(command)
        elif command == tc[1]:
            #self._extract_packages()
            pass
        elif command == tc[2]:
            TraitGenWin(self.conn, self.suite)
            
    def _trait_select_dialog(self, name):
        dialog = dialogs.CList(name, name=name)
        self.main.set_table(ujoin(self.browser.suite, 'traits'))
        traits = self.main.select(fields=['trait'])
        dialog.set_rows(traits)
        dialog.set_ok(self.select_trait)
        dialog.set_cancel(self.destroy_dialog)
        self.dialogs[name] = dialog

    def select_trait(self, *args):
        trait = self.dialogs['select trait'].get_selected_data()[0].trait
        self.destroy_dialog(self.dialogs['select trait'])
        self.set_trait(trait)
        self.set_title('suite: %s  trait:%s' %(self.browser.suite, trait))

    def set_trait(self, trait):
        self.browser.extracted = None
        self.browser.select_trait(trait)
        
                    
    def templates(self):
        return [x.template for x in self.browser.traittemplate.templates()]

    def ask_file_dialog(self, menuitem, name):
        if name in ['open', 'save']:
            filesel = FileSelection(title=name)
            filesel.cancel_button.connect('clicked',
                                          lambda x: filesel.destroy())
            filesel.show()
        if name == 'save':
            if not has_extension(self.filename, 'template'):
                path = self._tmpl_path_()
            else:
                path = pjoin(self.template_path, self.filename)
            makepaths(dirname(path))
        elif name =='open':
            self.filename = ''
            path = pjoin(self.tmp_path, self.filename)
            print 'open', path
        elif name == 'edit' and self.filename:
            path = self._tmpl_path_()
            self._fill_from_path(self._tmpl_path_())
            
        if name in ['open', 'save']:
            filesel.set_filename(path)
            filesel.ok_button.connect('clicked', self.ok_file, filesel)
            filesel.set_data('action', name)

    def set_trait_selection(self, menuitem, command):
        print menuitem, command
        if command == 'all':
            self.browser.trait_selection = '_all_traits_'
            self.browser.reset_rows()
        else:
            dialog = dialogs.CList('hi there', name='select profile')
            profiles = self.main.select(fields=['profile'],
                                        table='profiles', clause=Eq('suite', self.suite))
            dialog.set_rows(profiles)
            dialog.set_ok(self.profile_dialog_selected)
            dialog.set_cancel(self.destroy_dialog)
            self.dialogs['select profile'] = dialog

    def profile_dialog_selected(self, *args):
        profile = self.dialogs['select profile'].get_selected_data()[0][0]
        self.destroy_dialog(self.dialogs['select profile'])
        self.browser.trait_selection = profile
        self.browser.reset_rows()
        

        

        
if __name__ == '__main__':
    from useless.db.lowlevel import QuickConn
    g = PaellaConfig()
    conn = QuickConn(g)
    rconn = RepositoryConnection()
    #tb  = TemplateBrowser(conn)
    #tb.set_suite('woody')
    
    #win = MenuWindow()
    #win.vbox.add(tb)
    win = TemplateManager(conn, rconn)
    win.connect('destroy', mainquit)
    mainloop()
    pass
    

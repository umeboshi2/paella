import os, os.path
from os.path import join as pjoin
from os.path import dirname, isfile
from copy import deepcopy as copy

from paella.base import Error, debug
from paella.base.util import readfile, ujoin, makepaths
from paella.base.util import writefile, strfile
from paella.base.util import has_extension, get_sub_path

from paella.base.config import Configuration
from paella.base.defaults import DELIMITERS

from paella.gtk.simple import TextScroll, SimpleMenu, RadioMenu
from paella.gtk.windows import MenuWindow
from paella.gtk import dialogs
from paella.gtk.helpers import populate_menu

from paella.db.midlevel import StatementCursor, Environment

from paella.profile.base import PaellaConnection
from paella.profile.trait import TraitParent, TraitTemplate

from template import TemplateEnvironment
from environ import EnvironmentEditorWin

from gtk import MenuItem, FileSelection
from gtk import TRUE, FALSE, mainquit, mainloop


def_vars = ['hostname', 'domain', 'host_ipaddr', 'remotedb', 'foo_path']
more_vars = ['admin_user', 'dbadmin', 'remote_path', 'mirror_path']


# notes-- make a place to show templates that are already there
# so they can be edited, etc...
# make a traittemplate cursor for tempplates
#+

def get_file_path(path, conf_path):
    tpath = get_sub_path(path, conf_path)
    package = tpath.split('/')[0]
    return tpath[len(package):][1:]


class ConfigGen(MenuWindow):
    def __init__(self, conn, suite, trait, tmp_path, name='ConfigGen'):
        MenuWindow.__init__(self)
        self.__original_text__ = ''
        self.editor = TemplateEnvironment(conn)
        self.editor.set_suite(suite)
        self.editor.set_trait(trait)
        self.vbox.add(self.editor)
        self.conn = conn
        self.__add_menus__()
        self.filename = ''
        self.filesel = None
        self.set_size_request(600, 500)
        self.cfg = Configuration()
        self.cfg.section = 'paella-admin'
        self.conf_path = self.cfg['config_path']
        self.template_path = pjoin(self.cfg['template_path'], suite, trait)
        self.tmp_path = tmp_path
        makepaths(self.template_path)
        self.dialogs = {}.fromkeys(['template_record', 'environment'])

    def __add_menus__(self):
        self.add_menu(['open', 'edit', 'save'], 'file', self.ask_file_dialog)
        self.add_menu(['preview', 'insert', 'update'], 'template', self.template_commands)
        self.add_menu(['diff'], 'diff', self.diff_commands)
        self.add_menu(['display', 'edit'], 'environment', self.env_commands)
        
        
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

    def _tmpl_path_(self):
        return pjoin(self.template_path, self.filename + '.template')

    def ok_file(self, button, filesel):
        path = filesel.get_filename()
        print path, '  --->is path'
        print self.tmp_path, ' tmppath'
        action = filesel.get_data('action')
        filesel.destroy()
        if action == 'open':
            self._fill_from_path(path)
            self.filename = get_file_path(path, self.tmp_path)
            self.set_title(self.filename)
        elif action == 'save':
            writefile(path, get_buffer_text(self.editor.tbuffer))

    def _fill_from_path(self, path):
        self.__original_text__ = readfile(path)
        self.editor.set_text(copy(self.__original_text__))



    def set_delimiters(self, *args):
        print args

    def template_commands(self, menuitem, name):
        if name == 'preview':
            self.editor.preview()            
        elif name in ['insert', 'update']:
            self.show_template_record()

    def show_template_record(self):
        template = self.filename
        relation = self.editor.traittemplate
        data = dict(owner='root', grp_owner='root', mode='0100644')
        data['template'] = template
        if not self.dialogs['template_record']:
            self.dialogs['template_record'] = dialogs.RecordEntry(self.editor.trait, data,
                                                                  name='template_record')
            record = self.dialogs['template_record']
            if relation.has_template(template):
                record.update(relation.get_row(template))
                record.label.set_text('already in database')
                record.ok_button.set_label('update')
            else:
                record.update(data)
                record.label.set_text('not yet inserted')
                record.ok_button.set_label('insert')
            record.set_ok(self.update_template_record)
            record.set_cancel(self.destroy_dialog)
            
    def update_template_record(self, button):
        action = button.get_label()
        record = self.dialogs['template_record']
        relation = self.editor.traittemplate
        data = dict(record.items())
        if action == 'update':
            relation.update_template(data)
        elif action == 'insert':
            relation.insert_template(data)
        self.destroy_dialog(record)
            
                
    def env_commands(self, menuitem, name):
        environ = self.editor.traitparent.Environment()
        trait = self.editor.trait
        env = 'environment'
        if name == 'display':
            if not self.dialogs[env]:
                self.dialogs[env] = dialogs.RecordEntry(trait, environ, name=env)
                record = self.dialogs[env]
                record.set_cancel(self.destroy_dialog)
        elif name == 'edit':
            EnvironmentEditorWin(self.conn, self.editor.suite)
            
    def diff_commands(self, menuitem, name):
        if name == 'diff':
            print self.filename
            tmpl_path = self._tmpl_path_()
            print tmpl_path
            if isfile(tmpl_path):
                diff = 'xxdiff %s - ' % tmpl_path
                input, output = os.popen2(diff)
                input.write(get_buffer_text(self.editor.tbuffer))
                input.close()

    def destroy_dialog(self, dying):
        name = dying.get_name()
        print name
        self.dialogs[name] = None
        dying.destroy()
        
                
if __name__ == '__main__':
    conn = PaellaConnection()

    mainloop()
    



#if __name__ == '__main__':

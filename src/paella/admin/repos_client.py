from os.path import join, expanduser, dirname
import re
from paella.base import Error, debug, NoFileError, ExistsError
from paella.base.objects import DbBaseRow
from paella.gtk.base import rowpacker, set_receive_targets
from paella.gtk.windows import MenuWindow, CommandBoxWindow
from paella.gtk.middle import ListNoteBook, ScrollCList
from paella.gtk.middle import ListAboveNoteBook
from paella.gtk import dialogs
from paella.gtk.helpers import HasMenuDialog, make_menu
from paella.gtk.helpers import HasDialogs
from paella.gtk.utils import DownloadPoolBox

from gtk import FileSelection, VPaned, Label, VBox
from gtk import mainloop, mainquit, TRUE, FALSE
from gtk import threads_enter, threads_leave
from gtk import Window

from paella.sqlgen.clause import Eq
from paella.debian.base import RepositorySource, parse_sources_list
from paella.debian.repos_base import RepositoryManager, RepositoryConnection
from paella.debian.repos_local import LocalRepository
from paella.debian.repos_remote import RemoteRepository

source_target = ('source-line', 0, 34)
repos_target = ('repos-name', 0, 35)
good_word = re.compile('^[\w_]+$')

class DownloadWindow(Window):
    def __init__(self):
        Window.__init__(self)
        self.pool = DownloadPoolBox(3)
        self.add(self.pool)
        self.show()


class _DragListWindow(dialogs.CList):
    def __init__(self, message, packer, rows, targets,
                      name='_DragListWindow'):
        dialogs.CList.__init__(self, message, name=name, dnd=self.drag_rows,
                               targets=targets)
        self.set_rows(rows)
        self.__packer__ = packer
        self.set_select_mode('multi')

    def drag_rows(self, listbox, context, selection, targettype, time):
        rows = self.__packer__(listbox.get_selected_data())
        selection.set(selection.target, 0, rows)


class SourcesWindow(_DragListWindow):
    def __init__(self, name='SourcesWindow'):
        pass

class SourceStatus(VBox):
    def __init__(self):
        VBox.__init__(self)
        self.status_label = Label('blank')
        self.source_label = Label('blank')
        self.pack_start(self.status_label, FALSE, FALSE, 0)
        self.pack_end(self.source_label, FALSE, FALSE, 0)
        self.status_label.show()
        self.source_label.show()
        self.show()
        
class SourceView(VPaned, HasDialogs):
    def __init__(self, repos, dialogs, name='SourceView'):
        VPaned.__init__(self)
        self.repos = repos
        self.set_name(name)
        commands = ['update section lists', 'check for missing',
                    'check for corrupt']
        self.release_menu = make_menu(commands, self.release_command)
        self.release = ScrollCList(rcmenu=self.release_menu)
        self.add2(self.release)
        self.status = SourceStatus()
        self.add1(self.status)
        self.show()
        rp = self.repos
        sources_text = '\n'.join(map(str, [rp.remote_src, rp.local_src]))
        self.status.source_label.set_text(sources_text)
        if self.repos.check_local_release_file():
            self.reset_rows()
        self.dialogs = dialogs
        
    def release_command(self, menuitem, action):
        print action
        if action == 'update section lists':
            rows = self.repos.local.check_all_dist_sections()
            dl = dialogs.CList('section lists status')
            dl.set_rows(rows)
            dl.set_usize(500, 300)
            bad_rows = [row for row in rows if row.status in ['missing', 'corrupt']]
            jobs = [[self.repos.fulldistpath(row.path), row.full_path] for row in bad_rows]
            if self.dialogs['downloads'] is None:
                self.dialogs['downloads'] = DownloadWindow()
                self.dialogs['downloads'].connect('destroy', self.destroy_dialog)
            if self.dialogs['downloads'] is not None:
                for url, path in jobs:
                    self.dialogs['downloads'].pool.put(url, path)
            
        elif action == 'check for missing':
            status_rows = self.repos.local.check_all_sections()
            status_rows = [row for row in status_rows if row.status == 'missing']
            dl = dialogs.CList('status')
            dl.set_rows(status_rows)
            dl.set_usize(500, 300)
        elif action == 'check for corrupt':
            status_rows = self.repos.local.check_all_sections(quick=False)
            status_rows = [row for row in status_rows if row.status == 'corrupt']
            dl = dialogs.CList('status')
            dl.set_rows(status_rows)
            dl.set_usize(500, 300)
        self.reset_rows()
        
    def reset_rows_orig(self):
        section_files = self.repos.release.select()
        rowdesc = ['name', 'type', 'section', 'path', 'status']
        rows =[]
        for rfile in section_files:
            section, release = self.repos.release.parse_path(rfile.path)
            status = self.repos.local.check_dist_section(section, release)
            rowvals = [rfile.name, rfile.type, section, rfile.path, status]
            rows.append(DbBaseRow(rowdesc, rowvals))
        self.release.set_rows(rows)

    def reset_rows(self):
        section_files = self.repos.release.select()
        rows = self.repos.local.check_all_dist_sections()
        self.release.set_rows(rows)
        

class RepositoryBrowser(ListNoteBook, HasDialogs):
    def __init__(self, conn, name='RepositoryBrowser'):
        self.menu = self.__make_mainmenu_()
        ListNoteBook.__init__(self, name=name)
        self._targets_ = [repos_target]
        self._dnd = self.drag_rows
        self.set_usize(300, 200)
        self.conn = conn
        self.current = None
        self.repos = RepositoryManager(self.conn)
        self.sources_menu = make_menu(['update release'], self.sources_command)
        self.reset_rows()
        self.dialogs = {}.fromkeys(['downloads'])
        
    def drag_rows(self, listbox, context, selection, targettype, time):
        row = listbox.get_selected_data()[0]
        selection.set(selection.target, 0, '^&^'.join([row.name, row.type]))

    def __make_mainmenu_(self):
        commands = ['update release']
        return make_menu(commands, self.sources_command)

    def __set_pages(self):
        pages = dict(self.pages)
        nameclause = Eq('name', self.current.name)
        binclause = nameclause & Eq('type', 'deb')
        srcclause = nameclause & Eq('type', 'deb-src')

    def reset_rows(self):
        self.set_rows(self.repos.sources.select(fields=['name', 'type']))
        self.set_row_select(self.repos_selected)

    def repos_selected(self, listbox, row, column, event):
        self.current = listbox.get_selected_data()[0]
        c = self.current
        remote = RemoteRepository(self.conn, c.name, c.type)
        pages = dict(self.pages)
        tab = self._page_tab_(c.name, c.type)
        if tab not in pages:
            self.append_page(SourceView(remote, self.dialogs, name=tab), tab)
        else:
            pages[tab].reset_rows()
        self.set_current_page(tab)


    def _page_tab_(self, name, type):
        return '%s %s' % (name, type)

    def sources_command(self, menuitem, action):
        pages = dict(self.pages)
        if action == 'update release':
            c = self.current
            remote = RemoteRepository(self.conn, c.name, c.type)
            remote.update_release()
            pages[self._page_tab_(c.name, c.type)].reset_rows()
        else:
            dialogs.Message('nothing done')
        
    def release_command(self, menuitem, action):
        if action == 'add binary repos':
            type = 'deb'
        if action == 'update':
            dialogs.Message('need to update release')
            
        if action == 'drop':
            if self.current:
                self.repos.drop_source(self.current.name, self.current.type)
            self.reset_rows()
        else:
            print action

class RepositoryBrowserWindow(MenuWindow):
    def __init__(self, conn, name='RepositoryBrowserWindow'):
        MenuWindow.__init__(self, name=name)
        self.conn = conn
        self.browser = RepositoryBrowser(self.conn)
        self.vbox.add(self.browser)
        self.add_menu(['add', 'remove'], 'repository', self.repos_command)
        self.set_usize(600, 450)
        self.dialogs = {}.fromkeys(['add-source', 'add-repos'])

    def add_repository(self, button):
        action = button.get_name()
        if action == 'add-repos':
            name = self.dialogs[action]['name']
            if not good_word.match(name):
                dialogs.Message('bad name')
            else:
                d = self.dialogs['add-repos']
                line = ' '.join([d['type'], d['local'], d['suite']] + d['sections'].split())
                rline = ' '.join([d['type'], d['remote'], d['suite']] + d['sections'].split())
                #dialogs.Message('Source: %s, %s' %(d['name'], line))
                try:
                    self.browser.repos.add_source(d['name'], line)
                    self.browser.repos.add_source(d['name'], rline)
                except ExistsError:
                    dialogs.Message('%s already exists' % line)
                self.browser.reset_rows()
                
    def drop_source(self, listbox, context, x, y, selection, targettype, time):
        source = selection.data
        self.dialogs['add']['source'] = source

    def drop_repos(self, listbox, context, x, y, selection, targettype, time):
        name, type = selection.data.split('^&^')
        self.dialogs['add-repos']['name'] = name
        self.dialogs['add-repos']['type'] = type
        source = self.browser.repos.make_source(name, type)
        remote = self.browser.repos.get_remote(name, type)
        self.dialogs['add-repos']['local'] = source.uri
        self.dialogs['add-repos']['sections'] = ' '.join(source.sections)
        self.dialogs['add-repos']['suite'] = source.suite
        self.dialogs['add-repos']['remote'] = remote.uri
        
    def repos_command(self, menuitem, action):
        if action == 'add':
            dkey = 'add-repos'
            if not self.dialogs[dkey]:
                msg = 'enter a new repository'
                data = dict(name='', local='',
                            type='deb',
                            suite='woody',
                            sections='main contrib non-free',
                            remote='http://ftp.us.debian.org/debian')
                self.dialogs[dkey] = dialogs.RecordEntry(msg, data, name=dkey)
                self.dialogs[dkey].set_ok(self.add_repository)
                self.dialogs[dkey].set_usize(400, 200)
                self.dialogs[dkey].add_button('browse', self._select_a_directory, 'browse')
                self.dialogs[dkey].add_button('type', self._toggle_type_, 'type')
                set_receive_targets(self.dialogs[dkey], self.drop_repos,
                                    [repos_target])
            self.dialogs[dkey].set_cancel(self.destroy_dialog)
        print action

    def _toggle_type_(self, button):
        dialog = self.dialogs['add-repos']
        if dialog['type'] == 'deb':
            dialog['type'] = 'deb-src'
        elif dialog['type'] == 'deb-src':
            dialog['type'] = 'deb'
        else:
            badtype = dialog['type']
            dialog['type'] = 'deb'
            dialogs.Message('bad type %s' %badtype)

    def _select_a_directory(self, button):
        print button, button.get_name()
        filesel = FileSelection(title='_select_a_directory')
        filesel.cancel_button.connect('destroy',
                                      lambda x : filesel.destroy())
        filesel.show()
        filesel.ok_button.connect('clicked', self.ok_directory, filesel)
        

    def ok_directory(self, button, filesel):
        action = filesel.get_data('action')
        directory = dirname(filesel.get_filename())
        filesel.destroy()
        uri = 'file:%s' % directory
        print uri, action
        self.dialogs['add-repos']['local'] = uri


if __name__ == '__main__':
    conn = RepositoryConnection()
    win = RepositoryBrowserWindow(conn)
    win.connect('destroy', mainquit)
    m = win.browser.repos.main
    mainloop()
    

    
if False:
    import CORBA
    
    
    CORBA._load_idl(join(cfg['local_idl_path'], 'repos.idl'))
    from _GlobalIDL import Repos
    
    orb = CORBA.ORB_init()
    
    ior = file('ior').readline()
    
    o = orb.string_to_object(ior)
    #o.init('deb file:/mirrors/debian sid main contrib non-free')
    #o.update()
    #o.parse()


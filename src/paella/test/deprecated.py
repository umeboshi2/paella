
from paella.gtk.base import right_click_pressed
from paella.gtk.dialogs import Dialog, CList, ScrollVBox, TextDialog
from paella.gtk.simple import ItemLabel
from paella.gtk.simple import SimpleMenu, BetterMenu
from paella.gtk.listboxes import ScrollCList



class ConfigBrowser(CList):
    def __init__(self, config):
        CList.__init__(self, 'packages')
        self.config = config
        self.set_right_click(self._show_menu)
        self.set_rows(self.config.filelist.keys(), 'Packages')
        self.menu = SimpleMenu()
        self.menu.add('conffiles', self.__hello__)
        self.menu.add_separator()
        self.menu.add('md5sums', self.__hello__)
        self.menu.add('filelist', self.__hello__)
        
        
    def __hello__(self, *args):
        print args
        print '__hello__'
        data = self.listbox.get_selected_data()[0][0]
        print data
        choice = args[1]
        if choice == 'filelist':
            PackageListWindow(self.config.filelist[data], data)
        elif choice == 'conffiles':
            if self.config.conffiles.has_key(data):
                PackageListWindow(self.config.conffiles[data], data)
            else:
                TextDialog('sorry, no connfiles for %s' %data, 'hello there')
        elif choice == 'md5sums':
            if self.config.md5sums.has_key(data):
                Md5Window(self.config, data)
            else:
                TextDialog('sorry, no md5sums for %s' %data, 'hello there')
                

    def _show_menu(self, *args):
        clist, event = args
        print event
        print dir(event)
        e = event
        if right_click_pressed(event):
            if len(self.listbox.get_selected_data()):
                self.menu.popup(None, None, None, e.button, e.time)
        

class PackageListWindow(CList):
    def __init__(self, filelist, package):
        CList.__init__(self, package)
        self.set_rows(filelist, ['file'])

class Md5Window(ScrollVBox):
    def __init__(self, config, package):
        ScrollVBox.__init__(self, package)
        self.config = config
        for k,v in self.config.md5sums[package].items():
            self.mbox.add(ItemLabel((v,k)))
        self.set_usize(400,200)
        
def new_function(foo):
    print 'hello there'

    for i in range(200):
        print 'new_function'
        
class ReposMirror(object):
    def __init__(self, path, suite='sid', arch='i386', sections=SECTIONS,
                 mirror=MAIN_REPOS, sources=True):
        object.__init__(self)
        self.path = path
        self.arch = arch
        self.mirror = mirror
        self.sources = sources
        self.change_suite(suite, sections=sections)
                
    def _make_distpath_(self):
        makepaths(self.distpath)
        for section in self.sections:
            binpath = pjoin(self.distpath, section, _binpath(self.arch))
            srcpath = pjoin(self.distpath, section, SRCPATH)
            makepaths(binpath, srcpath)
    

    def change_suite(self, suite, sections=SECTIONS):
        self.suite = suite
        self.sections = sections
        self.distpath = pjoin(self.path, DISTS, self.suite)
        self.rdistpath = pjoin(self.mirror, DISTS, self.suite)
        if not isdir(self.distpath):
            self._make_distpath_()
            self.update_release()
        self._parse_release_()
    
    def update_release(self):
        lpath_real = pjoin(self.distpath, 'Release')
        lpath = tempfile.mktemp()
        makepaths(lpath)
        url = pjoin(self.mirror, DISTS, self.suite, 'Release')
        pnew = pjoin(lpath, 'Release')
        print url, '->', pnew
        wget(url, pnew)
        if isfile(lpath_real):
            mreal = md5sum(lpath_real)
        else:
            mreal = 'missing'
        mnew = md5sum(pnew)
        if mreal != mnew:
            os.system('mv %s %s' %(pnew, lpath_real))
        else:
            print 'release a-ok'
        self._parse_release_()
        
    def _listfile(self, src=False, release=False):
        if src and not release:
            return dotjoin('Sources', zip[self.suite])
        elif release:
            return 'Release'
        else:
            return dotjoin('Packages', zip[self.suite])

    def _listpath(self, section, src=False, distpath=False, release=False):
        if distpath == False:
            distpath = self.distpath
        if src:
            midpath = SRCPATH
        else:
            midpath = _binpath(self.arch)
        return pjoin(distpath, section, midpath, self._listfile(src=src, release=release))
        
    def _parse_release_(self):
        release_file = pjoin(self.distpath, 'Release')
        if not isfile(release_file):
            self.update_release()
        self.release = email.message_from_string(readfile(release_file))
        self.release_sums = parse_release_md5sums(self.release['md5sum'],
                                                  sources=self.sources)

    def _checkandget_(self, rpath, lpath, path):
        if not isfile(lpath):
            get_file(rpath, lpath)
        elif md5sum(lpath) != self.release_sums[path].md5sum:
            print 'not current'
            get_file(rpath, lpath, result='corrupt')
        else:
            print path, 'a-ok'
        
        

    def check_release(self, section, src=False, release=True):
        lpath = self._listpath(section, src=src, release=release)
        rpath = self._listpath(section, src=src,
                               distpath=self.rdistpath, release=release)
        path = self._listpath(section, src=src, distpath='', release=release)
        self._checkandget_(rpath, lpath, path)

    def _check_package_list(self, section, src=False):
        self.check_release(section, src=src)
        lpath = self._listpath(section, src=src)
        rpath = self._listpath(section, src=src, distpath=self.rdistpath)
        path = self._listpath(section, src=src, distpath='')
        self._checkandget_(rpath, lpath, path)
        
    def check_lists(self, src=False):
        for section in self.sections:
            self._check_package_list(section, src=src)

    def check_packages(self, section, quick=False):
        list_file = self._listpath(section)
        parsed = parse_packages(list_file)
        for package in parsed:
            path, md5 = parsed[package]
            lpath = pjoin(self.path, path)
            rpath = pjoin(self.mirror, path)
            check_and_get_file(rpath, lpath, md5, quick)

    def check_sources(self, section, quick=False):
        list_file = self._listpath(section, src=True)
        parsed = parse_sources(list_file)
        for package in parsed:
            dir, sfiles = parsed[package]
            ldir = pjoin(self.path, dir)
            rdir = pjoin(self.mirror, dir)
            makepaths(ldir)
            srcs = {}
            for source in sfiles:
                lpath = pjoin(ldir, source.name)
                rpath = pjoin(rdir, source.name)
                check_and_get_file(rpath, lpath, source.md5sum, quick)

    def check_all(self, ptype='both', quick=False):
        if ptype in ['bin', 'both']:
            for section in self.sections:
                self.check_packages(section, quick=quick)
        if ptype in ['src', 'both']:
            for section in self.sections:
                self.check_sources(section, quick=quick)

    def parse(self, section, src=False):
        list_file = self._listpath(section, src=src)
        return full_parse(list_file)

    def sync_current(self, suites):
        for suite in suites:
            self.change_suite(suite)
            



def backup_repos(remote, suites, path):
    repos = ReposMirror(path, mirror=remote)
    for suite in suites:
        repos.change_suite(suite)
        repos.update_release()
        repos.check_lists(src=False)
        repos.check_lists(src=True)
        repos.check_all('both')



def _update_sid(path='/mirrors/debian', mirror=RMIRROR):
    rp = ReposMirror(path)
    rp.update_release()
    rp.check_lists()
    rp.check_lists(1)
    zip['sid'] = 'gz'
    rp.check_lists()
    rp.check_lists(1)
    zip['sid'] = 'bz2'
    return rp

def update_sid(path='/mirrors/debian', mirror=RMIRROR):
    rp = _update_sid(path=path, mirror=mirror)
    rp.check_all('both', quick=True)

def check_sid(path='/mirrors/debian', mirror=RMIRROR):
    rp = _update_sid(path=path, mirror=mirror)
    rp.check_all('both', quick=False)




class TraitBrowser_orig(ListNoteBook):
    def __init__(self, conn, suite):
        ListNoteBook.__init__(self)
        self.cfg = Global()
        self.cfg.section = 'paella-admin'           
        self.suite = suite
        self.menu = make_menu(['install', 'remove', 'purge', 'drop', 'edit'],
                              self.set_package)
        self.pmenu = make_menu(['drop'], self.set_parent)
        self.conn = conn
        self.cmd = StatementCursor(conn, name='TraitBrowser')
        self.__set_cursors__()
        self.reset_rows()
        self.append_page(ScrollCList(rcmenu=self.menu), 'packages')
        self.append_page(ScrollCList(rcmenu=self.pmenu), 'parents')
        self.set_usize(400, 300)

    def __set_cursors__(self):
        self.traits = StatementCursor(self.conn, name='traits')
        self.traits.set_table(ujoin(self.suite, 'traits'))
        self.traits.set_fields(['trait'])
        self.traitpackage = TraitPackage(self.conn, self.suite)
        self.traitparent = TraitParent(self.conn, self.suite)
        self.packages = TableDict(self.conn, ujoin(self.suite, 'packages'),
                                  'package', 'filename')
        
    def __close_cursors__(self):
        self.traits.close()
        self.traitpackage.close()
        self.traitparent.close()

    def reset_rows(self):
        self.set_rows(self.traits.select(fields=['trait']))
        self.set_row_select(self.trait_selected)
        
    def __make_menu__(self):
        self.menu = SimpleMenu()
        for option in []:
            self.menu.add(option, self.set_package)
    
    def __set_droptargets__(self, pages):
        set_receive_targets(pages['packages'].listbox,
                            self.drop_package, TARGETS.get('package', self.suite))
        set_receive_targets(pages['parents'].listbox,
                            self.drop_trait, TARGETS.get('trait', self.suite))

    def set_parent(self, menu_item, data):
        pages = dict(self.pages)
        parents = [x.parent for x in pages['parents'].listbox.get_selected_data()]
        print parents
        
    def set_package(self, menu_item, data):
        print 'menu connected'
        pages = dict(self.pages)
        packages = [x.package for x in pages['packages'].listbox.get_selected_data()]
        trait = self.current_trait
        if data != 'edit':
            self.traitpackage.set_action(data, packages)
        else:
            print 'have to sync repos object and get files'
            print data, packages
            self._extract_packages(packages)
        self.__set_pages(self.current_trait)

    def _extract_packages(self, packages):
        raise Error, 'DEPRECATED'
        tmp = join(self.cfg['tmp_extract_path'], self.suite, self.current_trait)
        makepaths(tmp)
        os.system('rm %s/* -fr' %tmp)
        for package in packages:
            tmp_path = join(tmp, package)
            makepaths(tmp_path)
            archive = join(self.cfg['local_mirror'],
                           self.packages[package])
            extdeb = 'dpkg-deb -x %s %s' % (archive, tmp_path)
            print extdeb
            os.system(extdeb)
        cg = ConfigGen(self.conn, self.suite, self.current_trait, tmp)
        cg.ask_file_dialog(None, 'open')
        
    def pop_mymenu(self, widget, event, menu):
        print 'menu popper'
        if right_click_pressed(event):
            menu.popup(None, None, None, event.button, event.time)
    
    def trait_selected(self, listbox, row, column, event):
        trait = listbox.get_selected_data()[0].trait
        self.current_trait = trait
        self.__set_pages(self.current_trait)

    def __set_pages(self, trait):
        pages = dict(self.pages)
        #set packages for trait
        self.traitpackage.set_trait(trait)
        pages['packages'].set_rows(self.traitpackage.packages())
        pages['packages'].set_select_mode('multi')
        #set parents for trait
        self.traitparent.set_trait(trait)
        pages['parents'].set_rows(self.traitparent.parents())
        pages['parents'].set_select_mode('multi')
        self.__set_droptargets__(pages)

    def change_suite(self, widget, suite):
        self.suite = suite
        self.traits.clear(clause=True)
        self.set_rows(self.traits.select())
        self.set_row_select(self.trait_selected)

    def __drop_something__(self, items, cursor, field):
        current_items = [x[field] for x in cursor.select()]
        diff_items = [i for i in items if i not in current_items]
        insert_data = {'trait' : self.current_trait,
                       field : None}
        for item in diff_items:
            insert_data[field] = item
            cursor.set_data(insert_data)
            cursor.insert()
        debug('%s dropped' %field, current_items, diff_items)
        self.__set_pages(self.current_trait)

    def drop_package(self, *args):
        listbox, context, x, y, selection, targettype, time = args
        packages = Set(selection.data.split('^&^'))
        self.traitpackage.insert_packages(packages)
        self.__set_pages(self.current_trait)


    def drop_trait(self, *args):
        listbox, context, x, y, selection, targettype, time = args
        traits = selection.data.split('^&^')
        self.traitparent.insert_parents(traits)
        self.__set_pages(self.current_trait)




class _LocalShelf_(object):
    def __init__(self, dbpath):
        object.__init__(self)
        self._dbpath = dbpath
        self._db = None

    def open(self):
        if not isfile(self._dbpath):
            self._db = shelve.open(self._dbpath)
            self.__init_new_db__()
        else:
            self._db = shelve.open(self._dbpath)

    def close(self):
        if self._db is None:
            raise Error, 'no db to close'
        self._db.close()
        self._db = None

    def __init_new_db__(self):
        self._db['__mainkeys__'] = {}.fromkeys(['local', 'remote', 'sections'])
        for key in self._db['__mainkeys__']:
            self._db['__mainkey__%s' % key] = []

    def insert_local_source(self, name, source):
        local_names = self._db['__mainkey__local']
        if name in local_names:
            raise Error, '%s already in db'
        self._db[ujoin('local', name)] = source
        local_names.append(name)
        self._db['__mainkey__local'] = local_names
        
    def insert_local_section(self, name, section, data):
        prekey = ujoin('sections', name, section)
        for package in data:
            self._db[ujoin(prekey, package)] = data[package]
        
    def insert_remote_source(self, name, source):
        self._db[ujoin('remote', name)] = source

    def get_local_source(self, name):
        return self._db[ujoin('local', name)]

    def get_package(self, name, section, package):
        return self._db[ujoin('sections', name, section, package)]

    def names(self):
        return self._db['__mainkey__local']

class RepositoryDatabase(SuperShelf):
    def __init__(self, dbpath, flag='w'):
        SuperShelf.__init__(self, dbpath, self.__init_new_repos__, flag=flag)

    def __init_new_repos__(self):
        self.__init_new_db__()
        self.insert_field('name')
        self.insert_field('section')
        self.insert_field('package')
        self.insert_field('type')
        self.insert_field('source')
        self.insert_order('source', ['source', 'name', 'type'])
        self.insert_order('package', ['name', 'section', 'type', 'package'])
        
    def add_source(self, name, source):
        source = make_source(source)
        if islocaluri(source.uri):
            self.insert_item('source', ['local', name, source.type], str(source))
        else:
            self.insert_item('source', ['remote', name, source.type], str(source))

    def insert_package(self, name, section, type, package, data):
        self.insert_item('package', [name, section, type, package], data)


    def __repr__(self):
        keys = [k for k in self.keys() if k[:6] == 'local_']
        sources = [self[key] for key in keys]
        return '\n'.join(sources) + '\n'
        
    def names(self):
        return self.fieldkeys('name')

class Repository(object):
    def __init__(self, conn, arch='i386'):
        object.__init__(self)
        self.conn = conn
        self.arch = arch
        self.current = None
        self.release = None
        
    def set_source(self, name, type='deb'):
        self.name = name
        self.current = make_source(self.conn[ujoin('local', self.name, type)])
        
    def parse_release(self):
        if self.current.has_release():
            self.release = Release(self.current, arch=self.arch)

    def _parse_section_(self, section=None):
        listfile = self._listfile_(section)
        debug(listfile)
        if not isfile(listfile):
            raise NoFileError, 'file not there'
        if self.current.type == 'deb':
            return parse_packages(listfile)
        elif self.current.type == 'deb-src':
            return parse_sources(listfile)
        else:
            raise Error, 'bad source type'

    def update_section(self, section=None):
        parsed = self._parse_section_(section)
        for package, data in parsed.items():
            self.conn.insert_package(self.name, section, self.current.type, package, data)
    
        

    def _listfile_(self, section=None):
        if self.current.has_release():
            return join(self.current.distpath, self.release.path(section))
        else:
            return join(self.current.distpath, self.current.listfile())


class ReposBrowser_OLD(ListAboveNoteBook):
    def __init__(self, conn, name='ReposBrowser'):
        self.menu = self.__make_mainmenu_()
        ListAboveNoteBook.__init__(self, name=name)
        self._targets_ = [source_target]
        self._dnd = self.drag_rows
        self.set_usize(300, 200)
        self.conn = conn
        self.current = None
        self.repos = RepositoryManager(self.conn)
        self.release_menu = make_menu(['update'], self.release_command)
        self.append_page(ScrollCList(rcmenu=self.release_menu), 'release')
        self.reset_rows()
        
    def __make_mainmenu_(self):
        commands = ['drop', 'edit', 'add', 'remote']
        return make_menu(commands, self.main_command)

    def __set_pages(self):
        pages = dict(self.pages)
        pages['release'].set_rows(self.local.release.select())

    def reset_rows(self):
        self.set_rows(self.repos.sources.select())
        self.set_row_select(self.source_selected)

    def source_selected(self, listbox, row, column, event):
        self.current = listbox.get_selected_data()[0]
        self.local = LocalRepository(self.conn, self.current.name, self.current.type)
        print self.local.current
        self.__set_pages()

    def main_command(self, menuitem, action):
        if action == 'drop':
            if self.current:
                self.repos.drop_source(self.current.name, self.current.type)
            self.reset_rows()
        else:
            print action

    def release_command(self, menuitem, action):
        if action == 'update':
            self.local.update_release_file()
            self.__set_pages()
        
    def drag_rows(self, listbox, context, selection, targettype, time):
        row = listbox.get_selected_data()[0]
        source = self.repos.make_source_line(row.name, row.type)
        selection.set(selection.target, 0, source)
        


class ReposBrowserWindow(CommandBoxWindow, HasMenuDialog):
    def __init__(self, conn, name='ReposBrowserWindow'):
        CommandBoxWindow.__init__(self, name=name)
        self.conn = conn
        self.browser = RepositoryBrowser(self.conn)
        self.vbox.add(self.browser)
        self.tbar.add_button('add', 'add source', self.ask_add_source)
        self.set_usize(300, 200)
        self.dialogs = {}.fromkeys(['add'])
        
        
    def ask_add_source(self, button, data):
        if not self.dialogs[data]:
            if data == 'add':
                record = {}.fromkeys(['name', 'source'], '')
                msg = 'enter a new source'
                self.dialogs[data] = dialogs.RecordEntry(msg, record, name=data)
                self.dialogs[data].set_ok(self.add_source)
                self.dialogs[data].set_usize(450, 150)
                set_receive_targets(self.dialogs[data], self.drop_source,
                                    [source_target])
                
            self.dialogs[data].set_cancel(self.destroy_dialog)
            
    def add_source(self, button):
        name = button.get_name()
        if name == 'add':
            source_line = self.dialogs[name]['source']
            src_name = self.dialogs[name]['name']
            if not src_name:
                raise Error, 'must have a name'
            self.browser.repos.add_source(src_name, source_line)
            print source_line
        self.browser.reset_rows()

    def drop_source(self, listbox, context, x, y, selection, targettype, time):
        source = selection.data
        self.dialogs['add']['source'] = source







#######
# from paella.installer.cfdisk

    
def _quick_partition(device, data):
    i, o = os.popen2('sfdisk %s' % device)
    i.write(data)
    i.close()
    

    

def _quick_mkfs(device, partitions):
    for part in partitions:
        os.system('mkreiserfs -f -q %s%d' % (device, part))

def _quick_mount(device, part, mntpt, target='/tmp/target'):
    if mntpt != '/':
        target = join(target, mntpt)
        print target
        makepaths(target)
    os.system('mount %s%d %s' % (device, part, target))

def mount_partitions(device, mntdata, target='/tmp/target'):
    _quick_mount(device, mntdata['/'], '/', target=target)
    del mntdata['/']
    for mntpt in mntdata:
        _quick_mount(device, mntdata[mntpt], mntpt, target=target)
        
def quick_and_dirty_normal(device, diskcfg, target):
    _quick_partition(device, diskcfg)
    _quick_mkfs(device, [1,5,6,7])
    mntdata = { '/' : 1,
                'usr' : 5,
                'var' : 6,
                'home' : 7}
    mount_partitions(device, mntdata, target=target)

def quick_and_dirty_freespace(device, diskcfg, target):
    _quick_partition(device, diskcfg)
    _quick_mkfs(device, [1,5,6,7,8])
    mntdata = { '/' : 1,
                'usr' : 5,
                'var' : 6,
                'home' : 7,
                'freespace' : 8}
    mount_partitions(device, mntdata, target=target)



import os, sys
from os.path import join, dirname
from ConfigParser import RawConfigParser

from useless.gtk import dialogs
from useless.gtk.middle import ScrollCList, CommandBox
from useless.gtk.windows import MenuWindow, CommandBoxWindow

from gtk import FileSelection
from gtk import mainloop, mainquit

from useless.base import Error, debug
from useless.db.midlevel import StatementCursor

from paella.base import PaellaConfig
from paella.db import PaellaConnection
from paella.db import DefaultEnvironment
from paella.db.main import PaellaDatabase
from paella.db.machine.xmlgen import MachineDatabaseElement
from paella.db.machine import MachineHandler


from profilegen import ProfileGenWin
from traitgen import TraitGenWin
from template import TemplateManager
from environ import EnvironmentEditorWin
from scriptomatic import ScriptManager
from trait_manager import TraitManagerWin
from machines import MainMachineWin
from database import DatabaseManager, ClientManager
from families import FamilyWin
from differ import DifferWin

dbcommands = ['connect', 'disconnect', 'restore', 'backup']


class SuiteManager(CommandBoxWindow):
    def __init__(self, conn, suite, cfg=None, name='SuiteManager'):
        if cfg is None:
            cfg = PaellaConfig()
        CommandBoxWindow.__init__(self, name=name)
        self.set_title('%s toolbar' % suite)
        self.cfg = cfg
        self.conn = conn
        self.suite = suite
        self.tbar.add_button('traits', 'trait manager', self.traitgen)
        self.tbar.add_button('templates', 'template manager', self.templates)
        self.tbar.add_button('environ', 'environment manager', self.environ)
        #self.tbar.add_button('debconf', 'debconf manager', self.debconf)
        self.tbar.add_button('scripts', 'script manager', self.scripts)
        
    def traitgen(self, button=None, data=None):
        wname = '.'.join([self.suite, 'traits'])
        TraitGenWin(self.conn, self.suite, name=wname)

    def templates(self, button=None, data=None):
        wname = '.'.join([self.suite, 'templates'])
        TemplateManager(self.conn, self.suite)

    def environ(self, button=None, data=None):
        wname = '.'.join([self.suite, 'environment'])
        EnvironmentEditorWin(self.conn, self.suite, name=wname)

    def debconf(self, button=None, data=None):
        wname = '.'.join([self.suite, 'debconf'])
        DebconfBrowser(self.conn, self.suite, name=wname)

    def scripts(self, button=None, data=None):
        wname = '.'.join([self.suite, 'scripts'])
        ScriptManager(self.conn, self.suite, name=wname)


class DefEnvEditor(CommandBoxWindow):
    def __init__(self, conn):
        CommandBoxWindow.__init__(self)
        self.conn = conn
        self.defenv = DefaultEnvironment(self.conn)
        self.add_menu(['load', 'edit', 'save'], 'main', self.main_menu_selected)
        self.cursor = StatementCursor(self.conn)
        self.cursor.set_table('default_environment')
        self.view = ScrollCList()
        self.vbox.add(self.view)
        self.reset_rows()
        
    def reset_rows(self):
        self.view.set_rows(self.cursor.select(order=['section', 'option']))

    def main_menu_selected(self, menuitem, name):
        if name == 'edit':
            newcfg = self.defenv.edit()
            self._update_dfenv(newcfg)
        elif name in ['load', 'save']:
            filesel = FileSelection(title='%s Default Environment' % name)
            filesel.cancel_button.connect('clicked',
                                          lambda x: filesel.destroy())
            filesel.show()
            filesel.ok_button.connect('clicked', self.ok_filesel, filesel)
            filesel.set_data('action', name)

    def ok_filesel(self, button, filesel):
        path = filesel.get_filename()
        action = filesel.get_data('action')
        filesel.destroy()
        if action == 'save':
            self.defenv.write(file(path, 'w'))
        elif action == 'load':
            newcfg = RawConfigParser()
            newcfg.read(path)
            self._update_dfenv(newcfg)

    def _update_dfenv(self, newcfg):
            self.defenv.update(newcfg)
            self.defenv = DefaultEnvironment(self.conn)
            self.reset_rows()
            
class Manager(CommandBoxWindow):
    def __init__(self, name='Manager'):
        CommandBoxWindow.__init__(self)
        self.cfg = PaellaConfig('database')
        self.dialogs = {}.fromkeys(['dbname', 'suitemanager'])
        apps = ['profiles', 'families', 'suitemanager', 'traitmanager', 'machines',
                'traits', 'tdiff', 'sdiff', 'fdiff', 'default_environment', 'clients',
                'browser']
        self.workspace = {}.fromkeys(apps)
        self.add_menu(dbcommands, 'database', self.database_command)
        self.add_menu(self.workspace.keys(), 'edit', self.edit_command)
        self.set_size_request(150,200)
        self.conn = None
        self.dbname = None
        self.dblist = ScrollCList()
        self.vbox.add(self.dblist)
        conn = PaellaConnection(self.cfg)
        cursor = StatementCursor(conn, 'quicky')
        self.dblist.set_rows(cursor.select(table='pg_database'))
        cursor.close()
        conn.close()
        self.tbar.add_button('profiles', 'profile manager', self.run_tbar)
        self.tbar.add_button('families', 'family manager', self.run_tbar)
        self.tbar.add_button('machines', 'machine manager', self.run_tbar)
        self.tbar.add_button('traits', 'trait manager', self.run_tbar)
        self.tbar.add_button('tdiff', 'template differ', self.run_tbar)
        self.tbar.add_button('sdiff', 'script differ', self.run_tbar)
        self.tbar.add_button('fdiff', 'family differ', self.run_tbar)
        
    def edit_command(self, menuitem, name):
        if self.conn is None:
            dialogs.Message('Not Connected')
        else:
            if name == 'profiles':
                self.workspace['profiles'] = ProfileGenWin(self.conn, self.dbname)
            elif name in ['suitemanager']:
                if not self.dialogs[name]:
                    msg = 'select a suite'
                    self.dialogs[name] = dialogs.CList(msg, name=name)
                    lbox = self.dialogs[name]
                    lbox.set_rows(self.main.select(table='suites'))
                    lbox.set_ok(self.suite_selected)
                    lbox.set_cancel(self.destroy_dialog)
            else: self.run_tbar(None, name)
            

    def run_tbar(self, button=None, data=None):
        if data == 'profiles':
            self.workspace[data] = ProfileGenWin(self.conn, self.dbname)
        elif data == 'machines':
            self.workspace[data] = MainMachineWin(self.conn)
        elif data == 'traits':
            self.workspace[data] = TraitManagerWin(self.conn)
        elif data == 'families':
            self.workspace[data] = FamilyWin(self.conn)
        elif data == 'tdiff':
            self.workspace[data] = DifferWin(self.conn, 'template')
        elif data == 'sdiff':
            self.workspace[data] = DifferWin(self.conn, 'script')
        elif data == 'fdiff':
            self.workspace[data] = DifferWin(self.conn, 'family')
        elif data == 'default_environment':
            self.workspace[data] = DefEnvEditor(self.conn)
        elif data == 'clients':
            self.workspace[data] = ClientManager(self.conn)
        elif data == 'browser':
            self.workspace[data] = 'working'
            print data
            os.spawnlpe(os.P_NOWAIT, '/home/umeboshi/bin/paella-kde-management',
                        '--display :0', os.environ)
            print data, 'running'
        else:
            dialogs.Message('bad command %s' % data)
        
    def database_command(self, menuitem, name):
        if name == 'connect':
            if self.conn is None and not self.dialogs['dbname']:
                msg = 'connect to which database?'
                dbname = self.dblist.get_selected_data()[0].datname
                self.dialogs['dbname']  = dialogs.Entry(msg, name='dbname')
                entry = self.dialogs['dbname']
                entry.set_ok(self.ok_dialog)
                entry.set_cancel(self.destroy_dialog)
                entry.set(dbname)
            else:
                dialogs.Message('no multiple connections yet')
        elif name == 'disconnect':
            if self.conn is not None:
                self.main.close()
                self.conn.close()
                self.conn = None
                self.dbname = None
            else:
                dialogs.Message('no connection to leave')
        elif name in ['backup', 'restore']:
            filesel = FileSelection(title='%s database' %name)
            filesel.cancel_button.connect('clicked',
                                          lambda x: filesel.destroy())
            filesel.show()
            bkup_path = self.cfg['import_path']
            filesel.set_filename(self._filepath_(bkup_path))
            filesel.ok_button.connect('clicked', self.ok_file, filesel)
            filesel.set_data('action', name)
        else:
            dialogs.Message('%s unimplemented'%name)

    def ok_file(self, button, filesel):
        path = filesel.get_filename()
        mdpath = join(dirname(path), 'machine_database.xml')
        action = filesel.get_data('action')
        filesel.destroy()
        dir = dirname(path)
        dbm = DatabaseManager(self.conn)
        if action == 'backup':
            dbm.backup(dir)
        elif action == 'restore':
            dbm.restore(dir)
            
    def suite_selected(self, button):
        name = button.get_name()
        row = self.dialogs[name].get_selected_data()[0]
        debug(row.suite)
        self.destroy_dialog(self.dialogs[name])
        SuiteManager(self.conn, row.suite)
        
        
    def _filepath_(self, path):
        return join(path, self.dbname + '.xml')
    
    def ok_dialog(self, button):
        name = button.get_name()
        if name == 'dbname':
            dbname = self.dialogs[name].get()
            self.dbconnect(dbname)
        self.destroy_dialog(self.dialogs[name])
        
    def dbconnect(self, dbname):
        self.cfg.change('database')
        dsn = self.cfg.get_dsn()
        dsn['dbname'] = dbname
        self.conn = PaellaConnection(dsn)
        self.main = StatementCursor(self.conn, 'mainManager')
        self.dbname = dbname
        dialogs.Message('connected to database %s' %dbname)

        
    def destroy_dialog(self, dying):
        name = dying.get_name()
        self.dialogs[name] = None
        dying.destroy()
        


if __name__ == '__main__':
    win = Manager()
    win.connect('destroy', mainquit)
    
    mainloop()
    
        

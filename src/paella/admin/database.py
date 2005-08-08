import os, sys
from os.path import join, dirname

from useless.base import Error, debug
from useless.base.config import Configuration
from useless.base.util import makepaths

from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq, In
from useless.gtk.middle import ListTextView, ScrollCList
from useless.gtk.windows import CommandBoxWindow
from useless.gtk import dialogs


from paella.db import PaellaConfig, PaellaConnection, DefaultEnvironment
from paella.db.main import PaellaDatabase, PaellaProcessor
from paella.db.profile.xmlgen import PaellaProfiles
from paella.db.family import Family
from paella.db.machine import MachineHandler

#from paella.machines.xmlgen import ClientMachineDatabaseElement
#from paella.machines.xmlgen import MachineDatabaseElement
from paella.db.machine.xmlgen import MachineDatabaseElement
#from paella.machines.machine import MachineHandler

class DatabaseManager(object):
    def __init__(self, conn):
        object.__init__(self)
        self.cfg = PaellaConfig()
        self.conn = conn
        self.import_dir = self.cfg.get('database', 'import_path')
        self.export_dir = self.cfg.get('database', 'export_path')

    def backup(self, path):
        if not os.path.isdir(path):
            raise Error, 'arguement needs to be a directory'
        pdb = PaellaDatabase(self.conn, path)
        pdb.backup(path)
        mdbpath = join(path, 'machine_database.xml')
        #me = MachineDatabaseElement(self.conn)
        #mdfile = file(mdbpath, 'w')
        #mdfile.write(me.toprettyxml())
        #mdfile.close()
        #me.export_machine_database(path)
        mh = MachineHandler(self.conn)
        mh.export_machine_database(path)
    def restore(self, path):
        if not os.path.isdir(path):
            raise Error, 'arguement needs to be a directory'
        dbpath = join(path, 'database.xml')
        mdbpath = join(path, 'machine_database.xml')
        pp = PaellaProcessor(self.conn, self.cfg)
        pp.create(dbpath)
        mh = MachineHandler(self.conn)
        #md = mh.parse_xmlfile(mdbpath)
        mh.restore_machine_database(path)
        
class TextFileBrowser(ListTextView):
    def __init__(self, conn, name='TextFileBrowser'):
        ListTextView.__init__(self, name=name)
        self.conn = conn
        self.cursor = StatementCursor(self.conn)
        self.cursor.set_table('textfiles')

    def reset_rows(self):
        self.set_rows(self.cursor.select(fields=['fileid']))
        self.set_row_select(self.fileid_selected)

    def fileid_selected(self, listbox, row, column, event):
        pass
    

class ClientManager(CommandBoxWindow):
    def __init__(self, conn, name='ClientManager'):
        CommandBoxWindow.__init__(self)
        self.set_title('Client Manager')
        self.conn = conn
        self.cfg = PaellaConfig()
        client_cmds = ['import', 'export', 'remove']
        self.add_menu(client_cmds, 'client', self.menu_command)
        self.client_view = ScrollCList()
        self.vbox.add(self.client_view)
        self.client_path = self.cfg.get('management_gui', 'client_path')
        self.client_cfg = Configuration(files=[os.path.join(self.client_path, 'config')])
        self.clients = self.client_cfg.sections()
        self.client_view.set_rows(self.clients, ['client'])
        self.dialogs = {}.fromkeys(client_cmds)
        
    def menu_command(self, menuitem, name):
        client = self.client_view.get_selected_data()[0][0]
        if name == 'export':
            self.export_client(client)
        elif name == 'import':
            self.import_client(client)
        elif name == 'remove':
            self.remove_client(client)
        else:
            dialogs.Message('%s %s' % (name, client))
            
    def _cpaths_(self, client):
        cpath = os.path.join(self.client_path, client)
        ppath = os.path.join(cpath, 'profiles')
        fpath = os.path.join(cpath, 'families')
        tpath = os.path.join(cpath, 'traits')
        return [cpath, ppath, fpath, tpath]

    def _client_schema(self, client):
        profiles = self.client_cfg.get_list('profiles', client)
        families = self.client_cfg.get_list('families', client)
        traits = self.client_cfg.get_list('traits', client)
        return [profiles, families, traits]
    
    def _client_mdata(self, client):
        disks = self.client_cfg.get_list('disks', client)
        mtypes = self.client_cfg.get_list('machine_types', client)
        machines = self.client_cfg.get_list('machines', client)
        return [disks, mtypes, machines]
    
    def export_client(self, client):
        cpath, ppath, fpath, tpath = self._cpaths_(client)
        makepaths(cpath)
        profiles, families, traits = self._client_schema(client) 
        disks, mtypes, machines = self._client_mdata(client)
        if not disks:
            disks = None
        if not mtypes:
            mtypes = None
        if not machines:
            machines = None
        element = ClientMachineDatabaseElement(self.conn, disks, mtypes, machines)
        mdbpath = join(cpath, 'machine_database.xml')
        mdfile = file(mdbpath, 'w')
        mdfile.write(element.toprettyxml())
        mdfile.close()
        if profiles:
            makepaths(ppath)
            pp = PaellaProfiles(self.conn)
            for profile in profiles:
                pp.write_profile(profile, ppath)
        if families:
            makepaths(fpath)
            f = Family(self.conn)
            for family in families:
                f.write_family(family, fpath)
        if traits:
            makepaths(tpath)

    def import_client(self, client):
        cpath, ppath, fpath, tpath = self._cpaths_(client)
        profiles, families, traits = self._client_schema(client)
        mdbpath = join(cpath, 'machine_database.xml')
        if families:
            f = Family(self.conn)
            f.import_families(fpath)
        if profiles:
            pp = PaellaProcessor(self.conn, self.cfg)
            pp.main_path = cpath
            pp.insert_profiles()
        mh = MachineHandler(self.conn)
        md = mh.parse_xmlfile(mdbpath)
        mh.insert_parsed_element(md)    
        
            
    def remove_client(self, client):
        profiles, families, traits = self._client_schema(client)
        disks, mtypes, machines = self._client_mdata(client)
        cursor = StatementCursor(self.conn)
        if machines:
            cursor.delete(table='machines', clause=In('machine', machines))
        for mtype in mtypes:
            cursor.execute("select * from delete_mtype('%s')" % mtype)
        for disk in disks:
            cursor.execute("select * from delete_disk('%s')" % disk)
        for profile in profiles:
            cursor.execute("select * from delete_profile('%s')" % profile)
        for family in families:
            cursor.execute("select * from delete_family('%s')" % family)
            

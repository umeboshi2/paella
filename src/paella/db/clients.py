import os
from useless.base.config import Configuration
from useless.base.util import makepaths
from useless.db.midlevel import StatementCursor

from paella.db import PaellaConfig
from paella.db.family import Family
from paella.db.profile.xmlgen import PaellaProfiles
from paella.db.machine import MachineHandler
from paella.db.machine.xmlgen import ClientMachineDatabaseElement
from paella.db.main import PaellaProcessor



class ClientManager(object):
    def __init__(self, conn):
        self.conn = conn
        self.cfg = PaellaConfig()
        self.client_path = self.cfg.get('management_gui', 'client_path')
        self.client_cfg = Configuration(files=[os.path.join(self.client_path, 'config')])
        self.clients = self.client_cfg.sections()

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
            
        


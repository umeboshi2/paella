#import os
#from datetime import datetime, timedelta
#from zipfile import ZipFile
#from StringIO import StringIO
#import csv
#from io import BytesIO

import transaction
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc
from sqlalchemy import func

from paella.models.main import Machine, MacAddr
from paella.models.main import PartmanRecipe


# store keys in database.
# only database keys exists as files
# submit_machine generates keys that are stored in database
# set_install will make sure key is accepted by minion
# late command will send keypair to minion


class SaltKeyManager(object):
    def __init__(self, session):
        self.session = session

    def base_keyname(self, name, keytype='public'):
        print "basename of key"

    def keyname(self, name, keytype='public'):
        print "path/to/key"
        
    def generate_keypair(self, name):
        print "generate a key pair with this name"
        print "files are created"
        
    def check_key(self, name, keytype='public'):
        print "does this key exist"
        
    def does_keypair_exist(self, name):
        print "does this keypair exist"

    def get_public_key(self, name):
        print "get the public key, raise no exist error."
        print "return content"
        
    def get_private_key(self, name):
        print "get the private key, raise no exist error."
        print "return content"

    def get_keypair(self, name):
        print "get both keys for name"
        print "return dict(public=dict(name=name, content=content), private=)"


        
class PartmanRecipeManager(object):
    def __init__(self, session):
        self.session = session

    def _query(self):
        return self.session.query(PartmanRecipe)

    def get(self, id):
        return self._query().get(id)

    def add(self, name, content):
        with transaction.manager:
            pr = PartmanRecipe()
            pr.name = name
            pr.content = content
            self.session.add(pr)
        return self.session.merge(pr)

    def update(self, name, content):
        with transaction.manager:
            pr = self._query().filter_by(name=name).one()
            pr.content = content
            self.session.add(pr)
        return self.session.merge(pr)

    def list_recipes(self):
        return [r.name for r in self._query()]

    
        
class MachineAddressManager(object):
    def __init__(self, session):
        self.session = session

    def add_machine(self, name, uuid=None):
        with transaction.manager:
            m = Machine()
            m.name = name
            if uuid is not None:
                m.uuid = uuid
            self.session.add(m)
        return self.session.merge(m)

    def add_macaddr(self, address, machine_id):
        with transaction.manager:
            mc = MacAddr()
            mc.address = address
            mc.machine_id = machine_id
            self.session.add(mc)
        return self.session.merge(mc)

    def update_macaddr(self, address, machine_id):
        pass
    

    def get_machine_addresses(self, machine_id):
        q = self.session.query(MacAddr)
        q = q.filter_by(machine_id=machine_id)
        return q.all()

    def list_machine_addresses(self, name):
        m = self.session.query(Machine).filter_by(name=name).one()
        al = self.get_machine_addresses(m.id)
        return [a.address for a in al]
    

    def identify_machine_by_uuid(self, uuid, name=True):
        q = self.session.query(Machine)
        q = q.filter_by(uuid=uuid)
        machines = q.all()
        if len(machines) > 1:
            raise RuntimeError, "UUID should be unique"
        if not len(machines):
            name = None
        else:
            # this is ugly code, fix the api
            if name:
                name = machines[0].name
            else:
                name = machines[0]
        return name
        
        
    def identify_machine(self, address, name=True):
        q = self.session.query(MacAddr)
        q = q.filter_by(address=address)
        mc = q.one()
        m = self.session.query(Machine).get(mc.machine_id)
        if m is not None:
            if name:
                return m.name
            else:
                return m

    def add_new_machine(self, name, addresses, uuid=None):
        m = self.add_machine(name, uuid=uuid)
        alist = list()
        for a in addresses:
            am = self.add_macaddr(a, m.id)
            alist.append(am)
        return dict(machine=m, addresses=alist)

    def update_machine(self, name, addresses, uuid=None):
        q = self.session.query(Machine)
        if uuid is None:
            try:
                m = q.filter_by(name=name).one()
            except NoResultFound:
                return self.add_new_machine(name, addresses)
            # delete addresses in database, then
            # add the addresses passed.
            # FIXME
        else:
            try:
                m = q.filter_by(uuid=uuid).one()
            except NoResultFound:
                return self.add_new_machine(name, addresses, uuid=uuid)
            
    
    

    def delete_machine(self, name):
        m = self.session.query(Machine).filter_by(name=name).one()
        
            
    def list_machines(self):
        q = self.query(Machine)
        return q.all()
    
    def get_machine(self, name):
        return self.session.query(Machine).filter_by(name=name).one()

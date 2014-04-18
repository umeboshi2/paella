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
    

    def identify_machine_by_uuid(self, uuid):
        q = self.session.query(Machine)
        q = q.filter_by(uuid=uuid)
        machines = q.all()
        if len(machines) > 1:
            raise RuntimeError, "UUID should be unique"
        if not len(machines):
            name = None
        else:
            name = machines[0].name
        return name
        
        
    def identify_machine(self, address):
        q = self.session.query(MacAddr)
        q = q.filter_by(address=address)
        mc = q.one()
        m = self.session.query(Machine).get(mc.machine_id)
        if m is not None:
            return m.name
    

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
        m = self.query(Machine).filter_by(name=name).one()
        
            
    def list_machines(self):
        q = self.query(Machine)
        return q.all()
    

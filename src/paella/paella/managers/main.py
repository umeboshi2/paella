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

    def add_machine(self, name):
        with transaction.manager:
            m = Machine()
            m.name = name
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

    def identify_machine(self, address):
        q = self.session.query(MacAddr)
        q = q.filter_by(address=address)
        mc = q.one()
        m = self.session.query(Machine).get(mc.machine_id)
        if m is not None:
            return m.name
    

    def add_new_machine(self, name, addresses):
        m = self.add_machine(name)
        alist = list()
        for a in addresses:
            am = self.add_macaddr(a, m.id)
            alist.append(am)
        return dict(machine=m, addresses=alist)

    def update_machine(self, name, addresses):
        try:
            m = self.session.query(Machine).filter_by(name=name).one()
        except NoResultFound:
            return self.add_new_machine(name, addresses)
        # delete addresses in database, then
        # add the addresses passed.
        # FIXME

    
    

    def delete_machine(self, name):
        m = self.query(Machine).filter_by(name=name).one()
        
            
    def list_machines(self):
        q = self.query(Machine)
        return q.all()
    
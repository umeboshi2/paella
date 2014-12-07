import os
import logging

#from datetime import datetime, timedelta
#from zipfile import ZipFile
#from StringIO import StringIO
#import csv
#from io import BytesIO

import transaction
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc
from sqlalchemy import func

from paella.models.main import SaltKey, Machine

from paella.managers.util import generate_minion_keys

log = logging.getLogger(__name__)

class SaltKeyFiles(object):
    def __init__(self):
        self.pkipath = '/etc/salt/pki/master'
        self.minions_path = os.path.join(self.pkipath, 'minions')
        self.minions_pre_path = os.path.join(self.pkipath, 'minions_pre')
        self.minions_rejected_path = os.path.join(self.pkipath, 'minions_rejected')
        self.master_keyname = os.path.join(self.pkipath, 'master.pub')
        
        
    def _rm(self, filename):
        os.remove(filename)

    def _create(self, filename, content):
        with file(filename, 'w') as ofile:
            ofile.write(content)

    def _chmod(self, filename, mode):
        os.chmod(filename, mode)

    def get_masterkey(self):
        return file(self.master_keyname).read()
    
    def accept(self, name, content):
        if name in os.listdir(self.minions_rejected_path):
            raise RuntimeError, "Minion %s is rejected." % name
        if name in os.listdir(self.minions_pre_path):
            os.remove(os.path.join(self.minions_pre_path, name))
        filename = os.path.join(self.minions_path, name)
        if name in os.listdir(self.minions_path):
            return
        else:
            self._create(filename, content)
        if not os.path.isfile(filename):
           raise RuntimeError, "Problem accepting %s." % name     
                      

    

# store keys in database.
# only database keys exists as files
# submit_machine generates keys that are stored in database
# set_install will make sure key is accepted by minion
# late command will send keypair to minion
class SaltKeyManager(object):
    def __init__(self, session):
        self.session = session
        self.filemgr =SaltKeyFiles()
        self.masterkey = self.filemgr.get_masterkey()

    def query(self):
        return self.session.query(SaltKey)

    def get_machine(self, name):
        q = self.session.query(Machine)
        q = q.filter_by(name=name)
        try:
            machine = q.one()
        except NoResultFound:
            machine = None
        return machine
    
    def get(self, id):
        return self.query().get(id)

    def get_by_name(self, name):
        machine = self.get_machine(name)
        if machine is None:
            return
        return self.get(machine.id)

    def generate_minion_keys(self, name):
        log.info('generating minion keys for %s' % name)
        return generate_minion_keys(name)

    def add_keypair_no_txn(self, id, keydata):
        skey = SaltKey()
        skey.id = id
        for ktype in ['public', 'private']:
            setattr(skey, ktype, keydata[ktype])
        self.session.add(skey)
        return skey
    
    def generate_keypair(self, name):
        print "generate a key pair with this name"
        machine = self.get_machine(name)
        if machine is None:
            raise RuntimeError, "No such machine, %s" % name
        keydata = self.get(machine.id)
        if keydata is not None:
            raise RuntimeError, "Keys already exist for %s." % name
        #print "files are created, then destroyed"
        #print "generation can take time"
        with transaction.manager:
            keydata = self.generate_minion_keys(name)
            skey = self.add_keypair_without_txn(machine.id, keydata)
        return self.session.merge(skey)

    def accept_machine(self, machine):
        keydata = self.get(machine.id)
        self.filemgr.accept(machine.name, keydata.public)
        
        
        
        
    


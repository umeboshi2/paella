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

from paella.models.main import Machine
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

    def get_by_name(self, name):
        return self._query().filter_by(name=name).one()
    
    def add(self, name, content):
        with transaction.manager:
            pr = PartmanRecipe()
            pr.name = name
            pr.content = content
            self.session.add(pr)
        return self.session.merge(pr)

    def update(self, recipe, name=None, content=None):
        with transaction.manager:
            if name is not None or content is not None:
                if name is not None:
                    recipe.name = name
                if content is not None:
                    recipe.content = content
                self.session.add(recipe)
        return self.session.merge(recipe)

    def list_recipes(self):
        return [r.name for r in self._query()]

    def delete(self, recipe):
        with transaction.manager:
            self.session.delete(recipe)
            
class MachineManager(object):
    def __init__(self, session):
        self.session = session

    def _query(self):
        return self.session.query(Machine)

    def get(self, id):
        return self._query().get(id)

    def _get_one_by(self, **kw):
        return self._query().filter_by(**kw).one()
    
    def get_by_name(self, name):
        return self._get_one_by(name=name)
    
    def get_by_uuid(self, uuid):
        return self._get_one_by(uuid=uuid)
    
    def add(self, name, uuid, autoinstall=False, recipe=None):
        with transaction.manager:
            machine = Machine()
            machine.name = name
            machine.uuid = uuid
            machine.autoinstall = autoinstall
            if recipe is not None:
                machine.recipe_id = recipe.id
            self.session.add(machine)
        return self.session.merge(machine)

    def update(self, machine, name=None, autoinstall=None,
               recipe=None):
        with transaction.manager:
            if name is not None or autoinstall is not None \
                    or recipe is not None:
                if name is not None:
                    machine.name = name
                if autoinstall is not None:
                    machine.autoinstall = autoinstall
                if recipe is not None:
                    machine.recipe_id = recipe.id
                self.session.add(machine)
        return self.session.merge(machine)

    def list_machines(self):
        return [m.name for m in self._query()]
    
    def delete(self, machine):
        with transaction.manager:
            self.session.delete(machine)
            


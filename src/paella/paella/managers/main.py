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

import networkx as nx

from paella.models.main import Machine
from paella.models.main import PartmanRecipe

from paella.managers.saltkeys import SaltKeyManager

from paella.managers.util import prepare_recipe
        
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

    def prepare_recipe(self, id):
        r = self.get(id)
        if r is None:
            raise NoResultFound
        return prepare_recipe(r.content)
    
class MachineManager(object):
    def __init__(self, session):
        self.session = session
        self.keymanager = SaltKeyManager(self.session)

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

    def does_machine_exist(self, uuid):
        try:
            m = self.get_by_uuid(uuid)
            return True
        except NoResultFound:
            return False
        
    def add(self, name, uuid, autoinstall=False, recipe=None,
            arch=None):
        with transaction.manager:
            machine = Machine()
            machine.name = name
            machine.uuid = uuid
            machine.autoinstall = autoinstall
            if arch is not None:
                machine.arch = arch
            if recipe is not None:
                machine.recipe_id = recipe.id
            self.session.add(machine)
            machine = self.session.merge(machine)
            keydata = self.keymanager.generate_minion_keys(name)
            skey = self.keymanager.add_keypair_no_txn(machine.id, keydata)
        return self.session.merge(machine)

    def accept_machine(self, machine, id=None, name=None):
        self.keymanager.accept_machine(machine)

    

    def update(self, machine, name=None, autoinstall=None,
               recipe=None, ostype=None, release=None, arch=None,
               imagepath=None):
        with transaction.manager:
            if name is not None or autoinstall is not None \
                    or recipe is not None or ostype is not None \
                    or release is not None or arch is not None \
                    or imagepath is not None:
                if name is not None:
                    machine.name = name
                if autoinstall is not None:
                    machine.autoinstall = autoinstall
                if recipe is not None:
                    machine.recipe_id = recipe.id
                if ostype is not None:
                    machine.ostype = ostype
                if release is not None:
                    machine.release = release
                if arch is not None:
                    machine.arch = arch
                if imagepath is not None:
                    machine.imagepath = imagepath
                self.session.add(machine)
        return self.session.merge(machine)

    def list_machines(self):
        return [m.name for m in self._query()]
    
    def delete(self, machine):
        with transaction.manager:
            self.session.delete(machine)
            


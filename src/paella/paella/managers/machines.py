import logging

import transaction
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc
from sqlalchemy import func

import networkx as nx

from paella.models.main import Machine

from paella.managers.saltkeys import SaltKeyManager
from paella.managers.recipes import PartmanRecipeManager
from paella.managers.recipes import PartmanRaidRecipeManager

log = logging.getLogger(__name__)

class MachineManager(object):
    def __init__(self, session):
        self.session = session
        self.keymanager = SaltKeyManager(self.session)

    def _query(self):
        print "FIXME: don't use me"
        return self.session.query(Machine)

    def query(self):
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

    def accept_machine(self, machine, id=None, name=None, force=False):
        self.keymanager.accept_machine(machine, force=force)

    

    def update(self, machine, name=None, autoinstall=None,
               recipe=None, ostype=None, release=None, arch=None,
               imagepath=None, raid_recipe=None, iface=None,
               delete_recipe=False, delete_raid_recipe=False):
        with transaction.manager:
            # merge machine before update
            machine = self.session.merge(machine)
            updated = False
            if name is not None:
                machine.name = name
                updated = True
            if autoinstall is not None:
                machine.autoinstall = autoinstall
                updated = True
            log.info('MANAGERl: recipe is %s' % recipe)
            log.info('MANAGER: machine.recipe_id is %s' % machine.recipe_id)
            # partition recipe
            if recipe is not None:
                machine.recipe_id = recipe.id
                updated = True
            if delete_recipe:
                log.info("MANAGER---> delete_recipe:")
                machine.recipe_id = None
                updated = True

                    
            # raid recipe
            if raid_recipe is not None:
                machine.raid_recipe_id = raid_recipe.id
                updated = True
            if delete_raid_recipe:
                log.info("MANAGER---> delete_raid_recipe:")
                machine.raid_recipe_id = None
                updated = True

            if ostype is not None:
                machine.ostype = ostype
                updated = True
            if release is not None:
                machine.release = release
                updated = True
            if arch is not None:
                machine.arch = arch
                updated = True
            if imagepath is not None:
                machine.imagepath = imagepath
                updated = True
            if iface is not None:
                machine.iface = iface
                updated = True
            if updated:
                self.session.add(machine)
        return self.session.merge(machine)

    def list_machines(self, names=False):
        if names:
            return [m.name for m in self._query()]
        return [m.serialize() for m in self._query()]
    
    def delete(self, machine):
        with transaction.manager:
            self.session.delete(machine)

    def export(self, name):
        machine = self.get_by_name(name)
        return self._export(machine)

    def _export(self, machine):
        data = machine.serialize()
        data['minion_keys'] = self.keymanager.get(machine.id).serialize()
        if machine.recipe_id is not None:
            mgr = PartmanRecipeManager(self.session)
            data['recipe'] = mgr.get(machine.recipe_id).serialize()
        if machine.raid_recipe_id is not None:
            mgr = PartmanRaidRecipeManager(self.session)
            data['raid_recipe'] = mgr.get(machine.raid_recipe_id).serialize()
        return data



def export_machines(session):
    mgr = MachineManager(session)
    return dict(data=[mgr._export(m) for m in mgr._query()])
    
        


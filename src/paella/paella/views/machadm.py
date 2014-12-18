import os
import json
import logging

from pyramid.exceptions import HTTPNotFound
from pyramid.exceptions import HTTPBadRequest
from pyramid.exceptions import HTTPForbidden


from cornice.resource import resource, view


from paella.managers.machines import MachineManager
from paella.managers.recipes import PartmanRecipeManager
from paella.managers.recipes import PartmanRaidRecipeManager
from paella.managers.pxeconfig import make_pxeconfig, remove_pxeconfig
from paella.managers.pxeconfig import pxeconfig_filename


from paella.views.base import BaseResource, MAIN_RESOURCE_ROOT
from paella.views.util import make_resource as make_base_resource


log = logging.getLogger(__name__)

def make_resource(rpath, ident='id', cross_site=True):
    data = make_base_resource(rpath, ident=ident, cross_site=cross_site)
    data['permission'] = 'admin'
    return data


# Machine POST Actions
#
# submit - submit a brand new machien
#
# install - sets a machine to be installed
#
# stage_over - tells paella server that debian-installer has completed
#
# 
@resource(**make_resource(os.path.join(MAIN_RESOURCE_ROOT, 'admin/machines'),
                          ident='uuid'))
class MachineAdminResource(object):
    def __init__(self, request):
        self.request = request
        self.db = self.request.db
        self.mgr = MachineManager(self.db)
        self.recipes = PartmanRecipeManager(self.db)
        self.raid_recipes = PartmanRaidRecipeManager(self.db)
        

    def collection_get(self):
        return dict(data=self.mgr.list_machines())

    def get(self):
        uuid = self.request.matchdict['uuid']
        machine = self.mgr.get_by_uuid(uuid)
        return machine.serialize()


    # recipe is by name
    # if recipe is not None, we retrieve it from
    # the database.
    def _submit_machine(self, data):
        # FIXME machine parameter must go
        if 'name' in data:
            name = data['name']
        else:
            name = data['machine']
        if name in self.mgr.list_machines():
            msg = "A machine named %s already exists." % name
            raise HTTPForbidden, msg
        uuid = data['uuid']
        # check uuid against database
        if self.mgr.does_machine_exist(uuid):
            raise RuntimeError, "A machine with this uuid already exists."
        autoinstall = False
        if 'autoinstall' in data:
            autoinstall = data['autoinstall']
        recipe = None
        if 'recipe' in data:
            recipe = data['recipe']
        if recipe is not None:
            recipe = self.recipes.get_by_name(recipe)
        arch=None
        if 'arch' in data:
            arch = data['arch']
        machine = self.mgr.add(name, uuid, autoinstall=autoinstall,
                               recipe=recipe, arch=arch)
        self.mgr.accept_machine(machine)
        return machine.serialize()
    
        

    def _install_machine(self, data):
        uuid = data['uuid']
        settings = self.request.registry.settings
        machine = self.mgr.get_by_uuid(uuid)
        make_pxeconfig(machine, settings)
        filename = pxeconfig_filename(uuid)
        if not os.path.isfile(filename):
            raise RuntimeError, "%s doesn't exist." % filename
        return


    def _unset_install_pxeconfig(self, uuid):
        remove_pxeconfig(uuid) 
        filename = pxeconfig_filename(uuid)
        if os.path.isfile(filename):
            raise RuntimeError, "%s still exists." % filename
        return
        
    def _stage_one_over(self, data):
        uuid = data['uuid']
        self._unset_install_pxeconfig(uuid)
        

    def post(self):
        textkeys = ['name', 'autoinstall', 'ostype', 'release', 'arch',
                    'imagepath']
        data = self.request.json
        if not data:
            return {}
        uuid = self.request.matchdict['uuid']
        update = dict().fromkeys(textkeys)
        for key in data:
            if key in update:
                update[key] = data[key]
        update['recipe'] = None
        if 'recipe' in data:
            rname = data['recipe']
            recipe = self.recipes.get_by_name(rname)
            update['recipe'] = recipe
        update['recipe'] = None
        if 'raid_recipe' in data:
            rname = data['raid_recipe']
            recipe = self.raid_recipes.get_by_name(rname)
            update['raid_recipe'] = recipe
        machine = self.mgr.get_by_uuid(uuid)
        machine = self.mgr.update(machine, **update)
        return machine.serialize()
        
    def collection_post(self):
        data = self.request.json
        action = data['action']
        if action == 'submit':
            # submit a brand new machine
            data = self._submit_machine(data)
        elif action == 'install':
            # set a machine to be installed
            # creates pxeconfig
            self._install_machine(data)
            data = dict(result='success')
        elif action == 'stage_over':
            self._stage_one_over(data)
            data = dict(result='success')
        return data
        

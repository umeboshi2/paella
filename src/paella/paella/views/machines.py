import os
import json
import logging

from pyramid.exceptions import HTTPNotFound
from pyramid.exceptions import HTTPBadRequest
from pyramid.exceptions import HTTPForbidden


from cornice.resource import resource, view


from paella.views.base import BaseResource, MAIN_RESOURCE_ROOT
from paella.views.basemachines import BaseMachineResource
from paella.views.util import make_resource

log = logging.getLogger(__name__)


# Machine POST Actions
#
# submit - submit a brand new machine
#
# install - sets a machine to be installed
#
# stage_over - tells paella server that debian-installer has completed
#
# 

@resource(**make_resource(os.path.join(MAIN_RESOURCE_ROOT, 'machines'),
                          ident='uuid'))
class MachineResource(BaseMachineResource):
    def collection_get(self):
        return dict(data=self.mgr.list_machines(names=True))

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
        machine = self.mgr.get_by_uuid(uuid)
        self._set_machine_install(machine, install=True)

    def _unset_install_pxeconfig(self, uuid):
        machine = self.mgr.get_by_uuid(uuid)
        self._set_machine_install(machine, install=False)
        
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
        
    def _update_package_list(self):
        # the paella client will make a dictionary
        # from the package selection and send it
        # to the server in json format
        #
        # the server will then use the debrepos
        # manager to update the filter list
        #
        # a long running process such as updating
        # the repository after the list is updated
        # will wait until a job server is implemented
        raise RuntimeError, "Not implemented"
        
    def collection_post(self):
        data = self.request.json
        if 'uuid' not in data:
            raise HTTPBadRequest, "Request requires uuid."
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
        

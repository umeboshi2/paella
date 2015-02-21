import os
import json
import logging

from pyramid.exceptions import HTTPNotFound
from pyramid.exceptions import HTTPBadRequest
from pyramid.exceptions import HTTPForbidden


from cornice.resource import resource, view


from paella.views.base import BaseResource, MAIN_RESOURCE_ROOT
from paella.views.util import make_resource as make_base_resource
from paella.views.basemachines import BaseMachineResource

log = logging.getLogger(__name__)

def make_resource(rpath, ident='id', cross_site=True):
    data = make_base_resource(rpath, ident=ident, cross_site=cross_site)
    data['permission'] = 'admin'
    return data


# Machine POST Actions
#
#
# 

@resource(**make_resource(os.path.join(MAIN_RESOURCE_ROOT, 'admin/machines'),
                          ident='name'))
class MachineAdminResource(BaseMachineResource):
    def get(self):
        name = self.request.matchdict['name']
        machine = self.mgr.get_by_name(name)
        mdata = machine.serialize()
        mdata['all_recipes'] = self.recipes.list_recipes()
        mdata['all_raid_recipes'] = self.raid_recipes.list_recipes()
        mdata['pxeconfig'] = self.has_pxeconfig(machine)
        if machine.recipe_id is not None:
            mdata['recipe'] = self.recipes.get(machine.recipe_id).name
        if machine.raid_recipe_id is not None:
            mdata['raid_recipe'] = self.raid_recipes.get(machine.raid_recipe_id).name
        return mdata
    


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
    
        

    def put(self):
        data = self.request.json
        #[log.info('PUT[%s]: %s' % (k,v)) for k,v in data.items()]
        fields = ['arch', 'ostype', 'release', 'iface']
        recipeFields = ['recipe', 'raid_recipe']
        update = {}
        machine = self.mgr.get_by_uuid(data['uuid'])
        for field in fields:
            if data[field] != getattr(machine, field):
                #log.debug('update field %s with value %s' % (field, data[field]))
                update[field] = data[field]
        for rfield in recipeFields:
            attr = '%s_id' % rfield
            #log.debug('attr is %s...........................' % attr)
            if rfield in data:
                rname = data[rfield]
                if rname is None:
                    #log.debug("Delete %s from %s" % (rfield, machine.name))
                    delkey = 'delete_%s' % rfield
                    update[delkey] = True
                    continue
                #log.debug("recipe field %s present with value %s" % (rfield, rname))
                recipe = self.rmgr[rfield].get_by_name(rname)
                #log.debug("recipe_id is %d" % recipe.id)
                if getattr(machine, attr) != recipe.id:
                    update[rfield] = recipe
            elif getattr(machine, attr) is not None:
                #log.debug('attr %s is %s' % (attr, getattr(machine, attr)))
                update[rfield] = None
        #[log.debug('UPDATE:---> %s: %s' % (k,v)) for k,v in update.items()]
        self.mgr.update(machine, **update)
            
                
                    
                
                
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
        update['raid_recipe'] = None
        if 'raid_recipe' in data:
            rname = data['raid_recipe']
            recipe = self.raid_recipes.get_by_name(rname)
            update['raid_recipe'] = recipe
        machine = self.mgr.get_by_uuid(uuid)
        machine = self.mgr.update(machine, **update)
        return machine.serialize()
        
    def collection_post(self):
        data = self.request.json
        if 'uuid' not in data:
            raise HTTPBadRequest, "UUID is required"
        machine = self.mgr.get_by_uuid(data['uuid'])
        action = data['action']
        if action == 'submit':
            # submit a brand new machine
            data = self._submit_machine(data)
        elif action == 'install':
            # set a machine to be installed
            # creates pxeconfig
            self._set_machine_install(machine, install=True)
            data = dict(result='success')
        elif action == 'stage_over':
            self._set_machine_install(machine, install=False)
            data = dict(result='success')
        return data
        

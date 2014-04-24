import os
import json

from pyramid.exceptions import HTTPNotFound
from pyramid.exceptions import HTTPBadRequest
from pyramid.exceptions import HTTPForbidden


from cornice.resource import resource, view


from paella.managers.main import MachineManager
from paella.managers.main import PartmanRecipeManager
from paella.managers.pxeconfig import make_pxeconfig, remove_pxeconfig
from paella.managers.pxeconfig import pxeconfig_filename


from paella.views.base import BaseResource

@resource(collection_path='/api0/recipes',
          path='/api0/recipes/{name}')
class RecipeResource(object):
    def __init__(self, request):
        self.request = request
        self.db = self.request.db
        self.mgr = PartmanRecipeManager(self.db)

    def collection_get(self):
        return dict(data=self.mgr.list_recipes)

    def get(self):
        name = self.request.matchdict['name']
        recipe = self.mgr.get_by_name(name)
        return recipe.serialize()

    def collection_post(self):
        print "create a new recipe"

    def post(self):
        print "update a recipe"

    def delete(self):
        print "delete a recipe"
        
    

@resource(collection_path='/api0/machines',
          path='/api0/machines/{uuid}')
class MachineResource(object):
    def __init__(self, request):
        self.request = request
        self.db = self.request.db
        self.mgr = MachineManager(self.db)
        self.recipes = PartmanRecipeManager(self.db)

    def collection_get(self):
        return dict(data=self.mgr.list_machines())

    def get(self):
        uuid = self.request.matchdict['uuid']
        machine = self.mgr.get_by_uuid(uuid)
        return machine.serialize()


    # recipe is by name
    # if recipe is not None, we retrieve it from
    # the database.
    def _submit_machine(self, name, uuid, autoinstall=False,
                        recipe=None):
        if name in self.mgr.list_machines():
            msg = "A machine named %s already exists." % name
            raise HTTPForbidden, msg
        if recipe is not None:
            recipe = self.recipes.get_by_name(recipe)
        machine = self.mgr.add(name, uuid, autoinstall=autoinstall,
                               recipe=recipe)
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

    
    def _stage_one_over(self, data):
        uuid = data['uuid']
        remove_pxeconfig(uuid) 
        filename = pxeconfig_filename(uuid)
        if os.path.isfile(filename):
            raise RuntimeError, "%s still exists." % filename
        return


    def _update_machine(self, data):
        pass
    
        
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
        request = self.request
        settings = self.request.registry.settings
        baseparent = settings['debrepos_baseparent']
        from debrepos.server import PartialMirrorManager
        pmm = PartialMirrorManager(baseparent)
        # FIXME
        dist = 'wheezy'
        # package-list is a dictionary
        data = self.request.json['package-list']
        updated = pmm.update_list(dist, data)
        if updated:
            return dict(result='success')
        else:
            return dict(result='failed')
        
        
    def collection_post(self):
        data = self.request.json
        action = data['action']
        if action == 'submit':
            data = self._submit_machine(data)
        elif action == 'install':
            self._install_machine(data)
            data = dict(result='success')
        elif action == 'stage_over':
            self._stage_one_over(data)
            data = dict(result='success')
        elif action == 'update_package_list':
            data = self._update_package_list(data)
            
        return data
        
    def get(self):
        name = self.request.matchdict['name']
        return dict(name=name)
    
        
    

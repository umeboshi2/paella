import os
import json
import logging

from pyramid.exceptions import HTTPNotFound
from pyramid.exceptions import HTTPBadRequest
from pyramid.exceptions import HTTPForbidden


from cornice.resource import resource, view


from paella.managers.main import MachineManager
from paella.managers.recipes import PartmanRecipeManager
from paella.managers.recipes import PartmanRaidRecipeManager
from paella.managers.pxeconfig import make_pxeconfig, remove_pxeconfig
from paella.managers.pxeconfig import pxeconfig_filename

from paella.views.base import BaseResource

log = logging.getLogger(__name__)

class BaseRecipeResource(object):
    def __init__(self, request):
        self.request = request
        self.db = self.request.db
        self.mgr = self.mgrclass(self.db)
        
    def collection_get(self):
        #return dict(data=self.mgr.list_recipes())
        return dict(data=[x.serialize() for x in self.mgr.query()], result='success')
    
    def get(self):
        name = self.request.matchdict['name']
        recipe = self.mgr.get_by_name(name)
        return recipe.serialize()

    def collection_post(self):
        data = self.request.json
        name = data['name']
        content = data['content']
        recipe = self.mgr.add(name, content)
        return recipe.serialize()

    def post(self):
        data = self.request.json
        name = self.request.matchdict['name']
        recipe = self.mgr.get_by_name(name)
        content = data['content']
        recipe = self.mgr.update(recipe, content=content)
        return recipe.serialize()
        

    def delete(self):
        name = self.request.matchdict['name']
        recipe = self.mgr.get_by_name(name)
        self.mgr.delete(recipe)
        return dict(result='success')

    def put(self):
        recipe = self.mgr.get(self.request.json.get('id'))
        log.info('json is %s' % self.request.json)
        content = self.request.json.get('content')
        log.info('content is %s' % content)
        self.mgr.update(recipe, content=content)
        return dict(result='success')
        
    
        


@resource(collection_path='/rest/v0/main/recipes',
          path='/rest/v0/main/recipes/{name}')
class RecipeResource(BaseRecipeResource):
    mgrclass = PartmanRecipeManager

@resource(collection_path='/rest/v0/main/raidrecipes',
          path='/rest/v0/main/raidrecipes/{name}')
class RecipeResource(BaseRecipeResource):
    mgrclass = PartmanRaidRecipeManager


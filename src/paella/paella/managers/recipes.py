import logging

import transaction
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc
from sqlalchemy import func

import networkx as nx

from paella.models.main import Machine
from paella.models.main import PartmanRecipe, PartmanRaidRecipe

from paella.managers.saltkeys import SaltKeyManager

from paella.managers.util import prepare_recipe

log = logging.getLogger(__name__)

class BaseRecipeManager(object):
    def __init__(self, session):
        self.session = session
        
    def query(self):
        return self.session.query(self.dbmodel)

    def get(self, id):
        return self.query().get(id)

    def get_by_name(self, name):
        return self.query().filter_by(name=name).one()
    
    def add(self, name, content):
        with transaction.manager:
            pr = self.dbmodel()
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
        return [r.name for r in self.query()]

    def delete(self, recipe):
        with transaction.manager:
            self.session.delete(recipe)

    def prepare_recipe(self, id):
        r = self.get(id)
        if r is None:
            raise NoResultFound
        return prepare_recipe(r.content)
    

class PartmanRecipeManager(BaseRecipeManager):
    dbmodel = PartmanRecipe

class PartmanRaidRecipeManager(BaseRecipeManager):
    dbmodel = PartmanRaidRecipe
    

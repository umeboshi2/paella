import transaction
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc
from sqlalchemy import func

import networkx as nx

from paella.models.main import Trait, TraitParent, TraitVariable

    

def _directed_graph(foobar=None):
    g = nx.DiGraph()
    nodes = ['global', 'base', 'apt', 'users', 'default', 'desktop']
    for n in nodes:
        g.add_node(n)

    edges = [('base', 'global'),
             ('apt', 'base'),
             ('users', 'base'),
             ('default', 'apt'),
             ('default', 'users'),
             ('desktop', 'default'),]
    for e in edges:
        g.add_edge(*e)
    return g

    
             
class TraitManager(object):
    def __init__(self, session):
        self.session = session

    def query(self):
        return self.session.query(Machine)

    def get(self, id):
        return self.query().get(id)

    def _get_one_by(self, **kw):
        return self.query().filter_by(**kw).one()
    
    def get_by_name(self, name):
        return self._get_one_by(name=name)

    def add_trait(self, name, description=None):
        with transaction.manager:
            trait = Trait()
            trait.name = name
            if description is not None:
                trait.description = description
            self.session.add(trait)
        return self.session.merge(trait)
    
    def remove_trait(self, trait):
        raise NotImplementedError, "FIXME"

    def update_description(self, trait, newdesc):
        with transaction.manager:
            trait.description = newdesc
            self.session.add(trait)
        return self.session.merge(trait)

    def list_parents(self, trait_id):
        raise NotImplementedError, "FIXME"

    def _add_parent(self, trait_id, parent_id):
        with transaction.manager:
            tp = TraitParent()
            tp.trait_id = trait_id
            tp.parent_id = parent_id
            self.session.add(tp)
        return self.session.merge(tp)

    def add_parent(self, trait, parent=None, name=None):
        if name is None and parent is None:
            raise RuntimeError, "Can't identify parent."
        if name is not None:
            parent = self.get_by_name(name)
        return self._add_parent(trait.id, parent.id)
        
    def remove_parent(self, trait_id, parent_id):
        raise NotImplementedError, "FIXME"

    def trait_variables(self, trait_id):
        raise NotImplementedError, "FIXME"

    def add_variable(self, trait_id, name, value):
        raise NotImplementedError, "FIXME"

    def remove_variable(self, trait_id, name):
        raise NotImplementedError, "FIXME"
    
    
    

import logging

import transaction
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc
from sqlalchemy import func

from paella.models.main import Trait, TraitParent, TraitVariable

log = logging.getLogger(__name__)


# nx.predecessor(g, node) will return a dictionary of reachable nodes
#
# nx.has_path(g, source, target) returns bool

# make trait graph:
#
# add all traits first
# for trait in traits:
#     g.add_node(trait)
# for trait in traits:
#    for parent in trait.parents:
#        g.add_edge(trait, parent)

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
        with transaction.manager:
            self.session.delete(trait)

    def update_description(self, trait, newdesc):
        with transaction.manager:
            trait.description = newdesc
            self.session.add(trait)
        return self.session.merge(trait)

    def get_parents(self, trait):
        subquery = self.session.query(TraitParent.id).filter_by(trait_id=trait.id)
        q = self.query().filter(Trait.id in subquery)
        return q.all()

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
        with transaction.manager:
            tv = TraitVariable()
            tv.trait_id = trait_id
            tv.name = name
            tv.value = value
            self.session.add(tv)
        return self.session.merge(tv)

    def update_variable(self, trait_id, name, value):
        with transaction.manager:
            tv = self.session.query(TraitVariable).get((trait_id, name))
            if tv is not None:
                tv.value = value
                self.session.add(tv)
        tv = self.session.merge(tv)
        return tv
    
    def remove_variable(self, trait_id, name):
        with transaction.manager: 
            tv = self.session.query(TraitVariable).get((trait_id, name))
            self.session.delete(tv)
    
    
    

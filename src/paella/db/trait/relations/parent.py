import os
from os.path import join
from sets import Set
import tempfile

from kjbuckets import kjGraph

from useless.base import Error
from useless.base.util import ujoin, RefDict, strfile, filecopy

from useless.sqlgen.clause import one_many, Eq, In
from useless.db.midlevel import Environment

from paella.base.objects import TextFileManager

from base import TraitRelation

from paella import deprecated

class TraitParent(TraitRelation):
    def __init__(self, conn, suite):
        table = ujoin(suite, 'trait', 'parent')
        TraitRelation.__init__(self, conn, suite, table, name='TraitParent')
        self.graph = kjGraph([(r.trait, r.parent) for r in self.cmd.select()])

    def get_traitset(self, traits):
        dtraits = Set()
        for trait in traits:
            dtraits |=  Set([trait]) | Set(self.graph.reachable(trait).items())
        return dtraits

    def get_environment(self, traits):
        assoc_traits = list(self.get_traitset(traits))
        c, s = self.conn, self.suite
        return [(t, TraitEnvironment(c, s, t)) for t in assoc_traits]


    def get_superdict(self, traits, sep='_'):
        env = TraitEnvironment(self.conn, self.suite, traits[0])
        superdict = RefDict()
        for trait in traits:
            env.set_main(trait)
            items = [(trait+sep+key, value) for key, value in env.items()]
            superdict.update(dict(items))
        return superdict

    def Environment(self):
        traits = list(self.get_traitset([self.current_trait]))
        return self.get_superdict(traits)

    def parents(self, trait=None):
        if trait is None:
            trait = self.current_trait
        self.set_clause(trait)
        rows = self.cmd.select(fields=['parent'], order='parent')
        self.reset_clause()
        return rows
    
    def insert_parents(self, parents):
        self.insert('parent', parents)

    def delete(self, parents=[]):
        if parents:
            print parents, 'PARENTS'
            clause = In('parent', parents) & Eq('trait', self.current_trait)
            self.cmd.delete(clause=clause)
            self.reset_clause()

    def delete_trait(self, trait=None):
        if trait is None:
            trait = self.current_trait
        clause = Eq('trait', trait)
        self.cmd.delete(clause=clause)
        self.reset_clause()

    def insert_new_parents_list(self, parents):
        current_parents = [row.parent for row in self.parents()]
        new_parents = parents
        common_parents = [p for p in new_parents if p in current_parents]
        delete_parents = [p for p in current_parents if p not in common_parents]
        insert_parents = [p for p in new_parents if p not in common_parents]
        self.delete(parents=delete_parents)
        self.insert_parents(insert_parents)
        
        
if __name__ == '__main__':
    #f = file('tmp/trait.xml')
    #tx = TraitXml(f)
    import sys

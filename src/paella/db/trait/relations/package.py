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
from parent import TraitParent

from paella import deprecated

class TraitPackage(TraitRelation):
    def __init__(self, conn, suite):
        table = ujoin(suite, 'trait', 'package')
        TraitRelation.__init__(self, conn, suite, table, name='TraitPackage')
        self.cmd.set_fields(['package', 'action'])
        self.traitparent = TraitParent(conn, suite)
        
    def packages(self, traits=None):
        if traits is None:
            traits = [self.current_trait]
        #self.cmd.set_clause([('trait', trait) for trait in traits], join='or')
        clause = In('trait', traits)
        rows =  self.cmd.select(clause=clause, order='package')
        self.reset_clause()
        return rows
    
    def all_packages(self, traits, traitparent=None):
        if not traitparent:
            traitparent = self.traitparent
        return list(self.packages(traitparent.get_traitset(traits)))

    def set_action(self, action, packages, trait=None):
        if trait is None:
            trait = self.current_trait
        clause = Eq('trait', trait) & In('package', packages)
        if action == 'drop':
            self.cmd.delete(clause=clause)
        elif action in ['remove', 'install', 'purge']:
            self.cmd.set_data({'action' : action})
            self.cmd.update(clause=clause)
        else:
            raise Error, 'bad action in TraitPackage -%s-' % action

    def insert_package(self, package, action='install'):
        idata = {'trait' : self.current_trait,
                 'action' : action,
                 'package' : package}
        self.cmd.insert(data=idata)

    def delete_package(self, package, action):
        clause = Eq('package', package) & Eq('action', action)
        self.cmd.delete(clause=clause)
        

    def insert_packages(self, packages):
        diff = self.diff('package', packages)
        for package in packages:
            if package in diff:
                self.insert_package(package)
        

    def set_trait(self, trait):
        TraitRelation.set_trait(self, trait)
        self.traitparent.set_trait(trait)

if __name__ == '__main__':
    #f = file('tmp/trait.xml')
    #tx = TraitXml(f)
    import sys

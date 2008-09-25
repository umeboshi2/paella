from useless.base import AlreadyExistsError
from useless.base.path import path
from useless.sqlgen.clause import Eq

from useless.db.midlevel import StatementCursor, SimpleRelation
from useless.db.midlevel import Environment

from paella import PAELLA_TRAIT_NAME_SEP
from paella.base.util import make_deplist
from paella.base.objects import VariablesConfig
from paella.db.base import get_suite
from paella.db.trait import Trait
from paella.db.trait.relations.parent import TraitParent
from paella.db.family import Family

from xmlparse import parse_profile
from xmlgen import ProfileElement

class ProfileVariablesConfig(VariablesConfig):
    def __init__(self, conn, profile):
        VariablesConfig.__init__(self, conn, 'profile_variables',
                                 'trait', 'profile', profile)
        
class ProfileTrait(SimpleRelation):
    def __init__(self, conn):
        SimpleRelation.__init__(self, conn, 'profile_trait',
                                'profile', name='ProfileTrait')

    def set_profile(self, profile):
        self.set_current(profile)

    def traits(self, profile=None):
        if profile is None:
            profile = self.current
        self.set_clause(profile)
        rows = self.cmd.select(fields=['trait'], order=['ord', 'trait'])
        self.reset_clause()
        return rows

    def trait_rows(self, profile=None):
        if profile is None:
            profile = self.current
        self.set_clause(profile)
        rows = self.cmd.select(fields=['trait', 'ord'], order=['ord', 'trait'])
        self.reset_clause()
        return rows
        
    def insert_trait(self, trait, ord='0'):
        idata = dict(profile=self.current, trait=trait, ord=ord)
        self.cmd.insert(data=idata)

    def insert_traits(self, traits):
        diff = self.diff('trait', traits)
        for trait in diff:
            self.insert_trait(trait)

    def drop_profile(self, profile):
        self.cmd.delete(clause=Eq('profile', profile))

    def delete(self, trait):
        clause=Eq('profile', self.current) & Eq('trait', trait)
        self.cmd.delete(clause=clause)

    def delete_all(self):
        self.cmd.delete(clause=Eq('profile', self.current))
        
    def update(self, *args, **kw):
        self.cmd.update(*args, **kw)
        
class _ProfileEnvironment(Environment):
    def __init__(self, conn, profile):
        self.suite = get_suite(conn, profile)
        self.profile = profile
        Environment.__init__(self, conn, 'profile_variables', 'trait')
        self.traitparent = TraitParent(self.conn, self.suite)
        
    def set_trait(self, trait):
        self.set_main(trait)
        self.traitparent.set_trait(trait)
        
    def _single_clause_(self):
        return Eq('profile', self.profile) & Eq('trait', self.__main_value__)
    
    def __setitem__(self, key, value):
        try:
            self.cursor.insert(data={'profile' : self.profile,
                                     'trait' : self.__main_value__,
                                     self.__key_field__ : key,
                                     self.__value_field__ : value})
        except OperationalError:
            self.cursor.update(data={self.__value_field__ : value},
                               clause=self._double_clause_(key))
            
        
    def make_superdict(self, sep='_'):
        clause = Eq('profile', self.profile)
        return Environment.make_superdict(self, clause, sep=sep)
    
    def _get_defaults_(self, trait):
        return self.traitparent.get_environment([trait])

    def _update_defaults_(self, trait):
        for trait, data in self._get_defaults_(trait):
            self.set_trait(trait)
            self.update(data)

class ProfileEnvironment(object):
    def __init__(self, conn, profile=None):
        object.__init__(self)
        self.conn = conn
        self.profile = profile
        self.profiletraits = ProfileTrait(self.conn)
        self.env = None
        if profile is not None:
            self.env = _ProfileEnvironment(conn, profile)
            self.set_profile(profile)

    def set_profile(self, profile):
        self.profile = profile
        self.profiletraits.set_profile(profile)
        self.env = _ProfileEnvironment(self.conn, profile)
        
        
    def set_defaults(self):
        for trait in self.get_all_traits():
            self.env.set_trait(trait)
            data = TraitEnvironment(self.conn, self.env.suite, trait)
            self.env.update(data)        

    def get_all_traits(self):
        profile_traits = [row.trait for row in self.profiletraits.traits()]
        return list(self.env.traitparent.get_traitset(profile_traits))

    def ProfileData(self):
        # change sep here
        sep = PAELLA_TRAIT_NAME_SEP
        return self.env.make_superdict(sep=sep)

    def get_rows(self):
        clause = Eq('profile', self.profile)
        return self.env.cursor.select(clause=clause, order=['trait', 'name'])

    def get_traits(self):
        clause = Eq('profile', self.profile)
        rows =  self.env.cursor.select(fields=['distinct trait'], clause=clause)
        return [row.trait for row in rows]
    
    def append_defaults(self):
        for trait in self.get_all_traits():
            self.env.set_trait(trait)
            data = TraitEnvironment(self.conn, self.env.suite, trait)
            new_items = [(k,v) for k,v in data.items() if k not in self.env.keys()]
            self.env.update(dict(new_items))

class Profile(StatementCursor):
    def __init__(self, conn):
        StatementCursor.__init__(self, conn)
        self.conn = conn
        self.set_table('profiles')
        self._traits = ProfileTrait(conn)
        self._env = ProfileEnvironment(conn)
        self._pfam = StatementCursor(conn)
        self._pfam.set_table('profile_family')
        self._fam = Family(conn)
        self.current = None
        
    def drop_profile(self, profile):
        self.delete(clause=Eq('profile', profile))

    def make_new_profile(self, profile, suite):
        data = dict(profile=profile, suite=suite)
        self.insert(data=data)

    def make_environment_object(self):
        return ProfileEnvironment(self.conn)
    
    def set_profile(self, profile):
        self.clause = Eq('profile', profile)
        self.current = self.select_row(clause=self.clause)
        self._traits.set_profile(profile)
        self._env.set_profile(profile)

    
    def get_profile_data(self):
        return self._env.ProfileData()

    
    def get_family_data(self):
        families = self.get_families()
        return self._fam.FamilyData(families)

    def _make_traitlist(self, traits, log=None):
        tp = TraitParent(self.conn, self.current.suite)
        listed = traits
        all = list(tp.get_traitset(listed))
        setfun = tp.set_trait
        parfun = tp.parents
        return make_deplist(listed, all, setfun, parfun, log)

    def make_traitlist_with_traits(self, traits, log=None):
        return self._make_traitlist(traits, log=log)
    
    def make_traitlist(self, log=None):
        listed = [x.trait for x in self._traits.trait_rows()]
        return self._make_traitlist(listed, log=log)

    def get_traitlist_for_traits(self, traits):
        return self._make_traitlist(traits)
    
    def family_rows(self, profile=None):
        if profile is None:
            profile = self.current.profile
        return self._pfam.select(clause=Eq('profile', profile), order='family')
    

    def get_families(self, profile=None):
        return [r.family for r in self.family_rows(profile)]

    def get_trait_rows(self):
        return self._traits.trait_rows()
    
    def append_family(self, family):
        if family not in self.get_families():
            self._pfam.insert(data=dict(profile=self.current.profile, family=family))

    def append_trait(self, trait, ord):
        self._traits.insert_trait(trait, ord)
        
    def set_suite(self, suite):
        clause = Eq('profile', self.current.profile)
        self.update(data=dict(suite=suite), clause=clause)
        self.set_profile(self.current.profile)

    def copy_profile(self, src, dest):
        current = self.current
        self.set_profile(src)
        pfield = "'%s' as profile" % dest
        pclause = Eq('profile', src)
        pcursor = self
        tcursor = self._traits.cmd
        fcusor = self._pfam
        vcursor = self._env.env.cursor
        cursors = [ pcursor, tcursor, fcusor, vcursor]
        for cursor in cursors:
            sel = str(cursor.stmt.select(fields = [pfield] + cursor.fields()[1:], clause=pclause))
            cursor.execute('insert into %s (%s)' % (cursor.stmt.table, sel))
        if current is not None:
            self.set_profile(current.profile)
            

    def get_profile_list(self, suite=None):
        if suite is None:
            plist = [r.profile for r in self.select()]
        elif suite == 'all':
            plist = [(r.profile, r.suite) for r in self.select()]
        else:
            clause = Eq('suite', suite)
            plist = [r.profile for r in self.select(clause=clause)]
        return plist

    def edit_variables(self):
        config = ProfileVariablesConfig(self.conn, self.current.profile)
        newconfig = config.edit()
        config.update(newconfig)

    def delete_trait(self, trait):
        self._traits.delete(trait)

    def delete_all_traits(self):
        self._traits.delete_all()

    def delete_family(self, family):
        clause = Eq('profile', self.current.profile) & Eq('family', family)
        self._pfam.delete(clause=clause)

    def delete_all_families(self):
        clause = Eq('profile', self.current.profile)
        self._pfam.delete(clause=clause)

    def insert_new_traits(self, traits):
        self.delete_all_traits()
        num = 0
        for trait in traits:
            self.append_trait(trait, num)
            num += 1
            
            
    def generate_xml(self, profile=None, suite=None, env=None):
        if profile is None:
            profile = self.current.profile
            suite = self.current.suite
        if suite is None:
            row = self.select_row(clause=Eq('profile', profile))
            suite = row.suite
        if env is None:
            env = ProfileEnvironment(self.conn, profile)
        element = ProfileElement(profile, suite)
        element.append_traits(self._traits.trait_rows(profile))
        element.append_families(self.family_rows(profile))
        element.append_variables(env.get_rows())
        return element
    
    def import_profile(self, filename):
        profile = parse_profile(filename)
        if profile.name in self.get_profile_list():
            raise AlreadyExistsError, '%s already exists.' % profile.name
        self.insert(data=dict(profile=profile.name, suite=profile.suite))
        # insert profile traits
        idata = dict(profile=profile.name, trait=None, ord=0)
        for trait, ord in profile.traits:
            idata['trait'] = trait
            idata['ord'] = ord
            self.insert(table='profile_trait', data=idata)
        # insert profile families
        idata = dict(profile=profile.name)
        for family in profile.families:
            idata['family'] = family
            self.insert(table='profile_family', data=idata)
        # insert profile variables
        idata = dict(profile=profile.name, trait=None, name=None,
                     value=None)
        for trait, name, value in profile.vars:
            idata.update(dict(trait=trait, name=name, value=value))
            self.insert(table='profile_variables', data=idata)
        
    def export_profile(self, dirname, profile=None, env=None):
        element = self.generate_xml(profile=profile, env=env)
        if profile is None:
            profile = self.current.profile
        filename = path(dirname) / ('%s.xml' % profile)
        element.writexml(filename.open('w'), indent='\t', newl='\n',
                         addindent='\t')
        
    
    def import_all_profiles(self, dirname):
        dirname = path(dirname)
        files = [p for p in dirname.listdir() if p.endswith('.xml')]
        for filename in files:
            self.import_profile(filename)
            

    def export_all_profiles(self, dirname):
        for profile in self.get_profile_list():
            self.export_profile(dirname, profile=profile)
            
    
    
#class Profile(object):
#    def __init__(self, conn):
#        object.__init__(self)
#        self.conn = conn
#        self.current = None
#        
#    def set_profile(self, profile):
#        self.current = profile
        
    
if __name__ == '__main__':
    pass

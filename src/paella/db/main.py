import os
from os.path import join, dirname, isdir
#from sets import Set

from xml.dom.minidom import Element
from xml.dom.minidom import parse as parse_file

from useless.base.util import makepaths, ujoin
from useless.base import Error, UnbornError
from useless.db.midlevel import StatementCursor

from paella.db.schema.paellascheme import insert_packages, make_suite
from paella.db.schema.paellascheme import start_schema

from trait import Trait
from trait.main import TraitsElement
from trait.relations import TraitPackage, TraitParent
from trait.relations import TraitTemplate
from family import Family
from profile import Profile, ProfileTrait
from profile.xmlgen import PaellaProfiles

from xmlgen import SuiteElement, SuitesElement
from xmlparse import PaellaParser, ProfileParser
#from xmlparse import PaellaParser, ProfilesParser, ProfileParser
#from xmlgen import EnvironElement, SuitesElement
#from xmlgen import SuiteElement, ProfileElement
#from xmlgen import ProfileVariableElement

#generate xml        
class PaellaDatabase(Element):
    def __init__(self, conn, path='/'):
        Element.__init__(self, 'paelladatabase')
        self.conn = conn
        self.stmt = StatementCursor(self.conn)
        self._profile_traits_ = ProfileTrait(self.conn)
        self.path = path
        self.suites = SuitesElement()
        self.appendChild(self.suites)
        for row in self._suite_rows():
            args = map(str, [row.suite, row.nonus, row.updates, row.local, row.common])
            element = SuiteElement(*args)
            self.suites.appendChild(element)
        self.profiles = PaellaProfiles(self.conn)
        self.family = Family(self.conn)
        suites = [x.suite for x in self._suite_rows()]
        for suite in suites:
            self.appendChild(TraitsElement(self.conn, suite))

    def _suite_rows(self):
        return self.stmt.select(table='suites', order='suite')

    def write(self, filename):
        path = join(self.path, filename)
        xmlfile = file(path, 'w')
        self.writexml(xmlfile, indent='\t', newl='\n', addindent='\t')

    def backup(self, path=None):
        if path is None:
            path = self.path
        if not isdir(path):
            raise Error, '%s not a directory' % path
        dbfile = file(join(path, 'database.xml'), 'w')
        self.writexml(dbfile, indent='\t', newl='\n', addindent='\t')
        dbfile.close()
        self.backup_profiles(path)
        self.backup_families(path)
        suites = [x.suite for x in self._suite_rows()]
        for suite in suites:
            makepaths(join(path, suite))
            trait = Trait(self.conn, suite)
            for t in trait.get_trait_list():
                trait.set_trait(t)
                trait.backup_trait(join(path, suite))

    def backup_profiles(self, path=None):
        profiles_dir = join(path, 'profiles')
        makepaths(profiles_dir)
        self.profiles.export_profiles(profiles_dir)

    def backup_families(self, path=None):
        fpath = join(path, 'families')
        makepaths(fpath)
        self.family.export_families(fpath)
        
        
        
class PaellaProcessor(object):
    def __init__(self, conn, cfg=None):
        object.__init__(self)
        self.conn = conn
        self.cfg = cfg
        self.__set_cursors__()
        self.main_path = None
        
    def parse_xml(self, filename):
        self.dbdata = PaellaParser(filename)
        self.main_path = dirname(filename)

    def start_schema(self):
        start_schema(self.conn)
        self._sync_suites()

    def _sync_suites(self):
        self.main.set_table('suites')
        current_suites = [row.suite for row in self.main.select()]
        for suite in self.dbdata.suites:
            if suite.name not in current_suites:
                self.main.insert(data=suite)
                make_suite(self.main, suite.name)
                insert_packages(self.cfg, self.main, suite.name, quick=False)
            else:
                self.main.update(data=suite)

    def insert_families(self):
        path = join(self.main_path, 'families')
        print 'path is in insert_families', path
        self.family.import_families(path)
        
        
    def insert_profiles(self):
        path = join(self.main_path, 'profiles')
        print 'path is in insert_profiles', path
        xmlfiles = [join(path, x) for x in os.listdir(path) if x[-4:] == '.xml']
        profiles = PaellaProfiles(self.conn)
        for xmlfile in xmlfiles:
            xml = parse_file(xmlfile)
            elements = xml.getElementsByTagName('profile')
            if len(elements) != 1:
                raise Error, 'bad profile number %s' % len(elements)
            element = elements[0]
            parsed = ProfileParser(element)
            profiles.insert_profile(parsed)
        

    def insert_profile(self, profile):
        idata = {'profile' : profile.name,
                 'suite' : profile.suite}
        self.main.insert(table='profiles', data=idata)
        idata = {'profile' : profile.name,
                 'trait' : None,
                 'ord' : 0}
        for trait, ord in profile.traits:
            print trait, ord
            idata['trait'] = trait
            idata['ord'] = ord #str(ord)
            self.main.insert(table='profile_trait', data=idata)
        idata = {'profile' : profile.name,
                 'trait' : None,
                 'name' : None,
                 'value': None}
        for trait, name, value in profile.vars:
            idata['trait'] = trait
            idata['name'] = name
            idata['value'] = value
            self.main.insert(table='profile_variables', data=idata)
    

    def insert_traits(self, suite):
        self.__set_suite_cursors__(suite)
        traits = [trait for trait in self.dbdata.get_traits(suite)]
        self._insert_traits_(traits, suite)

    def _clear_traits(self, suite):
        self.__set_suite_cursors__(suite)
        self.traitparent.cmd.delete()
        self.traitpackage.cmd.delete()
        self.main.delete(table=ujoin(suite, 'variables'))
        self.traits.delete()

    def _insert_traits_(self, traits, suite):
        while len(traits):
            trait = traits[0]
            print 'inserting %s' %trait, len(traits)
            try:
                self._insert_trait_(trait, suite)
            except UnbornError:
                traits.append(trait)
            del traits[0]
            
    def _insert_trait_(self, trait, suite):
        traitdb = Trait(self.conn, suite)
        #path = join(self.main_path, suite, trait + '.tar')
        path = join(self.main_path, suite, trait)
        traitdb.insert_trait(path, suite)
        
        
    def __set_cursors__(self):
        self.main = StatementCursor(self.conn, 'main_paella_cursor')
        self.all_traits = StatementCursor(self.conn, 'all_traits')
        self.all_traits.set_table('traits')

    def __set_suite_cursors__(self, suite):
        self.traits = StatementCursor(self.conn, 'traits')
        self.traits.set_table(ujoin(suite, 'traits'))
        self.traitparent = TraitParent(self.conn, suite)
        self.traitpackage = TraitPackage(self.conn, suite)
        self.traittemplate = TraitTemplate(self.conn, suite)
        self.family = Family(self.conn)
        

    def create(self, filename):
        self.parse_xml(filename)
        self.start_schema()
        for suite in self.dbdata.suites:
            self.insert_traits(suite.name)
        self.insert_families()
        self.insert_profiles()


if __name__ == '__main__':
    pass

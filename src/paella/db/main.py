import os

from xml.dom.minidom import Element
from xml.dom.minidom import parse as parse_file

from useless.base.util import makepaths, ujoin
from useless.base import Error, UnbornError
from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq

from paella.base import PaellaConfig

from paella.db.schema.main import start_schema
from paella.db.schema.suitehandler import SuiteHandler

from trait import Trait
from trait.main import TraitsElement
from trait.relations import TraitPackage, TraitParent
from trait.relations import TraitTemplate

from family import Family

from profile import Profile, ProfileTrait
from profile.xmlgen import PaellaProfiles
from profile.xmlparse import ProfileParser

from machine import MachineHandler

from xmlgen import AptSourceElement, AptSourceListElement
from xmlgen import SuiteElement, SuitesElement, SuiteAptElement
from xmlparse import PaellaParser

# imports for ClientManager
from useless.base.config import Configuration

#generate xml        
class PaellaDatabase(Element):
    def __init__(self, conn, path='/'):
        Element.__init__(self, 'paelladatabase')
        self.conn = conn
        self.stmt = StatementCursor(self.conn)
        self._profile_traits_ = ProfileTrait(self.conn)
        self.path = path
        self.aptsources = AptSourceListElement()
        self.appendChild(self.aptsources)
        if 'apt_sources' in self.stmt.tables():
            for row in self.stmt.select(table='apt_sources', order=['apt_id']):
                element = AptSourceElement(row.apt_id, row.uri, row.dist, row.sections,
                                           row.local_path)
                self.aptsources.appendChild(element)
            self.suites = SuitesElement()
            self.appendChild(self.suites)
            for row in self._suite_rows():
                args = map(str, [row.suite, row.nonus, row.updates, row.local, row.common])
                element = SuiteElement(*args)
                for suiteapt in self.stmt.select(table='suite_apt_sources', order=['ord'],
                                                 clause=Eq('suite', row.suite)):
                    element.appendChild(SuiteAptElement(row.suite,
                                                        suiteapt.apt_id, str(suiteapt.ord)))
                self.suites.appendChild(element)
        else:
            print 'WARNING, apt_sources table does not exist, backing up anyway'
        self.profiles = PaellaProfiles(self.conn)
        self.family = Family(self.conn)
        suites = [x.suite for x in self._suite_rows()]
        for suite in suites:
            self.appendChild(TraitsElement(self.conn, suite))

    def _suite_rows(self):
        return self.stmt.select(table='suites', order='suite')

    def write(self, filename):
        path = os.path.join(self.path, filename)
        xmlfile = file(path, 'w')
        self.writexml(xmlfile, indent='\t', newl='\n', addindent='\t')

    def backup(self, path=None):
        if path is None:
            path = self.path
        if not os.path.isdir(path):
            raise Error, '%s not a directory' % path
        dbfile = file(os.path.join(path, 'database.xml'), 'w')
        self.writexml(dbfile, indent='\t', newl='\n', addindent='\t')
        dbfile.close()
        self.backup_profiles(path)
        self.backup_families(path)
        suites = [x.suite for x in self._suite_rows()]
        for suite in suites:
            makepaths(os.path.join(path, suite))
            trait = Trait(self.conn, suite)
            for t in trait.get_trait_list():
                trait.set_trait(t)
                trait.export_trait(os.path.join(path, suite))

    def backup_profiles(self, path=None):
        profiles_dir = os.path.join(path, 'profiles')
        makepaths(profiles_dir)
        self.profiles.export_profiles(profiles_dir)

    def backup_families(self, path=None):
        fpath = os.path.join(path, 'families')
        makepaths(fpath)
        self.family.export_families(fpath)
        
        
        
class PaellaProcessor(object):
    def __init__(self, conn, cfg=None):
        object.__init__(self)
        self.conn = conn
        self.cfg = cfg
        self.__set_cursors__()
        self.main_path = None
        self.suitehandler = SuiteHandler(self.conn, self.cfg)
        
    def parse_xml(self, filename):
        self.dbdata = PaellaParser(filename)
        self.main_path = os.path.dirname(filename)

    def start_schema(self):
        start_schema(self.conn)
        self._insert_aptsources()
        self._sync_suites()

    def _sync_suites(self):
        self.main.set_table('suites')
        current_suites = [row.suite for row in self.main.select()]
        for suite in self.dbdata.suites:
            if suite.name not in current_suites:
                self.main.insert(data=suite)
                for apt in suite.aptsources:
                    data = dict(suite=suite.name, apt_id=apt.apt_id, ord=apt.order)
                    self.main.insert(table='suite_apt_sources', data=data)
                self.suitehandler.set_suite(suite.name)
                self.suitehandler.make_suite()
            else:
                raise Error, '%s already exists.' % suite
                #self.main.update(data=suite)

    def _insert_aptsources(self):
        for apt in self.dbdata.aptsources:
            data = dict(apt_id=apt.apt_id, uri=apt.uri, dist=apt.dist,
                        sections=apt.sections, local_path=apt.local_path)
            self.main.insert(table='apt_sources', data=data)
            
    
    def insert_families(self):
        path = os.path.join(self.main_path, 'families')
        print 'path is in insert_families', path
        self.family.import_families(path)
        
        
    def insert_profiles(self):
        path = os.path.join(self.main_path, 'profiles')
        print 'path is in insert_profiles', path
        xmlfiles = [os.path.join(path, x) for x in os.listdir(path) if x[-4:] == '.xml']
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
        missing = self._find_missing_packages(suite, traits)
        if missing:
            print 'missing these packages in suite', suite
            self._make_missing_packages_report(missing)
            raise RuntimeError, 'Missing packages declared in suite %s' % suite
        else:
            self._insert_traits_(traits, suite)

    def _make_missing_packages_report(self, missing):
        traits = missing.keys()
        traits.sort()
        for t in traits:
            print '%s:' % t
            for p in missing[t]:
                print '\t%s' % p
        
    def _find_missing_packages(self, suite, traits):
        missing = dict()
        tdb = Trait(self.conn, suite)
        print suite, traits
        for trait in traits:
            path = self._get_trait_path(suite, trait)
            traitxml = tdb.parse_trait_xml(path, suite=suite)
            missing_list = tdb.find_missing_packages(traitxml)
            if missing_list:
                #print 'in trait,', trait, ', missing packages:  ', missing_list
                missing[trait] = missing_list
        return missing
    
    def _clear_traits(self, suite):
        self.__set_suite_cursors__(suite)
        self.traitparent.cmd.delete()
        self.traitpackage.cmd.delete()
        self.main.delete(table=ujoin(suite, 'variables'))
        self.traits.delete()

    def _get_trait_path(self, suite, trait):
        return os.path.join(self.main_path, suite, trait)
    
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
        path = self._get_trait_path(suite, trait)
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
        # use the machine handler to insert
        # machine types and such
        if os.path.isfile(os.path.join(self.main_path, 'machine_database.xml')):
            mh = MachineHandler(self.conn)
            mh.restore_machine_database(self.main_path)

class DatabaseManager(object):
    def __init__(self, conn):
        self.cfg = PaellaConfig()
        self.conn = conn
        self.import_dir = self.cfg.get('database', 'import_path')
        self.export_dir = self.cfg.get('database', 'export_path')

    def backup(self, path):
        if not os.path.isdir(path):
            raise Error, 'argument needs to be a directory'
        pdb = PaellaDatabase(self.conn, path)
        pdb.backup(path)
        mh = MachineHandler(self.conn)
        mh.export_machine_database(path)

    def restore(self, path):
        if not os.path.isdir(path):
            raise Error, 'argument needs to be a directory'
        dbpath = os.path.join(path, 'database.xml')
        mdbpath = os.path.join(path, 'machine_database.xml')
        pp = PaellaProcessor(self.conn, self.cfg)
        pp.create(dbpath)


if __name__ == '__main__':
    pass


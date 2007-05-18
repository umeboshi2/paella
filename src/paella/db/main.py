import os

from xml.dom.minidom import Element
from xml.dom.minidom import parse as parse_file

from useless.base.util import makepaths, ujoin
from useless.base.path import path
from useless.base import Error, UnbornError
from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq

from paella.base import PaellaConfig

from paella.db import DefaultEnvironment
from paella.db import CurrentEnvironment

from paella.db.schema.main import start_schema
from paella.db.schema.main import AlreadyPresentError

from trait import Trait
from trait.main import TraitsElement
from trait.relations.parent import TraitParent
from trait.relations.package import TraitPackage
from trait.relations.template import TraitTemplate

from family import Family

from profile import Profile, ProfileTrait
from profile.xmlgen import PaellaProfiles
from profile.xmlparse import ProfileParser

from machine import MachineHandler

from xmlgen import AptSourceElement, AptSourceListElement
from xmlgen import SuiteElement, SuitesElement, SuiteAptElement
from xmlparse import PaellaParser

from aptsrc import AptSourceHandler
from base import SuiteCursor
# imports for ClientManager
from useless.base.config import Configuration

class MissingPackagesError(RuntimeError):
    pass


def report_missing_packages(missing):
    traits = missing.keys()
    traits.sort()
    report = 'These packages for these traits do not exist.\n'
    for trait in traits:
        report += 'trait %s:\n' % trait
        for package in missing[trait]:
            report += '\t%s\n' % package
            
    return report

class TraitsElement(Element):
    def __init__(self, suite):
        Element.__init__(self, 'traits')
        self.suite = suite
        self.setAttribute('suite', self.suite)

    def append_trait(self, trait):
        element = Element('trait')
        element.setAttribute('name', trait)
        self.appendChild(element)
        
class PaellaDatabaseElement(Element):
    def __init__(self):
        Element.__init__(self, 'paelladatabase')
        self.aptsources = AptSourceListElement()
        self.appendChild(self.aptsources)
        self.suites_element = SuitesElement()
        self.suites = {}
        self.suite_traits = {}
        self.appendChild(self.suites_element)
        
    def append_apt_source(self, apt_id, uri, dist, sections, local_path):
        element = AptSourceElement(apt_id, uri, dist, sections, local_path)
        self.aptsources.appendChild(element)
        
    def append_suite(self, suite):
        element = SuiteElement(suite)
        self.suites[suite] = element
        self.suites_element.appendChild(element)

    def append_suite_apt_source(self, suite, apt_id, order):
        element = SuiteAptElement(suite, apt_id, order)
        self.suites[suite].appendChild(element)

    def append_suite_traits(self, suite, traits=[]):
        element = TraitsElement(suite)
        self.suite_traits[suite] = element
        for trait in traits:
            self.append_trait(suite, trait)
        self.appendChild(element)

    def append_trait(self, suite, trait):
        self.suite_traits[suite].append_trait(trait)
        
class PaellaExporter(object):
    def __init__(self, conn):
        self.conn = conn
        self.cursor = self.conn.cursor(statement=True)
        self.suitecursor = SuiteCursor(self.conn)
        self.init_db_element()
        if len(self.cursor.tables()):
            self.setup_cursors()
            
    def setup_cursors(self):
        self.profile = Profile(self.conn)
        self.family = Family(self.conn)
        self.machines = MachineHandler(self.conn)

    def init_db_element(self):
        self.dbelement = PaellaDatabaseElement()
        

    def make_complete_db_element(self):
        self.init_db_element()
        self._append_apt_sources_to_db_element()
        fields = ['suite']
        for suite in self.suitecursor.get_suites():
            self._append_suite_to_db_element(suite)
            
    def _append_apt_sources_to_db_element(self):
        rows = self.cursor.select(table='apt_sources', order=['apt_id'])
        for row in rows:
            self.dbelement.append_apt_source(row.apt_id, row.uri, row.dist,
                                             row.sections, row.local_path)
            
    def _append_suite_to_db_element(self, suite):
        self.dbelement.append_suite(suite)
        rows = self.cursor.select(table='suite_apt_sources', order=['ord'],
                                  clause=Eq('suite', suite))
        for row in rows:
            self.dbelement.append_suite_apt_source(row.suite, row.apt_id,
                                                   str(row.ord))
        rows = self.cursor.select(fields=['trait'], table='%s_traits' % suite,
                                  order=['trait'])
        traits = [row.trait for row in rows]
        self.dbelement.append_suite_traits(suite, traits=traits)
        
    
    def set_db_export_path(self, dirname):
        self.db_export_path = path(dirname)

    def export_db_element(self, dirname=None, filename='database.xml'):
        if dirname is None:
            dirname = self.db_export_path
        filename = path(dirname) / filename
        dbfile = filename.open('w')
        self.dbelement.writexml(dbfile, indent='\t', newl='\n', addindent='\t')                                
        dbfile.close()
        
        
    def _make_suite_export_path(self, suite):
        suitedir = self.db_export_path / suite
        makepaths(suitedir)
        return suitedir
    
    def export_all_profiles(self, dirname=None):
        if dirname is None:
            dirname = self.db_export_path / 'profiles'
        makepaths(dirname)
        profiles = self.profile.get_profile_list()
        self.report_total_profiles(len(profiles))
        env = self.profile.make_environment_object()
        for profile in profiles:
            env.set_profile(profile)
            self.profile.export_profile(dirname, profile=profile, env=env)
            self.report_profile_exported(profile)
            

    def export_all_families(self, dirname=None):
        if dirname is None:
            dirname = self.db_export_path / 'families'
        makepaths(dirname)
        self.family.export_families(dirname)

    def export_trait(self, trait, suite=None, dirname=None, traitdb=None):
        if traitdb is None:
            if suite is None:
                RuntimeError, "you must pass a suite if you don't pass a Trait object"
            print "make new traitdb"
            traitdb = Trait(self.conn, suite)
        traitdb.set_trait(trait)
        if suite is None:
            suite = traitdb.suite
        if dirname is None:
            dirname = self._make_suite_export_path(suite)
        traitdb.export_trait(dirname)
        self.report_trait_exported(trait, dirname)
        

    def export_all_traits(self, suite, dirname=None):
        self.report_start_exporting_traits()
        traitdb = Trait(self.conn, suite)
        traits = traitdb.get_trait_list()
        self.report_total_traits(len(traits))
        for trait in traits:
            self.export_trait(trait, dirname=dirname, traitdb=traitdb)
        #self.report_all_traits_exported()
            
    def export_suite(self, suite, dirname=None):
        self.export_all_traits(suite, dirname=dirname)

    def export_all_suites(self, dirname=None):
        suites = self.suitecursor.get_suites()
        self.report_total_suites(len(suites))
        for suite in suites:
            self.report_exporting_suite(suite)
            self.export_suite(suite, dirname=dirname)
            self.report_suite_exported(suite)

    def export_machine_database(self, dirname=None):
        if dirname is None:
            dirname = self.db_export_path
        else:
            dirname = path(dirname)
        self.machines.export_machine_database(dirname)
                                
    def _export_environment_common(self, dirname, envtype):
        if dirname is None:
            dirname = self.db_export_path
        else:
            dirname = path(dirname)
        if envtype == 'default':
            envclass = DefaultEnvironment
        elif envtype == 'current':
            envclass = CurrentEnvironment
        else:
            raise RuntimeError, 'bad envtype %s' % envtype
        env = envclass(self.conn)
        #filename = os.path.join(path, '%s-environment' % envtype)
        #efile = file(filename, 'w')
        #env.write(efile)
        #efile.close()
        filename = '%s-environment' % envtype
        fullname = dirname / filename
        env.write(fullname.open('w'))
        
    def export_default_environment(self, path=None):
        self._export_environment_common(path, 'default')
        
    def export_current_environment(self, path=None):
        self._export_environment_common(path, 'common')

    def perform_full_export(self, path):
        self.make_complete_db_element()
        self.set_db_export_path(path)
        self.export_db_element()
        self.export_all_suites()
        self.export_all_profiles()
        self.export_all_families()
        self.export_machine_database()
        self.export_default_environment()
        

    ###################
    # reporting methods
    ####################
    def report_total_suites(self, total):
        print 'exporting %d suites' % total

    def report_exporting_suite(self, suite):
        print 'exporting suite %s' % suite
        
    def report_suite_exported(self, suite):
        print 'suite %s exported'
        
    def report_total_traits(self, total):
        print 'exporting %d traits' % total

    def report_trait_exported(self, trait, path):
        print 'trait %s exported to %s' % (trait, path)

    def report_all_traits_exported(self, *args):
        print 'all traits exported'

    def report_start_exporting_traits(self):
        print 'starting to export traits'

    def report_total_profiles(self, total):
        print 'exporting %d profiles' % total

    def report_profile_exported(self, profile):
        print 'profile %s exported' % profile

class PaellaImporter(object):
    def __init__(self, conn):
        self.conn = conn
        self.suitecursor = SuiteCursor(self.conn)
        self.aptsrc = AptSourceHandler(self.conn)
        self.main_path = None
        self.profile = Profile(self.conn)
        self.family = Family(self.conn)
        
    def set_main_path(self, dirname):
        self.main_path = path(dirname)
        
    def parse_main_xml(self, filename=None):
        if filename is None:
            filename = self.main_path / 'database.xml'
        parsed = PaellaParser(filename)
        return parsed

    def start_schema(self):
        try:
            start_schema(self.conn)
        except AlreadyPresentError:
            print "primary tables already present"

    def import_all_families(self, dirname=None):
        if dirname is None:
            dirname = self.main_path / 'families'
        xmlfiles = dirname.listdir('*.xml')
        self.report_total_families(len(xmlfiles))
        while xmlfiles:
            familyxml = xmlfiles.pop(0)
            try:
                self.import_family(familyxml)
            except UnbornError:
                xmlfiles.append(familyxml)
                
            
        print 'import families from', dirname
        

    def import_family(self, filename):
        self.family.import_family_xml(filename)
        self.report_family_imported(filename.namebase)
        
    
    def import_all_profiles(self, dirname=None):
        if dirname is None:
            dirname = self.main_path / 'profiles'
        dirname = path(dirname)
        xmlfiles = dirname.listdir('*.xml')
        self.report_total_profiles(len(xmlfiles))
        for xmlfile in xmlfiles:
            self.profile.import_profile(xmlfile)
            self.report_profile_imported(xmlfile.namebase)
            
    
    # here suite is a parsed xml object (find name)
    def make_suite(self, suite):
        current_suites = self.suitecursor.get_suites()
        if suite.name not in current_suites:
            apt_ids = [e.apt_id for e in suite.aptsources]
            self.suitecursor.make_suite(suite.name, apt_ids)
        else:
            raise RuntimeError, 'suite %s already exists' % suite

    # aptsources is the PaellaParser.aptsources attribute
    def import_apt_sources(self, aptsources):
        self.report_total_apt_sources(len(aptsources))
        for apt in aptsources:
            self.import_parsed_apt_source(apt)
            
    # here apt is an AptSourceParser object
    def import_parsed_apt_source(self, apt):
        self.report_importing_aptsrc(apt.apt_id)
        self.aptsrc.insert_apt_source_row(apt.apt_id, apt.uri, apt.dist,
                                          apt.sections, apt.local_path)
        self.aptsrc.insert_packages(apt.apt_id)
        self.report_aptsrc_imported(apt.apt_id)
        

    def _import_traits(self, suite, traitlist, dirname):
        self.report_total_traits(len(traitlist))
        missing = self._find_missing_packages(suite, traitlist, dirname)
        if missing:
            self.report_missing_packages(missing)
            raise MissingPackagesError, report_missing_packages(missing)
        else:
            while len(traitlist):
                trait = traitlist.pop(0)
                try:
                    self._import_trait(suite, dirname / trait)
                    self.report_trait_imported(trait)
                except UnbornError:
                    traitlist.append(trait)

    # the dirname here must have the trait.xml and
    # scripts and templates for the trait
    def _import_trait(self, suite, dirname):
        traitdb = Trait(self.conn, suite)
        traitdb.insert_trait(dirname, suite)
        
    def _find_missing_packages(self, suite, traits, dirname):
        missing = dict()
        traitdb = Trait(self.conn, suite)
        for trait in traits:
            tdir = dirname / trait
            traitxml = traitdb.parse_trait_xml(tdir, suite=suite)
            missing_list = traitdb.find_missing_packages(traitxml)
            if missing_list:
                missing[trait] = missing_list
        return missing
    

    def perform_full_import(self, dirname):
        self.set_main_path(dirname)
        dbdata = self.parse_main_xml()
        self.start_schema()
        self.import_apt_sources(dbdata.aptsources)
        self.report_total_suites(len(dbdata.suites))
        for suite in dbdata.suites:
            self.make_suite(suite)
            suitedir = self.main_path / suite.name
            self._import_traits(suite.name, dbdata.get_traits(suite.name), suitedir)
            self.report_suite_imported(suite.name)
            
        self.import_all_families()
        self.import_all_profiles()
        machinedb = self.main_path / 'machine_database.xml'
        if machinedb.isfile():
            mh = MachineHandler(self.conn)
            mh.restore_machine_database(self.main_path)
            
            
        
    
    def report_missing_packages(self, missing):
        print report_missing_packages(missing)
        
    def report_total_apt_sources(self, total):
        print 'importing %d apt sources' % total

    def report_importing_aptsrc(self, apt_id):
        print 'importing %s' % apt_id
        
    def report_aptsrc_imported(self, apt_id):
        print 'apt source %s imported' % apt_id

    def report_total_suites(self, total):
        print 'importing %d suites' % total

    def report_importing_suite(self, suite):
        print 'importing suite %s' % suite
        
    def report_suite_imported(self, suite):
        print 'suite %s imported' % suite

    def report_total_traits(self, total):
        print 'importing %d traits' % total

    def report_importing_trait(self, trait, numtraits):
        print 'importing trait', trait

    def report_trait_imported(self, trait, numtraits):
        print 'trait %s imported' % trait

    def report_total_families(self, total):
        print 'importing %d families' % total

    def report_family_imported(self, family):
        print 'family %s imported' % family

    def report_total_profiles(self, total):
        print 'importing %d profiles' % total

    def report_profile_imported(self, profile):
        print 'profile %s imported' % profile
        
#generate xml        
        
class PaellaProcessor(object):
    def __init__(self, conn, cfg=None):
        object.__init__(self)
        self.conn = conn
        self.cfg = cfg
        self.__set_cursors__()
        self.main_path = None
        self.suitecursor = SuiteCursor(self.conn)
        self.aptsrc = AptSourceHandler(self.conn)
        
        
    def parse_xml(self, filename):
        self.dbdata = PaellaParser(filename)
        self.main_path = os.path.dirname(filename)

    def start_schema(self):
        try:
            start_schema(self.conn)
        except AlreadyPresentError:
            print "primary tables already present"
            pass
        
    def insert_apt_sources(self):
        self._insert_aptsources()

    def _sync_suites(self):
        self.main.set_table('suites')
        current_suites = [row.suite for row in self.main.select()]
        for suite in self.dbdata.suites:
            if suite.name not in current_suites:
                apt_ids = [e.apt_id for e in suite.aptsources]
                self.suitecursor.make_suite(suite.name, apt_ids)
            else:
                raise Error, '%s already exists.' % suite
                #self.main.update(data=suite)

    def _insert_aptsources(self):
        for apt in self.dbdata.aptsources:
            self.aptsrc.insert_apt_source_row(apt.apt_id, apt.uri, apt.dist,
                                              apt.sections, apt.local_path)
            self.aptsrc.insert_packages(apt.apt_id)
            
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
        self.insert_apt_sources()
        self._sync_suites()
        
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
        default_path = path(self.cfg.get('database', 'default_path')).expand()
        self.import_dir = default_path
        self.export_dir = default_path
        #self.importer = PaellaProcessor(self.conn, self.cfg)
        #self.exporter = PaellaDatabase(self.conn, '/')
        self.exporter = PaellaExporter(self.conn)
        self.importer = PaellaImporter(self.conn)
        
    def export_all(self, path):
        self.exporter.perform_full_export(path)

    def import_all(self, dirname):
        self.importer.perform_full_import(dirname)
        
        
    def restore(self, path):
        if not os.path.isdir(path):
            raise Error, 'argument needs to be a directory'
        dbpath = os.path.join(path, 'database.xml')
        mdbpath = os.path.join(path, 'machine_database.xml')
        pp = PaellaProcessor(self.conn, self.cfg)
        pp.create(dbpath)


if __name__ == '__main__':
    pass


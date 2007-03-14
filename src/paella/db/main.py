import os

from xml.dom.minidom import Element
from xml.dom.minidom import parse as parse_file

from useless.base.util import makepaths, ujoin
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
        self.profiles = PaellaProfiles(self.conn)
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
        
    
    def set_db_export_path(self, path):
        self.db_export_path = path

    def export_db_element(self, dirname=None, filename='database.xml'):
        if dirname is None:
            dirname = self.db_export_path
        dbfile = file(os.path.join(dirname, filename), 'w')
        self.dbelement.writexml(dbfile, indent='\t', newl='\n', addindent='\t')
        dbfile.close()
        
        
    def _make_suite_export_path(self, suite):
        path = os.path.join(self.db_export_path, suite)
        makepaths(path)
        return path
    
    def export_all_profiles(self, path=None):
        if path is None:
            path = os.path.join(self.db_export_path, 'profiles')
        makepaths(path)
        self.profiles.export_profiles(path)

    def export_all_families(self, path=None):
        if path is None:
            path = os.path.join(self.db_export_path, 'families')
        makepaths(path)
        self.family.export_families(path)

    def export_trait(self, trait, suite=None, path=None, traitdb=None):
        if traitdb is None:
            if suite is None:
                RuntimeError, "you must pass a suite if you don't pass a Trait object"
            traitdb = Trait(self.conn, suite)
        traitdb.set_trait(trait)
        if suite is None:
            suite = traitdb.suite
        if path is None:
            path = self._make_suite_export_path(suite)
        traitdb.export_trait(path)

    def export_all_traits(self, suite, path=None):
        self.report_start_exporting_traits()
        traitdb = Trait(self.conn, suite)
        traits = traitdb.get_trait_list()
        self.report_total_traits(len(traits))
        for trait in traits:
            self.export_trait(trait, path=path, traitdb=traitdb)
            self.report_trait_exported(trait, path)
        #self.report_all_traits_exported()
            
    def export_suite(self, suite, path=None):
        self.export_all_traits(suite, path=path)

    def export_all_suites(self, path=None):
        suites = self.suitecursor.get_suites()
        self.report_total_suites(len(suites))
        for suite in suites:
            self.export_suite(suite, path=path)
            self.report_suite_exported(suite)

    def export_machine_database(self, path=None):
        if path is None:
            path = self.db_export_path
        self.machines.export_machine_database(path)
                                
    def _export_environment_common(self, path, envtype):
        if path is None:
            path = self.db_export_path
        if envtype == 'default':
            envclass = DefaultEnvironment
        elif envtype == 'current':
            envclass = CurrentEnvironment
        else:
            raise RuntimeError, 'bad envtype %s' % envtype
        env = envclass(self.conn)
        filename = os.path.join(path, '%s-environment' % envtype)
        efile = file(filename, 'w')
        env.write(efile)
        efile.close()
        
    def export_default_environment(self, path=None):
        self._export_environment_common(path, 'default')
        
    def export_current_environment(self, path=None):
        self._export_environment_common(path, 'common')

    ###################
    # reporting methods
    ####################
    def report_total_suites(self, total):
        print 'exporting %d suites' % total

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

class PaellaImporter(object):
    def __init__(self):
        self.conn = conn
        self.suitecursor = SuiteCursor(self.conn)
        self.aptsrc = AptSourceHandler(self.conn)
        self.main_path = None

    def set_main_path(self, dirname):
        self.main_path = dirname
        
    def parse_main_xml(self, filename=None):
        if filename is None:
            filename = os.path.join(self.main_path, 'database.xml')
        parsed = PaellaParser(filename)
        return parsed

    def start_schema(self):
        try:
            start_schema(self.conn)
        except AlreadyPresentError:
            print "primary tables already present"

    def import_all_families(self, dirname):
        pass
    
    def make_suite(self):
        pass

            
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
        default_path = self.cfg.get('database', 'default_path')
        self.import_dir = default_path
        self.export_dir = default_path
        self.importer = PaellaProcessor(self.conn, self.cfg)
        #self.exporter = PaellaDatabase(self.conn, '/')
        self.exporter = PaellaExporter(self.conn)

    def export_all(self, path):
        self.exporter.make_complete_db_element()
        self.exporter.set_db_export_path(path)
        self.exporter.export_db_element()
        self.exporter.export_all_suites()
        self.exporter.export_all_profiles()
        self.exporter.export_all_families()
        self.exporter.export_machine_database()
        
    def restore(self, path):
        if not os.path.isdir(path):
            raise Error, 'argument needs to be a directory'
        dbpath = os.path.join(path, 'database.xml')
        mdbpath = os.path.join(path, 'machine_database.xml')
        pp = PaellaProcessor(self.conn, self.cfg)
        pp.create(dbpath)


if __name__ == '__main__':
    pass


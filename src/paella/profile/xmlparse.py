from xml.dom.minidom import parse as parse_file
from xml.dom.minidom import parseString as parse_string

from paella.base import Error, debug
from paella.base.xmlfile import ParserHelper, DictElement

from xmlgen import EnvironElement

class SuiteParser(ParserHelper):
    def __init__(self, element):
        ParserHelper.__init__(self)
        self.__desc__ = ['suite', 'nonus', 'updates', 'local', 'common']
        name = element.tagName.encode()
        if name != 'suite':
            raise Error, 'bad tag fro SuiteParser'
        for att in self.__desc__:
            if att == 'suite':
                setattr(self, 'name', self.get_attribute(element, 'name'))
                setattr(self, 'suite', self.get_attribute(element, 'name'))
            else:
                setattr(self, att, self.get_attribute(element, att))
        
        #self.name = self.get_attribute(element, 'name')
        #self.local = self.get_attribute(element, 'local')
        #self.nonus = self.get_attribute(element, 'nonus')
        #self.updates = self.get_attribute(element, 'updates')
        
    def __repr__(self):
        return 'SuiteParser: %s' % self.name

    def __getitem__(self, key):
        if key in self.__desc__:
            return getattr(self, key)
        else:
            raise Error, 'key error in SuiteParser'

    def __setitem__(self, key, value):
        if key in self.__desc__:
            if key == 'suite':
                setattr(self, 'name', value)
            setattr(self, key, value)
        else:
            raise Error, 'key error in SuiteParser'

    def keys(self):
        return [key for key in self.__desc__]

    def values(self):
        return [getattr(self, key) for key in self.__desc__]

    def items(self):
        return zip(self.__desc__, self.values())
    
    
    
#parse xml
class TraitParser(ParserHelper):
    def __init__(self, element):
        ParserHelper.__init__(self)
        name = element.tagName.encode()
        if name != 'trait':
            raise Error, 'bad tag'
        self.name = element.getAttribute('name').encode()
        self.suite = element.getAttribute('suite').encode()
        self.packages = {}
        self._get_packages(element)
        self.parents = []
        self._get_parents(element)
        self.environ = {}
        self._get_environ(element)
        self.templates = []
        self._get_templates(element)
        self.debconf = {}
        self._get_debconf(element)
        self.scripts = []
        self._get_scripts(element)
        
    def _get_packages(self, element):
        packages = self.get_elements_from_section(element, 'packages', 'package')
        for package in packages:
            action = package.getAttribute('action').encode().strip()
            pname = package.firstChild.data.encode().strip()
            self.packages[pname] = action
    
    def _get_parents(self, element):
        parents = self.get_elements_from_section(element, 'parents', 'parent')
        for parent in parents:
            self.parents.append(parent.firstChild.data.encode().strip())

    def _get_environ(self, element):
        environ = self._get_single_section(element, 'environ')
        if len(environ):
            env_element = EnvironElement({})
            env_element.reform(environ[0])
            self.environ = dict(env_element.items())

    def _get_templates(self, element):
        templates = self.get_elements_from_section(element, 'templates', 'template')
        for template in templates:
            value = template.firstChild.data.encode().strip()
            tdict = {}
            for field in ['package', 'mode', 'owner', 'grp_owner']:
                tdict[field] = template.getAttribute(field).encode().strip()
            self.templates.append([tdict['package'], value, tdict])

    def _get_debconf(self, element):
        debconf = self.get_elements_from_section(element, 'debconfiguration', 'debconf')
        for dc in debconf:
            dc_element = DictElement('debconf', {})
            dc_element.reform(dc)
            tdict = {}
            tdict.update(dc_element)
            self.debconf[tdict['name']] = tdict

    def _get_scripts(self, element):
        scripts = self.get_elements_from_section(element, 'scripts', 'script')
        for script in scripts:
            name = script.getAttribute('name').encode().strip()
            self.scripts.append(name)
            
                
class FamilyParser(ParserHelper):
    def __init__(self, element):
        ParserHelper.__init__(self)
        name = element.tagName.encode()
        if name != 'family':
            raise Error, 'bad tag: %s' % name
        self.name = element.getAttribute('name').encode()
        self.parents = self._parse_parents(element)
        self.environ = self._parse_environ(element)
        

    def _parse_parents(self, element):
        parents = self.get_elements_from_section(element, 'parents', 'parent')
        return [p.firstChild.data.encode().strip() for p in parents]
    
    def _parse_environ(self, element):
        vars = self.get_elements_from_section(element, 'environ', 'family_variable')
        rows = []
        for v in vars:
            trait = v.getAttribute('trait').encode()
            name = v.getAttribute('name').encode()
            value = v.firstChild.data.encode().strip()
            rows.append(dict(trait=trait, name=name, value=value))
        return rows
            
class TraitsParser(ParserHelper):
    def __init__(self, element):
        ParserHelper.__init__(self)
        name = element.tagName.encode()
        if name != 'traits':
            raise Error, 'bad tag for TraitsParser'
        self.suite = element.getAttribute('suite').encode()
        self.trait_elements = element.getElementsByTagName('trait')
        self.traits = [e.getAttribute('name').encode() for e in self.trait_elements]
        
        
        

class ProfileParser(ParserHelper):
    def __init__(self, element):
        ParserHelper.__init__(self)
        name = element.tagName.encode()
        if name != 'profile':
            raise Error, 'bad tag for profileparser'
        self.name = element.getAttribute('name').encode()
        self.suite = element.getAttribute('suite').encode()
        self.traits = []
        self._get_traits(element)
        self.families = []
        self._get_families(element)
        self.vars = []
        self._get_variables(element)
        
    def _get_variables(self, element):
        vars = self.get_elements_from_section(element, 'environ', 'profile_variable')
        for var in vars:
            trait = var.getAttribute('trait').encode()
            name = var.getAttribute('name').encode()
            value = var.firstChild.data.encode().strip()
            self.vars.append((trait, name, value))
        
    def _get_traits(self, element):
        traits = self.get_elements_from_section(element, 'traits', 'trait')
        for trait in traits:
            trait_ = trait.firstChild.data.encode().strip()
            ord = trait.getAttribute('ord').encode()
            self.traits.append([trait_, ord])

    def _get_families(self, element):
        families = self.get_elements_from_section(element, 'families', 'family')
        for family in families:
            fam = family.firstChild.data.encode().strip()
            self.families.append(fam)
            


class ProfilesParser(ParserHelper):
    def __init__(self, path):
        ParserHelper.__init__(self)
        f = file(path)
        self.xml = parse_file(f)
        f.close()
        
        name = self.xml.firstChild.tagName
        if name != 'profiles':
            raise Error, 'bad tag for ProfilesParser'
        element = self.xml.firstChild
        self.profile_elements = self.get_elements_from_section(self.xml, 'profiles',
                                                               'profile')
        self.profiles = [ProfileParser(element) for element in self.profile_elements]
        
        
    
class PaellaParser(ParserHelper):
    def __init__(self, filename):
        ParserHelper.__init__(self)
        f = file(filename)
        self.xml = parse_file(f)
        f.close()
        if self.xml.firstChild.tagName != 'paelladatabase':
            raise Error, 'bad type of xmlfile for PaellaParser'
        self.db_element = self.xml.firstChild
        self.suite_elements = self.get_elements_from_section(self.db_element, 'suites',
                                                             'suite')
        self.suites = [SuiteParser(element) for element in self.suite_elements]
        children = [node for node in self.db_element.childNodes]
        traits_elements = []
        for node in children:
            if hasattr(node, 'tagName') and node.tagName not in ['profiles', 'suites']:
                traits_elements.append(node)
        self.traits = [TraitsParser(element) for element in traits_elements]

    def get_traits(self, suite):
        traitslist = [x for x in self.traits if x.suite == suite]
        if len(traitslist) == 1:
            return traitslist[0].traits
        elif len(traitslist) > 1:
            raise Error, 'too many traits sections'
        else:
            return []
        
        
        
if __name__ == '__main__':
    pass

from xml.dom.minidom import parse as parse_file
from xml.dom.minidom import parseString as parse_string

from useless.base import Error, debug
from useless.base.xmlfile import ParserHelper, DictElement

from xmlgen import EnvironElement

#parse xml
class TraitParser(ParserHelper):
    def __init__(self, element):
        ParserHelper.__init__(self)
        name = element.tagName.encode()
        if name != 'trait':
            raise Error, 'bad tag'
        self.name = element.getAttribute('name').encode()
        self.suite = element.getAttribute('suite').encode()
        self.packages = []
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
            #self.packages[pname] = action
            self.packages.append((pname, action))
            
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
            
                
class TraitsParser(ParserHelper):
    def __init__(self, element):
        ParserHelper.__init__(self)
        name = element.tagName.encode()
        if name != 'traits':
            raise Error, 'bad tag for TraitsParser'
        self.suite = element.getAttribute('suite').encode()
        self.trait_elements = element.getElementsByTagName('trait')
        self.traits = [e.getAttribute('name').encode() for e in self.trait_elements]
        
        
        
if __name__ == '__main__':
    pass

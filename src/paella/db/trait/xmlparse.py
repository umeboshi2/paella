from xml.dom.minidom import parse as parse_file
from xml.dom.minidom import parseString as parse_string

from useless.base import Error, debug
from useless.base.xmlfile import ParserHelper, DictElement

from xmlgen import EnvironElement
from xmlgen import TraitVariableElement

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

    # This method is pretty ugly right now as there is a change of
    # format for the environ section in progress.  This method will
    # successfully parse both the old and new formats.
    # In the future, after enough time has passed, this will be cleaned up.
    def _get_environ(self, element):
        environ = self._get_single_section(element, 'environ')
        if len(environ):
            environ_element = environ[0]
            children = environ_element.childNodes
            # only count childNodes with tag names
            tagged_children = [e for e in children if hasattr(e, 'tagName')]
            num_children = len(tagged_children)
            if num_children:
                newtags = environ_element.getElementsByTagName('trait_variable')
                num_newtags = len(newtags)
                if num_newtags and num_newtags != num_children:
                    raise Error, "There are more elements than elements with tag trait_variable"
                if num_newtags:
                    print "parsing new trait_variable tags"
                    self.environ = {}
                    for child in tagged_children:
                        key = child.getAttribute('name')
                        value = child.firstChild.data.encode().strip()
                        self.environ[key] = value
                else:
                    print "This xmlfile needs updating to new trait_variable tags"
                    print "suite", self.suite, "name", self.name
                    env_element = EnvironElement({})
                    env_element.reform(environ[0])
                    self.environ = dict(env_element.items())

    def _get_templates(self, element):
        templates = self.get_elements_from_section(element, 'templates', 'template')
        for template in templates:
            template_name = template.firstChild.data.encode().strip()
            tdict = {}
            for field in ['mode', 'owner', 'grp_owner']:
                tdict[field] = template.getAttribute(field).encode().strip()
            self.templates.append([template_name, tdict])

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

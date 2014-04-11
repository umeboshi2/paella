from xml.dom.minidom import parse as parse_file
from xml.dom.minidom import parseString as parse_string

from useless.base import Error, debug
from useless.base.xmlfile import ParserHelper

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
            
if __name__ == '__main__':
    pass

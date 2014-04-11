from xml.dom.minidom import parse as parse_file
from xml.dom.minidom import parseString as parse_string

from useless.base import Error
from useless.base.xmlfile import ParserHelper

class ParseError(RuntimeError):
    pass

class BadFormatError(ParseError):
    pass

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


def parse_profile(filename):
    doc = parse_file(filename)
    elements = doc.getElementsByTagName('profile')
    if len(elements) != 1:
        raise BadFormatError, "%s is not a proper profile xml export"
    element = elements[0]
    return ProfileParser(element)

    
if __name__ == '__main__':
    pass

from xml.dom.minidom import parse as parse_file
from xml.dom.minidom import parseString as parse_string

from useless.base import Error, debug
from useless.base.xmlfile import ParserHelper, DictElement

from xmlgen import EnvironElement

from trait.xmlparse import TraitsParser

class AptSourceParser(ParserHelper):
    def __init__(self, element):
        ParserHelper.__init__(self)
        self.apt_id = self.get_attribute(element, 'apt_id')
        self.uri = self.get_attribute(element, 'uri')
        self.dist = self.get_attribute(element, 'dist')
        self.sections = self.get_attribute(element, 'sections')
        self.local_path = self.get_attribute(element, 'local_path')
                
    def __repr__(self):
        ml = '%s %s %s' % (self.uri, self.dist, self.sections)
        return 'AptSource(%s) %s -> %s' % (self.apt_id, ml, self.local_path)

class SuiteAptParser(ParserHelper):
    def __init__(self, element):
        ParserHelper.__init__(self)
        self.suite = self.get_attribute(element, 'suite')
        self.apt_id = self.get_attribute(element, 'apt_id')
        self.order = self.get_attribute(element, 'order')

    def __repr__(self):
        return 'SuiteApt (%s, %s) :%s' % (self.suite, self.apt_id, self.order)
    
class SuiteParser(ParserHelper):
    def __init__(self, element):
        ParserHelper.__init__(self)
        self.__desc__ = ['suite', 'nonus', 'updates', 'local', 'common']
        name = element.tagName.encode()
        if name != 'suite':
            raise Error, 'bad tag for SuiteParser'
        for att in self.__desc__:
            if att == 'suite':
                setattr(self, 'name', self.get_attribute(element, 'name'))
                setattr(self, 'suite', self.get_attribute(element, 'name'))
            else:
                setattr(self, att, self.get_attribute(element, att))
        aptlist = element.getElementsByTagName('suiteapt')
        self.aptsources = [SuiteAptParser(e) for e in aptlist]
        
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
    
    
class PaellaParser(ParserHelper):
    def __init__(self, filename):
        ParserHelper.__init__(self)
        f = file(filename)
        self.xml = parse_file(f)
        f.close()
        if self.xml.firstChild.tagName != 'paelladatabase':
            raise Error, 'bad type of xmlfile for PaellaParser'
        self.db_element = self.xml.firstChild
        self.aptsource_elements = self.get_elements_from_section(self.db_element,
                                                                 'aptsources', 'aptsource')
        self.aptsources = [AptSourceParser(e) for e in self.aptsource_elements]
        self.suite_elements = self.get_elements_from_section(self.db_element, 'suites',
                                                             'suite')
        self.suites = [SuiteParser(element) for element in self.suite_elements]
        children = [node for node in self.db_element.childNodes]
        traits_elements = []
        for node in children:
            if hasattr(node, 'tagName') and node.tagName not in ['aptsources', 'profiles', 'suites']:
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

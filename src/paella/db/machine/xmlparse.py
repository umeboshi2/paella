import os
from os.path import join
from xml.dom.minidom import parseString

from useless.base.xmlfile import ParserHelper
from useless.base import Error

from base import Machine, MachineType, MachineModules

def get_child(element):
    return element.firstChild.data.encode().strip()

def get_attribute(attribute, element):
    return element.getAttribute(attribute).encode().strip()

def parse_module(element):
    module = get_child(element)
    order = get_attribute('order', element)
    return int(order), module

def parse_machine(element):
    name = get_child(element)
    mtype = get_attribute('machine_type', element)
    kernel = get_attribute('kernel', element)
    profile = get_attribute('profile', element)
    return Machine(name, mtype, kernel, profile)

class MachineTypeParser(ParserHelper):
    def __init__(self, element):
        ParserHelper.__init__(self)
        self.name = element.getAttribute('name')
        self.parent = None
        if element.hasAttribute('parent'):
            self.parent = element.getAttribute('parent')
        mods = element.getElementsByTagName('module')
        fams = element.getElementsByTagName('family')
        scripts = element.getElementsByTagName('script')
        vars_ = element.getElementsByTagName('machine_type_variable')
        
        self.mtype = MachineType(self.name)
        moddict = dict(map(parse_module, mods))
        modorder = moddict.keys()
        modorder.sort()
        modules = []
        for i in modorder:
            modules.append(moddict[i])
        self.mtype.append_modules(modules)
        for f in fams:
            family = get_child(f)
            self.mtype.append_family(family)
        for s in scripts:
            name = s.getAttribute('name')
            self.mtype.append_script(name, name)
        for v in vars_:
            trait = v.getAttribute('trait')
            name = v.getAttribute('name')
            value = get_child(v)
            self.mtype.append_variable(trait, name, value)
            
class MachineDatabaseParser(ParserHelper):
    def __init__(self, path, element):
        ParserHelper.__init__(self)
        self.path = path
        self.mtypepath = join(path, 'machine_types')
        
        name = element.tagName.encode()
        get_em = self.get_elements_from_section
        self.kernels = map(get_child, get_em(element, 'kernels', 'kernel'))
        self.mtypes = map(self._parse_mtype, get_em(element, 'machine_types',
                                                    'machine_type'))
        self.machines = map(parse_machine, get_em(element, 'machines', 'machine'))
        
    def _get_mtype_element(self, mtype):
        path = join(self.mtypepath, mtype)
        xml = join(path, 'machine_type.xml')
        element = parseString(file(xml).read())
        return element
    
    def _parse_mtype(self, element):
        name = get_attribute('name', element)
        return name

if __name__ == '__main__':
    pass


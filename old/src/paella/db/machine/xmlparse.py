import os
from os.path import join
from xml.dom.minidom import parseString

from useless.base import Error
from useless.base.xmlfile import ParserHelper
from useless.base.path import path

from base import Machine

def get_child(element):
    return element.firstChild.data.encode().strip()

def get_attribute(attribute, element):
    return element.getAttribute(attribute).encode().strip()

class MachineParser(ParserHelper):
    def __init__(self, element):
        ParserHelper.__init__(self)
        self.name = element.getAttribute('name').encode()
        self.machine = Machine(self.name)
        for attr in ['parent', 'diskconfig', 'kernel', 'profile']:
            setattr(self, attr, None)
            if element.hasAttribute(attr):
                setattr(self, attr, element.getAttribute(attr).encode())
            setattr(self.machine, attr, getattr(self, attr))
        mods = element.getElementsByTagName('module')
        fams = element.getElementsByTagName('family')
        scripts = element.getElementsByTagName('script')
        vars_ = element.getElementsByTagName('machine_variable')
        
        for f in fams:
            family = get_child(f)
            self.machine.append_family(family)
        for s in scripts:
            name = s.getAttribute('name').encode()
            self.machine.append_script(name)
        for v in vars_:
            trait = v.getAttribute('trait').encode()
            name = v.getAttribute('name').encode()
            value = get_child(v)
            self.machine.append_variable(trait, name, value)
            
class MachineDatabaseParser(ParserHelper):
    def __init__(self, dirname, element):
        ParserHelper.__init__(self)
        self.dirname = path(dirname)
        name = element.tagName.encode()
        if name != 'machine_database':
            msg = "This doesn't seem to be the proper xml file.\n"
            msg += "The main tag is %s instead of machine_database.\n" % name
            raise RuntimeError , msg
        self.machines_dir = dirname / 'machines'
        get_em = self.get_elements_from_section
        self.kernels = map(get_child, get_em(element, 'kernels', 'kernel'))
        self.machines = []
        for machine_name_element in get_em(element, 'machines', 'machine'):
            name = machine_name_element.getAttribute('name').encode()
            self.machines.append(name)
            
if __name__ == '__main__':
    pass


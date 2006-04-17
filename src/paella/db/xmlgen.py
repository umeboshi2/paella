from xml.dom.minidom import Element

from useless.base.xmlfile import TextElement, DictElement


#generate and reform xml
class ParentElement(TextElement):
    def __init__(self, parent):
        TextElement.__init__(self, 'parent', parent)

#generate and reform xml
class PackageElement(TextElement):
    def __init__(self, package, action='install'):
        TextElement.__init__(self, 'package', package)
        self.setAttribute('action', action)
        self.package = package
        self.action = action
        
    def reform(self, element):
        name = element.tagName.encode()
        if name != 'package':
            raise Error, 'bad package tag'
        package = element.firstChild.data.encode()
        action = element.getAttribute('action').encode()
        TextElement.__init__(self, package, action)

#generate xml
class TemplateElement(TextElement):
    def __init__(self, package, template, mode='0100644',
                 owner='root', grp_owner='root'):
        TextElement.__init__(self, 'template', template)
        self.setAttribute('package', package)
        self.setAttribute('mode', mode)
        self.setAttribute('owner', owner)
        self.setAttribute('grp_owner', grp_owner)

class Debconf_object(object):
    def __init__(self):
        object.__init__(self)
        self.name = None
        self.template = None
        self.owners = None
        self.value = None

#generate xml
class DebConfElement(Element):
    def __init__(self, trait, data):
        Element.__init__(self, 'debconf')
        self.setAttribute('trait', trait)
        self.dc = Debconf_object()
        self.dc.name = TextElement('name', data['name'])
        self.appendChild(self.dc.name)
        self.dc.template = TextElement('template', data['template'])
        self.appendChild(self.dc.template)
        self.dc.owners = TextElement('owners', data['owners'])
        self.appendChild(self.dc.owners)
        self.dc.value = TextElement('value', data['value'])
        self.appendChild(self.dc.value)
        

class AptSourceElement(Element):
    def __init__(self, apt_id, uri, dist, sections, local_path):
        Element.__init__(self, 'aptsource')
        self.setAttribute('apt_id', apt_id)
        self.setAttribute('uri', uri)
        self.setAttribute('dist', dist)
        self.setAttribute('sections', sections)
        self.setAttribute('local_path', local_path)

class AptSourceListElement(Element):
    def __init__(self):
        Element.__init__(self, 'aptsources')
        
class ScriptElement(Element):
    def __init__(self, name):
        Element.__init__(self, 'script')
        self.setAttribute('name', name)
    
#generate xml
class DebConfigurationElement(Element):
    def __init__(self):
        Element.__init__(self, 'debconfiguration')

class SuiteAptElement(Element):
    def __init__(self, suite, apt_id, order):
        Element.__init__(self, 'suiteapt')
        self.setAttribute('suite', suite)
        self.setAttribute('apt_id', apt_id)
        self.setAttribute('order', order)
        
#generate xml
class SuiteElement(Element):
    def __init__(self, suite, nonus=False, updates=False, local=False, common=False):
        Element.__init__(self, 'suite')
        self.setAttribute('name', suite)
        self.setAttribute('nonus', nonus)
        self.setAttribute('updates', updates)
        self.setAttribute('local', local)
        self.setAttribute('common', common)
        
#generate xml        
class SuitesElement(Element):
    def __init__(self):
        Element.__init__(self, 'suites')

#generate xml        
class EnvironElement(DictElement):
    def __init__(self, environ):
        DictElement.__init__(self, 'environ', environ)

#generate xml
class ProfileElement(Element):
    def __init__(self, name, suite):
        Element.__init__(self, 'profile')
        self.setAttribute('name', name)
        self.setAttribute('suite', suite)
        self.traits = Element('traits')
        self.appendChild(self.traits)
        self.families = Element('families')
        self.appendChild(self.families)
        self.environ = Element('environ')
        self.appendChild(self.environ)

    def append_traits(self, trait_rows):
        for trait in trait_rows:
            telement = TextElement('trait', trait.trait)
            telement.setAttribute('ord', str(trait.ord))
            self.traits.appendChild(telement)

    def append_families(self, rows):
        for row in rows:
            felement = TextElement('family', row.family)
            self.families.appendChild(felement)
            
    def append_variables(self, rows):
        for row in rows:
            velement = ProfileVariableElement(row.trait, row.name, row.value)
            self.environ.appendChild(velement)


class ProfileEnvironmentElement(DictElement):
    def __init__(self, trait, environ):
        DictElement.__init__(self, 'profile_variable', environ)
        self.setAttribute('trait', trait)

class BaseVariableElement(TextElement):
    def __init__(self, etype, trait, name, value):
        TextElement.__init__(self, etype, value)
        self.setAttribute('trait', trait)
        self.setAttribute('name', name)

class ProfileVariableElement(BaseVariableElement):
    def __init__(self, trait, name, value):
        BaseVariableElement.__init__(self, 'profile_variable',
                                     trait, name, value)

class FamilyVariableElement(BaseVariableElement):
    def __init__(self, trait, name, value):
        BaseVariableElement.__init__(self, 'family_variable',
                                     trait, name, value)
        

class FamilyElement(Element):
    def __init__(self, name):
        Element.__init__(self, 'family')
        self.setAttribute('name', name)
        self.parents = Element('parents')
        self.environ = Element('environ')
        self.appendChild(self.parents)
        self.appendChild(self.environ)
        
    def append_parents(self, parents):
        for parent in parents:
            pelement = TextElement('parent', parent)
            #pelement.setAttribute('ord', str(trait.ord))
            self.parents.appendChild(pelement)

    def append_variables(self, rows):
        for row in rows:
            velement = FamilyVariableElement(row.trait, row.name, row.value)
            self.environ.appendChild(velement)

if __name__ == '__main__':
    pass

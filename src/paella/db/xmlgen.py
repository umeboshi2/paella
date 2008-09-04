from xml.dom.minidom import Element

from useless.base.xmlfile import TextElement, DictElement


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
    
class SuiteAptElement(Element):
    def __init__(self, suite, apt_id, order):
        Element.__init__(self, 'suiteapt')
        self.setAttribute('suite', suite)
        self.setAttribute('apt_id', apt_id)
        self.setAttribute('order', order)
        
# generate xml
class SuiteElement(Element):
    def __init__(self, suite):
        Element.__init__(self, 'suite')
        self.setAttribute('name', suite)

        
# generate xml        
class SuitesElement(Element):
    def __init__(self):
        Element.__init__(self, 'suites')

# generate xml
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

# here etype is the tagname of the element
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

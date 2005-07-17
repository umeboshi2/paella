from xml.dom.minidom import Element

from useless.base.xmlfile import TextElement, DictElement

from paella.db.xmlgen import BaseVariableElement

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

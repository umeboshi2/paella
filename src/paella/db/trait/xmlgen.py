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

class ScriptElement(Element):
    def __init__(self, name):
        Element.__init__(self, 'script')
        self.setAttribute('name', name)
    
#generate xml        
class EnvironElement(DictElement):
    def __init__(self, environ):
        DictElement.__init__(self, 'environ', environ)

if __name__ == '__main__':
    pass

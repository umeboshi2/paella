from xml.dom.minidom import DOMImplementation, Document
from xml.dom.minidom import Element, Text
from xml.dom.ext import PrettyPrint
from xml.dom.minidom import parse as parse_file
from xml.dom.minidom import parseString as parse_string

from paella.base import Error, debug
from paella.base.util import strfile


#class Element(_Element):
#    def writexml(self, file, indent='\t', newl='\n', addindent='\t'):
#        _Element.writexml(self, file, indent=indent, newl=newl,
#                          addindent=addindent)
    

class TextElement(Element):
    def __init__(self, name, value):
        Element.__init__(self, name)
        self.set(value)

    def set(self, value):
        while self.hasChildNodes():
            del self.childNodes[0]
        if value is not None:
            textnode = Text()
            textnode.data = value
            self.appendChild(textnode)

    def get(self):
        if self.hasChildNodes():
            return self.firstChild.data.encode().strip()
        else:
            return None

    def reform(self, element):
        name = element.tagName.encode()
        if element.hasChildNodes():
            try:
                value = element.firstChild.data.encode()
            except AttributeError:
                value = None
        else:
            value = None
        TextElement.__init__(self, name, value)

class DictElement(Element):
    def __init__(self, name, data):
        Element.__init__(self, name)
        self.__data_dict__  = {}
        for key, value in data.items():
            self.__data_dict__[key] = TextElement(key, value)
            self.appendChild(self.__data_dict__[key])

    def __getitem__(self, key):
        return self.__data_dict__[key].get()

    def __setitem__(self, key, value):
        self.__data_dict__[key].set(value)

    def keys(self):
        return self.__data_dict__.keys()

    def values(self):
        return [telement.get() for telement in self.__data_dict__.values()]

    def items(self):
        return [(k, v.get()) for k,v in self.__data_dict__.items()]

    def element(self, key):
        return self.__data_dict__[key]

    def reform(self, element):
        name = element.tagName.encode()
        data = {}
        for node in element.childNodes:
            try:
                data[node.tagName.encode()] = node.firstChild.data.encode()
            except AttributeError:
                pass
        DictElement.__init__(self, name, data)


class RowElement(DictElement):
    def __init__(self, row):
        DictElement.__init__(self, 'row', row)

class PkRowElement(DictElement):
    def __init__(self, key, row):
        DictElement.__init__(self, key, row)

class TableElement(Element):
    def __init__(self, name, rows, key=False):
        Element.__init__(self, name)
        for row in rows:
            if key:
                rowdata = PkRowElement(row[key], row)
            else:
                rowdata = RowElement(row)
            self.appendChild(rowdata)

        
class XmlDoc(object):
    def __init__(self):
        object.__init__(self)
        self.dom = DOMImplementation()
        self.doctype = self.dom.createDocumentType('xmltable', 0, '')
        self.doc = Document()
        self.doc.appendChild(self.doctype)

    def insert(self, parent, tag, text=None):
        if text:
            element = TextElement(tag, text)
        else:
            element = Element(tag)
        parent.appendChild(element)
        return element

    def write(self, path=None):
        if not path:
            fobj = strfile()
        else:
            fobj = file(path, 'w')
        PrettyPrint(self.doc, fobj)
        if not path:
            fobj.seek(0)
            return fobj.read()
        

class ParserHelper(object):
    def __init__(self):
        object.__init__(self)
        
    def _get_single_section(self, element, section):
        sections = element.getElementsByTagName(section)
        if len(sections) > 1:
            raise Error, 'too many %s sections' %section
        else:
            return sections

    def get_elements_from_section(self, element, section, tag, atts=[]):
        sections = self._get_single_section(element, section)
        if len(sections):
            return sections[0].getElementsByTagName(tag)
        else:
            return []

    def get_attribute(self, element, attribute):
        return element.getAttribute(attribute).encode()
            
        
if __name__ == '__main__':
    from paella.base.config import Configuration
    from paella.db.lowlevel import QuickConn
    from paella.db.midlevel import TableDict
    conn = QuickConn(g)
    e = TableDict(conn, 'woody_variables')
    
    x = XmlDoc()
    x.hello = x.insert(x.doc, 'hello')
    t = TextElement('person', 'hank')
    td = dict(foo='bar', a='a', b='sdf', dd='val')
    
    d = DictElement('foodict', e)
    rows = e.cursor.select()
    ss = parse_string(d.toxml())
    
    

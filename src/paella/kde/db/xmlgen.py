#from operator import and_
from xml.dom.minidom import Element, Text

from paella.base import NoExistError
from paella.sqlgen.clause import Eq, In

from paella.kde.base.xmlgen import Html, Body, Anchor
from paella.kde.base.xmlgen import BR, HR, Bold
from paella.kde.base.xmlgen import TR, TD
from paella.kde.base.xmlgen import TableElement
from paella.kde.base.xmlgen import BaseElement, TextElement


#db is BaseDatabase from konsultant.db
class BaseDbElement(BaseElement):
    def __init__(self, db, tagname, **atts):
        BaseElement.__init__(self, tagname, **atts)
        self.db = db
        
class BaseDocument(BaseDbElement):
    def __init__(self, app, **atts):
        BaseDbElement.__init__(self, app, 'html', **atts)
        self.app = app
        self.db = app.db
        self.body = Body()
        self.appendChild(self.body)

    def clear_body(self):
        while self.body.hasChildNodes():
            del self.body.childNodes[0]
        
class BaseParagraph(BaseDbElement):
    def __init__(self, app, key, href=None, **atts):
        BaseDbElement.__init__(self, app, 'p', **atts)
        data = self.makeParagraph(key)
        if href is not None:
            node = Anchor(href, data)
        else:
            node = Text()
            node.data = data
        self.appendChild(node)

    def makeParagraph(self, key):
        #all subclasses must define this member
        raise Exception, 'makeParagraph not overidden'
    
    
class RecordDoc(BaseDocument):
    def __init__(self, app, manager=None, records=None):
        BaseDocument.__init__(self, app)
        self.manager = manager(self.app)
        self.records = {}

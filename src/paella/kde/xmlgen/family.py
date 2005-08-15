from xml.dom.minidom import Text

from useless.sqlgen.clause import Eq
from useless.xmlgen.base import BaseElement, TextElement
from useless.xmlgen.base import Anchor, Html, Body
from useless.xmlgen.base import ListItem, UnorderedList
from useless.xmlgen.base import BR, HR, Bold, TR, TD, Paragraph
from useless.xmlgen.base import SimpleTitleElement

#from useless.db.midlevel import StatementCursor
#from paella.db.trait import Trait
#from paella.db.profile import Profile
from paella.db.family import Family
#from paella.db.machine import MachineHandler
#from paella.db.machine.mtype import MachineTypeHandler

from base import BaseDocument
from base import SectionTitle
from base import PVarTable

class FamilyDoc(BaseDocument):
    def __init__(self, app, **atts):
        BaseDocument.__init__(self, app, **atts)
        self.family = Family(self.conn)
        
    def set_family(self, family):
        self.family.set_family(family)
        parents = self.family.parents()
        erows = self.family.environment_rows()
        self.clear_body()
        title = SimpleTitleElement('Family:  %s' % family, bgcolor='IndianRed',
                                   width='100%')
        self.body.appendChild(title)
        self.body.appendChild(SectionTitle('Parents'))
        if len(parents):
            plist = UnorderedList()
            for p in parents:
                plist.appendChild(ListItem(p))
            self.body.appendChild(plist)
        vtitle = Anchor('edit.variables.%s' % self.family.current, 'Variables')
        self.body.appendChild(SectionTitle(vtitle))
        if len(erows):
            self.body.appendChild(PVarTable(erows, bgcolor='MistyRose2'))
            

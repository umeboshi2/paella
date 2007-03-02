from forgetHTML import UnorderedList, ListItem
from forgetHTML import Anchor

from paella.db.family import Family

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
        title = SectionTitle('Family:  %s' % family)
        title['bgcolor'] = 'IndianRed'
        title['width'] = '100%'

        self.body.append(title)
        self.body.append(SectionTitle('Parents'))
        if len(parents):
            plist = UnorderedList()
            for p in parents:
                plist.append(ListItem(p))
            self.body.append(plist)
        vtitle = Anchor('Variables', href='edit.variables.%s' % self.family.current)
        self.body.append(SectionTitle(vtitle))
        if len(erows):
            self.body.append(PVarTable(erows, bgcolor='MistyRose2'))


# first draft complete


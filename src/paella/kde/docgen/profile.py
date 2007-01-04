from forgetHTML import UnorderedList, ListItem
from forgetHTML import Table, TableRow, TableCell
from forgetHTML import Anchor

from paella.db.profile import Profile

from base import SectionTitle, BaseDocument
from base import PVarTable
from base import TraitTable

class ProfileDoc(BaseDocument):
    def __init__(self, app, **atts):
        BaseDocument.__init__(self, app, **atts)
        self.profile = Profile(self.conn)

    def set_profile(self, profile):
        self.clear_body()
        self.profile.set_profile(profile)
        title = SectionTitle('Profile:  %s' % profile)
        title['bgcolor'] = 'IndianRed'
        title['width'] = '100%'
        self.body.append(title)
        rows = self.profile.get_trait_rows()
        ptitle = Anchor('Traits', href='edit.traits.%s' % self.profile.current.profile)
        self.body.append(SectionTitle(ptitle))
        if len(rows):
            self.body.append(TraitTable(rows, bgcolor='IndianRed1'))
        vtitle = Anchor('Variables', href='edit.variables.%s' % self.profile.current.profile)
        self.body.append(SectionTitle(vtitle))
        erows = self.profile._env.get_rows()
        if len(erows):
            self.body.append(PVarTable(erows, bgcolor='MistyRose2'))
        etitle = Anchor('Families', href='edit.families.%s' % self.profile.current.profile)
        self.body.append(SectionTitle(etitle))
        families = self.profile.get_families()
        flist = UnorderedList()
        for f in families:
            flist.append(ListItem(f))
        self.body.append(flist)
        
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


# first draft completed

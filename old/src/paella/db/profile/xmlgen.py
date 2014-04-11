from os.path import join
from xml.dom.minidom import Element

from useless.base.xmlfile import TextElement
from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq

from paella.db.xmlgen import BaseVariableElement

class ProfileVariableElement(BaseVariableElement):
    def __init__(self, trait, name, value):
        BaseVariableElement.__init__(self, 'profile_variable',
                                     trait, name, value)

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

    
#generate xml
class PaellaProfiles(Element):
    def __init__(self, conn):
        Element.__init__(self, 'profiles')
        self.conn = conn
        self.cursor = StatementCursor(self.conn)
        self.env = ProfileEnvironment(self.conn)
        self.profiletraits = ProfileTrait(self.conn)
        self._profiles = {}
        self._profile = Profile(self.conn)
        
        for row in self.cursor.select(table='profiles', order='profile'):
            self._append_profile(row.profile, row.suite)
                
    def _append_profile(self, profile, suite):
        element = self.export_profile(profile, suite)
        self._profiles[profile] = element
        self.appendChild(self._profiles[profile])

    def export_profile(self, profile, suite=None):
        if suite is None:
            row = self.cursor.select_row(table='profiles',clause=Eq('profile', profile))
            suite = row['suite']
        suite = str(suite)
        profile = str(profile)
        self.env.set_profile(profile)
        element = ProfileElement(profile, suite)
        element.append_traits(self.profiletraits.trait_rows(profile))
        element.append_families(self._profile.family_rows(profile))
        element.append_variables(self.env.get_rows())
        return element

    def insert_profile(self, profile):
        idata = {'profile' : profile.name,
                 'suite' : profile.suite}
        self.cursor.insert(table='profiles', data=idata)
        idata = {'profile' : profile.name,
                 'trait' : None,
                 'ord' : 0}
        for trait, ord in profile.traits:
            print trait, ord
            idata['trait'] = trait
            idata['ord'] = ord #str(ord)
            self.cursor.insert(table='profile_trait', data=idata)
        idata = {'profile' : profile.name,
                 'trait' : None,
                 'name' : None,
                 'value': None}
        idata = dict(profile=profile.name)
        for family in profile.families:
            idata['family'] = family
            self.cursor.insert(table='profile_family', data=idata)
        idata = dict(profile=profile.name)
        for trait, name, value in profile.vars:
            idata['trait'] = trait
            idata['name'] = name
            idata['value'] = value
            self.cursor.insert(table='profile_variables', data=idata)

    def export_profiles(self, path):
        rows = self.cursor.select(fields='profile', table='profiles', clause=None)
        self.report_total_profiles(len(rows))
        for row in rows:
            self.write_profile(row.profile, path)
            self.report_profile_exported(row.profile, path)
        
    def write_profile(self, profile, path):
        xmlfile = file(join(path, '%s.xml' % profile), 'w')
        data = self.export_profile(profile)
        data.writexml(xmlfile, indent='\t', newl='\n', addindent='\t')
        xmlfile.close()
        

    def report_profile_exported(self, profile, path):
        print 'profile %s exported to %s' % (profile, path)

    def report_total_profiles(self, total):
        print 'exporting %d profiles' % total
        
if __name__ == '__main__':
    pass

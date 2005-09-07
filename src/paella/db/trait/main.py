import os
from os.path import dirname, join
from sets import Set
from xml.dom.minidom import Element
from tarfile import TarFile
from xml.dom.minidom import parse as parse_file

from useless.base import ExistsError, UnbornError, Error, debug

from useless.xmlgen.base import TextElement
from useless.base.util import ujoin, makepaths
from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq


from base import AllTraits, Traits
from relations import TraitParent, TraitPackage
from relations import TraitTemplate, TraitEnvironment
from relations import TraitScript
#from base import TraitRelation, TraitEnvironment
#from base import Template, TextFileManager

from xmlgen import EnvironElement, ParentElement
from xmlgen import PackageElement, TemplateElement
from xmlparse import TraitParser


def make_trait_tarfile(trait, traittemplate, template_path, tarname):
    pass


    
    
def store_trait(traittemplate, tmpl_path, bkup_path, name):
    trait = traittemplate.current_trait
    suite = traittemplate.suite
    conn = traittemplate.conn
    xmldata = TraitElement(conn, suite)
    xmldata.set(trait)
    root_path = join(bkup_path, suite, trait, name)
    os.system('rm %s -fr' %root_path)
    makepaths(root_path)
    xmlfile = file(join(root_path, 'trait.xml'), 'w')
    xmlfile.write(xmldata.toprettyxml())
    xmlfile.close()
    traittemplate.set_template_path(tmpl_path)
    traittemplate.backup_templates(join(root_path, 'templates'))
    

def backup_trait(conn, suite, trait, tball_path):
    t = Trait(conn, suite)
    t.set_trait(trait)
    t.backup_trait(tball_path)
    
    
                   



class TraitXml(TraitParser):
    def __init__(self, fileobj):
        TraitParser.__init__(self, parse_file(fileobj).firstChild)
        
class TraitTarFile(TarFile):
    def __init__(self, *arg, **kw):
        TarFile.__init__(self, *arg, **kw)

    def add_trait_data(self, xmlobj):
        pass

    def get_trait(self):
        return TraitXml(self.extractfile('trait.xml'))    

    def get_template(self, package, template):
        path = join('templates', package, template + '.template')
        return self.extractfile(path)

    def get_script(self, name):
        path = join('scripts', name)
        return self.extractfile(path)
    

class Trait(object):
    def __init__(self, conn, suite='sarge'):
        object.__init__(self)
        self.conn = conn
        self.suite = suite
        self._alltraits = AllTraits(self.conn)
        self._traits = Traits(self.conn, self.suite)
        self._parents = TraitParent(self.conn, self.suite)
        self._packages = TraitPackage(self.conn, self.suite)
        self._templates = TraitTemplate(self.conn, self.suite)
        self._scripts = TraitScript(self.conn, self.suite)
        self.current_trait = None
        self.environ = {}
        
    def set_trait(self, trait):
        self.current_trait = trait
        self.environ = TraitEnvironment(self.conn, self.suite, trait)
        self._parents.set_trait(trait)
        self._packages.set_trait(trait)
        self._templates.set_trait(trait)
        self._scripts.set_trait(trait)
        
    def parents(self, trait=None):
        return [x.parent for x in self._parents.parents(trait)]
    
    def templates(self, trait=None, fields=None):
        rows = self._templates.templates(trait, fields)
        if fields is None:
            return [row.template for row in rows]
        else:
            return rows

    def packages(self, trait=None, action=False):
        if trait is None:
            trait = self.current_trait
        rows = self._packages.packages([trait])
        if action:
            return rows
        else:
            return [row.package for row in rows]

        
    def get_package_rows(self):
        return self._packages.packages([self.current_trait])

    def get_traits(self):
        return self._traits.select(fields=['trait'])

    def get_trait_list(self):
        return [row.trait for row in self.get_traits()]
    
    def get_template_rows(self):
        return self._templates.templates(self.current_trait)
    
    def set_action(self, action, packages):
        self._packages.set_action(action, packages)

    def get_traitset(self):
        return self._parents.get_traitset([self.current_trait])

    def insert_packages(self, packages):
        self._packages.insert_packages(packages)

    def insert_parents(self, traits):
        self._parents.insert_parents(traits)

    def insert_template(self, template_data):
        self._templates.insert_template(template_data)

    def update_template(self, template_data):
        self._templates.update_template(template_data)

    def delete_parents(self, parents):
        self._parents.delete(parents)

    def create_trait(self, trait):
        insert_data = {'trait' : trait}
        if trait not in self._alltraits.list():
            self._alltraits.insert(data=insert_data)
        if trait not in self._traits.list():
            self._traits.insert(data=insert_data)
        else:
            raise ExistsError, '%s already exists' % trait

    def delete_trait(self, trait):
        environ = TraitEnvironment(self.conn, self.suite, trait)
        environ.clear()
        self._templates.delete_trait(trait)
        self._parents.delete_trait(trait)
        self._packages.delete_trait(trait)
        self._scripts.delete_trait(trait)
        self._traits.set_clause([('trait', trait)])
        self._traits.delete()
        self._traits.clear(clause=True)

    def insert_trait(self, path, suite=None):
        #tar = TraitTarFile(path)
        #trait = tar.get_trait()
        trait = TraitXml(file(join(path, 'trait.xml')))
        if suite is not None:
            trait.suite = suite
        all = Set([x.trait for x in self._alltraits.select()])
        suite_traits = Set([x.trait for x in self._traits.select()])
        parents = Set(trait.parents)
        debug(parents)
        if not parents.issubset(suite_traits):
            raise UnbornError, 'Parent Unborn'        
        if trait.name in suite_traits:
            raise Error, 'trait exists'
        idata ={'trait' : trait.name}
        if trait.name not in all:
            self._alltraits.insert(data=idata)
        if trait.name not in suite_traits:
            self._traits.insert(data=idata)
        lasttrait = self.current_trait
        self._parents.set_trait(trait.name)
        self._packages.set_trait(trait.name)
        self._templates.set_trait(trait.name)
        self._scripts.set_trait(trait.name)
        self._parents.insert_parents(trait.parents)
        for package, action in trait.packages:
            self._packages.insert_package(package, action)
        n = 0
        for package, template, data in trait.templates:
            #print template, data
            #templatefile = tar.get_template(data['package'], template)
            templatefile = file(join(path, 'template-%d' % n))
            idata = {'template' : template}
            #print idata
            idata.update(data)
            #print idata
            self._templates.insert_template(idata, templatefile)
            n += 1
        for script in trait.scripts:
            #scriptfile = tar.get_script(script)
            scriptfile = file(join(path, 'script-%s' % script))
            self._scripts.insert_script(script, scriptfile)
        environ = TraitEnvironment(self.conn, suite, trait.name)
        environ.update(trait.environ)
        self.set_trait(lasttrait)

    def backup_trait(self, tball_path):
        raise Error, 'this call is deprecated, use export_trait'
        
    def export_trait(self, suite_path):
        xmldata = TraitElement(self.conn, self.suite)
        xmldata.set(self.current_trait)
        bkup_path = join(suite_path, self.current_trait)
        makepaths(bkup_path)
        xmlfile = file(join(bkup_path, 'trait.xml'), 'w')
        xmlfile.write(xmldata.toprettyxml())
        xmlfile.close()
        self._templates.export_templates(bkup_path)
        self._scripts.export_scripts(bkup_path)
        #print 'all exported', os.listdir(bkup_path)
        print 'trait', self.current_trait, 'exported in suite', self.suite

    def get_description(self):
        trait = self.current_trait
        row = self._traits.select_row(clause=Eq('trait', trait))
        # we must use row['dsc'] instead of row.dsc here
        return row['description']

    def set_description(self, desc):
        trait = self.current_trait
        data = dict(description=desc)
        self._traits.update(data=data, clause=Eq('trait', trait))

    def add_package(self, package, action):
        self._packages.insert_package(package, action)
        
#generate xml
class TraitElement(Element):
    def __init__(self, conn, suite):
        self.conn = conn
        self.cursor = StatementCursor(self.conn, name='_Trait_')
        Element.__init__(self, 'trait')
        self.desc_element = TextElement('description', None)
        self.parent_element = Element('parents')
        self.pkg_element = Element('packages')
        self.env_element = Element('environ')
        self.templ_element = Element('templates')
        self.scripts_element = Element('scripts')
        self.appendChild(self.desc_element)
        self.appendChild(self.parent_element)
        self.appendChild(self.pkg_element)
        self.appendChild(self.env_element)
        self.appendChild(self.templ_element)
        self.appendChild(self.scripts_element)
        self.set_suite(suite)
        
    def set_suite(self, suite):
        self.suite = suite
        self.setAttribute('suite', self.suite)
        self.traitparent = TraitParent(self.conn, self.suite)
        self.traitpackage = TraitPackage(self.conn, self.suite)
        self.traittemplate = TraitTemplate(self.conn, self.suite)
        self.traitscripts = TraitScript(self.conn, self.suite)

    def set_environ(self):
        self.environ = TraitEnvironment(self.conn, self.suite, self.name)
        new_element = EnvironElement(self.environ)
        self.replaceChild(new_element, self.env_element)
        self.env_element = new_element

    def set_parents(self):
        self.parents = self.traitparent.parents(self.name)
        while self.parent_element.hasChildNodes():
            del self.parent_element.childNodes[0]
        for parent in self.parents:
            self.parent_element.appendChild(ParentElement(parent.parent))
            
    def set_packages(self):
        self.packages = self.traitpackage.packages([self.name])
        while self.pkg_element.hasChildNodes():
            del self.pkg_element.childNodes[0]
        for package in self.packages:
            pelement = PackageElement(package.package)
            pelement.setAttribute('action', package.action)
            self.pkg_element.appendChild(pelement)

    def set_templates(self):
        self.templates = self.traittemplate.templates(self.name)
        while self.templ_element.hasChildNodes():
            del self.templ_element.childNodes[0]
        for template in self.templates:
            element = TemplateElement(template.package, template.template)
            for att in ['package', 'mode', 'owner', 'grp_owner']:
                element.setAttribute(att, template[att])
            self.templ_element.appendChild(element)

    def set_scripts(self):
        self.scripts = [x.script for x in self.traitscripts.scripts(self.name)]
        while self.scripts_element.hasChildNodes():
            del self.scripts_element.childNodes[0]
        for script in self.scripts:
            element = Element('script')
            element.setAttribute('name', script)
            self.scripts_element.appendChild(element)
            

    def set_name(self, name):
        self.name = name
        self.setAttribute('name', self.name)

    def set_priority(self, priority):
        self.priority = priority
        self.setAttribute('priority', self.priority)

    def set(self, name):
        self.set_name(name)
        self.set_suite(self.suite)
        self.set_environ()
        self.set_parents()
        self.set_packages()
        self.set_templates()
        self.set_scripts()
        
    def str(self):
        print self.toprettyxml()
        
#generate xml
class TraitsElement(Element):
    def __init__(self, conn, suite):
        Element.__init__(self, 'traits')
        self.conn = conn
        self.suite = suite
        self.setAttribute('suite', self.suite)
        self._traits_ = StatementCursor(self.conn, 'Traits')
        self._traits_.set_table(ujoin(self.suite, 'traits'))
        self.traitnames = [row.trait for row in self._traits_.select(order='trait')]
        for t in self.traitnames:
            t_element = Element('trait')
            t_element.setAttribute('name', t)
            self.appendChild(t_element)
            

    def make_trait(self, trait):
        t_element = TraitElement(self.conn, self.suite)
        t_element.set(trait)
        return t_element

            



if __name__ == '__main__':
    #f = file('tmp/trait.xml')
    #tx = TraitXml(f)
    import sys
    tt = TraitTarFile(sys.argv[1])

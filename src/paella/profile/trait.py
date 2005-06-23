import os
from os.path import dirname, join
from sets import Set
from xml.dom.minidom import Element
from tarfile import TarFile
from xml.dom.minidom import parse as parse_file

from kjbuckets import kjGraph

from useless.base import ExistsError, UnbornError, Error, debug
from useless.base.xmlfile import TextElement
from useless.base.util import ujoin, makepaths, filecopy, strfile, RefDict
from useless.base.tarball import make_tarball

from useless.sqlgen.clause import one_many, Eq, In, NotIn

from useless.db.midlevel import StatementCursor

from xmlparse import TraitParser

from base import Suites, AllTraits, Traits
from base import _TraitRelation, TraitEnvironment
from base import Template, TextFileManager

from xmlgen import EnvironElement, ParentElement
from xmlgen import PackageElement, TemplateElement
from xmlgen import DebConfigurationElement
from xmlgen import DebConfElement


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
    

class TraitParent(_TraitRelation):
    def __init__(self, conn, suite):
        table = ujoin(suite, 'trait', 'parent')
        _TraitRelation.__init__(self, conn, suite, table, name='TraitParent')
        self.graph = kjGraph([(r.trait, r.parent) for r in self.cmd.select()])

    def get_traitset(self, traits):
        dtraits = Set()
        for trait in traits:
            dtraits |=  Set([trait]) | Set(self.graph.reachable(trait).items())
        return dtraits

    def get_environment(self, traits):
        assoc_traits = list(self.get_traitset(traits))
        c, s = self.conn, self.suite
        return [(t, TraitEnvironment(c, s, t)) for t in assoc_traits]


    def get_superdict(self, traits, sep='_'):
        env = TraitEnvironment(self.conn, self.suite, traits[0])
        superdict = RefDict()
        for trait in traits:
            env.set_main(trait)
            items = [(trait+sep+key, value) for key, value in env.items()]
            superdict.update(dict(items))
        return superdict

    

    def Environment(self):
        traits = list(self.get_traitset([self.current_trait]))
        return self.get_superdict(traits)

    def parents(self, trait=None):
        if trait is None:
            trait = self.current_trait
        self.set_clause(trait)
        rows = self.cmd.select(fields=['parent'], order='parent')
        self.reset_clause()
        return rows
    
    def insert_parents(self, parents):
        self.insert('parent', parents)
        

    def delete(self, parents=[]):
        print parents, 'PARENTS'
        clause = In('parent', parents) & Eq('trait', self.current_trait)
        self.cmd.delete(clause=clause)
        self.reset_clause()

    def delete_trait(self, trait=None):
        if trait is None:
            trait = self.current_trait
        clause = Eq('trait', trait)
        self.cmd.delete(clause=clause)
        self.reset_clause()
        
        
class TraitTemplate(_TraitRelation):
    def __init__(self, conn, suite):
        table = ujoin(suite, 'templates')
        _TraitRelation.__init__(self, conn, suite, table, name='TraitTemplate')
        self.traitparent = TraitParent(conn, suite)
        self.template = Template()
        self.template.set_suite(suite)
        self.template_path = None
        self.textfiles = TextFileManager(self.conn)
        self._jtable = '%s as s join textfiles as t ' % table
        self._jtable += 'on s.templatefile = t.fileid' 

    def _clause(self, package, template, trait=None):
        if trait is None:
            trait = self.current_trait
        return Eq('trait', trait) & Eq('package', package) & Eq('template', template)
    
    def templates(self, trait=None, fields=['*']):
        if trait is None:
            trait = self.current_trait
            self.reset_clause()
            return self.cmd.select(fields=fields, order=['package', 'template'])
        else:
            self.set_clause(trait)
            rows = self.cmd.select(fields=fields, order=['package', 'template'])
            self.reset_clause()
            return rows

    def has_template(self, template):
        return self.has_it('template', template)

    def get_row(self, template):
        return _TraitRelation.get_row(self, 'template', template)

    def insert_template(self, data, templatefile):
        if type(data) is not dict:
            raise Error, 'Need to pass dict'
        if len(data) == 2 and 'template' in data and 'package' in data:
            data.update(dict(owner='root', grp_owner='root', mode='0100644'))
        insert_data = {'trait' : self.current_trait}
        insert_data.update(data)
        id = self.textfiles.insert_file(templatefile)
        insert_data['templatefile'] = str(id)
        self.cmd.insert(data=insert_data)

    def update_template(self, data, templatefile):
        clause = self._clause(data['package'], data['template'])
        id = self.textfiles.insert_file(templatefile)
        fields = ['owner', 'grp_owner', 'mode']
        update = {}.fromkeys(fields)
        for field in update:
            update[field] = data[field]
        update['templatefile'] = str(id)
        self.cmd.update(data=update, clause=clause)
        self.reset_clause()

    def update_templatedata(self, package, template, data):
        clause = self._clause(package, template)
        id = self.textfiles.insert_data(data)
        self.cmd.update(data=dict(templatefile=str(id)), clause=clause)
        

    def drop_template(self, package, template):
        clause = self._clause(package, template)
        self._drop_template(clause)
        
    def _drop_template(self, clause):
        self.cmd.delete(clause=clause)
        self.reset_clause()

    def set_trait(self, trait):
        _TraitRelation.set_trait(self, trait)
        self.traitparent.set_trait(trait)
        self.template.set_trait(trait)
        
    def set_template(self, package, template):
        self.template.set_template(self.templatefile(package, template))
        self.template.update(self.traitparent.Environment())

    def set_template_path(self, path):
        self.template_path = join(path, self.suite, self.current_trait)
        
        
    def export_templates(self, bkup_path):
        n = 0
        for t in self.templates():
            npath = join(bkup_path, 'template-%d' % n)
            tfile = self.templatefile(t.package, t.template)
            filecopy(tfile, npath)
            tfile.close()
            n += 1
            
    def templatefile(self, package, template):
        return strfile(self.templatedata(package, template))
    
    def templatedata(self, package, template):
        return self._template_row(package, template).data

    def _template_row(self, package, template):
        table = self._jtable
        clause = self._clause(package, template)
        return self.cmd.select_row(fields=['data', 'templatefile'], table=table, clause=clause)

    def _template_id(self, package, template):
        return self._template_row(package, template).templatefile

    def remove_templatefile(self, package, template):
        print 'remove_templatefile deprecated'
        
    def save_template(self, package, template, templatefile):
        id = self.textfiles.insert_file(templatefile)
        clause = self._clause(package, template)
        self.cmd.update(data=dict(templatefile=str(id)), clause=clause)

class TraitScript(_TraitRelation):
    def __init__(self, conn, suite):
        table = ujoin(suite, 'scripts')
        _TraitRelation.__init__(self, conn, suite, table, name='TraitScript')
        self.textfiles = TextFileManager(self.conn)
        self._jtable = '%s as s join textfiles as t ' % table
        self._jtable += 'on s.scriptfile = t.fileid' 
        
    def scripts(self, trait=None):
        if trait is None:
            trait = self.current_trait
        self.set_clause(trait)
        rows = self.cmd.select(fields=['script'], order='script')
        self.reset_clause()
        return rows

    def scriptfile(self, name):
        return strfile(self.scriptdata(name))
            
    def _script_row(self, name):
        table = self._jtable
        clause = self._clause(name)
        return self.cmd.select_row(fields=['data'], table=table, clause=clause)
        
    def _script_id(self, name):
        return self._script_row(name).scriptfile
        
    def scriptdata(self, name):
        return self._script_row(name).data
        
    def save_script(self, name, scriptfile):
        id = self.textfiles.insert_file(scriptfile)
        clause = self._clause(name)
        self.cmd.update(data=dict(scriptfile=str(id)), clause=clause)

    def remove_scriptfile(self, name):
        print 'remove_scriptfile deprecated'

    def _clause(self, name, trait=None):
        if trait is None:
            trait = self.current_trait
        return Eq('trait', trait) & Eq('script', name)

    def get(self, name):
        clause = self._clause(name)
        rows = self.cmd.select(clause=clause)
        if len(rows) == 1:
            return self.scriptfile(name)
        else:
            return None

    def read_script(self, name):
        return self.scriptdata(name)
    
    def insert_script(self, name, scriptfile):
        insert_data = {'trait' : self.current_trait,
                       'script' : name}
        id = self.textfiles.insert_file(scriptfile)
        insert_data['scriptfile'] = str(id)
        self.cmd.insert(data=insert_data)

    def update_script(self, name, scriptfile):
        id = self.textfiles.insert_file(scriptfile)
        clause = self._clause(name)
        data = dict(scriptfile=str(id))
        self.cmd.update(data=data, clause=clause)

    def update_scriptdata(self, name, data):
        clause = self._clause(name)
        id = self.textfiles.insert_data(data)
        self.cmd.update(data=dict(scriptfile=str(id)), clause=clause)

    def export_scripts(self, bkup_path):
        for row in self.scripts():
            npath = join(bkup_path, 'script-%s' % row.script)
            nfile = self.scriptfile(row.script)
            filecopy(nfile, npath)
            nfile.close()

class TraitPackage(_TraitRelation):
    def __init__(self, conn, suite):
        table = ujoin(suite, 'trait', 'package')
        _TraitRelation.__init__(self, conn, suite, table, name='TraitPackage')
        self.cmd.set_fields(['package', 'action'])
        self.traitparent = TraitParent(conn, suite)
        
    def packages(self, traits=None):
        if traits is None:
            traits = [self.current_trait]
        #self.cmd.set_clause([('trait', trait) for trait in traits], join='or')
        clause = In('trait', traits)
        rows =  self.cmd.select(clause=clause, order='package')
        self.reset_clause()
        return rows
    
    def all_packages(self, traits, traitparent=None):
        if not traitparent:
            traitparent = self.traitparent
        return list(self.packages(traitparent.get_traitset(traits)))

    def set_action(self, action, packages, trait=None):
        if trait is None:
            trait = self.current_trait
        clause = Eq('trait', trait) & In('package', packages)
        if action == 'drop':
            self.cmd.delete(clause=clause)
        elif action in ['remove', 'install', 'purge']:
            self.cmd.set_data({'action' : action})
            self.cmd.update(clause=clause)
        else:
            raise Error, 'bad action in TraitPackage -%s-' % action

    def insert_package(self, package, action='install'):
        idata = {'trait' : self.current_trait,
                 'action' : action,
                 'package' : package}
        self.cmd.insert(data=idata)

    def insert_packages(self, packages):
        diff = self.diff('package', packages)
        for package in packages:
            if package in diff:
                self.insert_package(package)
        

    def set_trait(self, trait):
        _TraitRelation.set_trait(self, trait)
        self.traitparent.set_trait(trait)

class TraitDebconf(_TraitRelation):
    def __init__(self, conn, suite):
        table = ujoin(suite, 'debconf')
        _TraitRelation.__init__(self, conn, suite, table, name='TraitDebconf')

    def _make_section(self, row):
        items = ['%s: %s' % (k.capitalize(),v) for k,v in row.items() if k != 'trait']
        return '\n'.join(items)
        
    def get_config(self, trait=None, rows=None):
        if rows is None:
            rows = self.trait_debconf(trait)
        return '\n\n'.join([self._make_section(row) for row in rows])

    def get_debconf(self, name, trait=None):
        if trait is None:
            trait = self.current_trait
        clause = Eq('trait', trait) & Eq('name', name)
        rows = self.cmd.select(clause=clause)
        if len(rows) != 1:
            raise Error, 'no debconf for %s in %s' % (name, trait)
        return rows[0]

    def trait_debconf(self, trait=None):
        if trait is None:
            trait = self.current_trait
        clause = Eq('trait', trait)
        return self.cmd.select(clause=clause, order='name')
    

    def insert(self, data, trait=None):
        if trait is None:
            trait = self.current_trait
        data['trait'] = trait
        self.cmd.insert(data=data)

    def update(self, data, trait=None):
        if trait is None:
            trait = self.current_trait
        data['trait'] = trait
        self.cmd.update(data=data, clause=Eq('trait', trait) & Eq('name', data['name']))
        

    def delete(self, name, trait=None):
        if trait is None:
            trait = self.current_trait
        clause = Eq('trait', trait) & Eq('name', name)
        self.cmd.delete(clause=clause)
        
    def all_owners(self, trait=None):
        if trait is None:
            trait = self.current_trait
        clause = Eq('trait', trait)
        rows = self.cmd.select(fields=['distinct owners'], clause=clause)
        all_owners = []
        for row in rows:
            if row.owners.find(',') > -1:
                owners = map(''.strip, row.owners.split(','))
                for owner in owners:
                    if owner not in all_owners:
                        all_owners.append(owner)
            else:
                all_owners.append(row.owners.strip())
        return all_owners
    
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
        self._debconf = TraitDebconf(self.conn, self.suite)
        self._scripts = TraitScript(self.conn, self.suite)
        self.current_trait = None
        self.environ = {}
        
    def set_trait(self, trait):
        self.current_trait = trait
        self.environ = TraitEnvironment(self.conn, self.suite, trait)
        self._parents.set_trait(trait)
        self._packages.set_trait(trait)
        self._templates.set_trait(trait)
        self._debconf.set_trait(trait)
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
        self._debconf.delete_trait(trait)
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
        self._debconf.set_trait(trait.name)
        self._scripts.set_trait(trait.name)
        self._parents.insert_parents(trait.parents)
        for package, action in trait.packages.items():
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
        for debconf in trait.debconf.values():
            self._debconf.insert(debconf, trait.name)
        for script in trait.scripts:
            #scriptfile = tar.get_script(script)
            scriptfile = file(join(path, 'script-%s' % script))
            self._scripts.insert_script(script, scriptfile)
        environ = TraitEnvironment(self.conn, suite, trait.name)
        environ.update(trait.environ)
        self.set_trait(lasttrait)

    def get_config(self):
        return self._debconf.get_config()

    def backup_trait(self, tball_path):
        print 'this needs to be called export_trait'
        xmldata = TraitElement(self.conn, self.suite)
        xmldata.set(self.current_trait)
        bkup_path = join(tball_path, self.current_trait)
        makepaths(bkup_path)
        xmlfile = file(join(bkup_path, 'trait.xml'), 'w')
        xmlfile.write(xmldata.toprettyxml())
        xmlfile.close()
        self._templates.export_templates(bkup_path)
        self._scripts.export_scripts(bkup_path)
        print 'all exported', os.listdir(bkup_path)
        #make_tarball(bkup_path, tball_path, self.current_trait)
        #os.system('rm %s -fr' % bkup_path)
        
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
        self.debconf_element = DebConfigurationElement()
        self.appendChild(self.desc_element)
        self.appendChild(self.parent_element)
        self.appendChild(self.pkg_element)
        self.appendChild(self.env_element)
        self.appendChild(self.templ_element)
        self.appendChild(self.debconf_element)
        self.appendChild(self.scripts_element)
        self.set_suite(suite)
        
    def set_suite(self, suite):
        self.suite = suite
        self.setAttribute('suite', self.suite)
        self.traitparent = TraitParent(self.conn, self.suite)
        self.traitpackage = TraitPackage(self.conn, self.suite)
        self.traittemplate = TraitTemplate(self.conn, self.suite)
        self.traitdebconf = TraitDebconf(self.conn, self.suite)
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

    def set_debconf(self):
        self.debconf = self.traitdebconf.trait_debconf(self.name)
        while self.debconf_element.hasChildNodes():
            del self.debconf_element.childNodes[0]
        for debconf in self.debconf:
            element = DebConfElement(self.name, debconf)
            self.debconf_element.appendChild(element)

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
        self.set_debconf()
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

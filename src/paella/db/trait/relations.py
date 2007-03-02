import os
from os.path import join
from sets import Set
import tempfile

from kjbuckets import kjGraph

from useless.base import Error
from useless.base.util import ujoin, RefDict, strfile, filecopy

from useless.sqlgen.clause import one_many, Eq, In
from useless.db.midlevel import Environment

from paella.base.objects import TextFileManager

from base import TraitRelation
from base import Template

class TraitEnvironment(Environment):
    def __init__(self, conn, suite, trait):
        self.suite = suite
        table = ujoin(suite, 'variables')
        Environment.__init__(self, conn, table, 'trait')
        self.set_main(trait)


class TraitParent(TraitRelation):
    def __init__(self, conn, suite):
        table = ujoin(suite, 'trait', 'parent')
        TraitRelation.__init__(self, conn, suite, table, name='TraitParent')
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
        if parents:
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

    def insert_new_parents_list(self, parents):
        current_parents = [row.parent for row in self.parents()]
        new_parents = parents
        common_parents = [p for p in new_parents if p in current_parents]
        delete_parents = [p for p in current_parents if p not in common_parents]
        insert_parents = [p for p in new_parents if p not in common_parents]
        self.delete(parents=delete_parents)
        self.insert_parents(insert_parents)
        
        
        
class TraitTemplate(TraitRelation):
    def __init__(self, conn, suite):
        table = ujoin(suite, 'templates')
        TraitRelation.__init__(self, conn, suite, table, name='TraitTemplate')
        self.traitparent = TraitParent(conn, suite)
        self.template = Template()
        self.template.set_suite(suite)
        self.template_path = None
        self.textfiles = TextFileManager(self.conn)
        self._jtable = '%s as s join textfiles as t ' % table
        self._jtable += 'on s.templatefile = t.fileid' 

    def _clause(self, template, trait=None):
        if trait is None:
            trait = self.current_trait
        return Eq('trait', trait) & Eq('template', template)
    
    def templates(self, trait=None, fields=['*']):
        if trait is None:
            trait = self.current_trait
            self.reset_clause()
            return self.cmd.select(fields=fields, order=['template'])
        else:
            self.set_clause(trait)
            rows = self.cmd.select(fields=fields, order=['template'])
            self.reset_clause()
            return rows

    def has_template(self, template):
        return self.has_it('template', template)

    def get_row(self, template):
        return TraitRelation.get_row(self, 'template', template)

    def insert_template(self, data, templatefile):
        if type(data) is not dict:
            raise Error, 'Need to pass dict'
        if len(data) == 2 and 'template' in data and 'package' in data:
            data.update(dict(owner='root', grp_owner='root', mode='0100644'))
        insert_data = {'trait' : self.current_trait}
        insert_data.update(data)
        txtid = self.textfiles.insert_file(templatefile)
        insert_data['templatefile'] = str(txtid)
        self.cmd.insert(data=insert_data)

    def insert_template_from_tarfile(self, template_path, tarfileobj):
        templatefile = tarfileobj.extractfile(template_path)
        info = tarfileobj.getmember(template_path)
        data = dict(owner=info.uname, grp_owner=info.gname,
                    mode=oct(info.mode), template=template_path)
        self.insert_template(data, templatefile)
        
    def update_template(self, data, templatefile):
        clause = self._clause(data['template'])
        id = self.textfiles.insert_file(templatefile)
        fields = ['owner', 'grp_owner', 'mode']
        update = {}
        for f in fields:
            if f in data:
                update[f] = data[f]
        update['templatefile'] = str(id)
        self.cmd.update(data=update, clause=clause)
        self.reset_clause()

    def update_templatedata(self, template, data):
        clause = self._clause(template)
        txtid = self.textfiles.insert_data(data)
        self.cmd.update(data=dict(templatefile=str(txtid)), clause=clause)
        

    def update_template_v2(self, template, data=None, templatefile=None, contents=None):
        if templatefile is not None and contents is not None:
            raise RuntimeError, 'must either pass a file object or a string but not both'
        clause = self._clause(template)
        txtid = None
        if templatefile is not None:
            txtid = self.textfiles.insert_file(templatefile)
        if contents is not None:
            txtid = self.textfiles.insert_data(contents)
        update = {}
        if txtid is not None:
            update.update(dict(templatefile=str(txtid)))
        if data is not None:
            update.update(data)
        self.cmd.update(data=update, clause=clause)
        
    def drop_template(self, template):
        clause = self._clause(template)
        self._drop_template(clause)
        
    def _drop_template(self, clause):
        self.cmd.delete(clause=clause)
        self.reset_clause()

    def set_trait(self, trait):
        TraitRelation.set_trait(self, trait)
        self.traitparent.set_trait(trait)
        self.template.set_trait(trait)
        
    def set_template(self, template):
        self.template.set_template(self.templatefile(template))
        self.template.update(self.traitparent.Environment())

    def set_template_path(self, path):
        self.template_path = join(path, self.suite, self.current_trait)
        
    # set a keyword argument (to be removed sometime in the future)
    # to revert to previous way of naming template files.  The default is to
    # use the new method.
    def export_templates(self, bkup_path, numbered_templates=False):
        n = 0
        for t in self.templates():
            if numbered_templates:
                filename  = join(bkup_path, 'template-%d' % n)
            else:
                template_id = t.template.replace('/', '-slash-')
                filename = join(bkup_path, 'template-%s' % template_id)
            tfile = self.templatefile(t.template)
            filecopy(tfile, filename)
            tfile.close()
            n += 1
            
    def templatefile(self, template):
        return strfile(self.templatedata(template))
    
    def templatedata(self, template):
        return self._template_row(template).data

    def _template_row(self, template):
        table = self._jtable
        clause = self._clause(template)
        return self.cmd.select_row(fields=['data', 'templatefile'], table=table, clause=clause)

    def _template_id(self, template):
        return self._template_row(template).templatefile

    def save_template(self, template, templatefile):
        id = self.textfiles.insert_file(templatefile)
        clause = self._clause(template)
        self.cmd.update(data=dict(templatefile=str(id)), clause=clause)

    def edit_template(self, template):
        data = self.templatedata(template)
        tmp, path = tempfile.mkstemp('paella', 'template')
        tmp = file(path, 'w')
        tmp.write(data)
        tmp.close()
        os.system('$EDITOR %s' % path)
        tmp = file(path, 'r')
        mod = tmp.read()
        tmp.seek(0)
        if mod != data:
            print 'template modified'
            self.save_template(template, tmp)
        os.remove(path)
        
class TraitScript(TraitRelation):
    def __init__(self, conn, suite):
        table = ujoin(suite, 'scripts')
        TraitRelation.__init__(self, conn, suite, table, name='TraitScript')
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

    def edit_script(self, name):
        sfile = self.get(name)
        tmp, path = tempfile.mkstemp('paella', 'script')
        script = sfile.read()
        sfile.close()
        tmp = file(path, 'w')
        tmp.write(script)
        tmp.close()
        os.system('$EDITOR %s' % path)
        tmp = file(path, 'r')
        mod = tmp.read()
        tmp.seek(0)
        if mod != script:
            print 'script modified'
            self.save_script(name, tmp)
        os.remove(path)
        

class TraitPackage(TraitRelation):
    def __init__(self, conn, suite):
        table = ujoin(suite, 'trait', 'package')
        TraitRelation.__init__(self, conn, suite, table, name='TraitPackage')
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

    def delete_package(self, package, action):
        clause = Eq('package', package) & Eq('action', action)
        self.cmd.delete(clause=clause)
        

    def insert_packages(self, packages):
        diff = self.diff('package', packages)
        for package in packages:
            if package in diff:
                self.insert_package(package)
        

    def set_trait(self, trait):
        TraitRelation.set_trait(self, trait)
        self.traitparent.set_trait(trait)

if __name__ == '__main__':
    #f = file('tmp/trait.xml')
    #tx = TraitXml(f)
    import sys

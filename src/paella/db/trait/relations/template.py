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

from paella import deprecated

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

    def update_template(self, template, data=None, templatefile=None,
                        contents=None):
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
        
    def update_templatedata(self, template, data):
        deprecated('update_templatedata is deprecated use update_template instead')
        self.update_template(template, contents=data)
        
        

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
        
if __name__ == '__main__':
    #f = file('tmp/trait.xml')
    #tx = TraitXml(f)
    import sys

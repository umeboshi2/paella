import os
from os.path import join
from sets import Set
import tempfile
import difflib

from kjbuckets import kjGraph

from Cheetah.Template import Template as ChTemplate
from Cheetah.Parser import ParseError
from Cheetah.NameMapper import NotFound


from useless.base import Error
from useless.base.util import ujoin, RefDict, strfile, filecopy
from useless.base.template import Template

from useless.sqlgen.clause import one_many, Eq, In
from useless.db.midlevel import Environment

from paella.base.objects import TextFileManager

from base import TraitRelation
from parent import TraitParent

from paella import deprecated


class TraitTemplate(TraitRelation):
    def __init__(self, conn, suite):
        table = ujoin(suite, 'templates')
        TraitRelation.__init__(self, conn, suite, table, name='TraitTemplate')
        self.traitparent = TraitParent(conn, suite)
        self.template = Template()
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
        
    def drop_template(self, template):
        clause = self._clause(template)
        self._drop_template(clause)
        
    def _drop_template(self, clause):
        self.cmd.delete(clause=clause)
        self.reset_clause()

    def set_trait(self, trait):
        TraitRelation.set_trait(self, trait)
        self.traitparent.set_trait(trait)
        
    def set_template(self, template):
        self.template.set_template(self.templatedata(template))
        self.template.update(self.traitparent.Environment())

    def set_template_path(self, path):
        self.template_path = join(path, self.suite, self.current_trait)

    def export_templates(self, bkup_path):
        for t in self.templates():
            template_id = t.template.replace('/', '-slash-')
            filename = join(bkup_path, 'template-%s' % template_id)
            tfile = self.templatefile(t.template)
            filecopy(tfile, filename)
            tfile.close()
            
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
        
###################################
#Cheetah Template test code
###################################

# The conversion only converts to raw
# which isn't very useful
# I haven't yet determined the best
# way to provide an environment of
# variables to be used in the templates
# so the use of cheetah templates are on
# hold.  I think that anything that uses
# templates like cheetah, or jinja, etc. will
# be using the InstallerTools class to have
# a better chance of reaching all the variables
# and classes that paella uses.



class CheetahConversionError(RuntimeError):
    pass

def insert_raw_directives(text):
        lines = text.split('\n')
        if not lines[0].startswith('##cheetah'):
            raise RuntimeError, 'need the ##cheetah comment on the top'
        lines.insert(1, '#raw')
        if not lines[-1]:
            print 'insert at end'
            lines[-1] = '#end raw'
        else:
            lines.append('#end raw')
        #ctext = ''.join([line + '\n' for line in lines])
        ctext = '\n'.join(lines)
        return ctext

def convert_text_to_cheetah_template(text):
    assert not text.startswith('##cheetah')
    ctext = '##cheetah\n#raw\n' + text + '#end raw\n'
    if ctext.find('\$') > -1:
        print "replacing \$"
        ctext = ctext.replace('\$', '\\\$')
    if ctext.find('\#') > -1:
        print "replacing \#"
        ctext = ctext.replace('\#', '\\\#')
    ctemplate = ChTemplate(ctext)
    if text == str(ctemplate):
        return ctemplate
    else:
        added_endl = False
        removed_endl = False
        if str(ctemplate) + '\n' == text:
            removed_endl = True
        if str(ctemplate) == text + '\n':
            added_endl = True
        if added_endl or removed_endl:
            print 'things could be ok'
        else:
            raise CheetahConversionError, 'unable to convert template'


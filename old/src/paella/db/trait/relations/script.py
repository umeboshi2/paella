import os
from os.path import join
from sets import Set
import tempfile
import subprocess

from kjbuckets import kjGraph

from useless.base import Error
from useless.base.util import ujoin, RefDict, strfile, filecopy

from useless.sqlgen.clause import one_many, Eq, In
from useless.db.midlevel import Environment

from paella.base.objects import TextFileManager

from base import TraitRelation

from paella import deprecated

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

    def delete_script(self, name):
        clause = self._clause(name)
        self.cmd.delete(clause=clause)
        
    def export_scripts(self, bkup_path):
        for row in self.scripts():
            npath = join(bkup_path, 'script-%s' % row.script)
            nfile = self.scriptfile(row.script)
            filecopy(nfile, npath)
            nfile.close()

    def edit_script(self, name):
        sfile = self.get(name)
        tmp, filename = tempfile.mkstemp('paella', 'script')
        script = sfile.read()
        sfile.close()
        tmp = file(filename, 'w')
        tmp.write(script)
        tmp.close()
        #os.system('$EDITOR %s' % filename)
        editor = os.environ['EDITOR']
        subprocess.call([editor, filename])
        tmp = file(filename, 'r')
        mod = tmp.read()
        tmp.seek(0)
        if mod != script:
            print 'script modified'
            self.save_script(name, tmp)
        os.remove(filename)
        bkup = '%s~' % filename
        if os.path.isfile(bkup):
            os.remove(bkup)
            
        
if __name__ == '__main__':
    #f = file('tmp/trait.xml')
    #tx = TraitXml(f)
    import sys

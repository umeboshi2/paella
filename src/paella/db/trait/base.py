from os.path import join

from useless.base.util import ujoin
from useless.base.template import Template as _Template
from useless.db.midlevel import StatementCursor
from useless.db.midlevel import SimpleRelation

class AllTraits(StatementCursor):
    def __init__(self, conn):
        StatementCursor.__init__(self, conn, name='AllTraits')
        self.set_table('traits')

    def list(self):
        return [x.trait for x in self.select()]

class Traits(StatementCursor):
    def __init__(self, conn, suite):
        StatementCursor.__init__(self, conn, name='AllTraits')
        self.set_suite(suite)
        
        
    def set_suite(self, suite):
        self.suite = suite
        self.set_table(ujoin(self.suite, 'traits'))
        

    def list(self):
        return [x.trait for x in self.select(order=['trait'])]
    

class TraitRelation(SimpleRelation):
    def __init__(self, conn, suite, table, name='_TraitRelation'):
        SimpleRelation.__init__(self, conn, table, 'trait', name=name)
        self.suite = suite
        self.current_trait = None

    def set_trait(self, trait):
        self.set_current(trait)
        self.current_trait = self.current
        

    def delete_trait(self, trait):
        self.delete(trait)
        
class Template(_Template):
    def __init__(self, data={}):
        _Template.__init__(self, data)
        self.template_path = None

    def set_path(self, path):
        self.template_path = path
        
    #this returns the path from the root
    #of the trait tarfile to the template
    def _template_filename(self, suite, trait, package, template):
        tpath = join(self.template_path, suite, trait, package)
        return join(tpath, template + '.template')

    def _filesel(self, filesel, path):
        if filesel:
            path += '/'
        return path

    def _suite_template_path(self, suite, filesel=False):
        return self._filesel(filesel, join(self.template_path, suite))

    def _trait_temp_path(self, tmp_path, suite, trait, filesel=False):
        return self._filesel(filesel, join(tmp_path, suite, trait))
    
    def set_template(self, templatefile):
        _Template.set_template(self, templatefile.read())
        templatefile.close()

    def set_suite(self, suite):
        self.suite = suite

    def set_trait(self, trait):
        self.trait = trait
        
            
if __name__ == '__main__':
    pass

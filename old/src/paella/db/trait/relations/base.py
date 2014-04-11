import os

from useless.base.util import ujoin
from useless.base.template import Template as _Template
from useless.db.midlevel import SimpleRelation
from useless.db.midlevel import Environment

from paella import deprecated

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
        deprecated("This Template class is completely deprecated.")
        _Template.__init__(self, data)
        self.template_path = None

    def set_path(self, path):
        deprecated("Template.set_path has unknown importance")
        self.template_path = path
        
    #this returns the path from the root
    #of the trait tarfile to the template
    def _template_filename(self, suite, trait, package, template):
        msg = '_template_filename was only useful when the'
        msg += ' templates were stored in tarfiles'
        deprecated(msg)
        tpath = os.path.join(self.template_path, suite, trait, package)
        return os.path.join(tpath, template + '.template')

    def _filesel(self, filesel, path):
        deprecated('_filesel is not used anymore')
        if filesel:
            path += '/'
        return path

    def _suite_template_path(self, suite, filesel=False):
        deprecated("_suite_template_path is obsolete")
        return self._filesel(filesel, os.path.join(self.template_path, suite))

    def _trait_temp_path(self, tmp_path, suite, trait, filesel=False):
        deprecated("_trait_temp_path is obsolete")
        return self._filesel(filesel, os.path.join(tmp_path, suite, trait))
    
    def set_template(self, templatefile):
        _Template.set_template(self, templatefile.read())
        templatefile.close()

    def set_suite(self, suite):
        deprecated("set_suite is obsolete")
        self.suite = suite

    def set_trait(self, trait):
        deprecated("set_trait is obsolete")
        self.trait = trait
        
            

class TraitEnvironment(Environment):
    def __init__(self, conn, suite, trait):
        self.suite = suite
        table = ujoin(suite, 'variables')
        Environment.__init__(self, conn, table, 'trait')
        self.set_main(trait)

if __name__ == '__main__':
    pass

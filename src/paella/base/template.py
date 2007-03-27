import os
from os.path import isdir, isfile, join, basename, dirname

from useless.base.template import Template as _Template

from useless.base.util import RefDict, strfile



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
        

class TemplatedEnvironment(RefDict):
    def dereference(self, key):
        items = [(k,v) for k,v in self.items()]
        data = dict(items)
        print data
        tmpl = _Template(data=data)
        tmpl.update(data)
        print 'tmpl.keys', tmpl.keys()
        #value = RefDict.dereference(self, key)
        tmpl.set_template(self[key])
        return tmpl.sub()
    

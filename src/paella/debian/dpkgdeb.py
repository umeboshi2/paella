import os, sys
from os.path import join
import tarfile

debcmd = 'dpkg-deb'

class DpkgDeb(object):
    def __init__(self):
        object.__init__(self)

    def __run_cmd__(self, command, path=None, fields=None):
        if path is None:
            path = self.path
        if command in ['info', 'field', 'contents', 'fsys-tarfile']:
            if fields:
                cmd = '%s --%s %s %s' %(debcmd, command, path, ' '.join(fields))
            else:
                cmd = '%s --%s %s' %(debcmd, command, path)
        elif command == 'extract':            
            cmd = '%s --%s %s %s' %(debcmd, command, path, fields)
        elif command == 'control':            
            cmd = '%s --%s %s' %(debcmd, command, path)
        input, output = os.popen2(cmd)
        return input, output

    def set_path(self, path):
        self.path = path
    

    def info(self, path=None, component=None):
        if component:
            i,o = self.__run_cmd__('info', path, fields=[component])
        else:
            i,o = self.__run_cmd__('info', path)
        return o.read()
    
    def field(self, field, path=None):
        i,o = self.__run_cmd__('field', path, [field])
        return o.read().strip()

    def systar(self, path=None):
        i,o = self.__run_cmd__('fsys-tarfile', path)
        return tarfile.open(mode="r|", fileobj=o)

    def contents(self, path=None):
        i,o = self.__run_cmd__('contents', path)
        return o.read()

    def extract(self, archive, path):
        self.__run_cmd__('extract', archive, path)

    def control(self, archive, path):
        here = os.getcwd()
        os.chdir(path)
        self.__run_cmd__('control', archive)
        os.chdir(here)
        

if __name__ == '__main__':
    path = 'bash_2.05a-11_i386.deb'
    dd = DpkgDeb()
    dd.set_path(path)
    

        

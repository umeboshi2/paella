import os

from paella.installer.base import Modules

def setup_modules(target, modules):
    mfile = Modules(os.path.join(target, 'etc/modules'))
    for m in modules:
        mfile.append(m)
    mfile.write()
    

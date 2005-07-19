import sys, os
from distutils.core import setup

PACKAGES = ['base', 'debian', 'db', 'dbgtk', 'installer', 'admin', 'kde-admin']
package = None
if sys.argv[1] in PACKAGES:
    package = sys.argv[1]
    del sys.argv[1]


pd = {'' : 'src'}

print os.environ

PACKS = {
    'base' : ['paella', 'paella/base'],
    'db' : ['paella/db', 'paella/db/schema',
            'paella/db/trait', 'paella/db/family',
            'paella/db/profile', 'paella/db/machine'],
    'debian' : ['paella/debian', 'paella/debian/newrepos'],
    'kde-admin' : ['paella/kde']
    }

if package is not None:
    packages = ['paella/'+package]
    if package in PACKS:
        packages = PACKS[package]
else:
    packages = []
    package = 'dummy'

setup(name='paella-'+package,
      version="0.2",
      description = 'paella configuration/installation management system',
      author='Joseph Rawson',
      author_email='umeboshi@gregscomputerservice.com',
      package_dir = {'' : 'src'},
      packages = packages
      )



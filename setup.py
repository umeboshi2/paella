import sys
from distutils.core import setup

package = sys.argv[1]
del sys.argv[1]


pd = {'' : 'src'}


PACKS = {
    'base' : ['paella', 'paella/base'],
    'db' : ['paella/db', 'paella/db/schema',
            'paella/db/trait', 'paella/db/family',
            'paella/db/profile', 'paella/db/machine'],
    'debian' : ['paella/debian', 'paella/debian/newrepos']
    }

packages = ['paella/'+package]
if package in PACKS:
    packages = PACKS[package]

setup(name='paella-'+package,
      version="0.2",
      description = 'paella configuration/installation management system',
      author='Joseph Rawson',
      author_email='umeboshi@gregscomputerservice.com',
      package_dir = {'' : 'src'},
      packages = packages
      )



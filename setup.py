import sys
from distutils.core import setup

package = sys.argv[1]
del sys.argv[1]


pd = {'' : 'src'}



packages = ['paella/'+package]
if package == 'base':
    packages = ['paella'] + packages
setup(name='paella-'+package,
      version="0.2",
      description = 'paella configuration/installation management system',
      author='Joseph Rawson',
      author_email='umeboshi@gregscomputerservice.com',
      package_dir = {'' : 'src'},
      packages = packages
      )



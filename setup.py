import sys, os
from distutils.core import setup

PACKAGES = ['base', 'debian', 'db', 'dbgtk', 'installer', 'admin']
package = None
if sys.argv[1] in PACKAGES:
    package = sys.argv[1]
    del sys.argv[1]


pd = {'' : 'src'}

#print os.environ

PACKS = {
    'base' : ['paella',
              'paella/base'
              ],
    'db' : ['paella/db',
            'paella/db/trait',
            'paella/db/trait/relations',
            'paella/db/schema',
            'paella/db/family',
            'paella/db/profile',
            'paella/db/machine'
            ],
    'debian' : ['paella/debian',
                'paella/debian/newrepos'
                ],
    'admin' : ['paella/kde',
               'paella/kde/base',
               'paella/kde/trait',
               'paella/kde/machine',
               'paella/kde/docgen',
               'paella/kde/umlmanager',
               'paella/kde/aptsrc',
               'paella/kde/suites'
               ],
    'installer' : ['paella/installer',
                   'paella/installer/util'
                   ]
    }

if package is not None:
    packages = ['paella/'+package]
    if package in PACKS:
        packages = PACKS[package]
else:
    packages = []
    package = 'dummy'

_myfindcmdforpackages = 'find src -type d | grep -v svn | cut -f2- -d/'
url = 'http://paella.berlios.de'
setup(name='paella-'+package,
      version="0.2",
      description = 'paella configuration/installation management system',
      author='Joseph Rawson',
      author_email='umeboshi@gregscomputerservice.com',
      url=url,
      package_dir = {'' : 'src'},
      packages = packages
      )



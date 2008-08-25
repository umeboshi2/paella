import os, sys
import glob
from distutils.core import setup


from distutils.command.clean import clean as _clean
from distutils.command.build import build as _build

def get_version(astuple=False):
    topline = file('debian/changelog').next()
    VERSION = map(int, topline[topline.find('(')+1 :topline.find(')')].split('.'))
    if astuple:
        return tuple(VERSION)
    else:
        return '.'.join(map(str, VERSION))

class clean(_clean):
    def run(self):
        _clean.run(self)
        here = os.getcwd()
        for root, dirs, files in os.walk(here):
            for afile in files:
                if afile.endswith('~'):
                    #print "removing backup file", os.path.join(root, afile)
                    os.remove(os.path.join(root, afile))
                if afile.endswith('.pyc'):
                    os.remove(os.path.join(root, afile))
        os.chdir('docs')
        #map(os.remove, glob.glob('*.html'))
        os.system('rm -fr html')
        os.chdir(here)
        


data_files = []

class builddocs(_build):
    def run(self):
        _build.run(self)
        here = os.getcwd()
        os.chdir('docs')
        print "building docs"
        exclude = ['.svn', 'images']
        files = [f for f in os.listdir('.') if f not in exclude]
        print "source doc files:", ', '.join(files)
        os.mkdir('html')
        for srcfile in files:
            print "building", srcfile
            htmlfile = 'html/%s.html' % srcfile
            os.system('rst2html %s %s' % (srcfile, htmlfile))
            data_files.append('docs/%s' % htmlfile)
        os.chdir(here)
            

PACKAGES = ['base', 'debian', 'db', 'dbgtk', 'installer', 'admin', 'uml-admin']
package = None
docs = False
if sys.argv[1] in PACKAGES:
    package = sys.argv[1]
    del sys.argv[1]
elif sys.argv[1] == 'doc':
    docs = True
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
               'paella/kde/aptsrc',
               'paella/kde/suites'
               ],
    'installer' : ['paella/installer',
                   'paella/installer/util',
                   'paella/oldinstaller',
                   'paella/oldinstaller/util'
                   ],
    'uml-admin' : ['paella/uml',
                   'paella/kde/umlmanager'
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
version = get_version()
author_email = 'umeboshi3@gmail.com'
author = 'Joseph Rawson'
description = 'paella configuration/installation management system',

if docs:
    setup(name='paella-doc',
          version=version,
          description=description,
          author=author,
          author_email=author_email,
          url=url,
          data_files=data_files,
          cmdclass=dict(clean=clean, build=builddocs)
          )
else:
    setup(name='paella-'+package,
          version=version,
          description=description,
          author=author,
          author_email=author_email,
          url=url,
          package_dir = {'' : 'src'},
          packages = packages,
          cmdclass=dict(clean=clean)
          )



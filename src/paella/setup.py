import os

from distutils.core import Command
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
    
#http://stackoverflow.com/questions/1710839/custom-distutils-commands
class CleanCommand(Command):
    description = 'My Clean Command'
    user_options = []
    def initialize_options(self):
        self.cwd = None

    def finalize_options(self):
        self.cwd = os.getcwd()

    def run(self):
        for root, dirs, files in os.walk(self.cwd):
            for filename in files:
                if filename.endswith('~'):
                    os.remove(os.path.join(root, filename))
        

requires = [
    'pyramid',
    'pyramid_mako',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'SQLAlchemy',
    'psycopg2',
    'transaction',
    'zope.sqlalchemy',
    'pyramid-beaker',
    'waitress',
    'requests',
    'cornice',
    ]

setup(name='paella',
      version='0.0',
      description='paella',
      long_description='paella',
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='paella',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = paella:main
      [console_scripts]
      initialize_paella_db = paella.scripts.initializedb:main
      """,
      cmdclass=dict(clean=CleanCommand),
      )

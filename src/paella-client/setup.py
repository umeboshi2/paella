from setuptools import setup, find_packages
import sys, os

# http://stackoverflow.com/a/22147112/1869821
# if you are not using vagrant, just delete os.link directly,
# The hard link only saves a little disk space, so you should not care
if os.environ.get('USER','') == 'vagrant':
    del os.link


version = '0.1'

setup(name='paella-client',
      version=version,
      description="Command line paella client",
      long_description="""\
Command line paella client""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Joseph Rawson',
      author_email='joseph.rawson.works@gmail.com',
      url='https://github.com/umeboshi2/paella',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      paella-submit-machine = paellaclient.submit_machine:main
      """,
      )

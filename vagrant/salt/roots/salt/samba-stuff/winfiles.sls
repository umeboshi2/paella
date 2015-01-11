#!pydsl
# -*- mode: python -*-
import os
import logging

log = logging.getLogger(__name__)

download_files = __pillar__['paella_enable_software_download_states']
cache = '/vagrant/vagrant/cache'
winfiles = __pillar__['cached_windows_files']

for name in winfiles:
    id = 'cached_windows_file_%s' % name
    info = __pillar__[name]
    filename = os.path.join(cache, 'windows', info['name'])
    mfile = state(id)
    if os.path.exists(filename):
        mfile.file('exists', filename)
    else:
        mfile.file('managed',
                   source=info['source'],
                   source_hash=info['source_hash'],
                   name=filename,
                   makedirs=True)
                   

nu2_directory = os.path.join(cache, 'nu2-files')
zipname = 'bfd107.zip'
mdir = state('nu2_files_directory')
mdir.file('directory', name=nu2_directory, makedirs=True)

mfile = state('nu2-bfd.zip')
mfile.file('managed',
           source=os.path.join(__pillar__['nu2_mirror'], zipname),
           source_hash='sha256=768467860ce870010e977a051a26fae712ad853b96667bd242a71122ea049c01',
           name=os.path.join(nu2_directory, zipname))

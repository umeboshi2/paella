#!pydsl
# -*- mode: python -*-
import os
import logging

log = logging.getLogger(__name__)

check_iso = __pillar__['paella_really_download_or_check_the_large_iso_files']
download_files = __pillar__['paella_enable_software_download_states']
cache = '/vagrant/vagrant/cache'
win7 = __pillar__['win7_ultimate_iso']

filestate = 'exists'
if check_iso:
    filestate = 'managed'
    
for arch in ['i386', 'amd64']:
    id = 'win7-ultimate-%s-iso' % arch
    mfile = state(id)
    name = os.path.join(cache, 'win7-ultimate-%s.iso' % arch)
    if not check_iso:
        mfile.file('exists', name=name)
    else:
        mfile.file('managed',
                   name=name,
                   source=win7[arch]['source'],
                   source_hash=win7[arch]['source_hash'])
        
                   
for iso in __pillar__['cached_iso_files']:
    id = '%s_iso' % iso
    log.info("ID is %s" % id)
    info = __pillar__[iso]
    mfile = state(id)
    filename = os.path.join(cache, info['name'])
    if not check_iso:
        mfile.file('exists', name=filename)
    else:
        mfile.file('managed', source=info['source'],
                   source_hash=info['source_hash'],
                   name=filename)

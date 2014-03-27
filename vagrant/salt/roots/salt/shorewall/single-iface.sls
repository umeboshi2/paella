#!pydsl
# -*- mode: python -*-

import os

saltpath_prefix = 'salt://shorewall/templates/single'
shorewall_path = '/etc/shorewall'
defaults = dict(user='root', group='root', mode='0644')


conffiles = ['shorewall.conf', 'interfaces', 'policy', 'rules',
             'zones']

for cfile in conffiles:
    fullpath = os.path.join(shorewall_path, cfile)
    src = os.path.join(saltpath_prefix, cfile)
    fstate = state(fullpath)
    fstate.file('managed',
                source=src,
                template='mako',
                **defaults)

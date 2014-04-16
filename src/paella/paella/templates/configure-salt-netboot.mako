#!/usr/bin/env python

import os, sys
import subprocess
import json

import requests


machine='${machine}'

print "Configure Salt Netboot Started..."

cmd = ['/etc/init.d/salt-minion', 'stop']
subprocess.call(cmd)

cmd = ['update-rc.d', '-f', 'salt-minion', 'remove']
subprocess.check_call(cmd)

# FIXME - fix ip address
minion_config = """\
master: 10.0.4.1
id: ${machine}
"""

rc_local = """\
#!/bin/sh -e

# FIXME
# This should be run as a true initscript
# that can be removed later without disturbing the 
# system.
if ! [ -r /etc/salt/highstate-complete ]; then
    salt-call state.highstate
    touch /etc/salt/highstate-complete
fi
exit 0
"""

with file('/etc/salt/minion', 'w') as mfile:
    mfile.write(minion_config)

with file('/etc/rc.local', 'w') as rfile:
    rfile.write(rc_local)

subprocess.call(['chmod', '755', '/etc/rc.local'])




# FIXME - fix ip address
url = 'http://10.0.4.1/paella/api0/machines'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}    
data = dict(action='stage_over', machine=machine)

r = requests.post(url, data=json.dumps(data), headers=headers)

if not r.ok:
    raise RuntimeError, "Something bad happened: %s" % r.status_code



# does everything work?
sys.exit(0)

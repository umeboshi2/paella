#!/usr/bin/env python

import os, sys
import subprocess
import json

import requests


machine='${machine}'
uuid='${uuid}'

print "Configure Salt Netboot Started..."

cmd = ['/etc/init.d/salt-minion', 'stop']
subprocess.call(cmd)

cmd = ['update-rc.d', '-f', 'salt-minion', 'remove']
subprocess.check_call(cmd)

# FIXME - fix ip address
minion_config = """\
master: ${paella_server_ip}
id: ${machine}
"""

rc_local = """\
#!/bin/sh -e

# FIXME
# This should be run as a true initscript
# that can be removed later without disturbing the 
# system.
if ! [ -r /etc/salt/highstate-complete ]; then
    salt-call state.highstate | tee -a /root/paella-install.log
    touch /etc/salt/highstate-complete
fi
exit 0
"""

with file('/etc/salt/minion', 'w') as mfile:
    mfile.write(minion_config)

with file('/etc/rc.local', 'w') as rfile:
    rfile.write(rc_local)

subprocess.call(['chmod', '755', '/etc/rc.local'])

# We need to get the minion keys from the server.
# In order to get the keys, a POST request must
# be sent to the server with the system-uuid in
# the payload.


# FIXME - fix ip address
url = 'http://${paella_server_ip}/paella/api0/machines'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}    
data = dict(action='stage_over', uuid=uuid)

r = requests.post(url, data=json.dumps(data), headers=headers)

if not r.ok:
    raise RuntimeError, "Something bad happened: %s" % r.status_code



# does everything work?
sys.exit(0)

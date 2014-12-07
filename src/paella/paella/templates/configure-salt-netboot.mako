#!/usr/bin/env python
# WARNING: this is a mako template!  Be careful with symbols.
import os, sys
import subprocess
import json

import requests


machine = '${machine}'
uuid = '${uuid}'
paella_server_ip = '${paella_server_ip}'
template_data = dict(machine=machine, uuid=uuid,
                     paella_server_ip=paella_server_ip)

print "Configure Salt Netboot Started..."

#cmd = ['update-rc.d', '-f', 'salt-minion', 'remove']
#subprocess.check_call(cmd)

# FIXME - fix ip address
minion_config = """\
master: {paella_server_ip}
id: {machine}
grains:
    system-uuid: {uuid}
""".format(**template_data)

rc_local = """\
#!/bin/sh -e

# FIXME
# This should be run as a true initscript
# that can be removed later without disturbing the 
# system.

TIMEOUT=90
COUNT=0
while [ ! -f /etc/salt/pki/minion/minion_master.pub ]; do
    echo "Waiting for salt install."
    if [ "$COUNT" -ge "$TIMEOUT" ]; then
        echo "minion_master.pub not detected by timeout"
        exit 1
    fi
    sleep 5
    COUNT=$((COUNT+5))
done


if ! [ -r /etc/salt/highstate-complete ]; then
    salt-call state.highstate 2>&1 | tee -a /root/paella-install.log
    touch /etc/salt/highstate-complete
fi
exit 0
"""

keydir = '/etc/salt/pki/minion'
if not os.path.isdir(keydir):
    print "Creating %s" % keydir
    os.makedirs(keydir)

private_key = """\
${keydata.private}"""

pem = os.path.join(keydir, 'minion.pem')
print "Creating", pem
with file(pem, 'w') as pfile:
    pfile.write(private_key)
subprocess.check_call(['chmod', '600', pem])
del pem

public_key = """\
${keydata.public}"""

pub = os.path.join(keydir, 'minion.pub')
print "Creating", pub
with file(pub, 'w') as pfile:
    pfile.write(public_key)
del pub


with file('/etc/salt/minion', 'w') as mfile:
    mfile.write(minion_config)

masterkey = """\
${masterkey}"""

#mk_filename = os.path.join(keydir, 'minion_master.pub')
#print "Creating", mk_filename
#with file(mk_filename, 'w') as mfile:
#    mfile.write(masterkey)
#

with file('/etc/rc.local', 'w') as rfile:
    rfile.write(rc_local)

subprocess.call(['chmod', '755', '/etc/rc.local'])

# We need to get the minion keys from the server.
# In order to get the keys, a POST request must
# be sent to the server with the system-uuid in
# the payload.


# FIXME - fix ip address
url = 'http://{paella_server_ip}/paella/api0/machines'.format(**template_data)
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}    
data = dict(action='stage_over', uuid=uuid)

r = requests.post(url, data=json.dumps(data), headers=headers)

if not r.ok:
    raise RuntimeError, "Something bad happened: %s" % r.status_code

#saltcmd = ['salt-call', '-l', 'debug', 'state.highstate']
#with file('/var/log/installer/salt-call-install.log', 'a') as logfile:
#    subprocess.check_call(cmd, stderr=subprocess.STDOUT, stdout=logfile)

# does everything work?
sys.exit(0)

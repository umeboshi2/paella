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
#log_file: udp://paella:514
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


rclocal_systemd_unit_file_content = """\
#  This file is part of systemd.
#
#  systemd is free software; you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 2.1 of the License, or
#  (at your option) any later version.

# This unit gets pulled automatically into multi-user.target by
# systemd-rc-local-generator if /etc/rc.local is executable.
[Unit]
Description=/etc/rc.local Compatibility
ConditionFileIsExecutable=/etc/rc.local
After=network.target

[Service]
Type=forking
ExecStart=/etc/rc.local start
TimeoutSec=0
RemainAfterExit=yes
SysVStartPriority=99
StandardOutput=syslog+console
"""

if os.path.isdir('/etc/systemd'):
    with file('/etc/systemd/system/rc-local.service', 'w') as rfile:
        rfile.write(rclocal_systemd_unit_file_content)

print "="*20 + "Env" + 20*'='
for k,v in os.environ.items():
    print '%s: %s' % (k,v)
    
if 'http_proxy' in os.environ:
    print "Deleting http_proxy: %s" % os.environ['http_proxy']
    del os.environ['http_proxy']
    
# FIXME - fix ip address
url = 'http://{paella_server_ip}/paella/rest/v0/main/machines'.format(**template_data)
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

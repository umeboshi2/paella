import os
import sys
import subprocess
import json
import requests

from paellaclient.config import config

base_url = config.get('main', 'machines_url')

def get_mac_addresses(interface=''):
    process = subprocess.Popen(['/sbin/ifconfig'], stdout=subprocess.PIPE)
    retval = process.wait()
    if retval:
        raise RuntimeError , "ifconfig returned %d" % retval
    if interface:
        raise RuntimeError , "interface keyword is currently ignored"
    macs = []
    for line in process.stdout:
        if line.startswith('eth'):
            # convert to lowercase
            line = line.lower()
            columns = [c.strip() for c in line.split()]
            mac = columns[4].replace(':', '-')
            # ethernet is ARP 1 type
            mac = '01-%s' % mac
            macs.append(mac)
    return macs

# this command uses sudo because
# it needs access to read the smbios
# for the uuid.
def get_system_uuid():
    cmd = ['sudo', 'dmidecode', '-s', 'system-uuid']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    retval = proc.wait()
    if retval:
        raise RuntimeError , "command failed with %d" % retval
    content = proc.stdout.read()
    # enforce lowercase here
    return content.strip().lower()

def make_identity_request(uuid):
    url = os.path.join(base_url, uuid)
    headers = {'Content-type': 'application/json',
               'Accept': 'application/json'}    
    r = requests.get(url, headers=headers)
    if not r.ok:
        raise RuntimeError, "FIXME something bad happened"
    return json.loads(r.content)

def selections_to_dictionary(fileobj, install=False):
    data = dict()
    for line in fileobj:
        line = line.strip()
        package, action = [i.strip() for i in line.split()]
        #print '%s: %s' % (package, action)
        multiarch_stripped = False
        if ':' in package:
            print "multiarch detected: %s" % package
            package = package.split(':')[0]
            multiarch_stripped = True
        if package in data and not multiarch_stripped:
            msg = 'Package %s already present...' % package
            raise RuntimeError, msg
        else:
            if install:
                action = 'install'
            if action != 'install':
                print "WARNING: %s set for action %s" % (package, action)
            data[package] = action
    return data





if __name__ == '__main__':
    uuid = get_system_uuid()
    

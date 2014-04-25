import os
import sys
import subprocess
import StringIO
import json
from optparse import OptionParser

import requests

from paellaclient.base import get_mac_addresses, get_system_uuid
from paellaclient.base import selections_to_dictionary

from paellaclient.config import config

base_url = config.get('main', 'addresses_url')


parser = OptionParser()

opts, args = parser.parse_args(sys.argv[1:])


def get_machine_name():
    addresses = get_mac_addresses()
    uuid = get_system_uuid()
    headers = {'Accept': 'application/json'}
    machine = None
    url = config.get('main', 'machines_url')
    params = dict(uuid=uuid)
    r = requests.get(url, params=params, headers=headers)
    if r.ok:
        data = json.loads(r.content)
        machine = data['name']
    if machine is None:
        for address in addresses:
            url = os.path.join(base_url, address)
            r = requests.get(url, headers=headers)
            if r.ok:
                data = json.loads(r.content)
                machine = data['name']
                break
    if machine is None:
        raise RuntimeError, "No entry found for this machine."
    return machine

def make_install_request(machine):
    data = dict(action='install', machine=machine)
    url = config.get('main', 'machines_url')
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}    
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r

####################################################

def poll_process_for_complete_output(cmd):
    output = StringIO.StringIO()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    while True:
        nextline = proc.stdout.readline()
        if nextline == '' and proc.poll() is not None:
            break
        output.write(nextline)
        output.flush()
    if proc.returncode:
        msg = "There was a problem with command: %s" % cmd
        raise RuntimeError, msg
    output.seek(0)
    return output

def get_dpkg_selections():
    cmd = ['dpkg', '--get-selections']
    outfile = poll_process_for_complete_output(cmd)
    return selections_to_dictionary(outfile, install=True)

def make_update_list_request():
    data = dict(action='update_package_list')
    data['package-list'] = plist
    




def main():
    print "update the package list on the server"
    
if __name__ == '__main__':
    main()
    
        

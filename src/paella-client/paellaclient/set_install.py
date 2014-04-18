import os
import sys
import subprocess
import json
from optparse import OptionParser

import requests

from paellaclient.base import get_mac_addresses, get_system_uuid
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

def main():
    name = get_machine_name()
    r = make_install_request(name)
    if r.ok:
        print "Machine %s set to install." % name
    else:
        raise RuntimeError, "Unable to set %s to install." % name
    
if __name__ == '__main__':
    main()
    
        

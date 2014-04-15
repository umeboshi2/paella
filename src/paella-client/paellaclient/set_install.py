import os
import sys
import subprocess
import json
from optparse import OptionParser

import requests

from paellaclient.base import get_mac_addresses


#FIXME!
base_url = 'http://10.0.4.1/paella/api0/addresses'



parser = OptionParser()

opts, args = parser.parse_args(sys.argv[1:])


def get_machine_name():
    addresses = get_mac_addresses()
    headers = {'Accept': 'application/json'}
    machine = None
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
    #FIXME
    url = 'http://10.0.4.1/paella/api0/machines'
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}    
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r

def main():
    name = get_machine_name()
    r = make_install_request(name)
    print "Machine %s not really set to install yet." % name

if __name__ == '__main__':
    main()
    
        

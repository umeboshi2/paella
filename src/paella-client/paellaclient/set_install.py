import os
import sys
import subprocess
import json
from optparse import OptionParser

import requests

from paellaclient.base import get_mac_addresses


#FIXME!
base_url = 'http://10.0.4.1/paella/api0/addresses'

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

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


def make_data(name):
    addresses = get_mac_addresses()
    data = dict(machine=name, addresses=addresses)
    return json.dumps(data)

def main():
    name = get_machine_name()
    print "Machine %s not really set to install yet." % name

if __name__ == '__main__':
    main()
    
        

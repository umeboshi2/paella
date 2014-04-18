import sys
import subprocess
import json
from optparse import OptionParser

import requests

from paellaclient.base import get_mac_addresses
from paellaclient.base import get_system_uuid

#FIXME!
url = 'http://10.0.4.1/paella/api0/machines'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

parser = OptionParser()

opts, args = parser.parse_args(sys.argv[1:])

if not len(args) or len(args) != 1:
    raise RuntimeError, "Improper arguments.  Just one argument."

name = args[0]


def make_data(name):
    addresses = get_mac_addresses()
    uuid = get_system_uuid()
    data = dict(action='submit', machine=name, uuid=uuid,
                addresses=addresses)
    return data

def sumbit_machine(name):
    data = make_data(name)
    r = requests.post(url, data=json.dumps(data), headers=headers)
    if not r.ok:
        raise RuntimeError, "Server responded with %d" % r.status_code

def main():
    for a in get_mac_addresses():
        print "Address: %s" % a
    print "System UUID:", get_system_uuid()
    sumbit_machine(name)
    print "Machine %s submitted to paella." % name

if __name__ == '__main__':
    main()
    
        

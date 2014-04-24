import sys
import subprocess
import json
from optparse import OptionParser

import requests

from paellaclient.base import get_system_uuid
from paellaclient.config import config

url = config.get('main', 'machines_url')
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

parser = OptionParser()

opts, args = parser.parse_args(sys.argv[1:])

if not len(args) or len(args) != 1:
    raise RuntimeError, "Improper arguments.  Just one argument."

name = args[0]


def make_data(name):
    uuid = get_system_uuid()
    data = dict(action='submit', machine=name, uuid=uuid)
    return data

def sumbit_machine(name):
    data = make_data(name)
    r = requests.post(url, data=json.dumps(data), headers=headers)
    if not r.ok:
        raise RuntimeError, "Server responded with %d" % r.status_code

def main():
    print "System UUID:", get_system_uuid()
    sumbit_machine(name)
    print "Machine %s submitted to paella." % name

if __name__ == '__main__':
    main()
    
        

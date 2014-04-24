import os
import sys
import subprocess
import json
from optparse import OptionParser

import requests

from paellaclient.base import get_system_uuid
from paellaclient.config import config

base_url = config.get('main', 'machines_url')

parser = OptionParser()

opts, args = parser.parse_args(sys.argv[1:])

def make_identity_request(uuid):
    url = os.path.join(base_url, uuid)
    headers = {'Content-type': 'application/json',
               'Accept': 'application/json'}    
    r = requests.get(url, headers=headers)
    if not r.ok:
        raise RuntimeError, "FIXME something bad happened"
    return json.loads(r.content)


def make_install_request(uuid):
    url = base_url
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}    
    data = dict(action='install', uuid=uuid)
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r

def main():
    uuid = get_system_uuid()
    machine = make_identity_request(uuid)
    
    r = make_install_request(uuid)
    if r.ok:
        print "Machine %s set to install." % uuid
    else:
        raise RuntimeError, "Unable to set %s to install." % uuid
    
if __name__ == '__main__':
    main()
    
        

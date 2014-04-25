import os
import sys
import subprocess
import json
from optparse import OptionParser

import requests

from paellaclient.base import get_system_uuid
from paellaclient.base import make_identity_request
from paellaclient.config import config

base_url = config.get('main', 'machines_url')

parser = OptionParser()

parser.add_option('--recipe', type='string', action='store',
                  dest='recipe', default='')
parser.add_option('--name', type='string', action='store',
                  dest='name', default='')
parser.add_option('--autoinstall', action='store_true',
                  dest='autoinstall', default=None)
parser.add_option('--no-autoinstall', action='store_false',
                  dest='autoinstall', default=None)


opts, args = parser.parse_args(sys.argv[1:])


def make_install_request(uuid):
    url = base_url
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}    
    data = dict(action='install', uuid=uuid)
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r

def make_update_request(uuid, name=None, autoinstall=None,
                        recipe=None):
    url = os.path.join(base_url, uuid)
    headers = {'Content-type': 'application/json',
               'Accept': 'application/json'}
    data = dict()
    if name is not None:
        data['name'] = name
    if autoinstall is not None:
        data['autoinstall'] = autoinstall
    if recipe is not None:
        data['recipe'] = recipe
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r

    

def main():
    uuid = get_system_uuid()
    machine = make_identity_request(uuid)
    update = dict().fromkeys(['name', 'autoinstall', 'recipe'])
    
    if opts.autoinstall is not None:
        print "Set autoinstall to", opts.autoinstall
        update['autoinstall'] = opts.autoinstall
    if opts.name:
        print "Set name to", opts.name
        update['name'] = opts.name
    if opts.recipe:
        print "Set recipe to", opts.recipe
        update['recipe'] = opts.recipe
    r = make_update_request(uuid, **update)
    
    
if __name__ == '__main__':
    main()
    
        

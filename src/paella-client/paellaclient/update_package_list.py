import os
import sys
import subprocess
import StringIO
import json
from optparse import OptionParser

import requests

from paellaclient.base import get_system_uuid
from paellaclient.base import make_identity_request
from paellaclient.base import selections_to_dictionary

from paellaclient.config import config

base_url = config.get('main', 'debrepos_url')


parser = OptionParser()

opts, args = parser.parse_args(sys.argv[1:])


def get_machine_name():
    uuid = get_system_uuid()
    data = make_identity_request(uuid)
    return data['name']

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

def make_update_list_request(plist):
    data = dict(action='update_package_list')
    data['package-list'] = plist
    headers = {'Content-type': 'application/json',
               'Accept': 'application/json'}    
    url = base_url
    r = requests.post(url, data=json.dumps(data), headers=headers)
    if not r.ok:
        raise RuntimeError, "Something bad happened, returned %s" % r
    return r.content




def main():
    print "update the package list on the server"
    plist = get_dpkg_selections()
    make_update_list_request(plist)
    
    
if __name__ == '__main__':
    main()
    
        

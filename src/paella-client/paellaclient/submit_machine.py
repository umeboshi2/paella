import sys
import subprocess
import json
from optparse import OptionParser

import requests

#FIXME!
url = 'http://10.0.4.1/paella/api0/machines'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

parser = OptionParser()

opts, args = parser.parse_args(sys.argv[1:])

if not len(args) or len(args) != 1:
    raise RuntimeError, "Improper arguments.  Just one argument."

name = args[0]


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
            columns = [c.strip() for c in line.split()]
            mac = columns[4].replace(':', '')
            macs.append(mac)
    return macs

def make_data(name):
    addresses = get_mac_addresses()
    data = dict(machine=name, addresses=addresses)
    return json.dumps(data)

def sumbit_machine(name):
    data = make_data(name)
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r

def main():
    for a in get_mac_addresses():
        print "Address: %s" % a
    r = sumbit_machine(name)
    return r

if __name__ == '__main__':
    r = main()
    
        

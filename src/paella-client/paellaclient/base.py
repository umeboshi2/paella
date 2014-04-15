import sys
import subprocess
import json

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
            # convert to lowercase
            line = line.lower()
            columns = [c.strip() for c in line.split()]
            mac = columns[4].replace(':', '-')
            # ethernet is ARP 1 type
            mac = '01-%s' % mac
            macs.append(mac)
    return macs


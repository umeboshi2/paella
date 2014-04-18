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

# this command uses sudo because
# it needs access to read the smbios
# for the uuid.
def get_system_uuid():
    cmd = ['sudo', 'dmidecode', '-s', 'system-uuid']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    retval = proc.wait()
    if retval:
        raise RuntimeError , "command failed with %d" % retval
    content = proc.stdout.read()
    return content.strip()


if __name__ == '__main__':
    uuid = get_system_uuid()
    

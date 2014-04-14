import sys
import subprocess

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
            mac = 'hwaddr_%s' % columns[4].replace(':', '_')
            macs.append(mac)
    return macs

def main(*args):
    for a in get_mac_addresses():
        print "Address: %s" % a
    

if __name__ == '__main__':
    main(*sys.argv)
    
        

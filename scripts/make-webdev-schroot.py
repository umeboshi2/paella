import os, sys
import subprocess

def check_requirements():
    here = os.getcwd()
    bootstrap_file = os.path.join(here, 'vagrant/scripts/vagrant-bootstrap.sh')
    binaries = ['/usr/bin/rsync', '/usr/sbin/debootstrap',
                '/usr/bin/schroot']
    for b in binaries:
        if not os.path.isfile(b):
            basename = os.path.basename(b)
            raise RuntimeError, "Please run apt-get instal %s" % basename


def make_root_filesystem(dest, dist='wheezy'):
    cmd = ['debootstrap', dist, dest]
    retval = subprocess.check_call(cmd)
    
def main(dest):
    if os.getuid():
        raise RuntimeError, "This script needs root permissions."
    check_requirements()
    if not os.path.isdir(dest):
        make_root_filesystem(dest)
    if os.path.isdir(os.path.join(dest, 'debootstrap')):
        raise RuntimeError, "Try running debootstrap again"
        
                     
    

            
if __name__ == '__main__':
    dest = sys.argv[1]
    main(dest)
    
    
    
    

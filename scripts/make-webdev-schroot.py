import os, sys
import subprocess

def check_requirements():
    here = os.getcwd()
    bootstrap_file = os.path.join(here, 'vagrant/scripts/vagrant-bootstrap.sh')
    if not os.path.isfile(bootstrap_file):
        msg = "Please run this script from the project directory."
        raise RuntimeError, msg
        
    binaries = ['/usr/bin/rsync', '/usr/sbin/debootstrap',
                '/usr/bin/schroot']
    for b in binaries:
        if not os.path.isfile(b):
            basename = os.path.basename(b)
            raise RuntimeError, "Please run apt-get instal %s" % basename


def make_root_filesystem(dest, dist='wheezy'):
    cmd = ['debootstrap', dist, dest]
    retval = subprocess.check_call(cmd)

def bootstrap_salt(dest):
    here = os.getcwd()
    bootstrap_file = os.path.join(here, 'vagrant/scripts/vagrant-bootstrap.sh')
    cmd = ['schroot', '-c', 'webdev', '-u', 'root', 'bash', bootstrap_file]
    subprocess.check_call(cmd)

def prepare_salt_directories(dest):
    destsrv = os.path.join(dest, 'srv/')
    if not os.path.isdir(destsrv):
        raise RuntimeError, "%s doesn't exist" % destsrv
    here = os.getcwd()
    salt_roots = os.path.join(here, 'vagrant/salt/roots/')
    cmd = ['rsync', '-avHX', salt_roots, destsrv]
    subprocess.check_call(cmd)
    
def install_minion_config(dest):
    here = os.getcwd()
    minion_config = os.path.join(here, 'vagrant/salt/minion')
    destsaltdir = os.path.join(dest, 'etc/salt')
    if not os.path.isdir(destsaltdir):
        os.mkdir(destsaltdir)
    cmd = ['cp', minion_config, destsaltdir]
    subprocess.check_call(cmd)
    
def provision_webdev(dest):
    cmd = ['schroot', '-c', 'webdev', 'salt-call', 'state.highstate']
    subprocess.check_call(cmd)
    
def main(dest):
    if os.getuid():
        raise RuntimeError, "This script needs root permissions."
    check_requirements()
    if not os.path.isdir(dest):
        make_root_filesystem(dest)
    if os.path.isdir(os.path.join(dest, 'debootstrap')):
        raise RuntimeError, "Try running debootstrap again"
    bootstrap_salt(dest)
    prepare_salt_directories(dest)
    install_minion_config(dest)
    provision_webdev(dest)
    
    
                     
    

            
if __name__ == '__main__':
    dest = sys.argv[1]
    main(dest)
    
    
    
    

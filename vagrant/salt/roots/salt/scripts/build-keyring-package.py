import os, sys
import pwd
import hashlib
import subprocess

class BuildException29(Exception):
    pass


def _get_file(filename):
    if filename == '-':
        return sys.stdout
    return file(filename, 'w')

def sign_file(filename, output):
    cmd = ['gpg', '--no-tty', '--output', output, '-a',
           '--detach-sign', filename]
    subprocess.check_call(cmd)
    
def resign_index(checksum):
    with file('index', 'a') as index:
        line = 'sha256-%s  add-paella-insecure\n' % checksum
        index.write(line)
    os.remove('index.gpg')
    sign_file('index', 'index.gpg')
    
def build_package(srctree):
    here = os.getcwd()
    print "HERE", here
    os.chdir(srctree)
    cmd = ['debuild', '--no-tgz-check', '--no-lintian',
           '-us', '-uc']
    proc = subprocess.Popen(cmd, stderr=sys.stdout.fileno(),)
    os.chdir(here)
    proc.wait()
    if proc.returncode:
        if proc.returncode == 29:
            raise BuildException29, "BuildException29 raised"
        raise RuntimeError, "Build process returned %d" % proc.returncode


#gpg --no-tty --output debian-archive-keyring.gpg.asc -a --detach-sign debian-archive-keyring.gpg

def sign_keyring(srctree, keyring):
    keyring_path = os.path.join(srctree, 'keyrings')
    filename = os.path.join(keyring_path, 'debian-archive-keyring.gpg')
    signame = '%s.asc' % filename
    if os.path.isfile(signame):
        print "Removing", signame
        os.remove(signame)
        if os.path.isfile(signame):
            raise RuntimeError, "Removal failed"
    sign_file(filename, signame)
    print "Keyring %s signed." % filename
    
def sign_keyrings(srctree):
    sign_keyring(srctree, 'debian-archive-keyring.gpg')
    sign_keyring(srctree, 'debian-archive-removed.gpg')

    
#builduser = 'vagrant'    
#add_paellla_insecure = '/home/vagrant/add-paella-insecure'
#workspace = '/home/vagrant/workspace'
builduser = 'umeboshi'
add_paellla_insecure = '/tmp/debian/add-paella-insecure'
workspace = '/tmp/debian'
pkg = 'debian-archive-keyring'
version = '2014.1~deb7u1'
dirname = '%s-%s' % (pkg, version)
pkgdir = os.path.join(workspace, dirname)
dist = 'wheezy'

_s = hashlib.sha256()
_s.update(file(add_paellla_insecure).read())
checksum = _s.hexdigest()
del _s

if os.getuid() != pwd.getpwnam(builduser).pw_uid:
    raise RuntimeError, "This script must be run as the vagrant user"

here = os.getcwd()

if not os.path.isdir(workspace):
    print "Creating", workspace
    os.makedirs(workspace)

os.chdir(workspace)

subprocess.check_call(['apt-get', 'source', 'debian-archive-keyring'])

os.chdir(pkgdir)

debtree = os.getcwd()

cmd = ['dch', '-l-paella', '"add paella key"']
subprocess.check_call(cmd)

cmd = ['dch', '-r', dist]
subprocess.check_call(cmd)

for dest in ['active-keys/', 'team-members/']:
    cmd = ['cp', add_paellla_insecure, dest]
    subprocess.check_call(cmd)
    os.chdir(dest)
    resign_index(checksum)
    os.chdir(debtree)

if os.getcwd() != debtree:
    raise RuntimeError, "Not in %s directory." % debtree

os.chdir('removed-keys')
os.remove('index.gpg')
sign_file('index', 'index.gpg')
os.chdir(debtree)

print "Ready to build."
try:
    build_package(debtree)
except BuildException29:
    print "Caught BuildException29"
    sign_keyrings(debtree)
    print "Try to build again"
    build_package(debtree)
    





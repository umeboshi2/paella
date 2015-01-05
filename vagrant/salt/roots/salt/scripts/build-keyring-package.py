#!/usr/bin/env python
import os, sys
import pwd
import hashlib
import subprocess
from optparse import OptionParser

class BuildException29(Exception):
    pass


parser = OptionParser()
parser.add_option('-u', '--user', dest='builduser', default='vagrant')
parser.add_option('-w', '--workspace', dest='workspace',
                  default='')
parser.add_option('-s', '--script', dest='script',
                  default='/home/vagrant/add-paella-insecure')
parser.add_option('-v', '--version', dest='version',
                  default='2014.1~deb7u1')
parser.add_option('-d', '--dist', dest='dist', default='wheezy')
parser.add_option('-p', '--packagename', dest='packagename',
                  default='debian-archive-keyring')
parser.add_option('-m', '--mirror', dest='mirror',
                  default='http://ftp.us.debian.org/debian')

opts, args = parser.parse_args(sys.argv[1:])


def download_keyring_source_package(mirror, packagename, version):
    print "Downloading", packagename, version, "from", mirror
    url = '%s/pool/main/d/%s/%s_%s.dsc'
    url = url % (mirror, packagename, packagename, version)
    cmd = ['dget', '-xu', url]
    subprocess.check_call(cmd)
    
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


builduser = opts.builduser
add_paellla_insecure = opts.script
workspace = opts.workspace
if not workspace:
    workspace = os.getcwd()
pkg = opts.packagename
version = opts.version
dist = opts.dist
mirror = opts.mirror


dirname = '%s-%s' % (pkg, version)
pkgdir = os.path.join(workspace, dirname)




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

#subprocess.check_call(['apt-get', 'source', 'debian-archive-keyring'])
download_keyring_source_package(mirror, pkg, version)

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
    





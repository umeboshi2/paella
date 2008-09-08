import os, sys
import glob
import subprocess
import shutil

SVNURL = "svn://svn.debian.org/d-i/trunk/packages/partman"
SVNREV = 55436
PPC_IGNORE = ['partman-palo', 'partman-prep', 'partman-newworld']
ARM_IGNORE = ['partman-ext2r0']

IGNORE = PPC_IGNORE + ARM_IGNORE


def run(cmd):
    retval = subprocess.call(cmd)
    if retval:
        raise RuntimeError , "%s returned %d" % (' '.join(cmd), retval)
    

def checkout(url=SVNURL, rev=SVNREV):
    cmd = ['svn', 'co', '-r', str(rev), url, 'partman.wc']
    #cmd = ['rsync', '-a', '../partman.wc/', 'partman.wc/']
    run(cmd)

def export(workingcopy='partman.wc', dirname='partman.build'):
    cmd = ['svn', 'export', workingcopy, dirname]
    run(cmd)

def clean():
    cmd = ['rm', '-fr', 'partman', 'partman.build',
           'partman.wc', 'udebs', 'partman-sources']
    run(cmd)
    
def build(dirname='partman.build'):
    here = os.getcwd()
    os.chdir(dirname)
    ls = os.listdir('.')
    parent = os.getcwd()
    udebdir = '../udebs'
    if not os.path.isdir(udebdir):
        os.mkdir(udebdir)
    sources = '../partman-sources'
    if not os.path.isdir(sources):
        os.mkdir(sources)
    for package in ls:
        if package not in IGNORE:
            os.chdir(package)
            #run(['debuild'])
            run(['dpkg-buildpackage', '-rfakeroot', '-D', '-us', '-uc'])
            os.chdir(parent)
    udebs = glob.glob('*.udeb')
    for udeb in udebs:
        shutil.move(udeb, udebdir)
    dscs = glob.glob('*.dsc')
    for dsc in dscs:
        shutil.move(dsc, sources)
    tarballs = glob.glob('*.tar.gz')
    for tarball in tarballs:
        shutil.move(tarball, sources)
    os.chdir(here)

def install():
    udebs = os.listdir('udebs')
    for udeb in udebs:
        filename = os.path.join('udebs', udeb)
        cmd = ['dpkg-deb', '-x', filename, 'partman']
        run(cmd)
        

command = sys.argv[1]
# ugly hack to check for stamp
if os.path.isfile('paella-partman-build-stamp'):
    if command != 'clean':
        print "paella-partman-build-stamp is present, not running", command
        sys.exit(0)
        
if command == 'configure':
    if not os.path.isdir('partman.wc'):
        checkout()
elif command == 'build':
    run(['rm', '-fr', 'partman.build'])
    export()
    build()
elif command == 'install':
    install()
elif command == 'clean':
    clean()
    


#!/usr/bin/env python
import os, sys
import subprocess

from unipath import Path as path
from livebuild import md5sum


# You must be root to run this
# Packages required:  live-helper, paella-installer, syslinux, wget

#d802712c9255f13bea3bea87b83180b1  usr/share/keyrings/debian-archive-keyring.gpg

def unzip_initrd_gz(initrd, dest):
    cmd = ['gzip', '-cd', initrd]
    outfile = file(dest, 'w')
    subprocess.check_call(cmd, stdout=outfile)
    

def extract_initrd(initrd, dirname):
    here = os.getcwd()
    dirname = path(dirname)
    initrd = path(initrd).abspath()
    if dirname.exists():
        raise RuntimeError , "The temp build directory, %s, shouldn't exist." % dirname
    dirname.mkdir()
    os.chdir(dirname)
    cmd = ['cpio', '-id']
    subprocess.check_call(cmd, stdin=file(initrd))
    os.chdir(here)
    

def add_key_to_ring(key, keyring):
    cmd = ['gpg', '--no-default-keyring', '--keyring', keyring,
           '--import']
    subprocess.check_call(cmd, stdin=file(key))
    

def rmdir(dirname):
    return subprocess.check_call(['rm', '-fr', dirname])

    
def main():
    if os.getuid():
        raise RuntimeError , "You need to be root to run this script"

    initrd_gz = '/usr/lib/debian-installer/images/i386/text/initrd.gz'
    unzip_initrd_gz(initrd_gz, 'hi_dude')
    extract_initrd('hi_dude', 'tmp_initrd')
    

if __name__ == "__main__":
    main()

    

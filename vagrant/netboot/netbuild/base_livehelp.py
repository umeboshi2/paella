#!/usr/bin/env python
import os, sys
import subprocess

from unipath import Path as path
from useless.base.util import md5sum

# You must be root to run this
# Packages required:  live-build, paella-installer, syslinux, wget

# All of these functions assume that the current working
# directory is the live build directory.

def rmdir(dirname):
    return subprocess.call(['rm', '-fr', dirname])

def remove_chroot():
    dirname = path('chroot')
    if dirname.isdir():
        print "chroot/ exists......removing"
        rmdir(str(dirname))
    if dirname.exists():
        raise RuntimeError , "chroot/ not removed correctly."
    
def install_chroot(arch, machine):
    remove_chroot()

    msg = "Using paella to install %s for arch %s into chroot/"
    msg = msg % (machine, arch)
    print msg
    raise RuntimeError, "Not using paella to install chroot"
    
def prepare_stagedir():
    stagedir = path('.stage')
    if stagedir.isdir():
        print ".stage/ exists...removing"
        rmdir(str(stagedir))
    stagedir.mkdir()
    bootstrap_stage = stagedir / 'bootstrap'
    # touch empty file
    file(bootstrap_stage, 'w')
    

def call_live_build(logname):
    logfile = file(logname, 'w')
    print "live-build progress being logged in %s" % logname
    subprocess.call(['lb', 'build'], stdout=logfile, stderr=logfile)
    finish_statement = "live-build has finished."
    logfile.write('%s\n' % finish_statement)
    logfile.flush()
    logfile.close()
    

def clean_area():
    retval = subprocess.call(['lb', 'clean'])
    if retval:
        msg = "There was a problem running lb clean."
        raise RuntimeError , msg
    
    

if __name__ == "__main__":
    pass

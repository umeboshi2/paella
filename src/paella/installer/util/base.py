import os
from os.path import join
import tempfile
import commands
from time import sleep

from useless.base import Error
from useless.base.util import makepaths, runlog, echo

from paella import deprecated
from paella.debian.base import RepositorySource

def reverse_ip(ip):
    octets = ip.split('.')
    octets.reverse()
    return '.'.join(octets)

    
def make_fake_start_stop_daemon(target):
    daemon = join(target, 'sbin/start-stop-daemon')
    os.rename(daemon, '%s.REAL' % daemon)
    if os.path.isfile(daemon):
        raise Error, '%s should not exist' % daemon
    fakescript = file(daemon, 'w')
    fakescript.write('#!/bin/sh\n')
    fakescript.write('echo\n')
    fakescript.write('echo "Warning: Fake start-stop-daemon called, doing nothing"\n')
    fakescript.close()
    if os.system('chmod 755 %s' % daemon):
        raise RuntimeError, 'problem changing permissions on %s' % daemon

def remove_fake_start_stop_daemon(target):
    daemon = join(target, 'sbin/start-stop-daemon')
    real = '%s.REAL' % daemon
    if not os.path.isfile(real):
        raise OSError, '%s does not exist' % real
    os.remove(daemon)
    os.rename(real, daemon)
    
def make_script(name, data, target, execpath=False):
    """This function creates a script in the tmp directory
    on the target system.  If execpath is True, the path
    that is returned can be passed to chroot command, else
    the full path to the script is returned.
    """
    exec_path = join('/tmp', name + '-script')
    target_path = join(target, 'tmp', name + '-script')
    sfile = file(target_path, 'w')
    sfile.write(data.read())
    sfile.close()
    os.system('chmod 755 %s' % target_path)
    if not execpath:
        return target_path
    else:
        # for chroot target exec_path
        return exec_path
    

def makedev(target, devices=['generic']):
    here = os.getcwd()
    os.chdir(join(target, 'dev'))
    for dev in devices:
        echo('making device %s with MAKEDEV' % dev)
        runlog('./MAKEDEV %s' % dev)
    os.chdir(here)
    

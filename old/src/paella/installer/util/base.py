import os
import sys
from os.path import join
import tempfile
import commands
from time import sleep

from useless.base import Error
from useless.base.util import makepaths, echo

from paella import deprecated
from paella.debian.base import RepositorySource
from paella.installer.base import runlog

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
        raise RuntimeError , 'problem changing permissions on %s' % daemon

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


def install_packages_command(packages, defenv, action='install',
                             loginfo=None, logerror=None, trait=None, usertag=None):
    unauthenticated = defenv.getboolean('installer', 'allow_unauthenticated_packages')
    if loginfo is None:
        loginfo = sys.stdout.write
    if logerror is None:
        logerror = sys.stderr.write
    apt_cmd = 'apt-get'
    apt_opts = ''
    if defenv.has_option('installer', 'apt_command'):
        apt_cmd = defenv.get('installer', 'apt_command')
    if defenv.has_option('installer', 'apt_command_opts'):
        apt_opts = defenv.get('installer', 'apt_command_opts')
    loginfo('apt command is %s' % apt_cmd)
    opts = apt_opts.split()
    unauthenticated_optdict = {'apt-get' : '--allow-unauthenticated',
                               'aptitude' : '--allow-untrusted'}
    if unauthenticated and unauthenticated_optdict[apt_cmd] not in opts:
        opts.append(unauthenticated_optdict[apt_cmd])
    if '--assume-yes' not in opts:
        opts.append('--assume-yes')
    if apt_cmd == 'aptitude':
        if '--add-user-tag' not in opts:
            if trait is not None and usertag is None:
                usertag = 'paella-trait-%s' % trait
            opts += ['--add-user-tag', usertag]
    full_command = [apt_cmd] + opts + [action] + packages
    shell_cmd = ' '.join(full_command)
    for_phrase = ''
    if trait is not None:
        for_phrase = 'for trait %s ' % trait
    stmt = '%s command %sis:  %s' % (action, for_phrase, shell_cmd)
    loginfo(stmt)
    return full_command
            
    
    

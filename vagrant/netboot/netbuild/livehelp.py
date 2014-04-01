#!/usr/bin/env python
import os, sys
import subprocess

from useless.base.path import path
from useless.base.util import md5sum

from netbuild.cachedir import setup_cachedirs, create_cachedirs_tarball

from netbuild.base_livehelp import install_chroot, prepare_stagedir
from netbuild.base_livehelp import call_live_build, clean_area
from netbuild.base_livehelp import remove_chroot

# You must be root to run this
# Packages required:  live-build, paella-installer, syslinux, wget

#############################
# Variables
#############################

USE_CACHE = False


def setup_config(data):
    filenames = ['binary', 'bootstrap', 'chroot']
    configdir = path('config')
    for config in filenames:
        template_basename = '%s.template' % config
        template_filename = configdir / template_basename
        text = template_filename.text()
        contents = text % data
        configfile = configdir / config
        configfile.write_bytes(contents)

def make_image(arch, machine):
    prepare_stagedir()
    # try to install from cache first
    cachedir = 'chroot.%s' % arch
    cachedir = path(cachedir)
    if cachedir.isdir():
        print "Using cachedir: %s" % cachedir
        remove_chroot()
        subprocess.call(['cp', '-al', 'chroot.%s' % arch,
                         'chroot'])
    else:
        install_chroot(arch, machine)
    # if we didn't install from cache, create it
    if USE_CACHE and not cachedir.isdir():
        print "creating cache directory %s" % cachedir
        subprocess.call(['cp', '-al', 'chroot', 'chroot.%s' % arch])
    logfilename = 'live-build-log.%s' % arch
    call_live_build(logfilename)
        
    
def move_files(target, machine, arch):
    target = path(target)
    if not target.isdir():
        target.mkdir()
    tftpbootdir = target / path('tftpboot/%s' % machine)
    if not tftpbootdir.isdir():
        tftpbootdir.makedirs()
    nfsrootdir = target / path('nfsroot/%s' % machine)
    if not nfsrootdir.isdir():
        nfsrootdir.makedirs()
    os.rename('binary', nfsrootdir / arch)
    os.rename('tftpboot', tftpbootdir / arch)
    packages_filename = '%s.%s.packages' % (machine, arch)
    os.rename('binary.packages',
              nfsrootdir / arch / packages_filename)
    print "Removing chroot/"
    cmd = ['rm', '-fr', 'chroot/']
    retval = subprocess.call(cmd)
    if retval:
        raise RuntimeError , "Problem removing chroot/ directory."

def make_netboot_image(machine, arch, data, target):
    setup_config(data)
    make_image(arch, machine)
    move_files(target, machine, arch)
    clean_area()
    

def create_transportable_archive(filename, target):
    archive = filename
    taropts = 'c'
    if path(archive).isfile():
        print "removing old", archive
        os.remove(archive)
    print "creating new", archive
    here = os.getcwd()
    os.chdir(target)
    cmd = ['tar', taropts, '.']
    tarproc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    zipproc = subprocess.Popen(['pigz'], stdin=tarproc.stdout,
                               stdout=file(archive, 'w'))
    tar_retval = tarproc.wait()
    zip_retval = zipproc.wait()
    if tar_retval:
        raise RuntimeError , "problem tarring up %s" % archive
    if zip_retval:
        raise RuntimeError , "problem zipping up %s" % archive
    os.chdir(here)
    print "All Done!"
    


if __name__ == "__main__":
    #raise RuntimeError , "stop here"
    #main()
    #create_transportable_archive()
    cta = create_transportable_archive
    

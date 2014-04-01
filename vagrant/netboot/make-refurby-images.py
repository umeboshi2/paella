#!/usr/bin/env python
import os, sys
import subprocess

from useless.base.path import path
from useless.base.util import md5sum

from netbuild.clonezilla import CLONEZILLA_URL, download_clonezilla
from netbuild.clonezilla import unzip_clonezilla, move_clonezilla_files
from netbuild.cachedir import setup_cachedirs, create_cachedirs_tarball
from netbuild.tftpboot import make_pxelinux_menu

from netbuild.base_livehelp import install_chroot, prepare_stagedir
from netbuild.base_livehelp import call_live_build, clean_area
from netbuild.base_livehelp import remove_chroot

# You must be root to run this
# Packages required:  live-build, paella-installer, syslinux, wget




def dereference_dictionary(dictionary):
    newdict = dict([(k, dictionary[k] % dictionary) for k in dictionary])
    count = 0
    while newdict != dictionary:
        dictionary = newdict
        newdict = dict([(k, dictionary[k] % dictionary) for k in dictionary])
        if count > 2112:
            raise RuntimeError , "Danger of going into infinite loop!!"
    return newdict
    
def setup_config(arch):
    filenames = ['binary', 'bootstrap', 'chroot']
    configdir = path('config')
    for config in filenames:
        template_basename = '%s.template' % config
        template_filename = configdir / template_basename
        text = template_filename.text()
        data = ARCH_DATA[arch]
        contents = text % data
        configfile = configdir / config
        configfile.write_bytes(contents)

def make_image(arch):
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
        install_chroot(arch, 'refurby_installer')
    # if we didn't install from cache, create it
    if USE_CACHE and not cachedir.isdir():
        print "creating cache directory %s" % cachedir
        subprocess.call(['cp', '-al', 'chroot', 'chroot.%s' % arch])
    logfilename = 'live-build-log.%s' % arch
    call_live_build(logfilename)
        
    
def make_image_orig(arch):
    stagedir = path('.stage')
    if stagedir.isdir():
        print ".stage/ exists...removing"
        rmdir(str(stagedir))
    stagedir.mkdir()
    bootstrap_stage = stagedir / 'bootstrap'
    # touch empty file
    file(bootstrap_stage, 'w')
    cachedir = 'chroot.%s' % arch
    cachedir = path(cachedir)
    if cachedir.isdir():
        print "Using cachedir: %s" % cachedir
        remove_chroot()
        subprocess.call(['cp', '-al', 'chroot.%s' % arch,
                         'chroot'])
    else:
        install_chroot(arch, 'refurby_installer')
    if not cachedir.isdir():
        print "creating cache directory %s" % cachedir
        subprocess.call(['cp', '-al', 'chroot', 'chroot.%s' % arch])
    logfilename = 'live-build-log.%s' % arch
    logfile = file(logfilename, 'w')
    print "live-build progress being logged in %s" % logfilename
    subprocess.call(['lb', 'build'], stdout=logfile)
    finish_statement = "live-build has finished for %s." % arch
    logfile.write('%s\n' % finish_statement)
    logfile.flush()
    logfile.close()
    
    
    

def move_files(arch):
    done = path('done')
    if not done.isdir():
        done.mkdir()
    tftpbootdir = done / 'tftpboot'
    if not tftpbootdir.isdir():
        tftpbootdir.mkdir()
    nfsrootdir = done / 'nfsroot'
    if not nfsrootdir.isdir():
        nfsrootdir.mkdir()
    os.rename('binary', nfsrootdir / arch)
    os.rename('tftpboot', tftpbootdir / arch)
    packages_filename = '%s.packages' % arch
    os.rename('binary.packages', nfsrootdir / arch /packages_filename)
    print "Removing chroot/"
    cmd = ['rm', '-fr', 'chroot/']
    retval = subprocess.call(cmd)
    if retval:
        raise RuntimeError , "Problem removing chroot/ directory."

def make_netboot_image(arch):
    setup_config(arch)
    make_image(arch)
    move_files(arch)
    clean_area()
    

def create_transportable_archive():
    archive = 'refurby-installer-netboot-images.tar'
    taropts = 'cf'
    if template_data['chroot_filesystem'] == 'squashfs':
        archive = 'refurby-installer-netboot-images.tar.gz'
        taropts = 'cfz'
    if path(archive).isfile():
        print "removing old", archive
        os.remove(archive)
    print "creating new", archive
    cmd = ['tar', taropts, archive, 'done']
    retval = subprocess.call(cmd)
    if retval:
        raise RuntimeError , "problem tarring up %s" % archive
    print "All Done!"
    
    
def main():
    if os.getuid():
        raise RuntimeError , "You need to be root to run this script"
    if path('done').isdir():
        msg = "Please remove the done/ directory and try again."
        raise RuntimeError , msg
    download_clonezilla(CLONEZILLA_URL)
    archs = ['i386', 'amd64']
    if USE_CACHE:
        setup_cachedirs(archs)
    for arch in archs:
        make_netboot_image(arch)
        print "Creation of %s done." % arch
    if USE_CACHE:
        create_cachedirs_tarball()
    # now we handle clonezilla
    unzip_clonezilla(CLONEZILLA_URL)
    move_clonezilla_files()
    # now maybe make a menu?
    make_pxelinux_menu(archs)
    if False:
        cmd = ['rm', '-fr']
        for arch in archs:
            cmd += ['chroot.%s' % arch]
        print "Removing chroot.* directories"
        retval = subprocess.call(cmd)
        if retval:
            msg = "There was a problem with removing the chroot.* directories."
            raise RuntimeError , msg

    
#############################
# Variables
#############################

USE_CACHE = False

template_data = dict(arch='amd64',
                     dist='squeeze',
                     mirror='http://refurby/debrepos/debian',
                     mirror_security='http://refurby/debrepos/security',
                     binary_images='net',
                     bootloader='syslinux',
                     net_root_path='/freespace/paella/%(arch)s',
                     net_root_server='10.0.1.1',
                     syslinux_menu_entry='Paella Installer %(arch)s',
                     username='paella',
                     chroot_filesystem='squashfs',
                     linux_flavours=''
                     )

# testing filesystem
# can't use due do low space
#template_data['chroot_filesystem'] = 'plain'


i386_data = dict(template_data.items())
i386_data['arch'] = 'i386'
i386_data = dereference_dictionary(i386_data)
i386_data['linux_flavours'] = '686 486'

amd64_data = dict(template_data.items())
amd64_data['arch'] = 'amd64'
amd64_data = dereference_dictionary(amd64_data)

ARCH_DATA = dict(i386=i386_data, amd64=amd64_data)


if __name__ == "__main__":
    #raise RuntimeError , "stop here"
    #main()
    #create_transportable_archive()
    cta = create_transportable_archive
    

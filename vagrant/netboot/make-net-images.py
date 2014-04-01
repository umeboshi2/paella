#!/usr/bin/env python
import os, sys
import subprocess

from useless.base.path import path
from useless.base.util import md5sum

from netbuild.clonezilla import CLONEZILLA_URL, download_clonezilla
from netbuild.clonezilla import unzip_clonezilla, move_clonezilla_files
from netbuild.cachedir import setup_cachedirs, create_cachedirs_tarball
from netbuild.tftpboot import make_pxelinux_menu
from netbuild.tftpboot import arrange_tftpbootdir


from netbuild.base_livehelp import install_chroot, prepare_stagedir
from netbuild.base_livehelp import call_live_build, clean_area
from netbuild.base_livehelp import remove_chroot

from netbuild import livehelp

from netbuild.TemplateConfig import template_config

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
    data = ARCH_DATA[arch]
    livehelp.setup_config(data)
    

def make_image(arch, machine):
    livehelp.make_image(arch, machine)
        
    
def move_files(arch, machine):
    livehelp.move_files('done', machine, arch)


def make_netboot_image(arch, machine):
    setup_config(arch)
    make_image(arch, machine)
    move_files(arch, machine)
    clean_area()

def prepare():
    if os.getuid():
        raise RuntimeError , "You need to be root to run this script"
    if path('done').isdir():
        msg = "Please remove the done/ directory and try again."
        raise RuntimeError , msg

def create_netboot_images(machine):
    archs = template_config.get(machine, 'architectures')
    archs = [a.strip() for a in archs.split()]
    for arch in archs:
        template_config.set(machine, 'current_arch', arch)
        template_config.set(machine, 'arch', arch)
        data = dict(template_config.items(machine))
        flavor_key = 'linux_flavours_%s' % arch
        data['linux_flavours'] = ''
        if template_config.has_option(machine, flavor_key):
            data['linux_flavours'] = template_config.get(machine, flavor_key)
            
        livehelp.setup_config(data)
        paella_machine = data['machine']
        livehelp.make_image(arch, paella_machine)
        livehelp.move_files('done', machine, arch)
        clean_area()
        print "Creation of %s(%s) done." % (machine, arch)        

        
def main():
    prepare()
    tftpbootdir = path('done/tftpboot')
    machines = template_config.sections()
    for machine in machines:
        print "Creating images for machine: %s" % machine
        create_netboot_images(machine)
        


    # now we handle clonezilla
    download_clonezilla(CLONEZILLA_URL)
    unzip_clonezilla(CLONEZILLA_URL)
    move_clonezilla_files()
    # now maybe make a menu?
    #make_pxelinux_menu(archs)
    arrange_tftpbootdir(tftpbootdir, template_config)
    
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
    archive = 'refurby-installer-netboot-images.tar.gz'
    cta = livehelp.create_transportable_archive
    

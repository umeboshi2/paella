#!/usr/bin/env python
import os, sys
import subprocess

from useless.base.path import path
from useless.base.util import md5sum

from livebuild.TemplateConfig import template_config

from livebuild import livehelp

# You must be root to run this
# Packages required:  live-build, paella-installer, syslinux, wget


def prepare():
    if os.getuid():
        raise RuntimeError , "You need to be root to run this script"
    if path('done').isdir():
        msg = "Please remove the done/ directory and try again."
        raise RuntimeError , msg

def create_netboot_image(machine, arch):
    for option in ['current_arch', 'arch']:
        template_config.set(machine, option, arch)
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

def create_netboot_images(machine):
    archs = template_config.get_archs(machine)
    for arch in archs:
        create_netboot_image(machine, arch)



def main():
    prepare()
    tftpbootdir = path('done/tftpboot')
    machines = template_config.sections()
    for machine in machines:
        print "Creating images for machine: %s" % machine
        create_netboot_images(machine)
        


if __name__ == "__main__":
    #raise RuntimeError , "stop here"
    #main()
    #create_transportable_archive()
    archive = 'refurby-installer-netboot-images.tar.gz'
    cta = livehelp.create_transportable_archive
    prepare()
    

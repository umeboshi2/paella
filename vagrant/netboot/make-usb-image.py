#!/usr/bin/env python
import os, sys
import subprocess

from livebuild.path import path
from livebuild import md5sum

from livebuild.TemplateConfig import template_config

from livebuild.usb.loop import attach_loop, enable_loop_module

from livebuild.usb import paella, clonezilla
from livebuild.usb import caine
from livebuild.usb import syslinux



def make_disk_image(filename, size=100, sparse=False, bs='1M'):
    cmd = ['dd', 'if=/dev/zero', 'of=%s' % filename,
           'bs=%s' % bs]
    if sparse:
        cmd += ['seek=%d' % size, 'count=0']
    else:
        cmd += ['count=%d' % size]
    subprocess.check_call(cmd)
    # do we need to do this here?
    enable_loop_module()
    attach_loop('/dev/loop0', filename)
    
    

def install_syslinux_to_usb_device(device='/dev/sdc'):
    raise RuntimeError , "Not ready yet."
    # pretend this is a blank device and partition it
    # os.system('parted make my device')
    partition = '%s1' % device
    # install syslinux to partition
    cmd = ['syslinux', '-i', partition]
    subprocess.check_call(cmd)
    # install mbr to device
    mbr = '/usr/lib/syslinux/mbr.bin'
    if not os.path.isfile(mbr):
        raise RuntimeError , "%s is supposed to exist." % mbr
    cmd = ['dd', 'conv=notrunc', 'bs=440', 'count=1',
           'if=%s' % mbr, 'of=%s' % device]
    subprocess.check_call(cmd)
    # set first partition as bootable
    cmd = ['parted', device, 'set', '1', 'boot', 'on']
    subprocess.check_call(cmd)
    


def stage_machines():
    paella.install_all_machines(template_config)
    clonezilla.install_machine()
    caine.install_machine()
    

def make_menu():
    main_menu = syslinux.make_main_menu(template_config)
    main_menu += clonezilla.create_menu_entry(office=True)
    main_menu += clonezilla.create_menu_entry(office=False)
    main_menu += caine.create_menu_entry()
    return main_menu


def main():
    stage_machines()
    menu = make_menu()
    syslinux.install_syslinux_files(menu)
    
if __name__ == "__main__":
    m = 'snoopy'
    arch = 'i386'
    f = paella.menu_filename(m, arch)

    a = arch
    fm = paella.fix_menu
    

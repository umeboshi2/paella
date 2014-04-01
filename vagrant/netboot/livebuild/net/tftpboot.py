import os, sys
import subprocess

from useless.base.path import path


syslinux_libdir = path('/usr/lib/syslinux')


vesamenu_filename = syslinux_libdir / 'vesamenu.c32'
pxelinux_boot_filename = syslinux_libdir / 'pxelinux.0'


default_menu_contents = '''default vesamenu.c32
prompt 0
label i386
\tMENU LABEL Paella Installer (i386)
include debian-live/i386/boot-screens/menu.cfg
label amd64
\tMENU LABEL Paella Installer (amd64)
include debian-live/amd64/boot-screens/menu.cfg
label Clonezilla live
\tMENU LABEL Clonezilla live (Default settings, VGA 800x600)
\tkernel clonezilla/vmlinuz1
\tappend initrd=clonezilla/initrd1.img boot=live config noswap nolocales edd=on nomodeset nopromp ocs_live_run="ocs-live-general" ocs_live_extra_param="" ocs_live_keymap="NONE" ocs_live_batch="no" ocs_lang="" ocs_prerun="mount 10.0.1.1:/media/bigdisk/share/erasable/images /home/partimag" vga=788 xnosplash netboot=nfs nfsroot=10.0.1.1:/freespace/paella/clonezilla
'''

def copyfile(src, dest):
    cmd = ['cp', '-a', src, dest]
    return subprocess.call(cmd)

    
def copy_from_syslinux_libdir(filename, tftpbootdir):
    src = syslinux_libdir / filename
    dest = tftpbootdir / filename
    retval = copyfile(str(src), str(dest))
    if retval:
        msg = "There was a problem copying %s, cp returned %d"
        msg = msg % (filename, retval)
        raise RuntimeError , msg    

def make_relative_prefix(machine, arch):
    return path(machine) / arch

# tftpbootdir should be path object
def make_prefix(tftpbootdir, machine, arch):
    return tftpbootdir / machine / arch

def base_pxelinux_menu_filename(arch):
    return path('debian-live/%s/boot-screens/live.cfg' % arch)

def base_splash_filename(arch):
    return path('debian-live/%s/boot-screens/splash.png' % arch)
    
def relative_pxelinux_menu_filename(machine, arch):
    base = base_pxelinux_menu_filename(arch)
    return make_relative_prefix(machine, arch) / base


def pxelinux_menu_filename(tftpbootdir, machine, arch):
    rel = relative_pxelinux_menu_filename(machine, arch)
    return tftpbootdir / rel

def splash_filename(tftpbootdir, machine, arch):
    base = base_splash_filename(arch)
    prefix = make_relative_prefix(machine, arch)
    return tftpbootdir / prefix / base

def main_splash_filename(tftpbootdir):
    return tftpbootdir / 'splash.png'

def check_splash(tftpbootdir, machine, arch):
    main = main_splash_filename(tftpbootdir)
    if not main.isfile():
        splash = splash_filename(tftpbootdir, machine, arch)
        print "Using %s as splash screen" % splash
        content = splash.bytes()
        main.write_bytes(content)
        
def fix_menu_line(line, machine, arch):
    marker = 'debian-live/%s/' % arch
    corrected = '%s/%s/%s' % (machine, arch, marker)
    return line.replace(marker, corrected)

def fix_menu_file(tftpbootdir, machine, arch):
    marker = 'debian-live/%s/' % arch
    filename = pxelinux_menu_filename(tftpbootdir, machine, arch)
    menu_lines = filename.lines()
    bkup = path('%s.orig' % filename)
    if not bkup.isfile():
        filename.rename(bkup)
    new_lines = []
    for line in menu_lines:
        if marker in line:
            line = fix_menu_line(line, machine, arch)
        new_lines.append(line)
    filename.write_lines(new_lines)

def menu_header_lines():
    lines = [
        'default vesamenu.c32',
        'prompt 0',
        '',
        'menu background splash.png',
        'menu vshift 13',
        '',
        '',
        ]
    return lines

    
def create_menu_entry(machine, arch, entry):
    filename = str(relative_pxelinux_menu_filename(machine, arch))
    lbl_line = 'label %s-%s' % (machine, arch)
    line = 'include %s %s' % (filename, entry)
    return [lbl_line, line]


def fix_menu_files(tftpbootdir, template_config):
    machines = template_config.sections()
    main_menu = menu_header_lines()
    for machine in machines:
        archs = template_config.get(machine, 'architectures')
        archs = [a.strip() for a in archs.split()]
        for arch in archs:
            check_splash(tftpbootdir, machine, arch)
            fix_menu_file(tftpbootdir, machine, arch)
            template_config.set(machine, 'current_arch', arch)
            entry = template_config.get(machine, 'syslinux_menu_entry')
            main_menu += create_menu_entry(machine, arch, entry)
    return main_menu

def arrange_tftpbootdir(tftpbootdir, template_config):
    # fix menu files and make main menu
    main_menu = fix_menu_files(tftpbootdir, template_config)
    # copy files from syslinux
    for filename in ['vesamenu.c32', 'pxelinux.0']:
        copy_from_syslinux_libdir(filename, tftpbootdir)
    # create config directory
    pxecfgdir = tftpbootdir / 'pxelinux.cfg'
    if not pxecfgdir.isdir():
        pxecfgdir.mkdir()
    # here is where I should add to main_menu
    
    # make default menu file
    default_menu = pxecfgdir / 'default'
    default_menu.write_lines(main_menu)
    

def make_pxelinux_menu(archs, tftpbootdir):
    if not tftpbootdir.isdir():
        msg = "The tftpboot directory at %s needs to exist before doing this."
        raise RuntimeError , msg
    # move some files around in tftpbootdir
    deblive_dir = tftpbootdir / 'debian-live'
    if not deblive_dir.isdir():
        deblive_dir.mkdir()
    for arch in archs:
        topdir = tftpbootdir / arch / 'debian-live'
        archdir = topdir / arch
        if archdir.isdir():
            new_archdir = deblive_dir / arch
            os.rename(str(archdir), str(new_archdir))
            topdir.rmdir()
    # TODO - save space by removing extra copies of pxelinux.0
    # and other files
    print "Read the TODO in the comments...."
    # copy vesamenu.c32 to tftpboot
    for filename in ['vesamenu.c32', 'pxelinux.0']:
        copy_from_syslinux_libdir(filename, tftpbootdir)
    pxecfgdir = tftpbootdir / 'pxelinux.cfg'
    if not pxecfgdir.isdir():
        pxecfgdir.mkdir()
    default_menu = pxecfgdir / 'default'
    default_menu.write_bytes(default_menu_contents)
    
if __name__ == "__main__":
    archs = ['amd64', 'i386']
    make_pxelinux_menu(archs)
    

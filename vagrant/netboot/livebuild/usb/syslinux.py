import os, sys
import subprocess

from useless.base.path import path

from netbuild.usb.base import USB_PARENT
from netbuild.usb.base import copyfile

syslinux_libdir = path('/usr/lib/syslinux')


vesamenu_filename = syslinux_libdir / 'vesamenu.c32'

# convert -resize 640x480 -depth 16 -colors 14 yourfile.bmp splash.png

def copy_from_syslinux_libdir(filename, destdir):
    src = syslinux_libdir / filename
    dest = destdir / filename
    retval = copyfile(str(src), str(dest))
    if retval:
        msg = "There was a problem copying %s, cp returned %d"
        msg = msg % (filename, retval)
        raise RuntimeError , msg    


def fix_menu_line(line, machine, arch):
    marker = 'debian-live/%s/' % arch
    corrected = '%s/%s/%s' % (machine, arch, marker)
    return line.replace(marker, corrected)

def fix_menu_file(bootdir, machine, arch):
    marker = 'debian-live/%s/' % arch
    filename = pxelinux_menu_filename(bootdir, machine, arch)
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

def menu_color_lines():
    lines = [
        'menu color unsel 37;44 #ffcccc55 #cc222200 std',
        'menu color tabmsg 37;44 #ffcccc55 #cc222200 std',
        'menu color sel 7;37;40 #ffcccc55 #ff555555 all',
        'menu color cmdline 37;44 #ffcccc55 #cc222200 std',
        'menu color unsel 37;44 #ffcccc55 #cc222200 std',
        'menu color title 1;36;44 #ffcccc55 #cc220000 std',
        'menu color border 0 #00ffffff #00000000 std'
        ]
    return lines

def menu_title(title):
    return 'menu title %s' % title

    
    
def create_menu_entry(machine, arch, entry):
    filename = str(relative_pxelinux_menu_filename(machine, arch))
    lbl_line = 'label %s-%s' % (machine, arch)
    line = 'include %s %s' % (filename, entry)
    return [line]

def make_main_menu(config):
    machines = config.sections()
    main_menu = menu_header_lines()
    main_menu += menu_color_lines()
    main_menu.append(menu_title('PenUltimateMultiBootDrive'))
    for machine in machines:
        for arch in config.get_archs(machine):
            config.set(machine, 'current_arch', arch)
            entry = config.get(machine, 'syslinux_menu_entry')
            main_menu += create_menu_entry(machine, arch, entry)
    return main_menu


def install_syslinux_files(menu):
    for filename in ['vesamenu.c32']:
        copy_from_syslinux_libdir(filename, path(USB_PARENT))
    # THIS IS VERY UGLY, FIXME
    splash_src = path(USB_PARENT) / splash_filename(path(''), 'installer', 'i386')
    basename = splash_src.basename()
    splash_dest = path(USB_PARENT) / basename
    if not splash_dest.isfile():
        subprocess.check_call(['cp', splash_src, splash_dest])
    maincfg = path(USB_PARENT) / 'syslinux.cfg'
    maincfg.write_lines(menu)
    
#######################################

def make_relative_prefix(machine, arch):
    return path('boot/%s' % machine) / arch

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


if __name__ == "__main__":
    from netbuild.TemplateConfig import template_config
    cfg = template_config
    

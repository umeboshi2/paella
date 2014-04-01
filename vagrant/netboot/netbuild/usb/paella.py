import subprocess

from useless.base.path import path

from netbuild.tftpboot import base_pxelinux_menu_filename 

from netbuild.usb.base import ORIG_BOOT_DIR, ORIG_ROOT_DIR
from netbuild.usb.base import USB_BOOT_DIR, USB_ROOT_DIR
from netbuild.usb.base import rmdir, make_prefix

##############
#### MENU ####
##############

def check_menu_line(line):
    # strip whitespace (esp. preceding tab)
    line = line.strip()
    if line.startswith('kernel'):
        return 'kernel'
    elif line.startswith('append initrd='):
        return 'initrd'
    elif line.startswith('append'):
        return 'append'
    else:
        return ''


def fix_kernel_line(line, machine, arch):
    # we make sure that we put a ' ' (space)
    # in the split arg to preserve the
    # preceding and trailing whitespace in the line
    parts = line.split(' ')
    if len(parts) != 2:
        raise RuntimeError , 'bad kernel line: %s' % line
    newline = '%s boot/%s' % tuple(parts)
    #print 'newline', [newline]
    return newline

def manage_initrd_options(options, machine, arch):
    new_options = []
    for option in options:
        if option.startswith('initrd='):
            initrd = option.split('initrd=')[1]
            initrd = 'boot/%s' % initrd
            option = 'initrd=%s' % initrd
        elif option == 'netboot=nfs':
            option = ''
        elif option.startswith('nfsroot='):
            rpath = '/roots/%s/%s/live' % (machine, arch)
            option = 'live-media-path=%s' % rpath
        new_options.append(option)
    return new_options

            
def fix_initrd_line(line, machine, arch):
    # we make sure that we put a ' ' (space)
    # in the split arg to preserve the
    # preceding and trailing whitespace in the line
    parts = line.split(' ')
    options = parts[1:]
    newopts = manage_initrd_options(options, machine, arch)
    allopts = parts[:1] + newopts
    line = ' '.join(allopts)
    return line


def menu_filename(machine, arch):
    prefix = make_prefix(path(USB_BOOT_DIR), machine, arch)
    base = base_pxelinux_menu_filename(arch)
    return prefix / base


def fix_menu(machine, arch):
    filename = menu_filename(machine, arch)
    if not filename.isfile():
        raise RuntimeError, '%s not found.' % filename
    newlines = []
    for line in filename.open():
        checked = check_menu_line(line)
        if checked:
            if checked == 'kernel':
                line = fix_kernel_line(line, machine, arch)
            elif checked == 'initrd':
                #print "initrd-> do nothing"
                line = fix_initrd_line(line, machine, arch)
            elif checked == 'append':
                print "WARNING: found append without initrd="
            else:
                msg = "unhandled check criteria: %s" % checked
                raise RuntimeError , msg
        else:
            # line is unchanged
            pass
        newlines.append(line)
    #return newlines
    filename.write_lines(newlines)
    
###############
### BOOTDIR ###
###############

def orig_bootdir(machine, arch):
    return path(ORIG_BOOT_DIR) / machine / arch
    
def usb_bootdir(machine, arch):
    return path(USB_BOOT_DIR) / machine / arch

def orig_rootdir(machine, arch):
    return path(ORIG_ROOT_DIR) / machine / arch

def usb_rootdir(machine, arch):
    return path(USB_ROOT_DIR) / machine / arch

def copy_bootdir(machine, arch):
    src = '%s/' % orig_bootdir(machine, arch)
    dest = '%s/' % usb_bootdir(machine, arch)
    d = path(dest)
    if not d.dirname().isdir():
        d.dirname().makedirs()
    cmd = ['rsync', '-aHX', src, dest]
    subprocess.check_call(cmd)

def remove_bootdir(machine, arch):
    bootdir = '%s/' % usb_bootdir(machine, arch)
    rmdir(bootdir)

def install_bootdir(machine, arch, remove=False):
    if remove:
        remove_bootdir(machine, arch)
    copy_bootdir(machine, arch)
    fix_menu(machine, arch)
    

def install_all_bootdirs(config, remove=False):
    for machine in config.sections():
        for arch in config.get_archs(machine):
            install_bootdir(machine, arch, remove=remove)


def install_rootfs(machine, arch, remove=False):
    src = orig_rootdir(machine, arch)
    dest = usb_rootdir(machine, arch)
    if remove:
        rmdir(str(dest))
    if not dest.isdir():
        dest.makedirs()
    cmd = ['cp', '-al', str(src), str(dest.dirname())]
    subprocess.check_call(cmd)
    
def install_machine(machine, arch, remove=False):
    install_bootdir(machine, arch, remove=remove)
    install_rootfs(machine, arch, remove=remove)
    
def install_all_machines(config, remove=False):
    for machine in config.sections():
        for arch in config.get_archs(machine):
            install_machine(machine, arch, remove=remove)
            
    
if __name__ == '__main__':
    pass

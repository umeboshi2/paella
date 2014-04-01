import subprocess

from unipath import Path as path

from livebuild.tftpboot import base_pxelinux_menu_filename 

ORIG_BOOT_DIR = 'done/tftpboot'
ORIG_ROOT_DIR = 'done/nfsroot'

USB_PARENT = 'done/usb'
USB_BOOT_DIR = '%s/boot' % USB_PARENT
USB_ROOT_DIR = '%s/roots' % USB_PARENT



def make_prefix(parent, machine, arch):
    return parent / machine / arch

def rmdir(directory):
    cmd = ['rm', '-fr', directory]
    subprocess.check_call(cmd)    

def copyfile(src, dest):
    cmd = ['cp', '-a', src, dest]
    return subprocess.call(cmd)

def copy_all_boot_files():
    src = ORIG_BOOT_DIR + '/'
    dest = USB_BOOT_DIR + '/'
    d = path(dest)
    if not d.isdir():
        d.makedirs()
    cmd = ['rsync', '-aHX', src, dest]
    subprocess.check_call(cmd)


def remove_all_boot_files():
    directory = USB_BOOT_DIR + '/'
    rmdir(directory)    


def hardlink_dirs(src, dest, remove=False):
    if remove:
        rmdir(str(dest))
    if not dest.isdir():
        dest.makedirs()
    cmd = ['cp', '-al', str(src), str(dest.dirname())]
    subprocess.check_call(cmd)

            
    
if __name__ == '__main__':
    pass

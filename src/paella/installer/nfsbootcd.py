import os, sys
from os.path import isfile, isdir, join

from paella.base.util import makepaths

from paella.debian.dpkgdeb import DpkgDeb
from paella.profile.base import PaellaConfig

def unpack_kernel(kernel, target):
    isolinux_dir = join(target, 'isolinux')
    dp = DpkgDeb()
    tmp = join(target, 'tmp')
    if isdir(tmp):
        os.system('rm %s -fr' % tmp)
    makepaths(tmp)
    os.system('dpkg-deb -x %s %s' % (kernel, tmp))
    os.system('cp %s/boot/vmlinuz-* %s/vmlinuz' % (tmp, isolinux_dir))
    os.system('rm %s -fr' % tmp)
    
    

def setup_directory(target):
    isolinux_dir = join(target, 'isolinux')
    if not isdir(isolinux_dir):
        makepaths(isolinux_dir)
    if not isfile(join(isolinux_dir, 'isolinux.bin')):
        os.system('cp /usr/lib/syslinux/isolinux.bin %s' % isolinux_dir)

def isolinuxcfg(target):
    isolinux_dir = join(target, 'isolinux')
    lines = ['DEFAULT paella-install',
             'APPEND ip=dhcp root=/dev/nfs netdev=probe devfs=nomount',
             'LABEL paella-install',
             'KERNEL vmlinuz']
    filedata = '\n'.join(lines) + '\n'
    cfpath = join(isolinux_dir, 'isolinux.cfg')
    cffile = file(cfpath, 'w')
    cffile.write(filedata)
    cffile.close()


def make_image(target='/tmp/isotarget', kernel='kernel-image-2.6.2installer'):
    cfg = PaellaConfig()
    kpath = '/mirrors/debian/local/questron'
    setup_directory(target)
    isolinuxcfg(target)
    unpack_kernel(kernel, target)
    os.system('mkisofs -V "paella-nfsboot" -r -pad -b isolinux/isolinux.bin -no-emul-boot -boot-load-size 4 -boot-info-table -o nfsboot.iso %s' % target)
    os.system('rm %s -fr' % target)
    
if __name__ == '__main__':
    cfg = PaellaConfig()
    kernel = sys.argv[1]
    make_image(kernel=kernel)

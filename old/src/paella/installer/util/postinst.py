import os
import subprocess

from useless.base.path import path
from paella.installer.base import runlog

def loginfo(msg):
    print msg

logerror = loginfo
    

def install_kernel(package, target):
    script = "#!/bin/bash\n"
    script += 'set -e\n'
    t = path(target)
    fake = t / 'boot/vmlinuz-fake'
    if not fake.isfile():
        script += 'touch /boot/vmlinuz-fake\n'
    script += 'ln -s boot/vmlinuz-fake vmlinuz\n'
    script += 'apt-get -y install %s\n' % package
    script += 'echo "kernel %s installed"\n' % package
    script += '\n'
    sname = 'install_kernel.sh'
    full_path = os.path.join(target, sname)
    sfile = file(full_path, 'w')
    sfile.write(script)
    sfile.close()
    runlog('chmod a+x %s' % full_path)
    runlog('chroot %s ./%s' % (target, sname))
    os.remove(full_path)


def install_kernel_package(package, toolkit=None, target=None, loginfo=loginfo,
                           logerror=logerror):
    if toolkit is not None:
        target = toolkit.target
    if target is None:
        raise RuntimeError , "No target specified."
    target = path(target)
    chroot_precommand = ['chroot', str(target)]
    aptinstall = ['aptitude', '--assume-yes', 'install']
    cmd = chroot_precommand + aptinstall + [package]
    loginfo('install command is: %s' % ' '.join(cmd))
    kimgconf = target / 'etc' / 'kernel-img.conf'
    kimgconf_old = path('%s.paella-orig' % kimgconf)
    kimgconflines = ['do_bootloader = No',
                     'do_initrd = Yes',
                     'warn_initrd = No'
                     ]
    if kimgconf.exists():
        loginfo('/etc/kernel-img.conf already exists')
        k = '/etc/kernel-img.conf'
        msg ='renaming %s to %s.paella-orig' % (k, k)
        loginfo(msg)
        if kimgconf_old.exists():
            msg = '%s already exists, aborting install.' % kimgconf_old
            logerror(msg)
            raise RuntimeError , msg
        os.rename(kimgconf, kimgconf_old)
    kimgconf.write_lines(kimgconflines)
    subprocess.check_call(cmd)
    loginfo('Kernel installation is complete.')
    if kimgconf_old.exists():
        loginfo('Restoring /etc/kernel-img.conf')
        os.remove(kimgconf)
        os.rename(kimgconf_old, kimgconf)

    
        

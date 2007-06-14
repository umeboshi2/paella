import os

from useless.base.path import path
from paella.installer.base import runlog

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



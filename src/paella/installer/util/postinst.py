import os

from useless.base.util import runlog

def install_kernel(package, target):
    script = "#!/bin/bash\n"
    script += '#umount /proc\n'
    script += '#umount /proc\n'
    script += '#mount -t proc proc /proc\n'
    script += 'touch /boot/vmlinuz-fake\n'
    script += 'ln -s boot/vmlinuz-fake vmlinuz\n'
    script += 'apt-get -y install %s\n' % package
    script += 'echo "kernel %s installed"\n' % package
    script += '#umount /proc\n'
    script += '\n'
    sname = 'install_kernel.sh'
    full_path = os.path.join(target, sname)
    sfile = file(full_path, 'w')
    sfile.write(script)
    sfile.close()
    runlog('chmod a+x %s' % full_path)
    runlog('chroot %s ./%s' % (target, sname))
    os.remove(full_path)



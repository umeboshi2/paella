import os
from os.path import join
import tempfile
import commands
from time import sleep
import subprocess

from useless.base import Error
from useless.base.util import makepaths, echo

from paella import deprecated
from paella.debian.base import RepositorySource
from paella.installer.base import runlog


def make_interfaces_simple(target):
    i = file(os.path.join(target, 'etc/network/interfaces'), 'w')
    i.write('auto lo eth0\n')
    i.write('iface lo inet loopback\n')
    i.write('iface eth0 inet dhcp\n')
    i.write('\n\n')
    i.close()

def backup_target_command(target, tarball):
    exclude = "--exclude './proc/*'"
    location = '-C %s' % target
    fileopt = '--file %s' % tarball
    cmd = 'tar --create %s %s . %s' % (exclude, location, fileopt)
    return cmd
    
def remove_debs(target):
    archives = 'var/cache/apt/archives'
    debs = os.path.join(target, archives, '*.deb')
    pdebs = os.path.join(target, archives, 'partial', '*.deb')
    return runlog('rm %s %s -f' % (debs, pdebs))
    
def extract_tarball(target, tarball):
    opts = '-xf'
    if tarball[-7:] == '.tar.gz' or tarball[-4:] == '.tgz':
        opts = '-xzf'
    elif tarball[-8:] == '.tar.bz2':
        opts = '-xjf'
    cmd = 'tar -C %s %s %s' % (target, opts, tarball)
    echo('extracting tarball with command %s' % cmd)
    return runlog(cmd)

#password is 'a'
myline = 'root:$1$IImobcMx$4Lsn4oHhM7L9pNYZNP7zz/:0:0:root:/root:/bin/bash'

def set_root_passwd(target, rootline):
    p = file(os.path.join(target, 'etc/passwd'))
    lines = [rootline + '\n']
    for line in p:
        if line[:6] != 'root::':
            lines.append(line)
    p.close()
    p = file(os.path.join(target, 'etc/passwd'), 'w')
    p.writelines(lines)
    p.close()

def secure_target(target, admin, keys, homepath):
    while homepath[0] == '/':
        homepath = homepath[1:]
    os.system('chroot %s rm /etc/ssh/ssh_host_*' % target)
    os.system('chroot %s dpkg-reconfigure -plow ssh' % target)
    os.system('chroot %s shadowconfig on' % target)
    admin_home = os.path.join(target, homepath, admin)
    sshdir = os.path.join(admin_home, '.ssh')
    if not os.path.isdir(sshdir):
        makepaths(sshdir)
    authorized = os.path.join(sshdir, 'authorized_keys')
    authorizedfile = file(authorized, 'w')
    authorizedfile.write(keys + '\n')
    authorizedfile.close()
    chroot_home = os.path.join('/', homepath, admin)
    os.system('chroot %s chown -R %s:staff %s' % (target, admin, chroot_home))
    os.system('chmod 0600 %s' % authorized)
    os.system('chmod 0750 %s' % sshdir)

def add_hosts_to_nameserver(target, domain, hostdata):
    ldhosts = file(os.path.join(target, 'var/cache/bind/localdomain.hosts'), 'a+')
    ldrev = file(os.path.join(target, 'var/cache/bind/localdomain.rev'), 'a+')
    for ip, hostname in hostdata.items():
        hline = '%s.%s.\tIN\tA\t%s\n' % (hostname, domain, ip)
        ldhosts.write(hline)
        rev = reverse_ip(ip)
        rline = '%s.in-addr.arpa.\tIN\tPTR %s.%s.\n' % (rev, hostname, domain)
        ldrev.write(rline)
    ldhosts.write('\n')
    ldrev.write('\n')
    ldhosts.close()
    ldrev.close()

def pxe_base_data(label, kernel=None, initrd=None):
    lines = ['# default paella boot server config',
             'default %s' % label,
             'prompt 1',
             'say "--------------------------"',
             'say "Paella Network Boot Server"',
             'say "--------------------------"',
             'say "mem for memtest(not here)"',
             'say "enter for paella installer"',
             'say "autoboot in 10 seconds"',
             'DISPLAY boot.msg',
             'f1 boot.msg',
             'f2 say "help me"',
             '#timeout 100',
             'timeout 10'
             ]
    lines.append('label %s' % label)
    if kernel is None:
        kernel = 'vmlinuz-%s' % label
    if initrd is None:
        initrd = 'initrd.img-%s' % label
    lines.append('kernel %s' % kernel)
    argline = 'append initrd=%s netdev=probe ip=dhcp ' % initrd
    argline += 'devfs=nomount root=/dev/nfs'
    lines.append(argline)
    return '\n'.join(lines) + '\n'


def install_iso_contents(iso, install_path, removeiso=True,
                         mtpt='/tmp/isomount'):
    map(makepaths, [install_path, mtpt])
    mntcmd = ['mount', '-t', 'iso9660', '-o', 'loop', iso, mtpt]
    retval = subprocess.call(mntcmd)
    files = '%s/*' mtpt
    cpcmd = ['cp', '-a', files, install_path]
    subprocess.call(cpcmd)
    subprocess.call(['umount', mtpt])
    if removeiso:
        os.remove(iso)

def get_mac_addresses(interface=''):
    process = subprocess.Popen(['/sbin/ifconfig'], stdout=subprocess.PIPE)
    retval = process.wait()
    if retval:
        raise RuntimeError, "ifconfig returned %d" % retval
    if interface:
        raise RuntimeError, "interface keyword is currently ignored"
    macs = []
    for line in process.stdout:
        if line.startswith('eth'):
            columns = [c.strip() for c in line.split()]
            mac = 'hwaddr_%s' % columns[4].replace(':', '_')
            macs.append(mac)
    return macs


if __name__ == '__main__':
    macs = get_mac_addresses()
    

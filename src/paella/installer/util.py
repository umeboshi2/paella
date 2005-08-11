import os
from os.path import join
import tempfile
import commands
from time import sleep

from useless.base import Error
from useless.base.util import makepaths, runlog, echo
from paella.debian.base import RepositorySource

from base import Modules


def make_interfaces_simple(target):
    i = file(os.path.join(target, 'etc/network/interfaces'), 'w')
    i.write('auto lo eth0\n')
    i.write('iface lo inet loopback\n')
    i.write('iface eth0 inet dhcp\n')
    i.write('\n\n')
    i.close()

def mount_tmp():
    os.system('mount -t tmpfs tmpfs /tmp')

def backup_target_command(target, tarball):
    exclude = "--exclude './proc/*'"
    tarcmd = 'bash -c "tar -c %s ' % exclude
    tarcmd += '-C %s . > %s"' % (target, tarball)
    return tarcmd

def remove_debs(target):
    archives = 'var/cache/apt/archives'
    debs = os.path.join(target, archives, '*.deb')
    pdebs = os.path.join(target, archives, 'partial', '*.deb')
    return runlog('rm %s %s -f' % (debs, pdebs))
    
def extract_tarball_orig(target, tarball):
    here = os.getcwd()
    print 'extracting with tar'
    os.chdir(target)
    if tarball[-2:] == 'gz':
        opts = 'xzf'
    elif tarball[-3:] == 'bz2':
        opts = 'xjf'
    else:
        opts = 'xf'
    runlog('tar %s %s' % (opts, tarball))
    os.chdir(here)

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

def make_sources_list(cfg, target, suite):
    section = 'debrepos'
    aptdir = os.path.join(target, 'etc', 'apt')
    makepaths(aptdir)
    sources_list = file(os.path.join(aptdir, 'sources.list'), 'w')
    source = RepositorySource()
    source.uri = cfg.get('installer', 'http_mirror')
    source.suite = suite
    source.set_path()
    sources_list.write(str(source) +'\n')
    source.type = 'deb-src'
    sources_list.write(str(source) +'\n')
    source.type = 'deb'
    if suite == 'woody' or cfg.has_option(section, '%s_nonus' % suite):
        source.suite += '/non-US'
        sources_list.write(str(source) +'\n')
        source.type = 'deb-src'
        sources_list.write(str(source) +'\n')
    loption = suite + '_local'
    if cfg.has_option(section, loption) and cfg.get(section, loption) == 'true':
        sources_list.write('deb %s/local %s/\n' % (source.uri, suite))
        sources_list.write('deb-src %s/local %s/\n' % (source.uri, suite))
    coption = suite + '_common'
    if cfg.has_option(section, coption) and cfg.get(section, coption) == 'true':
        sources_list.write('deb %s/local common/\n' % source.uri)
        sources_list.write('deb-src %s/local common/\n' % source.uri)
    sources_list.write('\n')
    sources_list.close()


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

def make_fstab(fstabobj, target):
    fstab = file(os.path.join(target, 'etc/fstab'), 'w')
    fstab.write(str(fstabobj))
    fstab.close()

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

def make_filesystem(device, fstype):
    if fstype == 'reiserfs':
        cmd = 'mkreiserfs -f -q %s' % device
    elif fstype == 'ext3':
        cmd = 'mkfs.ext3 -F -q %s' % device
    elif fstype == 'ext2':
        cmd = 'mkfs.ext2 -F -q %s' % device
    else:
        raise Error,  'unhandled fstype %s '  % fstype
    echo(cmd)
    runlog(cmd, keeprunning=True)


#this is done after bootstrap or
#this is done after extracting the base tar
def ready_base_for_install(target, cfg, suite, fstabobj):
    set_root_passwd(target, myline)
    make_sources_list(cfg, target, suite)
    make_interfaces_simple(target)
    make_fstab(fstabobj, target)
    

def setup_modules(target, modules):
    mfile = Modules(os.path.join(target, 'etc/modules'))
    for m in modules:
        mfile.append(m)
    mfile.write()
    
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

def reverse_ip(ip):
    octets = ip.split('.')
    octets.reverse()
    return '.'.join(octets)

    
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
    mntcmd = 'mount -t iso9660 -o loop %s %s' % (iso, mtpt)
    os.system(mntcmd)
    cpcmd = 'cp -a %s/* %s' % (mtpt, install_path)
    os.system(cpcmd)
    os.system('umount %s' % mtpt)
    if removeiso:
        os.remove(iso)
        
def get_mac_addresses():
    if os.getuid():
        raise Error, 'must be root to use get_mac_addresses'
    i, o = os.popen2('ifconfig')
    macs = []
    for line in o:
        if line.startswith('eth'):
            columns = [c.strip() for c in line.split()]
            mac = 'hwaddr_%s' % columns[4].replace(':', '_')
            macs.append(mac)
    return macs

def make_fake_start_stop_daemon(target):
    daemon = join(target, 'sbin/start-stop-daemon')
    os.rename(daemon, '%s.REAL' % daemon)
    if os.path.isfile(daemon):
        raise Error, '%s should not exist' % daemon
    fakescript = file(daemon, 'w')
    fakescript.write('#!/bin/sh\n')
    fakescript.write('echo\n')
    fakescript.write('echo "Warning: Fake start-stop-daemon called, doing nothing"\n')
    fakescript.close()
    if os.system('chmod 755 %s' % daemon):
        raise Error, 'problem changing permissions on %s' % daemon

def remove_fake_start_stop_daemon(target):
    daemon = join(target, 'sbin/start-stop-daemon')
    real = '%s.REAL' % daemon
    if not os.path.isfile(real):
        raise Error, '%s does not exist' % real
    os.remove(daemon)
    os.rename(real, daemon)
    
def make_script(name, data, target, execpath=False):
    """This function creates a script in the tmp directory
    on the target system.  If execpath is True, the path
    that is returned can be passed to chroot command, else
    the full path to the script is returned.
    """
    exec_path = join('/tmp', name + '-script')
    target_path = join(target, 'tmp', name + '-script')
    sfile = file(target_path, 'w')
    sfile.write(data.read())
    sfile.close()
    os.system('chmod 755 %s' % target_path)
    if not execpath:
        return target_path
    else:
        # for chroot target exec_path
        return exec_path
    

def setup_disk_fai(disk_config, logpath,
                   script='/usr/lib/paella/scripts/setup_harddisks_fai'):
    fileid, disk_config_path = tempfile.mkstemp('paella', 'diskinfo')
    disk_config_file = file(disk_config_path, 'w')
    disk_config_file.write(disk_config)
    disk_config_file.close()
    options = '-X -f %s' % disk_config_path
    env = 'env LOGDIR=%s diskvar=%s' % (logpath, join(logpath, 'diskvar'))
    command = '%s %s %s' % (env, script, options)
    return runlog(command)
    
def make_filesystems(device, fsmounts, env):
    mddev = False
    if device == '/dev/md':
        mdnum = 0
        mddev = True
    for row in fsmounts:
        if mddev:
            pdev = '/dev/md%d' % mdnum
            mdnum += 1
        else:
            pdev = dev + str(row.partition)
        if row.mnt_name in env.keys():
            echo('%s held' % row.mnt_name)
        elif row.fstype == 'swap':
            runlog('echo making swap on %s' % pdev)
            runvalue = runlog('mkswap %s' % pdev)
            if runvalue:
                raise Error, 'problem making swap on %s' % pdev
        else:
            echo('making filesystem for %s' % row.mnt_name)
            make_filesystem(pdev, row.fstype)
            
def partition_disk(dump, device):
    i, o = os.popen2('sfdisk %s' % device)
    i.write(dump)
    i.close()

def create_raid_partition(devices, pnum, mdnum, raidlevel=1):
    opts = '--create /dev/md%d' % mdnum
    opts = '%s --force -l%d -n%d' % (opts, raidlevel, len(devices))
    devices = ['%s%d' % (device, pnum) for device in devices]
    cmd = 'mdadm %s %s' % (opts, ' '.join(devices))
    yes = 'bash -c "yes | %s' % cmd
    return runlog(yesman)

def create_mdadm_conf(target, devices):
    mdpath = join(target, 'etc/mdadm')
    makepaths(mdpath)
    mdconfname = join(mdpath, 'mdadm.conf')
    mdconf = file(mdconfname, 'w')
    devices = ['%s*' % d for d in devices]
    nl = '\n'
    line = 'DEVICE %s' % ' '.join(devices)
    mdconf.write(line + nl)
    arrdata = commands.getoutput('mdadm -E --config=%s -s' % mdconfname)
    mdconf.write(arrdata + nl)
    mdconf.write(nl)
    mdconf.close()
    
def wait_for_resync():
    mdstat = file('/proc/mdstat').read()
    while mdstat.find('resync') > -1:
        sleep(2)
        mdstat = file('/proc/mdstat').read()

def mount_target(target, mounts, device):
    mounts = [m for m in mounts if int(m.partition)]
    if mounts[0].mnt_point != '/':
        raise Error, 'bad set of mounts', mounts
    mddev = False
    mdnum = 0
    if device == '/dev/md':
        mddev = True
        pdev = '/dev/md0'
        mdnum += 1
    else:
        pdev = '%s%d' % (device, mounts[0].partition)
    runlog('echo mounting target %s to %s' % (pdev, target))
    runlog('mount %s %s' % (pdev, target))
    mounts = mounts[1:]
    mountable = [m for m in mounts if m.fstype != 'swap']
    for mnt in mountable:
        tpath = os.path.join(target, mnt.mnt_point[1:])
        makepaths(tpath)
        if mddev:
            pdev = '/dev/md%d' % mdnum
        else:
            pdev = '%s%d' % (device, mnt.partition)
        mdnum += 1
        runlog('echo mounting target %s to %s' % (pdev, tpath))
        runlog('mount %s %s' % (pdev, tpath))
        
def makedev(target, devices=['generic']):
    here = os.getcwd()
    os.chdir(join(target, 'dev'))
    for dev in devices:
        echo('making device %s with MAKEDEV' % dev)
        runlog('./MAKEDEV %s' % dev)
    os.chdir(here)
    
def mount_target_proc(target, umount=False):
    tproc = join(target, 'proc')
    cmd = 'mount --bind /proc %s' % tproc
    if umount:
        cmd = 'umount -l %s' % tproc
    return runlog(cmd)
    

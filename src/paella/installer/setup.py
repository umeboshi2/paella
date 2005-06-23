import os, sys, os.path
from os.path import join

from useless.db.midlevel import StatementCursor
from paella.installer.base import get_suite, InstallerConnection, PaellaConfig

#this is all old fai code

def probe_hardware(modules):
    os.system('modprobe -a %s' % ' '.join(modules))

def setup(conn):
    cu = CurrentEnvironment(conn, os.environ['HOSTNAME'])
    cu.update(os.environ)
    os.environ.update(cu)
    probe_hardware(['ide-probe-mod', 'ide-disk', 'ide-cd'])
    os.system('set_disk_info')
    os.system('save_dmesg')
    os.system('mount paella:/mirrors/debian/sid-mirror /mirrors/debian')
    os.environ['DNSDOMAIN'] = cu['DOMAIN']
    os.system('/usr/sbin/sshd')
    os.system('openvt -c2 /bin/bash')
    os.system('openvt -c3 /bin/bash')
    cu.update(os.environ)
    os.environ.update(cu)
    
def setup_harddrives(conn):
    cu = CurrentEnvironment(conn, os.environ['HOSTNAME'])
    cu.update(os.environ)
    logdir = cu['LOGDIR']
    diskvar = cu['diskvar']
    cu['classes'] = 'DEFAULT'
    os.environ.update(cu)
    disk_config = '/fai/disk_config/DEFAULT'
    input, output = os.popen2('setup_harddisks -d -X -f %s' %disk_config)
    format = file(join(logdir, 'format.log'),'w')
    format.write(output.read())
    format.close()

def mount_disks(conn):
    cu = CurrentEnvironment(conn, os.environ['HOSTNAME'])
    cu.update(os.environ)
    os.environ.update(cu)
    fstab = join(cu['LOGDIR'], cu['fstab'])
    if isfile(fstab):
        os.system('mount2dir %s %s' % (cu['target'], fstab))

def mount_mirrors(conn):
    cu = CurrentEnvironment(conn, os.environ['HOSTNAME'])
    cu.update(os.environ)
    os.environ.update(cu)
    root = cu['target']
    makepaths(root, 'mirrors', 'debian')
    makepaths(root, 'mirrors', 'common')
    makepaths(root, 'mirrors', 'bkups')
    makepaths(root, 'mirrors', 'share')
    mirror = cu['FAI_DEBMIRROR']
    mount = join(root, 'mirrors', 'debian')
    os.system('mount -o ro,nolock %s %s' %(mirror, mount))
    

need_old_code = False
if need_old_code:
    hostname = os.environ['HOSTNAME']
    
    if hostname == 'bailey':
        profile = 'fufu'
    else:
        profile = hostname
    
    cfg = PaellaConfig()
    conn = InstallerConnection()

    pfile = file('/tmp/fai/PAELLA_PROFILE', 'w')
    pfile.write(profile+'\n')
    pfile.close()
    os.environ['PAELLA_PROFILE'] = profile

    suite = get_suite(conn, profile)
    
    print 'SUITE is %s!!!!!' % suite
    goahead = True

    if goahead:
        for task in ['defclass', 'defvar', 'action']:
            os.system('skiptask %s' %task)


        diskvar = os.environ['diskvar']

        os.environ['SUITE'] = suite
        setup_harddrives()
        

        if os.path.isfile(diskvar):
            print parse_vars(diskvar)
        else:
            print 'NO DISK VAR'
            print 'NO DISK VAR'
            print 'NO DISK VAR'
            print 'NO DISK VAR'
            if 'fstab' not in os.environ:
                os.environ['fstab'] = 'fstab'
            os.system('task mountdisks')
            os.system('task extrbase')
            os.system('task mirror')
            os.system('task updatebase')
            os.system('task instsoft')








if __name__ == 'foobar':
    pass


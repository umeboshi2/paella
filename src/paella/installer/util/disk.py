import os
import tempfile
import commands
from time import sleep

from useless.base.util import makepaths

from paella.installer.base import runlog

#from paella import deprecated

def setup_disk_fai(disk_config, logpath,
                   script='/usr/lib/paella/scripts/setup_harddisks_fai'):
    fileid, disk_config_path = tempfile.mkstemp('paella', 'diskinfo')
    disk_config_file = file(disk_config_path, 'w')
    disk_config_file.write(disk_config)
    disk_config_file.close()
    #options = '-X -f %s' % disk_config_path
    options = ['-X', '-f', disk_config_path]
    #env = 'env LOGDIR=%s diskvar=%s' % (logpath, os.path.join(logpath, 'diskvar'))
    env = ['env', 'LOGDIR=%s' % logpath,
           'diskvar=%s' % os.path.join(logpath, 'diskvar')
           ]
    # use this to keep script running on machines
    # that don't reread the partition table properly
    os.environ['sfdisk'] = '--no-reread'
    
    #command = '%s %s %s' % (env, script, options)
    command = env + [script] + options
    return runlog(command)

# this function is hardly used anymore
# but it may be resurrected, as it allows
# the admin to maintain a specific
# partition table
def partition_disk(dump, device):
    i, o = os.popen2('sfdisk %s' % device)
    i.write(dump)
    i.close()
    
##############################
# these raid functions below haven't
# been used or tested since long before
# etch was stable
##############################

def create_raid_partition(devices, pnum, mdnum, raidlevel=1):
    opts = '--create /dev/md%d' % mdnum
    opts = '%s --force -l%d -n%d' % (opts, raidlevel, len(devices))
    devices = ['%s%d' % (device, pnum) for device in devices]
    cmd = 'mdadm %s %s' % (opts, ' '.join(devices))
    yes = 'bash -c "yes | %s"' % cmd
    return runlog(yes)

def create_mdadm_conf(target, devices):
    mdpath = os.path.join(target, 'etc/mdadm')
    makepaths(mdpath)
    mdconfname = os.path.join(mdpath, 'mdadm.conf')
    mdconf = file(mdconfname, 'w')
    devices = ['%s*' % d for d in devices]
    nl = '\n'
    line = 'DEVICE %s' % ' '.join(devices)
    mdconf.write(line + nl)
    mdconf.close()
    arrdata = commands.getoutput('mdadm -E --config=%s -s' % mdconfname)
    mdconf = file(mdconfname, 'a')
    mdconf.write(arrdata + nl)
    mdconf.write(nl)
    mdconf.close()
    

def check_for_resync():
    mdstat = file('/proc/mdstat').read()
    return mdstat.find('resync') > -1

def wait_for_resync():
    mdstat = file('/proc/mdstat').read()
    while mdstat.find('resync') > -1:
        sleep(2)
        mdstat = file('/proc/mdstat').read()

